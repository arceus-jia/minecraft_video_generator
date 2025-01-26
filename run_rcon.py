from mcrcon import MCRcon
import sys,os,time
import argparse

HOST = '127.0.0.1'
PORT = 25575
PASSWD = '123456'
COMMAND = 'status'

parser = argparse.ArgumentParser(description="gen pics")
parser.add_argument("--func", type=str, default='sao10', help="funcname")
args = parser.parse_args()

if __name__ == '__main__':
    mcr = MCRcon(HOST,PASSWD)
    mcr.connect()
    
    frame_count = 1000

    time.sleep(5)
    st = time.time()
    for i in range(1, frame_count + 1):
        endt = st + 1 * i
        cmd = 'function %s:frame_%03d' % (args.func,i)
        resp = mcr.command(cmd)
        print(int(st),int(endt),int(time.time()), resp)
        t = (endt - time.time())
        print('sleep:',t)
        time.sleep(t)