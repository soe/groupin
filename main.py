# imports
import webapp2
import settings

import sys
sys.path.append('libs')

# routes
routes = [    
    # welcome page
    ('/', 'handlers.index.Index'),
    
    # support
    ('/support', 'handlers.support.Support'),
    
    # route
    ('/route/create', 'handlers.route.Create'),
    
]

app = webapp2.WSGIApplication(
    routes = routes,
    debug = settings.DEBUG,
    config = settings.config,
)
