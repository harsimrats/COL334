There is a file parsehar.py in which we take file to be parsed as argument and using json library we parse tha har file. 

We create 2 dictionaries - 
 TCPlist and domainlist. 

 TCPlist contains total amount of data contained in that TCP connection
 domainlist contains another dicionary for TCP connections used by this domain and this TCP dictionary contains data transfered by TCP for this domain.

 Using these 2, we calculated goodput, time to load page etc.