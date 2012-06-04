from handlers import AbstractHandler

import gdata.gauth
import gdata.apps.groups.client

from google.appengine.api import memcache

from models import Configo

import settings
import logging

groups_client = gdata.apps.groups.client.GroupsProvisioningClient(domain=Configo.get('_domain', settings.config['GDATA']['DOMAIN']), source=settings.config['GDATA']['APP_NAME'])

class RequestToken(AbstractHandler):
    def get(self):
        # check for existing access token
           
        oauth_callback = 'http://%s/gdata/access_token' % self.request.host

        request_token = groups_client.GetOAuthToken(
            settings.config['GDATA']['SCOPES'], 
            oauth_callback, 
            settings.config['GDATA']['CONSUMER_KEY'], 
            consumer_secret=settings.config['GDATA']['CONSUMER_SECRET']
        )
        
        # save request token in memcache for later use for upgrading
        memcache.add(request_token.token, request_token)
        
        # redirect to google authorization page     
        self.redirect(str(request_token.generate_authorization_url()))
        
        
class AccessToken(AbstractHandler):
    def get(self):    
        request_token = gdata.gauth.AuthorizeRequestToken(memcache.get(self.request.get('oauth_token')), self.request.uri)
        
        # upgrade the request token to access token
        access_token = groups_client.GetAccessToken(request_token)
        
        # save access token in datastore for the user
        Configo.set('_gdata_token', access_token.token)
        Configo.set('_gdata_token_secret', access_token.token_secret)
        
        self.redirect('/admin/config')
        

class RevokeToken(AbstractHandler):
    def get(self):
        groups_client.auth_token = get_auth_token(Configo.get('_gdata_token'), Configo.get('_gdata_token_secret'))
        
        try:
            groups_client.RevokeToken()

            # also delete from datastore
            Configo.set('_gdata_token', None)
            Configo.set('_gdata_token_secret', None)
            
        except:
            pass
            
        self.redirect('/admin/config')
        
                            
def get_auth_token(token, secret):                              
    try:
        auth_token = gdata.gauth.OAuthHmacToken(
            settings.config['GDATA']['CONSUMER_KEY'], 
            settings.config['GDATA']['CONSUMER_SECRET'], 
            token, 
            str(secret), 
            gdata.gauth.ACCESS_TOKEN
        )
        
        return auth_token
    except:
        return None
