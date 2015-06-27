from redis import Redis
import pickle
import json
from hashlib import new
from random import random
import os
from flask import request,make_response,g

type_key = lambda key: 'content_type:{0}'.format(key)

_key = lambda x: 'FLASKNGBLOG2:{0}'.format(x)

def convert_uri_to_args(uri):
    if uri is None:
        return False
    trash,remainder = uri.split('://')
    login,host_info = remainder.split('@')
    user,pw = login.split(':')
    host,port = host_info.split(':')
    return dict(
        host=host,
        port=port,
        db=0,
        password=pw
    )

cache = Redis(
    **convert_uri_to_args(
                os.environ.get('HEROKU')\
                and 'redis://rediscloud:hQUeCl0o4Az3pLS2@pub-redis-17658.us-east-1-3.4.ec2.garantiadata.com:17658'
    ) or {}
)

def cache_response(res):
    if  request.method == 'GET':
        print 'checking cached'
        cached = g.get('cached')
        if cached:
            print 'We just pulled from the cache, so we shouldnt recache this'
            return res
        print 'We just loaded this response, so were going to cache it'
        key = _key(new('md5',request.path).hexdigest())
        res.direct_passthrough = False
        cache.set(key,res.get_data(),ex=60)
        print 'caching result with key - {0}'.format(key)
    return res
    


def check_cache():
    if  request.method == 'GET':
        print 'unsetting cached'
        g.cached = False
        print 'checking cache'
        key = _key(new('md5',request.path).hexdigest())
        result = cache.get(key)
        if result:
            print 'found {0} in cache'.format(key)
            g.cached = True
            print 'setting cached'
            res = make_response(result)
            try:
                json.loads(result)
                res.headers['Content-Type'] = 'application/json'
            except:
                pass
            return res





def cache_response_data(res):
    result = res.get_data()
    content_type = res.content_type
    key = hash(result)
    content_key = type_key(key)
    if set_cache(content_key,content_type):
        if set_cache(key,result):
            return key        
    return False
    
def get_cached_response(key):
    result = None
    content_type = get_cache(type_key(key))
    if content_type and 'application/json' in content_type:
        result = json.loads(get_cache(key))
    else:
        result = get_cache(key)
    return result
  
alg = 'md5'

def make_secret_key():
    return new(alg,str(random())).hexdigest()

def set_cache(key,val):
    key = get_key(key)
    val = pickle.dumps(val)
    return cache.set(key,val,ex=60*5)

def get_cache(key):
    key = get_key(key)
    itm = cache.get(key)
    if itm is not None:
        return pickle.loads(itm)
    return None

def get_key(val):
    return new(alg,val).hexdigest()

