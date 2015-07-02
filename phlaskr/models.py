from sqlalchemy.ext.declarative import declarative_base,declared_attr
from functools import partial
from flask import current_app,json
from inflection import pluralize, underscore
from jinja2 import Environment
from bcrypt import checkpw,gensalt,hashpw
import sqlalchemy as sa
from dates import format_date


_engine = lambda DB_URI,echo=False: sa.create_engine(DB_URI,echo=echo)

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

class PasswordHashMixin(object):
    #__abstract__ = True

    _pwhash = sa.Column(sa.Text)

    @property
    def pwhash(self):
        raise ValueError

    @pwhash.setter
    def pwhash(self,data):
        self._pwhash = hashpw(data,gensalt())

    def check_password(self,pw):
        return checkpw(pw,self._pwhash)

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

    @classmethod
    def get(cls,*args,**kwargs):
        return cls.get_by_id(*args,**kwargs)

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

class Page(BaseModel):
    
    name = sa.Column(sa.String(255),unique=True)
    post_id = sa.Column(sa.Integer,sa.ForeignKey('posts.id'))
    _content = sa.Column(sa.Text)
    post = sa.orm.relation('Post',uselist=False)
    
    
    def __init__(self,*args,**kwargs):
        if not 'content' in kwargs and not 'post_id' in kwargs:
            raise ValueError('need either content or post')
        if 'content' in kwargs:
            self._content = kwargs.pop('content')
        super(Page,self).__init__(*args,**kwargs)        
    
    @property
    def content(self):
        if self._content is None:
            return self.post.content
        return self._content


class Post(BaseModel):
    _env = None
    _context = {}

    author_id = sa.Column(sa.Integer,sa.ForeignKey('app_users.id'),nullable=False)
    author = sa.orm.relationship('AppUser',backref=sa.orm.backref('posts',lazy='dynamic'),uselist=False)
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
            date_added=format_date(self.date_added),
            id=self.id,
            tags=[x.name for x in self.tags.all()],
            comments=[x.to_json() for x in self.comments.all()],
            author_id=self.author_id,
            author=self.author.username
        )


    def _add_to_ctx(self,key,val):
        self._context[key] = val

    def __repr__(self):
        return '<Post:{0}'.format(self.slug)


class Email(BaseModel):

    __table_args__ = (
        (
        sa.UniqueConstraint('address','app_user_id'),
        sa.UniqueConstraint('address','public_user_id'),)
)

    address = sa.Column(sa.String(255))
    user_data_id = sa.Column(sa.Integer,sa.ForeignKey('user_profiles.id'))
    app_user_id = sa.Column(sa.Integer,sa.ForeignKey('app_users.id'))
    user_type = sa.Column(sa.Enum('public','app',name='user_type'),default='public')
    public_user_id = sa.Column(sa.Integer,sa.ForeignKey('public_users.id'))

    def to_json(self):
        return dict(
            address=self.address,
            user_id=getattr(self,self.user_id_col)
        )

    @property
    def user_id_col(self):
        return '{0}_user_id'.format(self.user_type)

    @property
    def user(self):
        user_types = dict(app=AppUser,public=PublicUser)
        return user_types[self.user_type].get_by_id(getattr(self,self.user_id_col))


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

class AppUser(PasswordHashMixin,BaseModel):

    emails = sa.orm.relationship('Email',lazy='dynamic')
    username = sa.Column(sa.String(255),unique=True,nullable=False)
    user_profile_id = sa.Column(sa.Integer,sa.ForeignKey('user_profiles.id'))
    profile = sa.orm.relationship('UserProfile',uselist=False,backref=sa.orm.backref('user'))

    def __repr__(self):
        return str(self.username)

    def __init__(self,*args,**kwargs):
        if 'password' in kwargs:
            self.pwhash = kwargs.pop('password')
        if 'email' in kwargs:
            email = [Email(address=kwargs.pop('email'),user_type='app').save()]
            kwargs['emails'] = kwargs.get('emails') and (email + kwargs.pop('emails')) or email
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
            emails=[x.to_json() for x in self.emails.all()],
            is_public=False
        )


class Tag(BaseModel):

    name = sa.Column(sa.String(255),unique=True,nullable=False)
    description = sa.Column(sa.Text)

    #relationships
    posts = sa.orm.relationship('Post',
                                lazy='dynamic',
                                secondary='posts_tags'
    )

    def to_json(self):
        return dict(
            name=self.name,
            description=self.description,
            id=self.id
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
            author_email=self.author and ((hasattr(self.author,'email') and self.author.email) or hasattr(self.author,'emails') and self.author.emails[0]).address or '',
            id=self.id,
            children=[x.to_json() for x in self.replys],
            parent=self.parent_comment_id,
            date=format_date(self.date_added)
        )


class PublicUser(BaseModel,PasswordHashMixin):
    username = sa.Column(sa.String(255),unique=True,nullable=False)
    email_id = sa.Column(sa.Integer,sa.ForeignKey('emails.id'))
    email = sa.orm.relation('Email',foreign_keys='[PublicUser.email_id]')

    def __init__(self,*args,**kwargs):
        addr = None
        if 'password' in kwargs:
            self.pwhash = kwargs.pop('password')
        if 'email' in kwargs:
            addr = kwargs.pop('email')
            self.email = Email.get_new(address=addr,user_type='public')
        if not 'username' in kwargs:
            kwargs['username'] = self.email.address
        super(PublicUser,self).__init__(*args,**kwargs)
        self.save()
        self.email.public_user_id = self.id
        self.email.save()


    def to_json(self):
        return dict(
            username=self.username,
            id=self.id,
            email=self.email.address,
            is_public=True
        )

posts_tags =\
    sa.Table(
        'posts_tags',
        BaseModel.metadata,
        sa.Column('post_id',sa.Integer,sa.ForeignKey('posts.id')),
        sa.Column('tag_id',sa.Integer,sa.ForeignKey('tags.id'))
)
