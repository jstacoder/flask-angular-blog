from api import api
from front import front
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug import run_simple

application = DispatcherMiddleware(front,{
    '/api/v1':api
})


if __name__ == "__main__":
    run_simple('0.0.0.0',8000,application,use_debugger=True,use_reloader=True)
