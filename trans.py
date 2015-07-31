
def fmt_url(url):
    driver,rest = url.split('://')
    user,rest = rest.split(':')
    pw,rest = rest.split('@')
    host =  rest.split('/')[0]
    #print rest
    db = rest.split('/')[-1]
    return host,user,pw,db

def get_cmd(url):
    return 'mysql -h {} -u"{}" -p"{}" "{}"'.format(fmt_url(url))



