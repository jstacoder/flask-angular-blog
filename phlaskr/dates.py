from execjs import get
from datetime import datetime

rt = get()


ctx = rt.compile('''
        function getDate(dte){
            var d = new Date(dte);
            return d.toJSON();
        }
''')


def test():
    print ctx.call('getDate',"Sun, 21 Jun 2015 21:49:44 GMT")

def format_date(dte):
    return ctx.call('getDate',(dte if not isinstance(dte,datetime) else dte.ctime()))


