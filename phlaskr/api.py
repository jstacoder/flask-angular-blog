from flask import Flask,views,jsonify,request,make_response,json
from models import Post,Tag

api = Flask(__name__+'api',static_folder='static')

api.config['DATABASE_URI'] = 'sqlite:///test3.db'

def json_response(content):
    res = make_response(json.dumps(content))
    res.headers['Content-Type'] = 'application/json'
    return res


class TagView(views.MethodView):
    def get(self,tag_id=None):
        if tag_id is None:
            return json_response([dict(name=x.name,description=x.description,id=x.id) for x in Tag.get_all()])
        else:
            tag = Tag.get_by_id(tag_id)
            if tag:
                return json_response(name=tag.name,description=tag.description,id=tag.id)
        return json_response(['error']),404

class AddTagView(views.MethodView):
    def post(self):
        if 'application/json' in request.headers['Content-Type']:
            tag = Tag(**json.loads(request.data))
        else:
            tag = Tag(**dict(request.form.items()))
        tag.save()
        return json_response(dict(name=tag.name,description=tag.description,id=tag.id))

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

api.add_url_rule('/post','get_posts',view_func=PostView.as_view('get_posts'))
api.add_url_rule('/post/<int:post_id>','get_post',view_func=PostView.as_view('get_post'))
api.add_url_rule('/post/delete/<int:post_id>','delete_post',view_func=DeletePostView.as_view('delete_post'))
api.add_url_rule('/tag','get_tags',view_func=TagView.as_view('get_tags'))
api.add_url_rule('/tag/<int:tag_id>','get_tag',view_func=TagView.as_view('get_tag'))
api.add_url_rule('/tag/add','add_tag',view_func=AddTagView.as_view('add_tag'))

if __name__ == "__main__":
    api.run(host='0.0.0.0',port=8000,debug=True)
