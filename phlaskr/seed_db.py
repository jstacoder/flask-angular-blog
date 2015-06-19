# coding: utf-8
from sqlalchemy import create_engine
from models import AppUser,UserProfile,Email
from api import api

def start():
    api.test_request_context().push()
    AppUser._engine = create_engine('sqlite:///test3.db',echo=True)
    AppUser.metadata.bind = AppUser._engine

def seed():
    kyle = AppUser.get_new(username='jstacoder',password='testing')
    email = Email(address='kyle@level2designs.com',user_id=kyle.id)
    email.save()

def reset():
    start()
    AppUser.metadata.drop_all()
    AppUser.metadata.create_all()
    seed()

if __name__ == "__main__":
    reset()
