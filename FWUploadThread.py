#!/usr/bin/python

from wizsocket.TCPClient import TCPClient
# from WIZUDPSock import WIZUDPSock
from WIZMSGHandler import WIZMSGHandler
import binascii
import sys
import time
# import logging
import threading
# import getopt
import os

OP_SEARCHALL = 1
OP_SETIP = 2
OP_CHECKIP = 3
OP_FACTORYRESET = 4
OP_GETDETAIL = 5
OP_FWUP = 6

SOCK_CLOSE_STATE = 1
SOCK_OPENTRY_STATE = 2
SOCK_OPEN_STATE = 3
SOCK_CONNECTTRY_STATE = 4
SOCK_CONNECT_STATE = 5

idle_state = 1
datasent_state = 2


def jumpToApp(mac_addr, idcode, conf_sock, sock_type):
    cmd_list = []

    conf_sock.open()
    wizmsghangler = WIZMSGHandler(conf_sock)

    # boot mode change: App boot mode
    print("[%s] Jump to app boot mode" % mac_addr)

    cmd_list.append(["MA", mac_addr])
    cmd_list.append(["PW", idcode])
    cmd_list.append(["AB", ""])
    wizmsghangler.makecommands(cmd_list, OP_FWUP)
    if sock_type == "udp":
        wizmsghangler.sendcommands()
    else:
        wizmsghangler.sendcommandsTCP()


