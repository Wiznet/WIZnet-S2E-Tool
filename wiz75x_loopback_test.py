#!/usr/bin/python

import socket
import time
import struct
import binascii
import sys
import getopt
import logging
from WIZ750CMDSET import WIZ750CMDSET
from WIZUDPSock import WIZUDPSock
from WIZMSGHandler import WIZMSGHandler
from TCPClientThread import TCPClientThread
from WIZArgParser import WIZArgParser
from wizconfig import WIZMakeCMD

OP_SEARCHALL = 1
OP_SETIP = 2
OP_CHECKIP = 3
OP_FACTORYRESET = 4
OP_GETDETAIL = 5

ONE_PORT_S2E = '1'
TWO_PORT_S2E = '2'

if __name__=='__main__':
    wizarg = WIZArgParser()
    args = wizarg.loopback_arg()
    # print(args)
        
    wizmakecmd = WIZMakeCMD()

    if len(sys.argv) <= 4:
        print('Invalid syntax. Please refer to %s -h\n' % sys.argv[0])
        sys.exit(0)

    threads = []

    try:
        retrycount = args.retry

        conf_sock = WIZUDPSock(5000, 50001)
        conf_sock.open()
        wizmsghangler = WIZMSGHandler(conf_sock)
        cmd_list = []

        ###################################
        # Search All Devices on the network
        cmd_list = wizmakecmd.search()
        # sys.stdout.write("%s\r\n" % cmd_list)
        wizmsghangler.makecommands(cmd_list, OP_SEARCHALL)
        wizmsghangler.sendcommands()
        retval = wizmsghangler.parseresponse()
        sys.stdout.write("%r devices are detected\r\n" % retval)

        ###################################
        # Set a consequent IP address and the same port number 5000 to each WIZ750SR Device
        # dst_ip = "192.168.50.50"
        dst_ip = args.targetip
        # print(dst_ip)
        ch0_dst_port = "5000"
        if args.select is TWO_PORT_S2E:
            ch1_dst_port = "5001"

        lastnumindex = dst_ip.rfind('.')
        lastnum = int(dst_ip[lastnumindex+1:len(dst_ip)])
        try:
            for i in range(0, retval):
                cmd_list[:] = []
                mac_addr = wizmsghangler.getmacaddr(i)
                mac_addr = mac_addr.decode('utf-8')
                print ("Device %d mac addr: %s" % (i+1, mac_addr))
                target_ip = dst_ip[:lastnumindex + 1] + str(lastnum + i)
                target_gw = dst_ip[:lastnumindex + 1] + str(1)
                cmd_list.append(["MA", mac_addr])
                cmd_list.append(["PW", " "])
                cmd_list.append(["LI", target_ip])
                cmd_list.append(["GW", target_gw])
                cmd_list.append(["LP", ch0_dst_port])
                if args.select is TWO_PORT_S2E:
                    cmd_list.append(["QL", ch1_dst_port])
                cmd_list.append(["OP", "1"])
                cmd_list.append(["SV", ""]) # save device setting
                cmd_list.append(["RT", ""]) # Device reboot
                # sys.stdout.write("%s\r\n" % cmd_list)
                wizmsghangler.makecommands(cmd_list, OP_SETIP)
                wizmsghangler.sendcommands()
                wizmsghangler.parseresponse()
    
                time.sleep(2)
                t = TCPClientThread(target_ip, int(ch0_dst_port), retrycount)
                t.start()
                threads.append(t)

                if args.select is TWO_PORT_S2E:
                    time.sleep(2)
                    t2 = TCPClientThread(target_ip, int(ch1_dst_port), retrycount)
                    t2.start()
                    threads.append(t2)
        except (KeyboardInterrupt, SystemExit):
            sys.stdout.write('Keyboard interrupt occured!!')
            for i in range(retrycount):
                threads[i].stop()

        end_flag = False
        stop_thread_count = 0

        while not end_flag:
            end_flag = not end_flag
            for i in range(len(threads)):
                end_flag &= not threads[i].is_alive()
            #     if(not threads[i].is_alive()):
            #         sys.stdout.write("thread[%r] is alive : %r\r\n" % (i, threads[i].is_alive()))
            #         stop_thread_count += 1
            #
            # if stop_thread_count is len(threads):
            #     break
            # else:
            #     stop_thread_count = 0
            #     #     sys.stdout.write("[%r] ")
                #     end_flag = False

        sys.stdout.write("all threads are dead\r\n")
    except (KeyboardInterrupt, SystemExit):
        for i in range(len(threads)):
            threads[i].stop()
            print('thread %d stop. %s' % (i, thread[i]))
    finally:
        print('Loopback test finished. Factory reset will be proceed.')
        for i in range(0, retval):
            cmd_list[:] = []
            mac_addr = wizmsghangler.getmacaddr(i)
            mac_addr = mac_addr.decode('utf-8')
            cmd_list.append(["MA", mac_addr])
            cmd_list.append(["PW", ""])
            cmd_list.append(["FR", ""])
            cmd_list.append(["RT", ""])
            # print(cmd_list)
            wizmsghangler.makecommands(cmd_list, OP_FACTORYRESET)
            wizmsghangler.sendcommands()
            wizmsghangler.parseresponse()
            
