#!/usr/bin/python
# -*- coding: utf-8 -*-

# Implemented by James YS Kim

import sys

sys.path.append('./TCPClient/')
import time
import socket
import getopt
import threading
# import thread
import errno

from TCPServer import TCPServer
from time import gmtime, strftime, localtime

from TCPClientThread import msg
# msg = "Hello WIZ750SR\r"

'''
TCP server
#socket = socket.socket( socket.AF_INET , socket.SOCK_STREAM )
1> socket.bind( addr )               // 서버의 아이피와 포트번호를 고정
2> socket.listen(0)                    // 클라이언트의 연결을 받을 수 있는 상태
3> socket.accept()                    // 클라이언트로부터 소켓과 클라이언트의 주소를 반환
4> socket.recv( byte수 )             // 연결되어진 클라이언트로부터 데이터를 받는다 
'''

class TCPServerThread(threading.Thread):
    def __init__(self, serverip, serverport, trycount):
    # def __init__(self)
        threading.Thread.__init__(self)
        self.serverip = serverip
        self.serverport = serverport
        # self.f = fd
        self.totaltrycount = 0
        self.successcount = 0
        self.failcount = 0
        self.trycount = trycount
        self.server = None

    def stop(self):
        if self.server is not None:
            self.server.close()
            self.server = None
        sys.stdout.write('thread for %r ' % self.serverip)
        sys.stdout.write('is shutdowning (server)\r\n')
        # if not self.f.closed:
        if self.totaltrycount > 0:
            logstr = "======================================\r\n"
            logstr = logstr + '[' + self.serverip + '] stopped at ' + strftime("%d %b %Y %H:%M:%S", localtime()) + '\r\n'
            logstr = logstr + 'Total try: ' + str(self.totaltrycount) + '\r\n'
            logstr = logstr + 'Success count: ' + str(self.successcount) + '\r\n'
            logstr = logstr + 'Fail count: ' + str(self.failcount) + '\r\n'
            logstr = logstr + 'Success Rate: ' + "{0:.1f}".format(
                float(self.successcount) / float(self.totaltrycount) * 100) + '%\r\n'
            logstr = logstr + '======================================\r\n'
            sys.stdout.write(logstr)
        else:
            logstr = "======================================\r\n"
            logstr = logstr + '[' + self.serverip + '] stopped at ' + strftime("%d %b %Y %H:%M:%S", localtime()) + '\r\n'
            logstr = logstr + 'Connection Failed\r\n'
            logstr = logstr + '======================================\r\n'
            sys.stdout.write(logstr)
        #     self.f.write(logstr)
        self._Thread__stop()

    # TCP Server
    def run(self):
        # SOCK_CLOSE_STATE = 1
        # SOCK_OPENTRY_STATE = 2
        # SOCK_OPEN_STATE = 3
        # SOCK_LISTEN_STATE = 4
        # SOCK_ACCEPT_STATE = 5
        
        SOCK_CLOSE_STATE = 1
        SOCK_OPENTRY_STATE = 2
        SOCK_OPEN_STATE = 3
        SOCK_CONNECTTRY_STATE = 4
        SOCK_CONNECT_STATE = 5

        idle_state = 1
        datasent_state = 2

        sys.stdout.write('thread for %r ' % self.serverip)
        sys.stdout.write('is starting\r\n')

        # TCPClient instance creation

        try:
            self.server = TCPServer(2, self.serverip, self.serverport)
        except:
            self.stop()

        while True:
            if self.server.state is SOCK_CLOSE_STATE:
                try:
                    cur_state = self.server.state
                    self.server.open()
                    # sys.stdout.write('1 : %r' % self.server.getsockstate())
                    if self.server.state is SOCK_OPEN_STATE:
                        sys.stdout.write('[%r] is OPEN\r\n' % (self.serverip))
                        # sys.stdout.write('[%r] client.working_state is %r\r\n' % (self.serverip, self.server.working_state))
                        time.sleep(1)
                except (KeyboardInterrupt, SystemExit):
                    sys.stdout.write('OPEN: keyboard interrupt occured!!')
                    for i in range(self.trycount):
                        print('trycount: ', i)

            elif self.server.state is SOCK_OPEN_STATE:
                cur_state = self.server.state
                try:
                    self.server.connect()
                    # time.sleep(3)
                except Exception as e:
                    time.sleep(1)
                    # print('Server.connect() error:', e)
                try:
                    # sys.stdout.write('2 : %r' % self.server.getsockstate())
                    if self.server.state is SOCK_CONNECT_STATE:
                        sys.stdout.write('[%r] is CONNECTED\r\n' % (self.serverip))
                        # sys.stdout.write('[%r] client.working_state is %r\r\n' % (self.serverip, self.server.working_state))
                        time.sleep(1)
                except (KeyboardInterrupt, SystemExit):
                    sys.stdout.write('CONNECT: keyboard interrupt occured!!\nExit.')
                    for i in range(self.trycount):
                        time.sleep(1)
                        self.stop()
