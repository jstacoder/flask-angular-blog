# coding: utf-8
from sqlalchemy import create_engine
from phlaskr.models import AppUser,UserProfile,Email,Post,Tag,Comment
from phlaskr.app import application as api

def start():
    AppUser._engine = create_engine(api.config.get('DATABASE_URI'),echo=True)
    AppUser.metadata.bind = AppUser._engine

def seed():

    content = {
            '1':'''
    Wow Youll never Guess !!!

    OMG!!!!
            ''',
            '2':'''
    Sometimes i think about all kinds of things

    I just never know where to start
            ''',
            '3':'''
    This was soooooo
    crazy, Im not sure
    if i beleive it myself.
            ''',
            '4':'''
    
    Now for some real magixc



    !!!!!!!
            '''
    }

    kyle = AppUser.get_new(username='admin',password='test')
    email = Email(address='test@test.com',app_user_id=kyle.id,user_type='app')
    email.save()
    tag = Tag.get_new(name='tag')
    post = Post.get_new(title='test post',content='fsfsfwsd',author_id=kyle.id,tags=[tag.id])
    post = Post.get_new(title='test post2',content='fsfsfwsd',author_id=kyle.id,tags=[tag.id])
    post = Post.get_new(title='test post3',content='fsfsfwsd',author_id=kyle.id,tags=[tag.id])
    post = Post.get_new(title='test post4',content='fsfsfwsd',author_id=kyle.id,tags=[tag.id])
    joel = AppUser.get_new(username='jstacoder',password='test')
    email = Email(address='jstacoder@test.com',app_user_id=joel.id,user_type='app')
    email.save()
    tag = Tag.get_new(name='tags')
    post = Post.get_new(title='First test post',content=content['1'],author_id=joel.id,tags=[tag.id])
    post = Post.get_new(title='Just my thoughts',content=content['2'],author_id=joel.id,tags=[tag.id])
    post = Post.get_new(title='Some crazy stuff',content=content['3'],author_id=joel.id,tags=[tag.id])
    post = Post.get_new(title='You Wont Beleive This',content=content['4'],author_id=joel.id,tags=[tag.id])

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
