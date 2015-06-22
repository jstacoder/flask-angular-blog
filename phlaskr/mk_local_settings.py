#!/usr/bin/env python
import os

filedata = '''class LocalConfig(object):
    pass
'''

open('local_settings.py','w').write(filedata)