#                        threads[i].stop()

            elif self.server.state is SOCK_CONNECT_STATE:
                if self.server.working_state == idle_state:
                    # sys.stdout.write('3 : %r' % self.server.getsockstate())
                    try:
                        if self.totaltrycount >= self.trycount:
                            break
                        # time.sleep(1)
                        self.server.write(msg)
                        # print('============== debug 3')
                        logstr = '[' + self.serverip + '] sent ' + msg + '\r\n'
                        sys.stdout.write(logstr)
                        # self.f.write(logstr)
                        self.server.working_state = datasent_state
                        self.totaltrycount += 1
                    except Exception as e:
                        time.sleep(1)
                        sys.stdout.write('%r\r\n' % e)
                        # if isinstance(e.args, tuple):
                        #     print('errno is %d', e[0])
                        #     if e[0] == errno.EPIPE:
                        #         # remote peer diconnected
                        #         print('Detected remote disconnect')
                        #     else:
                        #         pass
                        # else:
                        #     print('socket error', e)
                        # self.server.close()
                        # break

                elif self.server.working_state == datasent_state:
                    # sys.stdout.write('4 : %r' % self.server.getsockstate())
                    time.sleep(2)
                    response = self.server.readline()
                    # print('===> TCP reponse', response)
                    if (response != ""):
                        logstr = '[' + self.serverip + '] received ' + response + '\r\n'
                        sys.stdout.write(logstr)
                        sys.stdout.flush()
                        # self.f.write(logstr)
                        if (msg in response):
                            logstr = '[' + self.serverip + ']' + strftime(" %d %b %Y %H:%M:%S",
                                                                          localtime()) + ': success,'
                            self.successcount += 1
                        # sys.stdout.write(logstr)
                        #							self.f.write(logstr)
                        else:
                            logstr = '[' + self.serverip + ']' + strftime(" %d %b %Y %H:%M:%S",
                                                                          localtime()) + ': fail by broken data,'
                            #							sys.stdout.write(logstr)
                            self.failcount += 1
                        # self.f.write(logstr)

                        logstr = logstr + ' success rate: ' \
                                 + "{0:.2f}".format(float(self.successcount) / float(self.totaltrycount) * 100) + '%, [' \
                                 + str(self.successcount) + '/' + str(self.totaltrycount) + ']\r\n\r\n'
                        sys.stdout.write(logstr)
                        # self.f.write(logstr)
                        # time.sleep(1)
                        self.server.working_state = idle_state

                    response = ""

        self.stop()

if __name__ == '__main__':

    dst_ip = ''
    dst_port = 5000
    dst_num = 0
    retrycount = 10

    # msg = "Hello WIZ750SR\r"

    if len(sys.argv) <= 4:
        sys.stdout.write('Invalid syntax. Refer to below\r\n')
        sys.stdout.write('%s -s <WIZ107SR ip address> -c <server count>\r\n)' % sys.argv[0])
        sys.exit(0)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:c:r:")
    except getopt.GetoptError:
        sys.stdout.write('Invalid syntax. Refer to below\r\n')
        sys.stdout.write('%s -s <WIZ107SR ip address>  -c <server count>\r\n)' % sys.argv[0])
        sys.exit(0)

    sys.stdout.write('%r\r\n' % opts)

    threads = []

    try:
        for opt, arg in opts:
            if opt == '-h':
                sys.stdout.write('Valid syntax\r\n')
                sys.stdout.write('%s -s <WIZ107SR ip address>  -c <server count>\r\n' % sys.argv[0])
                sys.exit(0)
            elif opt in ("-s", "--sip"):
                dst_ip = arg
                sys.stdout.write('%r\r\n' % dst_ip)
            elif opt in ("-c", "--count"):
                dst_num = int(arg)
                sys.stdout.write('%r\r\n' % dst_num)
            elif opt in ("-r", "--retry"):
                retrycount = int(arg)
                sys.stdout.write('%r\r\n' % retrycount)

        lastnumindex = dst_ip.rfind('.')
        lastnum = int(dst_ip[lastnumindex + 1:len(dst_ip)])


    # filename = strftime("%d-%b-%Y", localtime()) + '_log.txt'
    # fd = open(filename, 'w')

        for i in range(dst_num):
            t = TCPClientThread(dst_ip[:lastnumindex + 1] + str(lastnum + i), dst_port, retrycount)
            threads.append(t)

        for i in range(dst_num):
            threads[i].start()

        end_flag = False

        while not end_flag:
            end_flag = not end_flag
            for i in range(len(threads)):
                end_flag &= not threads[i].is_alive()

    except (KeyboardInterrupt, SystemExit):
        for i in range(dst_num):
            threads[i].stop()
    # finally:
    #     #		time.sleep(5)
    #     fd.close()

