#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#192.168.5.87 - - [14/Jul/2014:16:04:21 +0200] "GET /ui/extauth_router/categories/Altair/?AltairID=135156877&embed=1&showifone=1&cd3Token=33604%0araw%0a%8f%ba7s.%f2%b2%ebX%b6%84I%b8_%9c%5dAUIC%13%01%a1k%ee%e0T%d6%0cIh%90%0aUser%3a+33604 HTTP/1.1" 302 5 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"

def main():
	accessLogFileName = 'nginx_access_log'
	errorLogFileName = 'nginx_access_log'
	
	aLog = open(accessLogFileName, 'r')
	print aLog.readline()
	return 0

if __name__ == '__main__':
	main()

