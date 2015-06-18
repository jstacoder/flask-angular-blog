from mongoengine import (
        Document,StringField,IntField,
        DateTimeField,DictField,ListField,
        EmbeddedDocumentField,ReferenceField,
        EmbeddedDocument,connect
)

conn = connect(db='new3')

class Email(EmbeddedDocument):
    address = StringField()

class Profile(EmbeddedDocument):
    first_name = StringField()
    last_name = StringField()

class User(Document):
    name = StringField(max_length=255)
    friends = ListField(ReferenceField('self'))
    profile = EmbeddedDocumentField(Profile)
    emails = ListField(EmbeddedDocumentField(Email))

class Tag(EmbeddedDocument):
    name = StringField()

class Comment(EmbeddedDocument):
    author = ReferenceField(User)
    subject = StringField()
    text = StringField()

class Post(Document):
    author = ReferenceField(User)
    title = StringField()
    content = StringField()
    tags = ListField(EmbeddedDocumentField(Tag))
    comments = ListField(EmbeddedDocumentField(Comment))



def seed_db():    
    seed_posts()

def seed_users():
    return User(name='kyle',emails=[Email(address='kyle@level2designs.com')],profile=Profile(first_name='kyle',last_name='roux')).save()

def seed_posts():
    post = Post(author=seed_users(),title='post1',content='zzzzz',tags=[],comments=[]).save()



if __name__ == "__main__":
    #seed_db()

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

    kyle.save()


    print kyle.name
    print kyle.friends
    print kyle.friends[0].name
    '''


    print User.objects


