import os
import sys
venv = os.path.realpath(os.path.join(os.path.dirname(os.path.dirname(__file__)),'venv','lib','python2.7','site-packages'))
sys.path.insert(0,venv)
import flask
import unittest
from flask_testing import TestCase
from models import AppUser,Post,Tag
from seed_db import reset
import json
from app_factory import get_app
from api import api
from front import front
from types import MethodType

if int(getattr(__import__('platform'),'python_version_tuple')()[1]) == 6:
    def assert_in(self,x,y):
        assert x in y
    TestCase.assertIn = MethodType(assert_in,None,TestCase)

TEST_EMAIL = 'test@t.com'
TEST_USERNAME = 'hank'
TEST_PW = 'cccc'

os.environ['APP_CONFIG'] = 'test'

class ApiTest(TestCase):

    def setUp(self):
        reset()
        AppUser.engine.echo = False

    def tearDown(self):
        AppUser.metadata.drop_all()
        AppUser.session.close()

    def create_app(self):
        return get_app('app',cfg='test',blueprints=dict(api=api,front=front))

    def _add_post(self):
        return self.client.post('/api/v1/post',data=dict(title='test title',content='klksdlkjsdklj',author_id=1,tags=[]))

    def _add_comment(self,post_data):
        return self.client.post('/api/v1/comment/add',data=dict(author_id=1,subject='testing',post_id=post_data['id'],content='test'))

    def _add_comment_reply(self,comment_data):
        return self.client.post('/api/v1/comment/add',data=dict(author_id=1,subject='testing',post_id=comment_data['post_id'],content='test',parent_comment_id=comment_data['id']))

    def _get_post(self,post_id):
        return json.loads(self.client.get('/api/v1/post/{0}'.format(post_id)).get_data())

        
    def test_added_comment_exists(self):
        post = json.loads(self._add_post().get_data())
        cmts = post['comments']
        cmt = self._add_comment(post)
        post = self._get_post(post['id'])
        self.maxDiff = None
        self.assertEquals(json.loads(cmt.get_data())['id'],post['comments'][0]['id'])

    def test_add_comment(self):
        post = json.loads(self._add_post().get_data())
        cmt = self._add_comment(post)
        self.assertIn('application/json',cmt.content_type)

    def test_add_comment_reply(self):
        post = json.loads(self._add_post().get_data())
        cmt = json.loads(self._add_comment(post).get_data())
        reply = self._add_comment_reply(cmt)
        self.assert200(reply)

    def test_add_comment_reply_exists(self):
        post = json.loads(self._add_post().get_data())
        cmt = json.loads(self._add_comment(post).get_data())
        reply = self._add_comment_reply(cmt)
        post = self._get_post(post['id'])
        self.assertEquals(len(post['comments'][0]['children']),1)
        
    def test_get_posts(self):
        res = self.client.get('/api/v1/post')
        self.assert200(res)

    def test_json(self):
        res = self.client.get('/api/v1/post')
        self.assertIn('application/json',res.content_type)

    def test_add_post(self):
        post_count = len(Post.get_all())
        res = self.client.post('/api/v1/post',data=dict(title='test title',content='klksdlkjsdklj',author_id=1,tags=[]))
        self.assertEquals(len(Post.get_all()),post_count+1)

    def test_add_user(self):
        count = AppUser.query.count()
        res = self.client.post('/api/v1/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        self.assertEqual(len(AppUser.get_all()),count+1)

    def test_user_exists(self):
        count = AppUser.query.count()
        self.client.post('/api/v1/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        res = self.client.post('/api/v1/user/add',data=dict(email='xxsdssx@yyy.com',username='hank',password='xxxx'))
        self.assertEqual(len(AppUser.get_all()),count+1)

    def test_email_exists(self):
        count = AppUser.query.count()
        self.client.post('/api/v1/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        res = self.client.post('/api/v1/user/add',data=dict(email='xxx@yyy.com',username='hanssssk',password='xxxx'))
        self.assertEqual(len(AppUser.get_all()),count+1)

    def test_user_pw(self):
        res = self.client.post('/api/v1/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        user = AppUser.get_by_id(json.loads(res.get_data()).get('id'))
        self.assertTrue(user.check_password('xxxx'))

    def test_user_pw_fail(self):
        res = self.client.post('/api/v1/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        user = AppUser.get_by_id(2)
        self.assertFalse(user.check_password('xsssxxx'))

    def test_get_post(self):
        res = self.client.get('/api/v1/post/1')
        post = json.loads(res.get_data())
        self.assertEqual(post['id'],1)

    def test_delete_post(self):
        post_count = len(Post.get_all())
        res = self.client.post('/api/v1/post/delete/1')
        self.assertEqual(len(Post.get_all()),post_count-1)

    def test_get_tags(self):
        _tags = map(lambda x: dict(name=x.name,description=x.description,id=x.id),Tag.get_all())
        res = self.client.get('/api/v1/tag')
        tags = json.loads(res.get_data())
        self.assertEqual(tags,_tags)

    def test_get_tag(self):
        test_name = 'test'
        tag = Tag.get_new(name=test_name)
        res = self.client.get('/api/v1/tag/{0}'.format(tag.id))
        _tag = json.loads(res.get_data())
        self.assertEqual(tag.to_json(),_tag)

    def test_login(self):
        res = self.client.post('/api/v1/user/add',data=dict(email=TEST_EMAIL,username=TEST_USERNAME,password=TEST_PW))
        self.assert200(res)
        res = self.client.post('/api/v1/login',data=dict(email=TEST_EMAIL,password=TEST_PW))
        self.assert200(res)

    def test_add_public_user(self):
        res = self.client.post('/api/v1/public/add',data=dict(email=TEST_EMAIL,password=TEST_PW,username='tester'))
        self.assert200(res)

    def test_get_user_posts(self):
        user = AppUser.get_all()[0]
        res = self.client.post('/api/v1/user/{0}/posts'.format(user.id))
        posts = json.loads(res.get_data())
        self.assertEqual(posts,map(lambda x: x.to_json(),user.posts.all()))

    def test_public_user_login(self):
        self.client.post('/api/v1/public/add',data=dict(email=TEST_EMAIL,password=TEST_PW,username='tester'))
        res = self.client.post('/api/v1/login',data=dict(email=TEST_EMAIL,password=TEST_PW))
        self.assert200(res)


def main():
    """Runs the unit tests without coverage."""
    tests = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == "__main__":
    main()
