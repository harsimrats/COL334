import argparse
import json
import numpy as np
from numpy import array
from urlparse import urlparse

domainList = {}
TCPList = {}

def sumMaxGoodPutTime():
        time = 0
        for domain in domainList:
            maxGoodPut = float(0)
            for connection in domainList[domain]['TCPConnections']:
                if(TCPList[connection]['maxGoodPut']>maxGoodPut):
                    maxGoodPut = TCPList[connection]['maxGoodPut']
            if maxGoodPut != 0:
            	temp = DomainContentSize(domain)/maxGoodPut
            	if time < temp:
                	time = temp
        return time

def DomainContentSize (d):
    size = 0
    for connection in domainList[d]['TCPConnections']:
        size+=domainList[d]['TCPConnections'][connection]['size']
    return size

def ObjectsPerDomain (d):
    count = 0
    for connection in domainList[d]['TCPConnections']:
        count+=domainList[d]['TCPConnections'][connection]['count']
    return count

def main (harfile_path):
    harfile = open(harfile_path)
    harfile_json = json.loads(harfile.read())

    pageOnloadTime= harfile_json['log']['pages'][0]['pageTimings']['onLoad']
    totalSizeDownloaded = 0
    totalRecieveTime = 0
    maxGoodPut = 0

    for entry in harfile_json['log']['entries']:
        url = entry['request']['url']
        domain = urlparse(entry['request']['url']).hostname
        if float(entry['response']['headersSize']) + float(entry['response']['bodySize']) >= 0:
	        size_kilobytes = (float(entry['response']['headersSize']) + float(entry['response']['bodySize']))/1024
        else:
        	size_kilobytes = float(entry['response']['_transferSize'])/1024
        totalSizeDownloaded += size_kilobytes

        if 'connection' in entry:
            TCPnumber = entry['connection']
        else:
            TCPnumber = 'unknown'

        if domain not in domainList:
            domainList[domain]={}
            domainList[domain]['dnsQueryTime'] = entry['timings']['dns']
            domainList[domain]['TCPConnections']={}
            if TCPnumber != 'unknown':
                domainList[domain]['TCPConnections'][TCPnumber]={}
                domainList[domain]['TCPConnections'][TCPnumber]['size'] = size_kilobytes
                domainList[domain]['TCPConnections'][TCPnumber]['count'] = 1
        
        else:                    
            if TCPnumber != 'unknown':
            	if entry['timings']['dns'] != -1:
            		domainList[domain]['dnsQueryTime'] = entry['timings']['dns']
                if TCPnumber not in domainList[domain]['TCPConnections']: 
                    domainList[domain]['TCPConnections'][TCPnumber]={}       
                    domainList[domain]['TCPConnections'][TCPnumber]['size'] = size_kilobytes
                    domainList[domain]['TCPConnections'][TCPnumber]['count'] = 1
                else:
                    domainList[domain]['TCPConnections'][TCPnumber]['size'] += size_kilobytes
                    domainList[domain]['TCPConnections'][TCPnumber]['count'] += 1
                    

        if TCPnumber not in TCPList:
            if TCPnumber != 'unknown':
                TCPList[TCPnumber]={}  
                TCPList[TCPnumber]['connectionTime'] = entry['timings']['connect']
                TCPList[TCPnumber]['count'] = 1
                TCPList[TCPnumber]['maxWaitTime'] = entry['timings']['wait']
                TCPList[TCPnumber]['averageWaitTime'] = entry['timings']['wait']
                TCPList[TCPnumber]['dnsTime'] = entry['timings']['dns']
                TCPList[TCPnumber]['receiveTime'] = entry['timings']['receive']
                TCPList[TCPnumber]['sendTime'] = entry['timings']['send']
                TCPList[TCPnumber]['sizeDownloaded'] = size_kilobytes
                TCPList[TCPnumber]['maxObject'] = size_kilobytes
                if entry['timings']['receive'] != 0:
                    TCPList[TCPnumber]['maxGoodPut'] = 1000*size_kilobytes/entry['timings']['receive']
                else:  
                    TCPList[TCPnumber]['maxGoodPut'] = 0
            
        else:
            if entry['timings']['connect'] != -1:
                    TCPList[TCPnumber]['connectionTime'] = entry['timings']['connect']
            if entry['timings']['dns'] > TCPList[TCPnumber]['dnsTime']:
                    TCPList[TCPnumber]['dnsTime'] = entry['timings']['dns']
            if TCPList[TCPnumber]['maxWaitTime'] < entry['timings']['wait']:
                TCPList[TCPnumber]['maxWaitTime'] = entry['timings']['wait']
            TCPList[TCPnumber]['averageWaitTime'] = (TCPList[TCPnumber]['averageWaitTime']*TCPList[TCPnumber]['count']+ entry['timings']['wait']) / (TCPList[TCPnumber]['count'] +1)
            TCPList[TCPnumber]['count'] += 1
            TCPList[TCPnumber]['receiveTime'] += entry['timings']['receive']
            TCPList[TCPnumber]['sendTime'] += entry['timings']['send']
            TCPList[TCPnumber]['sizeDownloaded'] += size_kilobytes
            if size_kilobytes > TCPList[TCPnumber]['maxObject']:
                TCPList[TCPnumber]['maxObject'] = size_kilobytes
                if entry['timings']['receive'] != 0:
                    TCPList[TCPnumber]['maxGoodPut'] = 1000*size_kilobytes/entry['timings']['receive']
                

    maxTotalTimeConsumed = 0
    for connection in TCPList:
        TCPList[connection]['averageGoodPut'] = 1000*TCPList[connection]['sizeDownloaded']/TCPList[connection]['receiveTime']
        if maxGoodPut < TCPList[connection]['maxGoodPut']:
            maxGoodPut = TCPList[connection]['maxGoodPut']

        TCPList[connection]['totalTimeConsumed'] = TCPList[TCPnumber]['dnsTime'] + TCPList[TCPnumber]['maxWaitTime'] + TCPList[TCPnumber]['receiveTime'] + TCPList[TCPnumber]['sendTime']
        if TCPList[TCPnumber]['connectionTime'] != -1:
            TCPList[connection]['totalTimeConsumed'] += TCPList[TCPnumber]['connectionTime']
        if maxTotalTimeConsumed < TCPList[connection]['totalTimeConsumed']:
            maxTotalTimeConsumed = TCPList[connection]['totalTimeConsumed']

    averageGoodPut = 0
    for connection in TCPList:
        averageGoodPut += TCPList[connection]['averageGoodPut']
    averageGoodPut = averageGoodPut / len(TCPList)

    print "Page Onload Time : %f s" % (float(pageOnloadTime) / 1000)
    print "Page Load time (if all connections are opened simultaneously) : %f s" % (float(maxTotalTimeConsumed) / 1000)
    print "Page Load time (if max Goodput is achieved) : %f s" % sumMaxGoodPutTime()
    print "Total No. of Objects Downloaded : %d" % len(harfile_json['log']['entries'])
    print "Total Size of Content Downloaded : %f KB" % totalSizeDownloaded
    print "\nAverage Goodput Of Network : %f KBps" % averageGoodPut
    print "Maximum Goodput Of Network : %f KBps" % maxGoodPut
    print "\nDomain Analysis:"
    for domain in domainList:
        print "\n\t%s" % domain
        print "\t\tDNS query time = %f ms" %domainList[domain]['dnsQueryTime'] 
        print  "\t\tSize of content downloaded = %f KB" % DomainContentSize(domain)
        print  "\t\tNo. of objects = %d" % ObjectsPerDomain(domain)
        print  "\t\tNo. of TCP connections = %d" % len(domainList[domain]['TCPConnections'])
        print  "\t\tTCP Connections:"
        for connection in domainList[domain]['TCPConnections']:
            print  "\t\t\t\t %s:  Size of Content Downloaded = %f KB   No. of Objects  = %d" % (connection, domainList[domain]['TCPConnections'][connection]['size'],TCPList[connection]['count'])
            
    print "\nTCP Analysis:"
    for connection in TCPList:
        print "\n\t%s:" % connection
        print "\t\tSize of Content Downloaded = %f KB" % TCPList[connection]['sizeDownloaded']
        print "\t\tConnection Time = %f ms" % TCPList[connection]['connectionTime']
        print "\t\tDNS Query Time = %f ms" % TCPList[connection]['dnsTime']
        print "\t\tAverage Wait Time = %f ms" % TCPList[connection]['averageWaitTime']
        print "\t\tTotal Receive Time = %f ms" % TCPList[connection]['receiveTime']
        print "\t\tAverage Goodput = %f KBps" % TCPList[connection]['averageGoodPut']
        print "\t\tMaximum Achieved GoodPut = %f KBps" % TCPList[connection]['maxGoodPut']

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        prog='parsehar',
        description='Parse .har files into comma separated values (csv).')
    argparser.add_argument('harfile', type=str, nargs=1,
                        help='path to harfile to be processed.')
    args = argparser.parse_args()
    
    main(args.harfile[0])