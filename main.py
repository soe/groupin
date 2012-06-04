# imports
import webapp2
import settings

import sys
sys.path.append('libs')

# routes
routes = [    
    # welcome page
    ('/', 'handlers.index.Index'),
    
    # service
    ('/service/test', 'handlers.service.Test'),
    ('/service/post', 'handlers.service.Post'),
    ('/service/queue_process', 'handlers.service.QueueProcess'),
    
    # gdata - oauth
    ('/gdata/authorize', 'handlers.gdata_oauth.RequestToken'), # just to make it looks good
    ('/gdata/request_token', 'handlers.gdata_oauth.RequestToken'),
    ('/gdata/access_token', 'handlers.gdata_oauth.AccessToken'),
    ('/gdata/unauthorize', 'handlers.gdata_oauth.RevokeToken'), # just to make it looks good
    ('/gdata/revoke_token', 'handlers.gdata_oauth.RevokeToken'),
    
    # admin
    ('/admin/config', 'handlers.admin.Config'),
    ('/admin', 'handlers.admin.Index'),
    ('/admin/test', 'handlers.service.Test'),
    
]

app = webapp2.WSGIApplication(
    routes = routes,
    debug = settings.DEBUG,
    config = settings.config,
)
