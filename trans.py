
def fmt_url(url):
    driver,rest = url.split('://')
    user,rest = rest.split(':')
    pw,rest = rest.split('@')
    host =  rest.split('/')[0]
    #print rest
    db = rest.split('/')[-1]
    return 'mysql -h {} -u"{}" -p"{}" "{}"'.format(host,user,pw,db)


def test():
    print fmt_url('mysql://be25ddb77ed3c5:0267a63b@us-cdbr-iron-east-02.cleardb.net/heroku_f25b2c47865568e?reconnect=true')


