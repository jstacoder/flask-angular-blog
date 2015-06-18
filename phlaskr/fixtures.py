from faker import Factory
from models import Post,Tag
from sqlalchemy import create_engine

fake = Factory().create()

def add_post():
    title = fake.bs()
    content = fake.paragraph()
    return Post(title=title,content=content).save()

def add_tag():
    name = fake.word()
    description = fake.sentence()
    return Tag(name=name,description=description).save()

def add_tag_to_post(tag,post):
    post.tags.append(tag)
    post.save()

Post._engine = create_engine('sqlite:///test3.db',echo=True)

def main():
    posts = [add_post() for x in range(10)]
    tags = [add_tag() for x in range(10)]
    for i in range(len(posts)):
        add_tag_to_post(tags[i],posts[i])


if __name__ == "__main__":
    main()
