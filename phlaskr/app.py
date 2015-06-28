from api import api
from front import front
from app_factory import get_app
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug import run_simple
from cache import make_secret_key
from htmlmin.middleware import HTMLMinMiddleware
import os


#application.register_blueprint(front)
#application.register_blueprint(api)

runserver = lambda host,port,app: run_simple(host,port,app,use_debugger=True,use_reloader=True)
if not os.environ.get('TESTING'):
    from gevent.pywsgi import WSGIServer
    run_server = lambda host,port,app: WSGIServer((host,port),app).serve_forever()

#front.config['DATABASE_URI'] = 'sqlite:///test3.db'
#api.config['DATABASE_URI'] = 'sqlite:///test3.db'

#application = DispatcherMiddleware(front,{
#    '/api/v1':api
#})


application = get_app('app',blueprints=dict(api=api,front=front))

if __name__ == "__main__":
    application.wsgi_app = HTMLMinMiddleware(application.wsgi_app)

    @application.before_first_request
    def set_secret():
        application.config['SECRET_KEY'] = make_secret_key()

    port = int(os.environ.get('PORT') or 8000)
    args = ['',port,application]
    run_server(*args)
