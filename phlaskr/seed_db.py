# coding: utf-8
from sqlalchemy import create_engine
from models import AppUser,UserProfile,Email,Post,Tag,Comment
from api import api

def start():
    AppUser._engine = create_engine(api.config.get('DATABASE_URI'),echo=True)
    AppUser.metadata.bind = AppUser._engine

def seed():
    kyle = AppUser.get_new(username='jstacoder',password='test')
    email = Email(address='kyle@level2designs.com',user_id=kyle.id)
    email.save()
    tag = Tag.get_new(name='tag')
    post = Post.get_new(title='test post',content='fsfsfwsd',author_id=kyle.id,tags=[tag.id])

def reset():
    ctx = api.test_request_context()
    ctx.push()
    start()
    AppUser.metadata.drop_all()
    AppUser.metadata.create_all()
    seed()
    ctx.pop()

if __name__ == "__main__":
    reset()
