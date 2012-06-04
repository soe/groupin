from handlers import AbstractHandler

from models import Configo, Status
from google.appengine.api import users

import logging
import settings

class Index(AbstractHandler):
    def get(self):
        status = self.request.get('status')
        
        statuses = Status.all()
        if(status): statuses.filter('status =', int(status))
        statuses.order('-created')
        statuses = statuses.fetch(100)

        template_vars = {
            'statuses': statuses,
            
            '_s_i': range(4),
            '_s_b_class': ['info', 'success', 'warning', 'danger'],
            '_s_l_class': ['info', 'success', 'warning', 'important'],
            '_s_text': ['Queued', 'Success', 'Warning', 'Error'],

            'app_name': settings.APP_NAME,
            'logout_url': users.create_logout_url('/'),
            'where': 'Queue Status'
        }

        self._output_template('admin.html', **template_vars)
            
        
        
class Config(AbstractHandler):
    def get(self):

        if not users.get_current_user():
            self.redirect('/')
            return
            
        # check if the user is admin
        if not users.is_current_user_admin():
            # unauthorized page
            template_vars = {'where': 'Configuration', 'email': users.get_current_user().email(), 'logout_url': users.create_logout_url('/'), }
            self._output_template('unauthorized.html', **template_vars)
            return

        
        template_vars = {
            'token_ok': Configo.get('_gdata_token') and Configo.get('_gdata_token_secret'),
            
            '_domain': Configo.get('_domain', settings.config['GDATA']['DOMAIN']),
            '_service_token': Configo.get('_service_token', '53cr3t'),
            '_allowed_ips': Configo.get('_allowed_ips', '*'),
            'saved': self.request.get('saved'),

            'app_name': settings.APP_NAME,
            'logout_url': users.create_logout_url('/'),
            'where': 'Configuration'
        }

        self._output_template('config.html', **template_vars)

    def post(self):
        if not users.is_current_user_admin():
            return
        
        #Configo.set('_gdata_token', self.request.get('_gdata_token'))
        #Configo.set('_gdata_token_secret', self.request.get('_gdata_token_secret'))
        Configo.set('_domain', self.request.get('_domain'))
        Configo.set('_service_token', self.request.get('_service_token'))
        Configo.set('_allowed_ips', self.request.get('_allowed_ips'))

        self.redirect('/admin/config?saved=1')
