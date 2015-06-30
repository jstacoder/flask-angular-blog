from flask import Flask,views,jsonify,request,make_response,json,g,redirect,abort,g,current_app
from ..models import Comment,Post,Tag,Email,AppUser as User,PublicUser
from itsdangerous import TimedJSONWebSignatureSerializer as signer
from ..app_factory import get_app
from ..cache import set_cache,get_cache,make_secret_key,get_key,cache_response,check_cache

api = get_app('api',is_bp=True,static_folder='static',url_prefix='/api/v1')

#check_cache = api.before_request(check_cache)
#cache_response = api.after_request(cache_response)


def get_data():
    print 'here'
    return json.loads(request.data) if request.data else dict(request.form.items())


def json_response(content):
    res = make_response(json.dumps(content))
    res.set_cookie('SECRET_KEY',current_app.config.get('SECRET_KEY'))
    res.headers['Content-Type'] = 'application/json'
    return res

def load_user(tkn):
    try:
        data = g.get('signer').loads(tkn)
    except:
        return redirect('/login')
    return AppUser.get_by_id(data['id'])

@api.before_request
def check_auth():
    g.signer = signer(current_app.config['SECRET_KEY'],60*60*24*7)
    if request.cookies.get('NGAPP_AUTH_TKN'):
        g.user = load_user(request.cookies.get('NGAPP_AUTH_TKN'))
        print g.user


@api.before_request
def cache_response():
    print request.path
    print get_key(request.path)


class TagView(views.MethodView):
    def get(self,tag_id=None):
        if tag_id is None:
            return json_response([dict(name=x.name,description=x.description,id=x.id) for x in Tag.get_all()])
        else:
            tag = Tag.get_by_id(tag_id)
            if tag:
                return json_response(dict(name=tag.name,description=tag.description,id=tag.id))
        return json_response(['error']),404

class AddTagView(views.MethodView):
    def post(self):
        if 'application/json' in request.headers['Content-Type']:
            tag = Tag(**json.loads(request.data))
        else:
            tag = Tag(**dict(request.form.items()))
        tag.save()
        return json_response(dict(name=tag.name,description=tag.description,id=tag.id))


class PostListView(views.MethodView):
    def get(self,user_id=None,tag_id=None):
        if user_id is not None:
            return json_response([x.to_json() for x in User.get_by_id(user_id).posts]),200

    def post(self,user_id=None):
        user_id = user_id or (g.get('user') and getattr(g.get('user'),'id') or None)
        if user_id is not None:
            return json_response([x.to_json() for x in User.get_by_id(user_id).posts]),200


class PostView(views.MethodView):
    def get(self,post_id=None):
        if post_id is None:
            return json_response(map(lambda x: x.to_json(),Post.get_all()))
        return jsonify(Post.get_by_id(post_id).to_json())

    def post(self,post_id=None):
        #print request.data
        #print request.json
        if 'application/json' in request.headers['Content-Type']:
            print json.loads(request.data)
            data = json.loads(request.data)
            p = Post.query.filter_by(title=data.get('title')).first()
            print '---->>>>',p
            post =\
                Post.query.filter_by(title=json.loads(request.data).get('title')).first() or\
                    (
                            Post.get_by_id(post_id) if\
                                    post_id is not None else\
                                        Post(**json.loads(request.data)
                                    )
                            )
        else:
            print dict(request.form.items())
            post = Post.get_by_id(post_id) if post_id is not None else Post(**dict(request.form.items()))
        post.update()
        return json_response(post.to_json())


class DeletePostView(views.MethodView):
    def post(self,post_id):
        result = [dict(success=False),404]
        post = Post.get_by_id(post_id)
        if post is not None:
            post.delete()
            result[0]['success'] = True
            result[1] = 200
        return jsonify(result[0]),result[1]

    def delete(self,post_id):
        result = [dict(success=False),404]
        post = Post.get_by_id(post_id)
        if post is not None:
            post.delete()
            result[0]['success'] = True
            result[1] = 200
        return jsonify(result[0]),result[1]



class LoginView(views.MethodView):
    def post(self):

        data = json.loads(request.data) if request.data else dict(request.form.items())
        open('log3','w').write(json.dumps(data))
        email = Email.query.filter_by(address=data.get('email')).first()
        if email is None:
            return json_response({'error':'email does not exist'}),404
        else:
            if email.user.check_password(data.get('password')):
                tkn = g.signer.dumps(email.user.to_json())
                response = make_response(json.dumps(dict(token=tkn)))
                response.headers['Content-Type'] = 'application/json'
                response.set_cookie('NGAPP_AUTH_TKN',tkn,expires=60*60*24)
                return response
            else:
                return json_response({'error':"incorrect login"}),403

class AddCommentView(views.MethodView):
    def post(self):
        return json_response(Comment.get_new(**get_data()).to_json())

class RegisterUserView(views.MethodView):
    def post(self):
        if 'application/json' in request.headers['Content-Type']:
            data = json.loads(request.data)
        else:
            data = dict(request.form.items())
        print data
        if not user_exists(data['username']):
            if not email_exists(data['email']):
                rtn = json_response(User.get_new(**data).to_json())
            else:
                rtn = json_response(dict(error=True,message="email in use"))
        else:
            rtn = json_response(dict(error=True,message="username in use"))
        return rtn,200

class AddPublicUserView(views.MethodView):
    def post(self):
        data = get_data()
        print data
        open('log2','w').write(json.dumps(data))
        if not email_exists(data.get('email')):
            rtn = json_response(PublicUser.get_new(**data).to_json())
        else:
            rtn = json_response(dict(error=True,message="email in use"))
        return rtn,200

def user_exists(username,public=False):
    user = ((public and PublicUser) or User).query.filter_by(username=username).first()
    return user is not None

def email_exists(email):
    return Email.query.filter(Email.address==email).first() is not None

api.add_url_rule('/post','get_posts',view_func=PostView.as_view('get_posts'))
api.add_url_rule('/post/<int:post_id>','get_post',view_func=PostView.as_view('get_post'))
api.add_url_rule('/post/delete/<int:post_id>','delete_post',view_func=DeletePostView.as_view('delete_post'))
api.add_url_rule('/post/<int:post_id>','int_delete_post',view_func=DeletePostView.as_view('int_delete_post'))
api.add_url_rule('/tag','get_tags',view_func=TagView.as_view('get_tags'))
api.add_url_rule('/tag/<int:tag_id>','get_tag',view_func=TagView.as_view('get_tag'))
api.add_url_rule('/tag/add','add_tag',view_func=AddTagView.as_view('add_tag'))
api.add_url_rule('/login','login',view_func=LoginView.as_view('login'))
api.add_url_rule('/comment/add','add_comment',view_func=AddCommentView.as_view('add_comment'))
api.add_url_rule('/user/add','add_user',view_func=RegisterUserView.as_view('add_user'))
api.add_url_rule('/user/<int:user_id>/posts','user_posts',view_func=PostListView.as_view('user_posts'))
api.add_url_rule('/user/posts','user__posts',view_func=PostListView.as_view('user__posts'))
api.add_url_rule('/public/add','add_public',view_func=AddPublicUserView.as_view('add_public'))


if __name__ == "__main__":
    api.run(host='0.0.0.0',port=8000,debug=True)
