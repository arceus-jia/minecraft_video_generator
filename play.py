from mcrcon import MCRcon
import sys,os,time
import argparse

HOST = '127.0.0.1'
PORT = 25575
PASSWD = '123456'
COMMAND = 'status'

parser = argparse.ArgumentParser(description="gen pics")
parser.add_argument("--func", '-f', type=str,  help="funcname")
parser.add_argument("--frame_count", '-c',  type=int, help="frame_count")
parser.add_argument("--frame_interval", '-i', default=0.1, type=float, help="frame_count")
args = parser.parse_args()

if __name__ == '__main__':
    mcr = MCRcon(HOST,PASSWD)
    mcr.connect()
    print ('connected')
    
    cmd = 'function %s:frame_0001' % args.func
    resp = mcr.command(cmd)
    idx = 0
    while True:      
        time.sleep(args.frame_interval)  
        cmd = 'function %s:frame_%04d' % (args.func, idx+2)
        resp = mcr.command(cmd)
        idx = (idx + 1) %  args.frame_count

# python play.py -f test1 -c 9 -i 0.1

