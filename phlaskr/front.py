from flask import Flask,render_template,views

front  = Flask(__name__+'front',static_folder='static')

front.config.DATABASE_URI = 'sqlite:///test3.db'

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
