from settings import configs
import os
from flask import Flask


def get_app(name,cfg=None,*args,**kwargs):
    if cfg is None:
        if os.environ.get('APP_CONFIG'):
            cfg = os.environ.get('APP_CONFIG')
        else:
            cfg = 'dev'
    app = Flask(name,*args,**kwargs)
    app.config.from_object(configs[cfg])
    return app

