from sqlalchemy.ext.declarative import declarative_base,declared_attr
from functools import partial
from flask import current_app,json
from inflection import pluralize, underscore
from jinja2 import Environment
from bcrypt import checkpw,gensalt,hashpw
import sqlalchemy as sa


_engine = lambda DB_URI: sa.create_engine(DB_URI,echo=True)

def get_base():
    base = declarative_base()
    base._sess = sa.orm.scoped_session(sa.orm.sessionmaker(
        )
    )
    return base

class classproperty(object):
    def __init__(self,getter):
        self.getter = getter

    def __get__(self,instance,owner):
        return self.getter(owner)

class DateMixin(object):
    __abstract__ = True

    @declared_attr
    def date_added(self):
        return sa.Column(sa.DateTime,default=sa.func.now())

    @declared_attr
    def date_modified(self):
        return sa.Column(sa.DateTime,default=sa.func.now(),onupdate=sa.func.now())

class BaseModel(get_base()):
    __abstract__ = True
    _engine = None
    _session = None

    @declared_attr
    def id(self):
        return sa.Column(sa.Integer,primary_key=True)

    @declared_attr
    def __tablename__(self):
        return pluralize(underscore(self.__name__))

    @classproperty
    def engine(cls):
        if cls._engine is None:
            BaseModel._engine = _engine(current_app.config.get('DATABASE_URI'))
            cls.metadata.bind = cls._engine
        return cls._engine

    @classproperty
    def session(cls):
        if BaseModel._session is None:
            BaseModel._session = BaseModel._sess()
            BaseModel._session.bind=cls.engine
        return BaseModel._session

    @classproperty
    def query(cls):
        return cls.session.query(cls)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_new(cls,**kwargs):
        return cls(**kwargs).save()

    @classmethod
    def get_by_id(cls,item_id):
        return cls.query.filter(cls.id==item_id).first()

    def save(self):
        self.session.add(self)
        self.session.commit()
        return self

    def update(self):
        return self.save()

    def delete(self):
        self.session.delete(self)
        return self in self.session.deleted and\
            self.session.commit()

'''
class UserPasswordHash(DateMixin,BaseModel):
    __tablename__ = 'user_passwords'

    user_id = sa.Column(sa.Integer,sa.ForeignKey('app_users.id'),nullable=False)
    _hash = sa.Column(sa.Text,nullable=False)

    @property
    def hash(self):
        return 'private'

    @hash.setter
    def hash(self,data):
        self._hash = data

    def __init__(self,*args,**kwargs):
        if not 'user_id' in kwargs:
            raise UserMissingException
        self.user_id = kwargs.pop('user_id')
        self._hash = hashpw(kwargs.pop('hash') or kwargs.pop('_hash'),gensalt())
        super(UserPasswordHash,self).__init__(*args,**kwargs)

    def check(self,pw):
        return checkpw(pw,self._hash)

'''

class Post(BaseModel):
    _env = None
    _context = {}

    title = sa.Column(sa.String(255),nullable=False)#,unique=True)
    _content = sa.Column(sa.Text)
    use_jinja = sa.Column(sa.Boolean,default=False)
    date_added = sa.Column(sa.DateTime,default=sa.func.now())
    date_modified = sa.Column(sa.DateTime,default=sa.func.now(),onupdate=sa.func.now())
    tags = sa.orm.relationship('Tag',lazy='dynamic',secondary="posts_tags")
    comments = sa.orm.relationship('Comment',lazy='dynamic')

    def __init__(self,*args,**kwargs):
        if 'content' in kwargs:
            self._content = kwargs.pop('content')
        if 'tags' in kwargs and kwargs.get('tags'):
            print kwargs.get('tags')
            tags = kwargs.pop('tags')
            if type(tags) == unicode:
                tags = json.loads(tags)
            print tags
            print type(tags)
            for t in tags:
                if t is not None:
                    tag = Tag.get_by_id(int(t))
                if tag:
                    self.tags.append(tag)
        self._env = Environment()
        self._context = {}
        super(Post,self).__init__(*args,**kwargs)

    def add_comment(self,*args,**kwargs):
        comment = Comment(post_id=self.id,**kwargs).save()
        return self


    @property
    def slug(self):
        return self.title.lower().replace(' ','_').replace(':','').replace('-','').replace('.','')

    @property
    def content(self):
        rtn = self._content
        if self.use_jinja:
            rtn = self._env.from_string(self._content).render(**self._context)
        return rtn

    @content.setter
    def content(self,data):
        self._content = data
        self.update()

    def to_json(self):
        return dict(
            title=self.title,
            slug=self.slug,
            content=self.content,
            date_added=self.date_added,
            id=self.id,
            tags=[x.name for x in self.tags.all()],
            comments=[x.to_json() for x in self.comments.all()]
        )

    def _add_to_ctx(self,key,val):
        self._context[key] = val

    def __repr__(self):
        return '<Post:{}'.format(self.slug)


