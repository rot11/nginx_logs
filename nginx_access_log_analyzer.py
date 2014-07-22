# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ex1.py
#

#import datetime
import time
import sys
import re


class LogAnalyzer():

    def __init__(self):
        #request types that will be count separately
        self.knownRequestTypes = ['api', 'ui', 'images', 'other']
        #request dictionary
        self.n = {}
        #Regular expression
        self.pattern = r'([\d]{1,3}.[\d]{1,3}.[\d]{1,3}.[\d]{1,3}) - - \[([\d]{2}/[A-Z][a-z]{2}/[0-9]{4}):([\d]{2}):' \
                       r'[\d]{2}:[\d]{2} \+0200] "[A-Z]{0,4} /([a-z\.?=]*).* HTTP/1.[01]" ([0-9]{3})'
        self.re = re.compile(self.pattern)

    def analyze(self, fileName):
        """
        Analyzes nginx access
        @param fileName: nginx access log file that will be analyzed
        """
        accessLogFile = open(fileName, 'r')

        for line in accessLogFile:

            result = self.re.search(line)
            [ip, date, hour, resource, code] = result.groups()

            #all js, styles, files that are not requests to API/UI/Images
            if resource is None or resource not in self.knownRequestTypes:
                resource = 'other'

            #using date + hour from access log as key in dictionary to get hourly statistics
            dateH = date + ':' + hour

            #general counting
            if dateH not in self.n:
                self.n[dateH] = {}
                self.n[dateH]['all'] = 0
                self.n[dateH]['IPs'] = {}
                for t in self.knownRequestTypes:
                    self.n[dateH][t] = 0

            self.n[dateH]['all'] += 1
            self.n[dateH][resource] += 1

            #requests count by IP address
            if ip not in self.n[dateH]['IPs']:
                self.n[dateH]['IPs'][ip] = {}
                self.n[dateH]['IPs'][ip]['all'] = 0
                for t in self.knownRequestTypes:
                    self.n[dateH]['IPs'][ip][t] = 0

            self.n[dateH]['IPs'][ip]['all'] += 1
            self.n[dateH]['IPs'][ip][resource] += 1

            #requests count by status codes
            if 'codes' not in self.n[dateH]:
                self.n[dateH]['codes'] = {}

            if code not in self.n[dateH]['codes']:
                self.n[dateH]['codes'][code] = 0

            self.n[dateH]['codes'][code] += 1

        accessLogFile.close()

    def stats(self):
        """
        Return result as a string
        """
        ret = ''
        for d in sorted(self.n.iterkeys()):
            ret += d + '\n'
            ret += '\tall\tavr\n'
            ret += 'all\t' + str(self.n[d]['all']) + '\t%0.3f' % (float(self.n[d]['all'])/3600, ) + '\n'
            for t in self.knownRequestTypes:
                if self.n[d][t] != 0:
                    ret += t + '\t' + str(self.n[d][t]) +'\t%.3f' % (float(self.n[d][t])/3600, ) +'\n'
            ret += '\n'
            for code in self.n[d]['codes']:
                ret += code + '=>' + str(self.n[d]['codes'][code]) + '\n'
            ret += '\n'
            for ip in self.n[d]['IPs']:
                ret += ip + '\t{'
                ret += 'all:' + str(self.n[d]['IPs'][ip]['all']) + ';'
                for ipReq in self.n[d]['IPs'][ip]:
                    if ipReq != 'all' and self.n[d]['IPs'][ip][ipReq]!=0 :
                        ret += ipReq + ':' + str(self.n[d]['IPs'][ip][ipReq]) + ';'
                ret = ret[:-1]
                ret += '}\n'
            ret += '\n'
        return ret


if __name__ == "__main__":
    def usage():
        print 'Usage:'
        print sys.argv[0] + ' nginx_access_log'
        print 'This will analyze the access log file and return to std output the results'

    if len(sys.argv) > 1:
        accessLogFileName = sys.argv[1]
        try:
            runTimeStart = time.time()

            analyzer = LogAnalyzer()
            analyzer.analyze(accessLogFileName)

            print 'File name:', accessLogFileName
            print analyzer.stats()
            runTimeStop = time.time()
            print 'Run time', runTimeStop - runTimeStart
        except IOError:
            print 'No such file:', accessLogFileName
            print 'Exiting'
    else:
        usage()
