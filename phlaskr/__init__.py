from api import api
from front import front
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug import run_simple
import os


runserver = lambda app,host,port: run_simple(host,port,app,use_debugger=True,use_reloader=True)
if not os.environ.get('TESTING'):
    from gevent.pywsgi import WSGIServer
    run_server = lambda app,host,port: WSGIServer((host,port),app).serve_forever()


#front.config['DATABASE_URI'] = 'sqlite:///test3.db'
#api.config['DATABASE_URI'] = 'sqlite:///test3.db'

application = DispatcherMiddleware(front,{
    '/api/v1':api
})


if __name__ == "__main__":
    run_server('0.0.0.0',8000,application)
