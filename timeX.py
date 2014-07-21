#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  time.py
#  
#  Copyright 2014 Stazysta <Stazysta@STAZYSTA-KOMP>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
#  14/Jul/2014:16:05:15 +0200
#  

import time

def nextHour(secs):
	#prev = time.gmtime(secs)[3]
	#while ((prev+1)!=time.gmtime(secs)[3]):
	#	secs+=1
	return time.gmtime(secs)[3]
def main():
	t = time.strptime('14/Jul/2014:16:05:15', '%d/%b/%Y:%H:%M:%S')
	print time.mktime(t)
	#print nextHour(time.time())
	return 0

if __name__ == '__main__':
	main()

