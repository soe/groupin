from handlers import AbstractHandler

from google.appengine.api import users

class Index(AbstractHandler):
    def get(self):
        
        # if user is not logged in yet
        if not users.get_current_user():
            # welcome page
            template_vars = {'where': 'Index', 'login_url': users.create_login_url('/')}
            self._output_template('welcome.html', **template_vars)
            return

        # user is logged in but not an admin
        if not users.is_current_user_admin():
            # unauthorized page
            template_vars = {'where': 'Administration', 'email': users.get_current_user().email(), 'logout_url': users.create_logout_url('/'), }
            self._output_template('unauthorized.html', **template_vars)
            return
            
        if users.is_current_user_admin():
            # admin page
            self.redirect('/support')
            return           