import pandas as pd
import whois

csv=[]
with open ("out.txt", "r") as myfile:
    data=myfile.readlines()
x=0;
while(x<len(data)):
    if(data[x]!="\n"):
        str = data[x].split()
        if(str[0]=="Starting"):
            f1= str[7]
            f2= str[8]
            x+=1
            f3=0
            while(data[x]!="\n"):
                str1 = data[x].split()
                if(str1[0] == "Nmap" and str1[1]  == "done:"):
                    f3= str1[5][1:]    
                    break
                x+=1
            csv.append([f1,f2,f3])
    x+=1
#print str[0]
df=pd.DataFrame(csv)
df.columns=["Date","time","hosts"]
df.to_csv("output.csv")
# w=whois.whois('www.google.com')
# print w

