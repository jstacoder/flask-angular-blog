import os
from flask import Flask,render_template,views,g,request
from models import AppUser
from app_factory import get_app
from itsdangerous import TimedJSONWebSignatureSerializer as signer

front  = get_app('front',static_folder='static',template_folder='templates',root_path=os.path.realpath(os.path.dirname(__file__)))

#front.config.DATABASE_URI = 'sqlite:///test3.db'

class IndexView(views.MethodView):
    def get(self,post_id=None,extra=None):
        return render_template('index.html')

def load_user(tkn):
    try:
        data = g.get('signer').loads(tkn)
    except:
        return redirect('/login')
    return AppUser.get_by_id(data['id'])

@front.before_request
def check_auth():
    g.signer = signer(front.config['SECRET_KEY'],60*60*24*7)
    if request.cookies.get('NGAPP_AUTH_TKN'):
        g.user = load_user(request.cookies.get('NGAPP_AUTH_TKN'))
        print g.user

front.add_url_rule(
    '/',
    'index',
    view_func = IndexView.as_view('index')
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

if __name__ == "__main__":
    front.run('0.0.0.0',8000,debug=True)
