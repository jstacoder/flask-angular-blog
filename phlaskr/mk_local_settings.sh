#!/bin/bash

#echo -n 'class LocalConfig(object):\n\tpass\n' > local_settings.py
rm local_settings.py
vi local_settings.py <<x23LimitStringx23
i
class LocalConfig(object):
    pass

wq!
x23LimitStringx23
exit

