import time, os, sys, string


def main(cmd, inc=60):
    while 1:
        os.system(cmd)
        time.sleep(inc)

if __name__ == '__main__' :
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print "usage: " + sys.argv[0] + " command [seconds_delay]"
        sys.exit(1)
    
    cmd = sys.argv[1]
    if len(sys.argv) < 3:
        main(cmd)
    else:
        inc = string.atoi(sys.argv[2])
        main(cmd, inc)

