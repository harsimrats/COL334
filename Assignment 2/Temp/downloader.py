import socket
import select
import argparse
import json
from urlparse import urlparse
import tldextract as tld
import threading
import os

#tpd = TCP per domain 
#opt = Objects per TCP

domainList={}

def ObjectsPerDomain(harfile_json):
	for entry in harfile_json['log']['entries']:
		url = urlparse(entry['request']['url'])
		path = url.path
		urld = tld.extract(entry['request']['url'])
		domain = urld.hostname
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
	os.mkdir('Downloaded')
	for domain in domainList:
		os.mkdir('Downloaded/'+domain)

def createThreads(tpd,opt):
	for domain in domainList:
		n=len(domainList[domain])
		p=tpd*opt
		count = 0
		while(n>p):
			for i in (0,tpd):
				r1 = opt * i + p * count
				r2 = opt * (i+1) +p * count
				t=threading.Thread(target=downloadObjects, args=(domainList[domain][r1 : r2], r1, ))
				t.start()
			n=n-p
			count+=1	
		
		q=n/tpd
		r=n%tpd
		for i in (0,r):
			r1 = i * (q+1) + p * count
			r2 = (i+1)*(q+1) + p * count
			t=threading.Thread(target=downloadObjects, args=(domainList[domain][r1 : r2], r1, ))
			t.start()
		for i in (r,tpd):
			r1 = i * (q) + p * count
			r2 = (i+1)*(q) + p * count
			t=threading.Thread(target=downloadObjects, args=(domainList[domain][r1 : r2], r1, ))
			t.start()
		
		for t in threading.enumerate():
			if t is not threading.currentThread():
				t.join()

def downloadObjects(l, num):
	i=0
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# print "LIST ==="
	# print l
	if (len(l)==0):
		return
	HOST = l[0]['hostname']
	PORT = l[0]['port']
	host_ip = socket.gethostbyname(HOST)
	s.connect((host_ip, PORT))
	for obj in l:
		request = obj['request']
		print "yeahhh"
		print request
		s.send(request)
		data = ''
		while select.select([s],[],[],3)[0]:
			res = s.recv(4096)
			if not res: 
				break
			data += res	
		recvd = data.split('\r\n\r\n')[0]
		image = data[len(recvd)+4:]
		path = 'Downloaded/'+HOST
		f = open(path +'/'+ str(num+i) , 'wb')
		f.write(image)
		f.close()
		s.close()
		i+=1

if __name__ == '__main__':
	argparser = argparse.ArgumentParser(prog='downloader', description='download objects of webpage from har file')
	argparser.add_argument('harfile', type=str, nargs=3, help='[path to harfile to be processed] [TCP per domain] [Objects per TCP]')
	args = argparser.parse_args()

harfile = open(args.harfile[0])
tpd= args.harfile[1]
opt =args.harfile[2]
harfile_json = json.loads(harfile.read())

ObjectsPerDomain(harfile_json)
makeDirectories()
createThreads(int(tpd),int(opt))


# for headers in entry['request']['headers']:
# 	l.append(headers['name'] + ": " + headers['value'])
# l1 = []
# for cookies in entry['request']['cookies']:
# 	l1.append(cookies['name'] + '=' + cookies['value'])
# stri = ';'.join(l1)
# l.append('Cookies: ' + stri)
# l.append('Content: ' + entry['request']['content']['text'])