import socket
import select
import argparse
import json
from urlparse import urlparse
import threading

#tpd = TCP per domain 
#opt = Objects per TCP

domainList={}

def ObjectsPerDomain(harfile_json):
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

def createThreads(tpd,opt):
	for domain in domainList:
		n=len(domainList[domain])
		p=tpd*opt
		count = 0
		while(n>p):
			for i in (0,tpd):
				r1 = opd * i + p * count
				r2 = opd * (i+1) +p * count
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
			if t is not main_thread:
				t.join()
		

def downloadObjects(l, num):
	i=1
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	HOST = l[0]['hostname']
	PORT = l[0]['port']
	host_ip = socket.gethostbyname(HOST)
	s.connect((host_ip, PORT))
	for obj in l:
		request = obj['request']
		s.send(request)
		data = ''
		while select.select([s],[],[],3)[0]:
			res = s.recv(4096)
			if not res: 
				break
			data += res	
		recvd = data.split('\r\n\r\n')[0]
		image = data[len(recvd)+4:]
		f = open(HOST + '/' + str(num) + '/' + str(i), 'wb')
		f.write(image)
		f.close()
		s.close()
		i+=1

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        prog='downloader',
        description='Parse .har files into comma separated values (csv).')
    argparser.add_argument('harfile', type=str, nargs=3, help='path to harfile to be processed.')
    args = argparser.parse_args()
harfile = open(args.harfile[0])
tpd= args.harfile[1]
opt =args.harfile[2]
harfile_json = json.loads(harfile.read())
ObjectsPerDomain(harfile_json)
createThreads(int(tpd),int(opt))

# for headers in entry['request']['headers']:
# 	l.append(headers['name'] + ": " + headers['value'])
# l1 = []
# for cookies in entry['request']['cookies']:
# 	l1.append(cookies['name'] + '=' + cookies['value'])
# stri = ';'.join(l1)
# l.append('Cookies: ' + stri)
# l.append('Content: ' + entry['request']['content']['text'])