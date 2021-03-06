# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ex1.py
#
#192.168.5.87 - - [14/Jul/2014:16:04:21 +0200] "GET /ui/extauth_router/categories/Altair/?AltairID=135156877&embed=1&showifone=1&cd3Token=33604%0araw%0a%8f%ba7s.%f2%b2%ebX%b6%84I%b8_%9c%5dAUIC%13%01%a1k%ee%e0T%d6%0cIh%90%0aUser%3a+33604 HTTP/1.1" 302 5 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"

#172.17.101.84 - - [14/Jul/2014:16:05:15 +0200] "GET / HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"
from parse import *
import datetime
import time
import sys
import pprint
import re



class LogAnalyzer():
    def inc(self, IP, typ):
        if typ not in self.IP[IP]:
            self.IP[IP][typ] = 1
        else:
            self.IP[IP][typ] += 1
        self.IP[IP]['all'] +=1


    def __init__(self, startTime=0, period=3600):
        self.knownRequestTypes = ['api', 'ui', 'images']
        #amount of requests
        self.n = 0

        self.period = period
        self.startTime = startTime

        if self.startTime != 0:
            self.stopTime = self.startTime + datetime.timedelta(seconds=self.period)
        else:
            self.stopTime = 0

        self.nTypes = {self.knownRequestTypes[0]: 0, self.knownRequestTypes[1]: 0, self.knownRequestTypes[2]: 0, 'other': 0}

        #amount of each status code
        self.nCode = {}

        self.IP = {}

        #pattern = '{} - - [{}:{}:{}:{} {}] "{} {} HTTP/1.{}" {} {} "{}" "{}"'
        #172.17.101.84 - - [14/Jul/2014:16:05:15 +0200] "GET / HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"

        #self.pattern = '{} - - [{}:{:d}:{}:{} {}] "{} {} HTTP/1.{}" {} {}'
        self.pattern = '{} - - [{} {}] "{} {} HTTP/1.{}" {} {}'
        #ip - - [dataCzas] "TYP ZASÓB HTTP/1.{}" KOD

        self.dateTimePattern = '%d/%b/%Y:%H:%M:%S'
        self.typePattern = '/{}/'

    def isInTimeRange(self, dateTime):
        if self.startTime <= dateTime < self.stopTime:
            return True
        return False

    def main(self, line):
        [ip, dateTime, timeZone, method, resource, http, code, trash] = search(self.pattern, line)

        dateTime = datetime.datetime.strptime(dateTime, self.dateTimePattern)
        #pprint.pprint(resource)
        if self.startTime == 0:
            self.startTime = dateTime
            self.stopTime = self.startTime + datetime.timedelta(seconds=self.period)

        if not self.isInTimeRange(dateTime):
            return False, self.stopTime

        #request count
        self.n += 1

        #IP
        if ip not in self.IP:
            self.IP[ip] = {'all': 0}

        #request type

        resType = search(self.typePattern, resource)
        if resType is None:
            requestType = 'other'
        else:
            requestType = resType[0]
            if not requestType in self.knownRequestTypes:
                requestType = 'other'

        self.nTypes[requestType] += 1
        self.inc(ip, requestType)

        #status code
        if code in self.nCode:
            self.nCode[code] +=1
        else:
            self.nCode[code] = 1

        return True, self.stopTime

    def stats(self):
        print self.generalStats()
        print self.statusCodeStats()
        print self.IPStats()

    def generalStats(self):
        formatString = "%d/%m/%Y %X"
        ret = self.startTime.strftime(formatString) + ' - ' + self.stopTime.strftime(formatString) + '\n'
        ret += 'All requests ' + str(self.n) + '\n'
        ret += 'Avr requests/s ' + str(float(self.n) / self.period) + '\n'
        ret += 'Avr API requests/s ' + str(float(self.nTypes['api']) / self.period) + '\n'
        ret += 'Avr UI requests/s ' + str(float(self.nTypes['ui']) / self.period) + '\n'
        ret += 'Avr Img requests/s ' + str(float(self.nTypes['images']) / self.period) + '\n'
        ret += 'Avr other requests/s ' + str(float(self.nTypes['other']) / self.period) + '\n'
        return ret

    def statusCodeStats(self):
        ret = 'Status code statistic\n'
        keys = self.nCode
        for key in keys:
            ret += str(key) + ' => ' + str(self.nCode[key]) + '\n'
        return ret

    def IPStats(self):
        ret = 'IP statistics\n'
        keys = self.IP
        for ip in keys:
            ret += str(ip) + '\t{'
            ret += 'ALL:' + str(self.IP[ip]['all']) + '; '
            for typ in self.IP[ip]:
                if typ != 'all':
                    ret += str(typ) + ':' + str(self.IP[ip][typ]) + ', '
            ret = ret[:-2]
            ret += '}\n'
        return ret


class LogAnalyzerMaster():
    def __init__(self, logFileName, defaultPeriod=3600):
        self.logFileName = logFileName
        self.defaultPeriod = defaultPeriod

        self.pattern = '{} - - [{} {}] "{} {} HTTP/1.{}" {} {}'
        self.dateTimePattern = '%d/%b/%Y:%H:%M:%S'

        self.currentContainer = 0
        self.containers = [LogAnalyzer(self.getStartDateTime(), self.defaultPeriod),]

    def getStartDateTime(self):
        file = open(self.logFileName)

        [ip, dateTime, timeZone, method, resource, http, code, trash] = search(self.pattern, file.readline())
        dateTime = datetime.datetime.strptime(dateTime, self.dateTimePattern)
        dateTime = dateTime.replace(minute=0,second=0)

        file.close()
        return dateTime

    def readfile(self):
        self.getStartDateTime()
        runTimeStart = time.time()
        file = open(self.logFileName, 'r')

        for line in file:
            [nextWorker, stop] = self.containers[self.currentContainer].main(line)
            while nextWorker == False:
                self.containers.append(LogAnalyzer(startTime=stop, period=self.defaultPeriod))
                self.currentContainer += 1
                [nextWorker, stop] = self.containers[self.currentContainer].main(line)
        runTimeStop = time.time()
        print 'Run time', runTimeStop - runTimeStart, '\n'

    def printStats(self):
        for container in self.containers:
            container.stats()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        accessLogFileName = sys.argv[1]
        defaultPeriod = int(sys.argv[2])
    else:
        accessLogFileName = 'nginx_access_log1'
        defaultPeriod = 3600
    print 'File name:', accessLogFileName
    print 'Period:', defaultPeriod

    master = LogAnalyzerMaster(accessLogFileName, defaultPeriod)
    master.readfile()
    #master.printStats()
