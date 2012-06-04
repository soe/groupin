from handlers import AbstractHandler
from handlers.gdata_oauth import groups_client, get_auth_token

from models import Configo, Status

from google.appengine.api import files, taskqueue, users
from google.appengine.ext import blobstore

import settings
import logging
from datetime import datetime

class Test(AbstractHandler):
    """Accept post request with CSV file"""
    def get(self):
        if not users.is_current_user_admin():
            self.redirect('/')
            return
            
        template_vars = {
            'app_name': settings.APP_NAME,

            'submitted': self.request.get('submitted'),
            
            'logout_url': users.create_logout_url('/'),
            'where': 'Test Service'
        }

        self._output_template('test.html', **template_vars)
        
class Post(AbstractHandler):
    """Accept post request with CSV file"""
    def get(self):
        self.response.set_status(405)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('GET Method not allowed')
                
    def post(self):
        error = check_service_request(self.request.get('token'), self.request.remote_addr)
        
        if error:
            self.response.set_status(401)
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write('Request unauthorized:' + error)
        else:
            # write to blobstore
            ref = datetime.now().strftime('%d/%m %H:%M:%S')
            
            csv = self.request.POST['csv']
            
            if(self.request.get('test')):
                csv = lambda: None
                setattr(csv, 'value', self.request.get('csv'))
                setattr(csv, 'filename', 'test.csv')
                setattr(csv, 'type', 'text/csv')
            
            if not csv.value:
                logging.debug('#GroupIn: at %s, blank or no file is posted' % (ref))
                self.response.set_status(406)
                self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write('No file attached or blank file')
                return
                
            # todo - check for empty file
            
            # Create the blob
            csv_blob = files.blobstore.create(mime_type='text/csv')

            # Open the file and write to it
            with files.open(csv_blob, 'a') as f:
                f.write(csv.value)

            # Finalize the file. Do this before attempting to read it.
            files.finalize(csv_blob)

            # Get the file's blob key
            blob_key = files.blobstore.get_blob_key(csv_blob)
            
            logging.info('#GroupIn: at %s, csv file, %s, is posted and stored to blob: %s' % (ref, csv.filename, blob_key))
            
            # also store to datastore to keep track of status
            s = Status.get_or_insert(ref + ' - ' + csv.filename)
            s.filename = csv.filename                
            s.blob_key = blob_key
            s.put()
            
            # add to task queue
            taskqueue.add(queue_name = 'QueueProcess', url = '/service/queue_process', params = {
                'ref': ref, 
                'blob_key': blob_key, 
                'filename': csv.filename,
            }, method = 'GET', )
            
            if(self.request.get('test')):
                self.redirect('/admin/test?submitted=1')
                return
            
            self.response.set_status(202)
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write('Accepted to be proccessed')

class QueueProcess(AbstractHandler):
    """Process CSV file in blobstore upon call from task queue """
    def get(self):
        groups_client.auth_token = get_auth_token(Configo.get('_gdata_token'), Configo.get('_gdata_token_secret'))

        ref = self.request.get('ref')
        blob_key = self.request.get('blob_key')
        filename = self.request.get('filename')
        
        users_groups = {}
        groups = []
        
        status = 1
        comment = []
        
        # get blob by blob_key
        csv_blob = blobstore.BlobReader(blob_key)

        # to skip the first line
        csv_blob.readlines(1)

        # parse blob
        for line in csv_blob:
            l = line.split(',')
            if(len(l) > 1):
                groups.append(l[1].split('@')[0].strip())
                users_groups.setdefault(l[0].strip(), []).append(l[1].split('@')[0].strip())
        
        #comment.append('#GroupIn: BlobKey - %s' % (blob_key))        
        #logging.info('#GroupIn: BlobKey - %s' % (blob_key)) 
        
        comment.append('#GroupIn: Ref - %s' % (ref))   
        logging.info('#GroupIn: Ref - %s' % (ref)) 
        
        comment.append('#GroupIn: QueueProcess parsed out %d users' % (len(users_groups)))
        logging.info('#GroupIn: QueueProcess parsed out %d users' % (len(users_groups)))
        
        # add groups which do not exist
        _groups = set([g.GetGroupName().lower() for g in groups_client.RetrieveAllGroups().entry])
        groups = set(groups)
        groups_to_create = []
        
        if len(groups) > len(_groups): groups_to_create = list(groups - _groups)

        for group in groups_to_create:
            logging.debug('#GroupIn: CreateGroup - %s' % (group))
            try:
                groups_client.CreateGroup(group, group)
            except Exception, e:
                status = handle_exception(e)
                    
                    
        for user, user_groups in users_groups.items():
            user_groups_x = []
            
            # first find out what to delete by reconciling
            logging.debug('#GroupIn: RetrieveGroups - %s' % (user))
            try:
                # existing groups
                _groups = groups_client.RetrieveGroups(user, direct_only=False)

                for g in _groups.entry:
                    g = g.GetGroupName().lower()

                    if g in user_groups: user_groups.remove(g) # don't add as it exists already
                    else: user_groups_x.append(g) # remove it!    
            except Exception, e:
                status = handle_exception(e)
                # todo - error here usually means user is not there - create user?
            
            
            # RemoveMemberFromGroup 
            for group_x in user_groups_x:
                logging.debug('#GroupIn: RemoveMemberFromGroup - %s, %s' % (group_x, user)) 
                try:
                    groups_client.RemoveMemberFromGroup(group_x, user)
                except Exception, e:
                    status = handle_exception(e)
            
            
            # AddMemberToGroup     
            for group in user_groups:
                logging.debug('#GroupIn: AddMemberToGroup - %s, %s' % (group, user)) 
                try:
                    groups_client.AddMemberToGroup(group, user)
                except Exception, e:
                    status = handle_exception(e)
         
           
        if status > 1:
            comment.append('Some warnings/errors have occured, check AppEngine log for more details. Filter out by #GroupIn: Ref - %s' % ref)
            
        # also store to datastore to keep track of status
        s = Status.get_or_insert(ref + ' - ' + filename)                       
        s.status = status
        s.comment = '<br />'.join(comment)
        s.put()

def handle_exception(e):
    try:
        e.message.index('1301')
        logging.warning(e.message.strip())
        return 2
    except:
        logging.error(e.message.strip())
        return 3
           
def check_service_request(token, ip):
    """Check token and ip address against those defined in config
    if both values don't match return error
    """
    error = ''
    
    # check if remote ip is in the allowed ips list
    if Configo.get('_allowed_ips', '*') != '*':
        if not ip in map(str.strip, str(Configo.get('_allowed_ips')).split(',')):
            error += ' <Your IP, '+ ip +', is not whitelisted>'
            
    # build up error message to be returned
    if token != Configo.get('_service_token', '53cr3t'):
        error += ' <Service token doesn\'t match>'

    return None if not len(error) else error