class Email(BaseModel):

    __table_args__ = (
        (sa.UniqueConstraint('address','user_id')),
    )

    address = sa.Column(sa.String(255))
    user_data_id = sa.Column(sa.Integer,sa.ForeignKey('user_profiles.id'))
    user_id = sa.Column(sa.Integer,sa.ForeignKey('app_users.id'))


    def to_json(self):
        return dict(
            address=self.address,
            user_id=self.user_id
        )


    @property
    def user(self):
        return AppUser.get_by_id(self.user_id)


class UserProfile(BaseModel):

    first_name = sa.Column(sa.String(255))
    last_name = sa.Column(sa.String(255))
    age = sa.Column(sa.Integer)
    date_added = sa.Column(sa.DateTime,default=sa.func.now())
    location = sa.Column(sa.String(255))
    emails = sa.orm.relationship('Email',backref=sa.orm.backref('user_profile'),lazy='dynamic')

    def __repr__(self):
        return (
                'FirstName:{:^20}\nLastName:{:^20}\n'
                'Age:{!s:^20}\nDate:{!s:^20}\nLocation:{:^20}\n'
               ).format(
                    self.first_name,self.last_name,
                    self.age,self.date_added,self.location
               )

class AppUser(BaseModel):

    emails = sa.orm.relationship('Email',lazy='dynamic')
    username = sa.Column(sa.String(255),unique=True,nullable=False)
    user_profile_id = sa.Column(sa.Integer,sa.ForeignKey('user_profiles.id'))
    profile = sa.orm.relationship('UserProfile',uselist=False,backref=sa.orm.backref('user'))
    _pwhash = sa.Column(sa.Text)#sa.orm.relationship('UserPasswordHash')
    #_pwid = sa.Column(sa.Integer,sa.ForeignKey('user_passwords'))

    def __repr__(self):
        return str(self.username)

    def __init__(self,*args,**kwargs):
        if 'password' in kwargs:
            self.pwhash = kwargs.pop('password')
        super(AppUser,self).__init__(*args,**kwargs)
        self.profile = UserProfile(id=self.id).save()

    @property
    def pwhash(self):
        raise ValueError

    @pwhash.setter
    def pwhash(self,data):
        self._pwhash = hashpw(data,gensalt())

    def check_password(self,pw):
        return checkpw(pw,self._pwhash)

    def to_json(self):
        return dict(
            username=self.username,
            id=self.id,
            emails=[x.to_json() for x in self.emails.all()]
        )


class Tag(BaseModel):

    name = sa.Column(sa.String(255),unique=True,nullable=False)
    description = sa.Column(sa.Text)

    #relationships
    posts = sa.orm.relationship('Post',
                                lazy='dynamic',
                                secondary='posts_tags'
    )

class Comment(BaseModel):

    subject = sa.Column(sa.String(255))
    post_id = sa.Column(sa.Integer,sa.ForeignKey('posts.id'))
    parent_comment_id = sa.Column(sa.Integer,sa.ForeignKey('comments.id'))
    date_added = sa.Column(sa.DateTime,default=sa.func.now())

    content = sa.Column(sa.Text)
    author_id = sa.Column(sa.Integer,sa.ForeignKey('app_users.id'))
    author = sa.orm.relationship('AppUser',backref=sa.orm.backref('comments',lazy='dynamic'))

    replys = sa.orm.relationship('Comment')
    parent = sa.orm.relationship('Comment',remote_side='Comment.parent_comment_id',uselist=False)
    post = sa.orm.relationship('Post')

    def to_json(self):
        return dict(
            subject=self.subject,
            post_id=self.post_id,
            content=self.content,
            author=self.author and self.author.username or '',
            id=self.id,
            children=[x.to_json() for x in self.replys],
            parent=self.parent_comment_id,
            date=self.date_added
        )


posts_tags =\
    sa.Table(
        'posts_tags',
        BaseModel.metadata,
        sa.Column('post_id',sa.Integer,sa.ForeignKey('posts.id')),
        sa.Column('tag_id',sa.Integer,sa.ForeignKey('tags.id'))
)
