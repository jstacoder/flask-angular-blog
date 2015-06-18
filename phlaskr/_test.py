# coding: utf-8
from sqlalchemy import create_engine
from models import AppUser,UserProfile
AppUser._engine = create_engine('sqlite:///test3.db',echo=True)
user = AppUser.query.filter_by(username='kyle').first()
print repr(user.profile)
