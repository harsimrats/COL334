import socket
import select
import argparse
import json
from urlparse import urlparse
import threading
import os
import shutil
import matplotlib.pyplot as plt
import datetime
from time import sleep

#tpd = TCP per domain 
#opt = Objects per TCP

domainList={}



def timeDifference(t1,t2):
	v1 = t1.hour*3600 + t1.minute*60 +t1.second + t1.microsecond/float(1000000)
	v2 = t2.hour*3600 + t2.minute*60 +t2.second + t2.microsecond/float(1000000)
	return v2-v1


def buildDomainList(harfile_json):
	# print len(harfile_json['log']['entries'])
	for entry in harfile_json['log']['entries']:
		url = urlparse(entry['request']['url'])
		domain = url.hostname
		path = url.path
		if path == "":
			path = "/"
	
		l = []	
		l.append(entry['request']['method'] + " " + path +" HTTP/1.1")
		l.append('Host: ' + url.hostname)
		l.append('Connection: Keep-Alive')
		request = '\r\n'.join(l)
		request+='\r\n\r\n'
		HOST = url.hostname
		PORT = 80
		if domain not in domainList:
			domainList[domain]=[]
		obj={}	
		obj['request']=request
		obj['hostname']=HOST
		obj['port']=PORT			
		domainList[domain].append(obj)

def makeDirectories():
	if os.path.isdir('Downloaded'):
		shutil.rmtree('Downloaded')
	os.mkdir('Downloaded')
	for domain in domainList:
		os.mkdir('Downloaded/'+domain)

def joinThreads(domain):
	for t in threading.enumerate():
		if t.name == domain:
			t.join()	

def createDomainThreads(tpd,opt):
	t1=datetime.datetime.time(datetime.datetime.now())
	for domain in domainList:
		t=threading.Thread(target=createThreads, args=(domain, tpd,opt, ))
		t.start()
	
	for t in threading.enumerate():
		if t is not threading.currentThread():
			t.join()
	t2=datetime.datetime.time(datetime.datetime.now())
	return timeDifference(t1,t2)	

def createThreads(domain,tpd,opt):
	n=len(domainList[domain])
	p=tpd*opt
	count = 0
	# tJoin =threading.Thread(target=joinThreads, args=(domain,))
	
	while(n>p):
		for i in range(0,tpd):
			r1 = opt * i + p * count
			r2 = opt * (i+1) +p * count
			t=threading.Thread(target=downloadObjects, args=(domainList[domain][r1 : r2], r1, ))
			t.setName(domain)
			t.start()
		# tJoin.start()	
		for t in threading.enumerate():
			if t.name == domain:
				t.join()	

		n=n-p
		count+=1	

	q=n/tpd
	r=n%tpd

	for i in range(0,r):
		r1 = i * (q+1) + p * count
		r2 = (i+1)*(q+1) + p * count
		t=threading.Thread(target=downloadObjects, args=(domainList[domain][r1 : r2], r1, ))
		t.start()


	for i in range(r,tpd):
		r1 = i * (q) + p * count
		r2 = (i+1)*(q) + p * count
		t=threading.Thread(target=downloadObjects, args=(domainList[domain][r1 : r2], r1, ))
		t.start()
		




def downloadObjects(l, num):
	i=0
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if (len(l)==0):
		return
	
	HOST = l[0]['hostname']
	PORT = l[0]['port']
	try:
		host_ip = socket.gethostbyname(HOST)
		s.connect((host_ip, PORT))
	except: 
		pass

	for obj in l:
		request = obj['request']
		try:
			s.send(request)
		except:
			pass
	
		data = ''
		while select.select([s],[],[],3)[0]:
			res = s.recv(2048)
			if not res: 
				break
			data += res	

		recvd = data.split('\r\n\r\n')[0]
		image = data[len(recvd)+4:]
		path = 'Downloaded/'+HOST
	
		f = open(path +'/'+ str(num+i) , 'wb')
		f.write(image)
		f.close()
		i+=1
	
	s.close()
	
def plotGraph(x,y):
	plt.plot(x, y, 'ro')
	plt.axis([4, 10, 0, 20])
	plt.show()


if __name__ == '__main__':

    argparser = argparse.ArgumentParser(
        prog='downloader',
        description='Parse .har files into comma separated values (csv).')
    argparser.add_argument('harfile', type=str, nargs=1, help='path to harfile to be processed.')
    args = argparser.parse_args()

harfile = open(args.harfile[0])
harfile_json = json.loads(harfile.read())
buildDomainList(harfile_json)
# makeDirectories()
# i=1
# j=1
print "tpd,opt,PageLoadTime" 

for i in range (1,6):
	for j in range (1,6):
		makeDirectories()
		print "%d,%d,%f" % (i,j,createDomainThreads(i,j))
		