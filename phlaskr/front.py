import os
from flask import Flask,render_template,views
from app_factory import get_app

front  = get_app('front',static_folder='static',template_folder='templates',root_path=os.path.realpath(os.path.dirname(__file__)))

#front.config.DATABASE_URI = 'sqlite:///test3.db'

class IndexView(views.MethodView):
    def get(self,post_id=None):
        return render_template('index.html')


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

if __name__ == "__main__":
    front.run('0.0.0.0',8000,debug=True)
