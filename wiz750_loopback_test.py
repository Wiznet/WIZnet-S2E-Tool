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

OP_SEARCHALL = 1
OP_SETIP = 2
OP_CHECKIP = 3
OP_FACTORYRESET = 4
OP_GETDETAIL = 5

if __name__=='__main__':

    retrycount = 10

    if len(sys.argv) <= 4:
        sys.stdout.write('Invalid syntax. Refer to below\r\n')
        sys.stdout.write('%s -r <packet_send count> -t <target_ip>\r\n' % sys.argv[0])
        sys.exit(0)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:r:")
    except getopt.GetoptError:
        sys.stdout.write('Invalid syntax. Refer to below\r\n')
        sys.stdout.write('%s -r <packet_send count> -t <target_ip>\r\n' % sys.argv[0])
        sys.exit(0)

    threads = []

    try:
        for opt, arg in opts:
            if opt == '-h':
                sys.stdout.write('Valid syntax\r\n')
                sys.stdout.write('%s -r <packet_send count> -t <target_ip>\r\n' % sys.argv[0])
                sys.exit(0)
            elif opt in ("-r", "--retry"):
                retrycount = int(arg)
                # sys.stdout.write('%r\r\n' % retrycount)
            elif opt in ("-t", "--target"):
                dst_ip = arg
                # sys.stdout.write('%r\r\n' % dst_ip)

        conf_sock = WIZUDPSock(5000, 50001)
        conf_sock.open()
        wizmsghangler = WIZMSGHandler(conf_sock)
        cmd_list = []

        ###################################
        # Search All Devices on the network
        cmd_list.append(["MA", "FF:FF:FF:FF:FF:FF"])
        cmd_list.append(["PW", " "])
        cmd_list.append(["MC", ""])
        cmd_list.append(["VR", ""])
        cmd_list.append(["MN", ""])
        cmd_list.append(["UN", ""])
        cmd_list.append(["ST", ""])
        cmd_list.append(["IM", ""])
        cmd_list.append(["OP", ""])
        cmd_list.append(["DD", ""])
        cmd_list.append(["CP", ""])
        cmd_list.append(["PO", ""])
        cmd_list.append(["DG", ""])
        # sys.stdout.write("%s\r\n" % cmd_list)
        wizmsghangler.makecommands(cmd_list, OP_SEARCHALL)
        wizmsghangler.sendcommands()
        retval = wizmsghangler.parseresponse()
        sys.stdout.write("%r devices are detected\r\n" % retval)

        ###################################
        # Set a consequent IP address and the same port number 5000 to each WIZ750SR Device

        # dst_ip = "192.168.50.50"
        dst_port = "5000"

        lastnumindex = dst_ip.rfind('.')
        lastnum = int(dst_ip[lastnumindex+1:len(dst_ip)])
        try:
            for i in range(0, retval):
                cmd_list[:] = []
                mac_addr = wizmsghangler.getmacaddr(i)
                print ("mac addr: " + mac_addr)
                target_ip = dst_ip[:lastnumindex + 1] + str(lastnum + i)
                target_gw = dst_ip[:lastnumindex + 1] + str(1)
                cmd_list.append(["MA", mac_addr])
                cmd_list.append(["PW", " "])
                cmd_list.append(["LI", target_ip])
                cmd_list.append(["GW", target_gw])
                cmd_list.append(["LP", dst_port])
                cmd_list.append(["OP", "1"])
                cmd_list.append(["SV", ""]) # save device setting
                cmd_list.append(["RT", ""]) # Device reboot
                # sys.stdout.write("%s\r\n" % cmd_list)
                wizmsghangler.makecommands(cmd_list, OP_SETIP)
                wizmsghangler.sendcommands()
                wizmsghangler.parseresponse()
    
                time.sleep(2)
                t = TCPClientThread(target_ip, int(dst_port), retrycount)
                t.start()
                threads.append(t)
                # time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            sys.stdout.write('Keyboard interrupt occured!!')
            for i in range(retrycount):
                threads[i].stop()

        ###################################
        # Factory Reset all selected Devices
        # for i in range(0, retval):
        #     cmd_list[:] = []
        #     mac_addr = wizmsghangler.getmacaddr(i)
        #     cmd_list.append(["MA", mac_addr])
        #     cmd_list.append(["PW", ""])
        #     cmd_list.append(["FR", ""])
        #     cmd_list.append(["RT", ""])
        #     # sys.stdout.write("%s\r\n" % cmd_list)
        #     wizmsghangler.makecommands(cmd_list, OP_FACTORYRESET)
        #     wizmsghangler.sendcommands()
        #     wizmsghangler.parseresponse()

        # sys.stdout.write("%s\r\n" % cmd_list)

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
    finally:
        for i in range(0, retval):
            cmd_list[:] = []
            mac_addr = wizmsghangler.getmacaddr(i)
            cmd_list.append(["MA", mac_addr])
            cmd_list.append(["PW", ""])
            cmd_list.append(["FR", ""])
            cmd_list.append(["RT", ""])
            # sys.stdout.write("%s\r\n" % cmd_list)
            wizmsghangler.makecommands(cmd_list, OP_FACTORYRESET)
            wizmsghangler.sendcommands()
            wizmsghangler.parseresponse()
            
