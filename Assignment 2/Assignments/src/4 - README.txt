To run the code 
    python downloader.py <har_file> <Max. TCP connections per domain> <Max. objects per TCP connection>

The program outputs the runThe downloaded objects will appear in Downloaded folder. 

Program summary:

    1) The HAR file is converted to JSON and parsed and domainList is created conatining the distribution of objects per domain.

    2) For each domain a separte thread is run to download objects in that domain.

    3) In a particular domain the distribution of objects is done on the basis of product p of TCP per domain and objects per TCP. if no. of objects > p 
    then the maximum capacity is used else suppose if n=5, tpd(TCP per domain) =3, opt(Objects per TCP) = 3 then in 2 TCP connections will download 2 objects 
    and 1 will download one object.
    
      