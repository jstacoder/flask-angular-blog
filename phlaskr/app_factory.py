from settings import configs
import os
from flask import Flask,Blueprint


def get_app(name,cfg=None,is_bp=False,*args,**kwargs):
    blueprints = None
    if not is_bp:
        # this is our actual app to configure
        if os.environ.get('APP_CONFIG'):
            cfg = os.environ.get('APP_CONFIG')
        else:
            cfg = 'dev'
        if 'blueprints' in kwargs:
            blueprints = kwargs.pop('blueprints')
        rtn = Flask(name,*args,**kwargs)
        rtn.config.from_object(configs[cfg])
        if blueprints is not None:
            for bp in blueprints:
                rtn.register_blueprint(blueprints[bp])
    else:
        rtn = Blueprint(__name__+'_'+name,name,*args,**kwargs)
    return rtn
