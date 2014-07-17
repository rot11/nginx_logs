# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ex1.py
#
#192.168.5.87 - - [14/Jul/2014:16:04:21 +0200] "GET /ui/extauth_router/categories/Altair/?AltairID=135156877&embed=1&showifone=1&cd3Token=33604%0araw%0a%8f%ba7s.%f2%b2%ebX%b6%84I%b8_%9c%5dAUIC%13%01%a1k%ee%e0T%d6%0cIh%90%0aUser%3a+33604 HTTP/1.1" 302 5 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"

#172.17.101.84 - - [14/Jul/2014:16:05:15 +0200] "GET / HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"
from parse import *
import time


class LogAnalyzer():
    def inc(self, IP, typ):
        if not self.IP[IP].has_key(typ):
            self.IP[IP][typ] = 1
        else:
            self.IP[IP][typ] += 1

    def hour(self, secs):
        #prev = time.gmtime(secs)[3]
        #while ((prev+1)!=time.gmtime(secs)[3]):
        #	secs+=1
        return time.gmtime(secs)[3]

    def __init__(self):
        #amount of requests
        self.n = 0
        self.nImg = 0
        self.nAPI = 0
        self.nUI = 0
        self.nOther = 0
        #amount of errors
        self.nErrors = {}
        #amount of requests by hours
        self.nH = 0  #amount of requests in last hour
        self.reqsH = {}

        self.IP = {}

        #pattern = '{} - - [{}:{}:{}:{} {}] "{} {} HTTP/1.{}" {} {} "{}" "{}"'
        #172.17.101.84 - - [14/Jul/2014:16:05:15 +0200] "GET / HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"
        self.pattern = '{} - - [{}:{}:{}:{} {}] "{} {} HTTP/1.{}" {} {} {}'
        #ip - - [dataCzas] "TYP ZASÓB HTTP/1.{}" KOD
        self.patternType = '/{}/'

    def main(self, logFileName):
        runTimeStart = time.time()

        logFile = open(logFileName, 'r')

        res = search(self.pattern, logFile.readline())
        timestr = "%s:%s:%s:%s" % (res[1], res[2], res[3], res[4])
        startTime = time.mktime(time.strptime(timestr, '%d/%b/%Y:%H:%M:%S'))

        #set pointer at the begin on file
        logFile.seek(0, 0)
        #start hour
        hour = res[2]

        for line in logFile:
            res = search(self.pattern, line)
            if int(res[2]) == (int(hour) + 1):
                self.reqsH[hour] = self.nH
                self.nH = 0
                hour = res[2]
            #request count
            self.n += 1
            self.nH += 1
            #IP
            if not self.IP.has_key(res[0]):
                self.IP[res[0]] = {}

            self.inc(res[0], 'all')

            #typ req
            resType = search(self.patternType, res[7])
            if resType == None:
                self.nOther += 1
                self.inc(res[0], 'other')
            else:
                requestType = resType[0]
                if requestType == 'images':
                    self.nImg += 1
                    self.inc(res[0], requestType)
                elif requestType == 'api':
                    self.nAPI += 1
                    self.inc(res[0], requestType)
                elif requestType == 'ui':
                    self.nUI += 1
                    self.inc(res[0], requestType)
                else:
                    self.nOther += 1
                    self.inc(res[0], 'other')

            #status code
            if self.nErrors.has_key(res[9]):
                self.nErrors[res[9]] += 1
            else:
                self.nErrors[res[9]] = 1

        self.reqsH[hour] = self.nH  #ostatnia godzina
        timestr = "%s:%s:%s:%s" % (res[1], res[2], res[3], res[4])
        stopTime = time.mktime(time.strptime(timestr, '%d/%b/%Y:%H:%M:%S'))
        self.time = stopTime - startTime
        logFile.close()
        runTimeStop = time.time()

        print 'Run Time:', str(runTimeStop - runTimeStart), 's'
        return 0

    def stats(self):
        ret = 'Timespan ' + str(self.time) + 's\n'
        ret += 'Requests statistic\n'
        ret += 'All requests ' + str(self.n) + '\n'
        ret += 'Avr requests/s ' + str(float(self.n) / self.time) + '\n'
        ret += 'Avr API requests/s ' + str(float(self.nAPI) / self.time) + '\n'
        ret += 'Avr UI requests/s ' + str(float(self.nUI) / self.time) + '\n'
        ret += 'Avr Img requests/s ' + str(float(self.nImg) / self.time) + '\n'
        ret += 'Avr other requests/s ' + str(float(self.nOther) / self.time) + '\n'
        return ret

    def errorStats(self):
        ret = 'Errors statistic\n'
        keys = self.nErrors
        for key in keys:
            ret += str(key) + ' => ' + str(self.nErrors[key]) + '\n'
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

if __name__ == "__main__":
    accessLogFileName = 'nginx_access_log1'
    analyzer = LogAnalyzer()
    analyzer.main(accessLogFileName)
    print analyzer.stats()
    print analyzer.errorStats()
    print analyzer.IPStats()
    print analyzer.reqsH
