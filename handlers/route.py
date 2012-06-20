from handlers import AbstractHandler

from models import Configo, Status
from google.appengine.api import users

from pubnub import Pubnub

import logging
import settings

## pubnub
pubnub = Pubnub(
    'pub-91077960-1dd7-4875-83c4-c8fd5c634bee', 
    'sub-786b929e-bab1-11e1-b880-a3fb466a40d5',
    'sec-YWNjYmIxZmYtZTVkZS00ZGNlLTk0NWUtYWRhZTk5OGUzN2Y1',
    False
)

class Create(AbstractHandler):
    def get(self):
        uuid = self.request.get('uuid')
        channel = self.request.get('channel')
        
        resp = {}
        resp['status'] = True
        resp['counselor'] = {
            'id': '12345',
            'name': 'Jennifer Anniston',
            'avatar': 'https://super-support/static/img/avatar.png',
            'organization': 'Holywood'
        }

        # publish the command
        info = pubnub.publish({
            'channel' : 'counselor-12345',
            'message' : {
                'action': 'create',
                'uuid': uuid,
                'channel' : channel
            }
        })
        
        self._json_response(resp)

class Remove(AbstractHandler):
    def get(self):
        uuid = self.request.get('uuid')
        channel = self.request.get('channel')
        
        resp = {}
        
        # publish the command
        info = pubnub.publish({
            'channel' : 'counselor-12345',
            'message' : {
                'action': 'remove',
                'uuid': uuid,
                'channel' : channel
            }
        })
        
        self._json_response(resp)