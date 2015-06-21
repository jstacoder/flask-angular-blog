from api import api
from front import front
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug import run_simple
from gevent.pywsgi import WSGIServer

#front.config['DATABASE_URI'] = 'sqlite:///test3.db'
#api.config['DATABASE_URI'] = 'sqlite:///test3.db'

application = DispatcherMiddleware(front,{
    '/api/v1':api
})


if __name__ == "__main__":
    server = WSGIServer(('0.0.0.0',8000),application)
    server.serve_forever()
    #run_simple('0.0.0.0',8000,application,use_debugger=True,use_reloader=True)
