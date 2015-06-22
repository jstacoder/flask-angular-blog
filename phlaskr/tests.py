from flask_testing import TestCase,TwillTestCase
from models import AppUser,Post,Tag
import os
from seed_db import reset
import json
from api import api
from front import front


TEST_EMAIL = 'test@t.com'
TEST_USERNAME = 'hank'
TEST_PW = 'cccc'

os.environ['APP_CONFIG'] = 'test'

print api.config.get('DATABASE_URI')
class ApiTest(TestCase):

    def setUp(self):
        reset()

    def tearDown(self):
        AppUser.metadata.drop_all()
        AppUser.session.close()

    def create_app(self):
        #api.test_request_context().push()
        return api

    def test_get_posts(self):
        res = self.client.get('/post')
        self.assert200(res)

    def test_json(self):
        res = self.client.get('/post')
        self.assertTrue('application/json' in res.content_type)

    def test_add_post(self):
        post_count = len(Post.get_all())
        res = self.client.post('/post',data=dict(title='test title',content='klksdlkjsdklj',author_id=1,tags=[]))
        self.assertEquals(len(Post.get_all()),post_count+1)

    def test_add_user(self):
        count = AppUser.query.count()
        res = self.client.post('/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        self.assertEqual(len(AppUser.get_all()),count+1)

    def test_user_exists(self):
        count = AppUser.query.count()
        self.client.post('/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        res = self.client.post('/user/add',data=dict(email='xxsdssx@yyy.com',username='hank',password='xxxx'))
        self.assertEqual(len(AppUser.get_all()),count+1)

    def test_email_exists(self):
        count = AppUser.query.count()
        self.client.post('/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        res = self.client.post('/user/add',data=dict(email='xxx@yyy.com',username='hanssssk',password='xxxx'))
        self.assertEqual(len(AppUser.get_all()),count+1)

    def test_user_pw(self):
        res = self.client.post('/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        user = AppUser.get_by_id(json.loads(res.get_data()).get('id'))
        self.assertTrue(user.check_password('xxxx'))

    def test_user_pw_fail(self):
        res = self.client.post('/user/add',data=dict(email='xxx@yyy.com',username='hank',password='xxxx'))
        user = AppUser.get_by_id(2)
        self.assertFalse(user.check_password('xsssxxx'))

    def test_get_post(self):
        res = self.client.get('/post/1')
        post = json.loads(res.get_data())
        self.assertEqual(post['id'],1)

    def test_delete_post(self):
        post_count = len(Post.get_all())
        res = self.client.post('/post/delete/1')
        self.assertEqual(len(Post.get_all()),post_count-1)

    def test_get_tags(self):
        _tags = map(lambda x: dict(name=x.name,description=x.description,id=x.id),Tag.get_all())
        res = self.client.get('/tag')
        tags = json.loads(res.get_data())
        self.assertEqual(tags,_tags)

    def test_get_tag(self):
        test_name = 'test'
        tag = Tag.get_new(name=test_name)
        res = self.client.get('/tag/{0}'.format(tag.id))
        _tag = json.loads(res.get_data())
        self.assertEqual(tag.to_json(),_tag)

    def test_login(self):
        res = self.client.post('/user/add',data=dict(email=TEST_EMAIL,username=TEST_USERNAME,password=TEST_PW))
        self.assert200(res)
        res = self.client.post('/login',data=dict(email=TEST_EMAIL,password=TEST_PW))
        self.assert200(res)

    def test_add_public_user(self):
        res = self.client.post('/public/add',data=dict(email=TEST_EMAIL,password=TEST_PW,username='tester'))
        self.assert200(res)

