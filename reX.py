#!/usr/bin/python
import re
import pprint

line = '192.168.0.85 - - [14/Jul/2014:16:15:05 +0200] "POST /ds/dasd HTTP/1.1" 200 812 "-" "-""'

searchObj = re.search( r'([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}) - - \[([0-9][0-9]/[A-Z][a-z]{2}/[0-9]{4}:[0-9][0-9]:[0-9][0-9]:[0-9][0-9]) \+0200] "[A-Z]{0,4} /([a-z\.?=]*).* HTTP/1.[01]" ([0-9]{3})', line, re.M|re.I)

if searchObj:
   [ip,dateTime,resource,code] = searchObj.groups()
   pprint.pprint(code)

   for g in searchObj.groups():
       print g
else:
   print "Nothing found!!"