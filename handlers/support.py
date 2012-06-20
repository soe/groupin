from handlers import AbstractHandler

from models import Configo, Status
from google.appengine.api import users

import logging
import settings

class Support(AbstractHandler):
    def get(self):
        status = self.request.get('status')

        template_vars = {
            'app_name': settings.APP_NAME,
            'logout_url': users.create_logout_url('/'),
            'where': 'Support'
        }

        self._output_template('support.html', **template_vars)