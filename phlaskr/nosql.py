from bcrypt import hashpw,gensalt,checkpw
from faker import Factory
from mongoengine import (
        Document,StringField,IntField,
        DateTimeField,DictField,ListField,
        EmbeddedDocumentField,ReferenceField,
        EmbeddedDocument,connect,BooleanField,
        GenericReferenceField,ObjectIdField
)


conn = connect(db='new6')
faker = Factory().create()

class Email(EmbeddedDocument):
    _id = ObjectIdField(required=True)
    address = StringField()

    meta = {
        'id_field':'_id'
    }

class Profile(EmbeddedDocument):
    _id = ObjectIdField(required=True)
    first_name = StringField()
    last_name = StringField()
    meta = {
        'id_field':'_id'
    }

class User(Document):
    _id = ObjectIdField(required=True)
    date_added = DateTimeField()
    username = StringField(max_length=255)
    emails = ListField(EmbeddedDocumentField(Email))
    is_public = BooleanField()
    _pwhash = StringField()

    def __init__(self,*args,**kwargs):
        if 'password' in kwargs:
            kwargs['_pwhash'] = hashpw(kwargs.pop('password'),gensalt())
        super(User,self).__init__(*args,**kwargs)

    @property
    def id(self):
        return self._id

    def check_pw(self,pw):
        return checkpw(self._pwhash,pw)

    meta = {
            'allow_inheritence' : True,
            'abstract':True,
            'id_field':'_id'
    }

class AppUser(User):
    friends = ListField(ReferenceField('self'))
    profile = EmbeddedDocumentField(Profile)

class PublicUser(User):
    is_public = True

class Tag(EmbeddedDocument):
    _id = ObjectIdField(required=True)
    name = StringField()
    post = ReferenceField('Post')
    meta = {
        'id_field':'_id'
    }

class Comment(EmbeddedDocument):
    _id = ObjectIdField(required=True)
    author = ReferenceField(User)
    parent = GenericReferenceField()
    subject = StringField()
    text = StringField()
    children = ListField(ReferenceField('self'))
    meta = {
        'id_field':'_id'
    }

class Post(Document):
    _id = ObjectIdField(required=True)
    author = ReferenceField(User)
    title = StringField()
    content = StringField()
    tags = ListField(EmbeddedDocumentField(Tag))
    comments = ListField(EmbeddedDocumentField(Comment))
    meta = {
        'id_field':'_id'
    }


models = dict(
    app_user=AppUser,
    post=Post,
    public_user=PublicUser
)

def seed_model(model_name,*args,**kwargs):
    return models[model_name](*args,**kwargs).save(validate=False,cascade=True)

def seed_post(user):
    rtn = seed_model(
            'post',
            author=user,
            content=faker.text(),
    )
    tags = [Tag(name=faker.slug(),post=rtn) for x in range(5)]
    comments = [Comment(author=user,parent=rtn,subject=faker.bs(),text=faker.text(),children=[]) for x in range(10)]
    map(rtn.comments.append,comments)
    map(rtn.tags.append,tags)
    return rtn

def seed_public_user():
    return seed_model(
        'public_user',
        username=faker.user_name(),
            emails = map(
                    lambda x: Email(
                            address = faker.email()
                    ) ,range(4)
            ),is_public = False,
            password = 'test'
    )

def seed_app_user():
    return seed_model(
            'app_user',
            username = faker.user_name(),
            emails = map(
                    lambda x: Email(
                            address = faker.email()
                    ) ,range(4)
            ),is_public = False,
            password = 'test'
    )

def seed_db():
    for x in range(20):
        user = seed_app_user()
        post = seed_post(user)
        pu = seed_public_user()

if __name__ == "__main__":
    seed_db()
    '''

    
    print User.objects(name='joe').first().name


    kyle =\
        User.objects(name='kyle').count() and\
        User.objects(name='kyle').get() or\
        User(name='kyle').save()

    joe =\
        User.objects(name='joe').count() and\
        User.objects(name='joe').get() or\
        User(name='joe').save()
    
    if not joe in kyle.friends:
        print 'adding joe to friends'
        kyle.friends.append(joe)

    post = Post(author=kyle,title='test',content='xcxxxx',tags=[Tag(name='xxx'),Tag(name='ttt'),Tag(name='vvv')])


    print kyle.name
    print kyle.friends
    print kyle.friends[0].name
    print Post.objects.all()
    print [t.name for t in Tag.objects.all()]
    


    print User.objects

    '''