class FWUploadThread(threading.Thread):
    # initialization
    def __init__(self, idcode, conf_sock, sock_type):
        threading.Thread.__init__(self)

        self.dest_mac = None
        self.bin_filename = None
        self.fd = None
        self.data = None
        self.client = None
        self.timer1 = None
        self.istimeout = 0
        self.serverip = None
        self.serverport = None
        self.idcode = idcode

        self.sentbyte = 0

        self.sock_type = sock_type
        self.conf_sock = conf_sock
        conf_sock.open()
        self.wizmsghangler = WIZMSGHandler(conf_sock)

    def setparam(self, dest_mac, binaryfile):
        self.dest_mac = dest_mac
        self.bin_filename = binaryfile
        self.fd = open(self.bin_filename, "rb")
        self.data = self.fd.read(-1)
        self.remainbytes = len(self.data)
        self.curr_ptr = 0

        sys.stdout.write("\nFirmware file size: %r\n\n" % len(self.data))

    def myTimer(self):
        # sys.stdout.write('timer1 timeout\r\n')
        self.istimeout = 1

    def jumpToApp(self):
        cmd_list = []

        # boot mode change: App boot mode
        print("[%s] Jump to app boot mode" % self.dest_mac)

        cmd_list.append(["MA", self.dest_mac])
        cmd_list.append(["PW", self.idcode])
        cmd_list.append(["AB", ""])
        self.wizmsghangler.makecommands(cmd_list, OP_FWUP)
        if self.sock_type == "udp":
            self.wizmsghangler.sendcommands()
        else:
            self.wizmsghangler.sendcommandsTCP()

            if self.conf_sock != None:
                self.conf_sock.shutdown()
            time.sleep(1)

        # print('jumpToApp cmd_list: %s' % cmd_list)

    # def run(self):
    def sendCmd(self, command):
        cmd_list = []
        self.resp = None

        # Send FW UPload request message
        cmd_list.append(["MA", self.dest_mac])
        cmd_list.append(["PW", self.idcode])
        cmd_list.append([command, str(len(self.data))])
        # sys.stdout.write("cmd_list: %s\r\n" % cmd_list)
        self.wizmsghangler.makecommands(cmd_list, OP_FWUP)

        # if no reponse from device, retry for several times.
        for i in range(3):
            if self.sock_type == "udp":
                self.wizmsghangler.sendcommands()
            else:
                self.wizmsghangler.sendcommandsTCP()
            self.resp = self.wizmsghangler.parseresponse()
            if self.resp != "":
                break
            time.sleep(1)

    def run(self):
        if self.resp != "":
            resp = self.resp.decode("utf-8")
            # print('resp', resp)
            params = resp.split(":")
            sys.stdout.write("Dest IP: %s, Dest Port num: %r\r\n" % (params[0], int(params[1])))
            self.serverip = params[0]
            self.serverport = int(params[1])

            # network reachable check
            os.system("ping " + ("-n 1 " if sys.platform.lower() == "win32" else "-c 1 ") + self.serverip)
            ping_reponse = os.system(
                "ping " + ("-n 1 " if sys.platform.lower() == "win32" else "-c 1 ") + self.serverip
            )
            # ping_reponse = os.system('ping -n 1 ' + params[0])
            if ping_reponse == 0:
                print("Device[%s] network OK" % self.dest_mac)
            else:
                print(
                    "<Ping Error>: Device[%s]: %s is unreachable.\n\tRefer --multiset or --ip options to set IP address."
                    % (self.dest_mac, self.serverip)
                )
                sys.exit(0)
        else:
            print("@@@@@ Device[%s]: No response from device. Check the network or device status." % (self.dest_mac))
            sys.exit(0)

        try:
            self.client = TCPClient(2, params[0], int(params[1]))
        except:
            pass
        self.retrycheck = 0
        try:
            # sys.stdout.write("%r\r\n" % self.client.state)
            while True:
                if self.retrycheck > 20:
                    break

                self.retrycheck += 1

                if self.client.state == SOCK_CLOSE_STATE:
                    if self.timer1 != None:
                        self.timer1.cancel()
                    cur_state = self.client.state
                    try:
                        self.client.open()
                        # sys.stdout.write('1 : %r\r\n' % self.client.getsockstate())
                        # sys.stdout.write("%r\r\n" % self.client.state)
                        if self.client.state == SOCK_OPEN_STATE:
                            # sys.stdout.write('[%r] is OPEN\r\n' % (self.serverip))
                            sys.stdout.write("[%r] is OPEN | %s\r\n" % (self.serverip, self.bin_filename))
                            # sys.stdout.write('[%r] client.working_state is %r\r\n' % (self.serverip, self.client.working_state))
                            time.sleep(0.1)
                    except Exception as e:
                        print(e)

                elif self.client.state == SOCK_OPEN_STATE:
                    cur_state = self.client.state
                    # time.sleep(2)
                    try:
                        self.client.connect()
                        # sys.stdout.write('2 : %r' % self.client.getsockstate())
                        if self.client.state == SOCK_CONNECT_STATE:
                            # sys.stdout.write('[%r] is CONNECTED\r\n' % (self.serverip))
                            sys.stdout.write("[%r] is CONNECTED | %s\r\n" % (self.serverip, self.bin_filename))
                            # sys.stdout.write('[%r] client.working_state is %r\r\n' % (self.serverip, self.client.working_state))
                            # time.sleep(1)
                    except Exception as e:
                        print(e)

                elif self.client.state == SOCK_CONNECT_STATE:
                    # if self.client.working_state == idle_state:
                    # sys.stdout.write('3 : %r' % self.client.getsockstate())
                    try:
                        while self.remainbytes != 0:
                            if self.client.working_state == idle_state:
                                if self.remainbytes >= 1024:
                                    msg = bytearray(1024)
                                    msg[:] = self.data[self.curr_ptr : self.curr_ptr + 1024]
                                    self.client.write(msg)
                                    self.sentbyte = 1024
                                    # sys.stdout.write('1024 bytes sent from at %r\r\n' % (self.curr_ptr))
                                    sys.stdout.write(
                                        "[%s] 1024 bytes sent from at %r\r\n" % (self.serverip, self.curr_ptr)
                                    )
                                    self.curr_ptr += 1024
                                    self.remainbytes -= 1024
                                else:
                                    msg = bytearray(self.remainbytes)
                                    msg[:] = self.data[self.curr_ptr : self.curr_ptr + self.remainbytes]
                                    self.client.write(msg)
                                    # sys.stdout.write('Last %r byte sent from at %r \r\n' % (self.remainbytes, self.curr_ptr))
                                    sys.stdout.write(
                                        "[%s] Last %r byte sent from at %r \r\n"
                                        % (self.serverip, self.remainbytes, self.curr_ptr)
                                    )
                                    self.curr_ptr += self.remainbytes
                                    self.remainbytes = 0
                                    self.sentbyte = self.remainbytes

                                self.client.working_state = datasent_state

                                self.timer1 = threading.Timer(2.0, self.myTimer)
                                self.timer1.start()
                            elif self.client.working_state == datasent_state:
                                # sys.stdout.write('4 : %r' % self.client.getsockstate())
                                response = self.client.readbytes(2)
                                if response != None:
                                    if int(binascii.hexlify(response), 16):
                                        self.client.working_state = idle_state
                                        self.timer1.cancel()
                                        self.istimeout = 0
                                    else:
                                        print(f"ERROR: Device[{self.dest_mac}]: No response from device. Stop FW upload...")
                                        self.client.close()
                                        sys.exit(0)

                                if self.istimeout == 1:
                                    self.istimeout = 0
                                    self.client.working_state = idle_state
                                    self.client.close()
                                    sys.exit(0)

                    except Exception as e:
                        print(e)
                        response = ""
                    break

            if self.retrycheck > 20:
                print(f"Device [{self.dest_mac}] firmware upload fail. (file: {self.bin_filename})\r\n")
            else:
                print(f"Device [{self.dest_mac}] firmware upload success! (file: {self.bin_filename})\r\n")
            # for send FIN packet
            time.sleep(1)
            self.client.shutdown()
        except (KeyboardInterrupt, SystemExit):
            print(e)
        finally:
            pass
