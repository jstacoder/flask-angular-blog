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
    post = Post.get_new(title='test post2',content='fsfsfwsd',author_id=kyle.id,tags=[tag.id])
    post = Post.get_new(title='test post3',content='fsfsfwsd',author_id=kyle.id,tags=[tag.id])
    post = Post.get_new(title='test post4',content='fsfsfwsd',author_id=kyle.id,tags=[tag.id])
    joel = AppUser.get_new(username='jr',password='test')
    email = Email(address='test@test.com',user_id=joel.id)
    email.save()
    tag = Tag.get_new(name='tags')
    post = Post.get_new(title='test postwww',content='fsfsfwsd',author_id=joel.id,tags=[tag.id])
    post = Post.get_new(title='test postwww2',content='fsfsfwsd',author_id=joel.id,tags=[tag.id])
    post = Post.get_new(title='test postwww3',content='fsfsfwsd',author_id=joel.id,tags=[tag.id])
    post = Post.get_new(title='test postwww4',content='fsfsfwsd',author_id=joel.id,tags=[tag.id])

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
