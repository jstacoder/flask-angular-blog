import os
from os import path as op
from flask import Flask,render_template,views,g,request,send_file,g,current_app
from ..models import AppUser
from ..app_factory import get_app
from itsdangerous import TimedJSONWebSignatureSerializer as signer
from ..cache import set_cache,get_cache,make_secret_key,get_key,cache_response,check_cache
from htmlmin import minify

front  = get_app(
            'front',
            is_bp = True,
            static_folder = 'static',
            template_folder = 'templates',
            root_path = os.path.realpath(
                                os.path.dirname(
                                    __file__
                                )
            ),
            url_prefix = ''
)

#check_cache = front.before_request(check_cache)
#cache_response = front.after_request(cache_response)

class IndexView(views.MethodView):
    def get(self,post_id=None,extra=None):
        rtn = send_file(
                    op.realpath(
                        op.join(
                            op.dirname(
                                op.dirname(
                                    __file__
                                )
                            ),
                            'templates',
                            'index.html'
                        )
                    )
                )
        rtn.direct_passthrough = False
        #rtn.data = minify(unicode(rtn.data))
        return rtn
        

class TestSpeedView(views.MethodView):
    def get(self):
        return send_file('./templates/index.html')

def load_user(tkn):
    try:
        data = g.get('signer').loads(tkn)
    except:
        return redirect('/login')
    return AppUser.get_by_id(data['id'])

@front.before_request
def check_auth():
    g.signer = signer(current_app.config['SECRET_KEY'],60*60*24*7)
    if request.cookies.get('NGAPP_AUTH_TKN'):
        g.user = load_user(request.cookies.get('NGAPP_AUTH_TKN'))
        print g.user

front.add_url_rule(
    '/',
    'index',
    view_func = IndexView.as_view('index')
)
front.add_url_rule(
        '/speed',
        'speed',
        view_func = TestSpeedView.as_view('speed')
)
front.add_url_rule(
    '/post/<post_id>',
    'post',
    view_func = IndexView.as_view('post')
)
front.add_url_rule(
    '/posts',
    'posts',
    view_func = IndexView.as_view('posts')
)
front.add_url_rule(
    '/post/add',
    'post_add',
    view_func = IndexView.as_view('post_add')
)
front.add_url_rule(
    '/login',
    'login',
    view_func = IndexView.as_view('login')
)
front.add_url_rule(
    '/logout',
    'logout',
    view_func = IndexView.as_view('logout')
)
front.add_url_rule(
    '/register',
    'register',
    view_func = IndexView.as_view('register')
)
front.add_url_rule(
    '/settings',
    'settings',
    view_func = IndexView.as_view('settings')
)
front.add_url_rule(
    '/user/<path:extra>',
    'user_extra',
    view_func = IndexView.as_view('user_extyra')
)
front.add_url_rule(
    '/admin',
    'admin',
    view_func = IndexView.as_view('admin')
)
front.add_url_rule(
    '/admin/<path:extra>',
    'admin_page',
    view_func = IndexView.as_view('admin_page')
)
if __name__ == "__main__":
    front.run('0.0.0.0',8000,debug=True)
