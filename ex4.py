# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ex1.py
#

import datetime
import time
import sys
import re


class LogAnalyzer():
    def inc(self, IP, typ):
        if typ not in self.IP[IP]:
            self.IP[IP][typ] = 1
        else:
            self.IP[IP][typ] += 1
        self.IP[IP]['all'] += 1

    def __init__(self, startTime=0, period=3600):
        self.knownRequestTypes = ['api', 'ui', 'images']
        # amount of requests
        self.n = 0

        self.period = period
        self.startTime = startTime

        if self.startTime != 0:
            self.stopTime = self.startTime + datetime.timedelta(seconds=self.period)
        else:
            self.stopTime = 0

        self.nTypes = {self.knownRequestTypes[0]: 0, self.knownRequestTypes[1]: 0, self.knownRequestTypes[2]: 0,
                       'other': 0}

        # amount of each status code
        self.nCode = {}

        self.IP = {}

        self.pattern = r'([\d]{1,3}.[\d]{1,3}.[\d]{1,3}.[\d]{1,3}) - - \[([\d]{2}/[A-Z][a-z]{2}/[0-9]{4}:[\d]{2}:[\d]{2}:[\d]{2}) \+0200] "[A-Z]{0,4} /([a-z\.?=]*).* HTTP/1.[01]" ([0-9]{3})'
        self.re = re.compile(self.pattern)

        self.dateTimePattern = '%d/%b/%Y:%H:%M:%S'

    def isInTimeRange(self, dateTime):
        if self.startTime <= dateTime < self.stopTime:
            return True
        return False

    def main(self, line):
        result = self.re.search(line)

        [ip, dateTime, resource, code] = result.groups()

        dateTime = datetime.datetime.strptime(dateTime, self.dateTimePattern)
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

        if resource is None or resource not in self.knownRequestTypes:
            resource = 'other'

        self.nTypes[resource] += 1
        self.inc(ip, resource)

        #status code
        if code in self.nCode:
            self.nCode[code] += 1
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

        self.pattern = r'([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}) - - \[([0-9][0-9]/[A-Z][a-z]{2}/[0-9]{4}:[0-9]' \
                       r'[0-9]:[0-9][0-9]:[0-9][0-9]) \+0200] "[A-Z]{0,4} /([a-z\.?=]*).* HTTP/1.[01]" ([0-9]{3})'
        self.re = re.compile(self.pattern)

        self.dateTimePattern = '%d/%b/%Y:%H:%M:%S'

        self.currentContainer = 0
        self.containers = [LogAnalyzer(self.getStartDateTime(), self.defaultPeriod), ]

    def getStartDateTime(self):
        file = open(self.logFileName)

        result = self.re.search(file.readline())

        [ip, dateTime, resource, code] = result.groups()

        dateTime = datetime.datetime.strptime(dateTime, self.dateTimePattern)
        dateTime = dateTime.replace(minute=0, second=0)

        file.close()
        return dateTime

    def readfile(self):
        file = open(self.logFileName, 'r')

        for line in file:
            [nextWorker, stop] = self.containers[self.currentContainer].main(line)
            while nextWorker == False:
                self.containers.append(LogAnalyzer(startTime=stop, period=self.defaultPeriod))
                self.currentContainer += 1
                [nextWorker, stop] = self.containers[self.currentContainer].main(line)

    def printStats(self):
        for container in self.containers:
            container.stats()


if __name__ == "__main__":
    runTimeStart = time.time()
    if len(sys.argv) > 2:
        accessLogFileName = sys.argv[1]
        defaultPeriod = int(sys.argv[2])
    else:
        accessLogFileName = 'nginx_access_log'
        defaultPeriod = 3600
    print 'File name:', accessLogFileName
    print 'Period:', defaultPeriod

    master = LogAnalyzerMaster(accessLogFileName, defaultPeriod)
    master.readfile()
    master.printStats()
    runTimeStop = time.time()
    print 'Run time', runTimeStop - runTimeStart, '\n'
