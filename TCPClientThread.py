#!/usr/bin/python

# Implemented by James YS Kim


import sys

sys.path.append('./TCPClient/')
import time
import socket
import getopt
import threading
# import thread

from TCPClient import TCPClient
from time import gmtime, strftime, localtime

msg = "Hello WIZ750SR\r"

class TCPClientThread(threading.Thread):
    def __init__(self, serverip, serverport, trycount):
        threading.Thread.__init__(self)
        self.serverip = serverip
        self.serverport = serverport
        # self.f = fd
        self.timer1 = None
        self.istimeout = 0
        self.totaltrycount = 0
        self.successcount = 0
        self.failcount = 0
        self.trycount = trycount
        self.client = None

    def stop(self):
        if self.client is not None:
            self.client.close()
            self.client = None
        if self.timer1 is not None:
            if self.timer1.is_alive():
                self.timer1.cancel()
        # sys.stdout.write('thread for %r ' % self.serverip)
        sys.stdout.write('thread for %s:%s ' % (self.serverip, self.serverport))
        sys.stdout.write('is shutdowning\r\n')
        # if not self.f.closed:
        if self.totaltrycount > 0:
            logstr = "======================================\r\n"
            logstr = logstr + '[' + self.serverip + ':' + str(self.serverport) + '] stopped at ' + strftime("%d %b %Y %H:%M:%S", localtime()) + '\r\n'
            logstr = logstr + 'Total try: ' + str(self.totaltrycount) + '\r\n'
            logstr = logstr + 'Success count: ' + str(self.successcount) + '\r\n'
            logstr = logstr + 'Fail count: ' + str(self.failcount) + '\r\n'
            logstr = logstr + 'Success Rate: ' + "{0:.1f}".format(
                float(self.successcount) / float(self.totaltrycount) * 100) + '%\r\n'
            logstr = logstr + '======================================\r\n'
            sys.stdout.write(logstr)
        else:
            logstr = "======================================\r\n"
            logstr = logstr + '[' + self.serverip + ':' + str(self.serverport) + '] stopped at ' + strftime("%d %b %Y %H:%M:%S", localtime()) + '\r\n'
            logstr = logstr + 'Connection Failed\r\n'
            logstr = logstr + '======================================\r\n'
            sys.stdout.write(logstr)
        #     self.f.write(logstr)
        self._Thread__stop()

    def myTimer(self):
        sys.stdout.write('timer1 timeout\r\n')
        self.istimeout = 1

    def run(self):
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
            self.client = TCPClient(2, self.serverip, self.serverport)
        except:
            self.stop()

        # time.sleep(2)
        #		filename = self.serverip + '_log.txt'

        # print(filename)
        IsTimeout = 0

        #		self.f = open(filename, 'w+')
        # self.f = fd
        try:
            while True:

                if self.client.state is SOCK_CLOSE_STATE:
                    if self.timer1 is not None:
                        self.timer1.cancel()
                    cur_state = self.client.state
                    self.client.open()
                    # sys.stdout.write('1 : %r' % self.client.getsockstate())
                    if self.client.state is SOCK_OPEN_STATE:
                        sys.stdout.write('[%r] is OPEN\r\n' % (self.serverip))
                        # sys.stdout.write('[%s:%s] is OPEN\r\n' % (self.serverip, self.serverport))
                        # sys.stdout.write('[%r] client.working_state is %r\r\n' % (self.serverip, self.client.working_state))
                        time.sleep(1)

                elif self.client.state is SOCK_OPEN_STATE:
                    cur_state = self.client.state
                    self.client.connect()
                    # sys.stdout.write('2 : %r' % self.client.getsockstate())
                    if self.client.state is SOCK_CONNECT_STATE:
                        sys.stdout.write('[%r] is CONNECTED\r\n' % (self.serverip))
                        # sys.stdout.write('[%s:%s] is CONNECTED\r\n' % (self.serverip, self.serverport))
                        # sys.stdout.write('[%r] client.working_state is %r\r\n' % (self.serverip, self.client.working_state))
                        time.sleep(1)

                elif self.client.state is SOCK_CONNECT_STATE:
                    if self.client.working_state == idle_state:
                        # sys.stdout.write('3 : %r' % self.client.getsockstate())
                        try:
                            if self.trycount is not -1 and self.totaltrycount >= self.trycount:
                                break

                            self.client.write(msg)
                            logstr = '[' + self.serverip + '] sent ' + msg + '\r\n'
                            sys.stdout.write(logstr)
                            # self.f.write(logstr)
                            self.client.working_state = datasent_state
                            self.istimeout = 0
                            self.totaltrycount += 1

                            self.timer1 = threading.Timer(2.0, self.myTimer)
                            self.timer1.start()
                            # sys.stdout.write('timer 1 started\r\n')
                        except Exception as e:
                            sys.stdout.write('%r\r\n' % e)
                    elif self.client.working_state == datasent_state:
                        # sys.stdout.write('4 : %r' % self.client.getsockstate())
                        # minimum delay
                        time.sleep(0.05)
                        # time.sleep(1.5)
                        response = self.client.readline()
                        if (response != ""):
                            logstr = '[' + self.serverip + '] received ' + response + '\r\n'
                            sys.stdout.write(logstr)
                            sys.stdout.flush()
                            # self.f.write(logstr)
                            self.timer1.cancel()
                            # sys.stdout.write('timer 1 cancelled\r\n')
                            self.istimeout = 0

                            if (msg in response):
                                logstr = '[' + self.serverip + ']' + strftime(" %d %b %Y %H:%M:%S",
                                                                              localtime()) + ': success, '
                                self.successcount += 1
                            # sys.stdout.write(logstr)
                            #							self.f.write(logstr)
                            else:
                                logstr = '[' + self.serverip + ']' + strftime(" %d %b %Y %H:%M:%S",
                                                                              localtime()) + ': fail by broken data, '
                                #							sys.stdout.write(logstr)
                                self.failcount += 1
                            # self.f.write(logstr)

                            logstr = logstr + 'success rate : ' \
                                     + "{0:.2f}".format(float(self.successcount) / float(self.totaltrycount) * 100) + '%, [' \
                                     + str(self.successcount) + '/' + str(self.totaltrycount) + ']\r\n'
                            sys.stdout.write(logstr)
                            # self.f.write(logstr)
                            time.sleep(0.1)
                            self.client.working_state = idle_state

                        if self.istimeout is 1:
                            # self.timer1.cancel()
                            self.istimeout = 0
                            logstr = '[' + self.serverip + ']' + strftime(" %d %b %Y %H:%M:%S",
                                                                          localtime()) + ': fail by timeout, '
                            #						sys.stdout.write(logstr)
                            self.failcount += 1
                            #						self.f.write(logstr)
                            logstr = logstr + ' success rate : ' \
                                     + "{0:.2f}".format(float(self.successcount) / float(self.totaltrycount) * 100) + '% [' \
                                     + str(self.successcount) + '/' + str(self.totaltrycount) + ']\r\n'
                            sys.stdout.write(logstr)
                            # self.f.write(logstr)
                            # time.sleep(3)
                            self.client.working_state = idle_state
                            self.client.close()

                        response = ""

                    # time.sleep(5)
                    # cur_state = self.client.state
                    # self.client.close()
                    # if self.client.state is SOCK_CLOSE_STATE:
                    #     sys.stdout.write('[%r] is CLOSED\r\n' % (self.serverip))
                    # time.sleep(2)

        except:
            pass
        finally:
            self.stop()

if __name__ == '__main__':

    dst_ip = ''
    dst_port = 5000
    dst_num = 0
    retrycount = 10

    # msg = "Hello WIZ750SR\r"

    if len(sys.argv) <= 4:
        sys.stdout.write('Invalid syntax. Refer to below\r\n')
        sys.stdout.write('%s -s <WIZ750SR ip address> -c <server count>\r\n)' % sys.argv[0])
        sys.exit(0)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:c:r:")
    except getopt.GetoptError:
        sys.stdout.write('Invalid syntax. Refer to below\r\n')
        sys.stdout.write('%s -s <WIZ750SR ip address>  -c <server count>\r\n)' % sys.argv[0])
        sys.exit(0)

    sys.stdout.write('%r\r\n' % opts)

    threads = []

    try:
        for opt, arg in opts:
            if opt == '-h':
                sys.stdout.write('Valid syntax\r\n')
                sys.stdout.write('%s -s <WIZ750SR ip address>  -c <server count>\r\n' % sys.argv[0])
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

