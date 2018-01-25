# -*- coding: utf-8 -*-

## Make Serial command

import socket
import time
import struct
import binascii
import sys
import getopt
import logging
import serial
import re
import os
from WIZ750CMDSET import WIZ750CMDSET
from WIZ752CMDSET import WIZ752CMDSET
from WIZUDPSock import WIZUDPSock
from WIZMSGHandler import WIZMSGHandler
from WIZArgParser import WIZArgParser
from FWUpload import FWUpload
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

OP_SEARCHALL = 1
OP_GETCOMMAND = 2
OP_SETCOMMAND = 3
OP_SETFILE = 4
OP_GETFILE = 5
OP_FWUP = 6

BAUDRATES = [300, 600, 1200, 1800, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400]

class WIZMakeCMD:
    def search(self):
        cmd_list = []
        # Search All Devices on the network
        # 장치 검색 시 필요 정보 Get
        cmd_list.append(["MA", "FF:FF:FF:FF:FF:FF"])
        cmd_list.append(["PW", " "])
        cmd_list.append(["MC", ""])
        cmd_list.append(["LI", ""])    # IP address
        cmd_list.append(["VR", ""])
        cmd_list.append(["MN", ""])
        cmd_list.append(["RH", ""])
        cmd_list.append(["RP", ""])
        cmd_list.append(["OP", ""]) # Network operation mode
        cmd_list.append(["IM", ""]) # IP address allocation method(Static/DHCP)
        return cmd_list
    
    def get_value(self, mac_addr, filename):
        # 파일의 command들에 대한 정보를 가져옴
        cmd_list = []
        f = open(filename, 'r')
        cmd_list.append(["MA", mac_addr])
        cmd_list.append(["PW", " "])
        for line in f:
#			print len(line), line.decode('hex')
            if len(line) > 2 :
                cmd_list.append([line[:2], ""])
        f.close()
        return cmd_list

    def set_value(self, mac_addr, filename):
        # 파일에서 cmd/parameter set 정보를 불러옴
        cmd_list = []
        f = open(filename, 'r')
        cmd_list.append(["MA", mac_addr])
        cmd_list.append(["PW", " "])
        getcmd_list = []
        for line in f:
            if len(line) > 2:
                cmd_list.append([line[:2], line[2:]])
                getcmd_list.append(line[:2])
        for cmd in getcmd_list:
            cmd_list.append([cmd, ""])
        cmd_list.append(["SV", ""])
        cmd_list.append(["RT", ""])
        f.close()
        return cmd_list

    # 장치 정보 획득 (Get)
    def getcommand(self, macaddr, command_list):
        cmd_list = []    # 초기화
        cmd_list.append(["MA", macaddr])
        cmd_list.append(["PW", " "])
        cmd_list.append(["MC", ""])
        for i in range(len(command_list)):
            cmd_list.append([command_list[i], ""]) 
        return cmd_list

    def setcommand(self, macaddr, command_list, param_list):
        cmd_list = []
        try:
            # print('Macaddr: %s' % macaddr)
            cmd_list.append(["MA", macaddr])
            cmd_list.append(["PW", " "])
            for i in range(len(command_list)):
                cmd_list.append([command_list[i], param_list[i]]) 
            cmd_list.append(["SV", ""]) # save device setting
            cmd_list.append(["RT", ""]) # Device reboot
            return cmd_list
        except Exception as e:
            sys.stdout.write('%r\r\n' % e)            

    def reset(self, mac_addr):
        cmd_list = []
        cmd_list.append(["MA", mac_addr])
        cmd_list.append(["PW", " "])
        cmd_list.append(["RT", ""])	
        return cmd_list
    
    def factory_reset(self, mac_addr):
        cmd_list = []
        cmd_list.append(["MA", mac_addr])
        cmd_list.append(["PW", " "])
        cmd_list.append(["FR", ""])	
        return cmd_list
    
    def set_maclist(self, mac_list):
        try:
            if os.path.isfile('mac_list.txt'):
                f = open('mac_list.txt', 'a+')
            else:
                f = open('mac_list.txt', 'w+')
            data = f.readlines()
        except Exception as e:
            sys.stdout.write(e)
        # print('data', data)
        for i in range(len(mac_list)):
            print('* Device %d: %s' % (i+1, mac_list[i]))
            info = "%s\r\n" % (mac_list[i])            
            if info in data:
                # print('===> already in')
                pass
            else:
                print('New Device: %s' % mac_list[i])
                f.write(info)
        f.close()

    def get_hostip(self):
        # Get Host IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

if __name__ == '__main__':
    wizmakecmd = WIZMakeCMD()

    wizarg = WIZArgParser()
    args = wizarg.config_arg()

    wiz750cmdObj = WIZ750CMDSET(1)

    conf_sock = WIZUDPSock(5000, 50001)
    conf_sock.open()
    wizmsghangler = WIZMSGHandler(conf_sock)

    FUObj = FWUpload(logging.DEBUG)

    cmd_list = []
    setcmd = {}
    op_code = OP_SEARCHALL
    # print(args)

    if args.search or args.clear:
        if len(sys.argv) is not 2:
            print('Invalid argument. Please refer to %s -h\n' % sys.argv[0])
            sys.exit(0)
    else:
        if len(sys.argv) < 3:
            print('Invalid argument. Please refer to %s -h\n' % sys.argv[0])
            sys.exit(0)
    ## single arg
    # if args.search:
    #     print('Start to Search devices...')
    #     cmd_list = wizmakecmd.search()

    # not send cmd
    if args.clear:
        print('Mac list clear')
        f = open('mac_list.txt', 'w')
        f.close()
    ## single or all device set
    else:
        if args.macaddr:
            mac_addr = args.macaddr
            if wiz750cmdObj.isvalidparameter("MC", mac_addr) is False :
                sys.stdout.write("Invalid Mac address!\r\n")
                sys.exit(0)
        # file config
        if args.getfile or args.setfile:
            if args.setfile:
                op_code = OP_SETFILE
                print('[Setfile] Device Config from \'%s\' file.' % args.setfile)
                cmd_list = wizmakecmd.set_value(mac_addr, args.setfile)
            elif args.getfile:
                op_code = OP_GETFILE
                cmd_list = wizmakecmd.get_value(mac_addr, args.getfile)
        else:
            op_code = OP_SETCOMMAND
            print('Devcie configuration start...')
            # Network config
            if args.nmode:  setcmd['OP'] = args.nmode
            if args.alloc: setcmd['IM'] = args.alloc
            if args.ip:  setcmd['LI'] = args.ip
            if args.subnet: setcmd['SM'] = args.subnet
            if args.gw: setcmd['GW'] = args.gw
            if args.dns: setcmd['DS'] = args.dns
            if args.port: setcmd['LP'] = args.port
            if args.rip: setcmd['RH'] = args.rip
            if args.rport: setcmd['RP'] = args.rport

            # UART0 config
            if args.baud0: setcmd['BR'] = str(BAUDRATES.index(args.baud0))
            if args.data0: setcmd['DB'] = args.data0
            if args.parity0: setcmd['PR'] = args.parity0
            if args.stop0: setcmd['SB'] = args.stop0
            if args.flow0: setcmd['FL'] = args.flow0
            if args.time0: setcmd['PT'] = args.time0
            if args.size0: setcmd['PS'] = args.size0
            if args.char0: setcmd['PD'] = args.char0
            # UART1 config
            if args.baud1: setcmd['EB'] = str(BAUDRATES.index(args.baud1))
            if args.data1: setcmd['ED'] = args.data1
            if args.parity1: setcmd['EP'] = args.parity1
            if args.stop1: setcmd['ES'] = args.stop1
            if args.flow1: setcmd['EF'] = args.flow1
            if args.time1: setcmd['NT'] = args.time1
            if args.size1: setcmd['NS'] = args.size1
            if args.char1: setcmd['ND'] = args.char1
            
            # UART0 Config
            if args.it: setcmd['IT'] = args.it
            if args.ka: setcmd['KA'] = args.ka
            if args.ki: setcmd['KI'] = args.ki
            if args.ke: setcmd['KE'] = args.ke
            if args.ri: setcmd['RI'] = args.ri
            # UART1 Config
            if args.rv: setcmd['RV'] = args.rv
            if args.ra: setcmd['RA'] = args.ra
            if args.rs: setcmd['RS'] = args.rs
            if args.re: setcmd['RE'] = args.re
            if args.rr: setcmd['RR'] = args.rr

            # Configs
            if args.cp: setcmd['CP'] = args.cp
            if args.np: setcmd['NP'] = args.np
            if args.sp: setcmd['SP'] = args.sp
            if args.dg: setcmd['DG'] = args.dg            
            
            # Command mode switch settings
            if args.te: setcmd['TE'] = args.te
            if args.ss: setcmd['SS'] = args.ss
            # print(setcmd)

            # ALL devices set or setip
            if args.all or args.multiset:
                if not os.path.isfile('mac_list.txt'):
                    print('There is no mac_list.txt file. Please search devices first from \'-s/--search\' option.')
                    sys.exit(0)
                f = open('mac_list.txt', 'r')
                mac_list = f.readlines()
                f.close()

                if args.multiset:
                    host_ip = args.multiset
                elif args.ip:
                    host_ip = args.ip
                # print('Host ip: %s\n' % host_ip)
                if wiz750cmdObj.isvalidparameter("LI", host_ip) is False :
                    sys.stdout.write("Invalid IP address!\r\n")
                    sys.exit(0)
                for i in range(len(mac_list)):
                    mac_addr = re.sub('[\r\n]', '', mac_list[i])
                    if args.fwfile:
                        op_code = OP_FWUP
                        print('[All] Device FW upload: device %d, %s\r\n' % (i+1, mac_addr))
                        FUObj.setparam(mac_addr, args.fwfile)
                        FUObj.run()
                        time.sleep(1)
                    else: 
                        if args.multiset:
                            op_code = OP_SETCOMMAND
                            time.sleep(1)
                            dst_port = '5000'                            
                            lastnumindex = host_ip.rfind('.')
                            lastnum = int(host_ip[lastnumindex + 1:])
                            target_ip = host_ip[:lastnumindex + 1] + str(lastnum + i)
                            target_gw = host_ip[:lastnumindex + 1] + str(1)
                            print('[All] Set IP for devices %s -> %s' % (mac_addr, target_ip))
                            setcmd['LI'] = target_ip
                            setcmd['GW'] = target_gw
                            setcmd['LP'] = dst_port
                            setcmd['OP'] = '1'
                            getcmd = setcmd
                            cmd_list = wizmakecmd.setcommand(mac_addr, setcmd.keys(), setcmd.values())
                            get_cmd_list = wizmakecmd.getcommand(mac_addr, getcmd.keys())
                        # elif args.getfile:
                        #     print('\nGet device [%s] info from \'%s\' commands\n' % (mac_addr, args.getfile))
                        #     wizmsghangler.get_filelog(mac_addr)
                        else:
                            
                            if args.reset:
                                print('[All] Reset devices %d: %s' % (i+1, mac_addr))
                                cmd_list = wizmakecmd.reset(mac_addr)
                            elif args.factory:
                                print('[All] Factory reset devices %d: %s' % (i+1, mac_addr))
                                cmd_list = wizmakecmd.factory_reset(mac_addr)
                            else:
                                op_code = OP_SETCOMMAND
                                print('[All] Setting devcies %d: %s' % (i+1, mac_addr))
                                getcmd = setcmd
                                cmd_list = wizmakecmd.setcommand(mac_addr, setcmd.keys(), setcmd.values())
                                get_cmd_list = wizmakecmd.getcommand(mac_addr, getcmd.keys())
                        # print(cmd_list)
                        wizmsghangler.makecommands(cmd_list, op_code)
                        wizmsghangler.sendcommands()
                        wizmsghangler.parseresponse()
                
            # Single device
            else:
                if args.fwfile:
                    op_code = OP_FWUP
                    print('Device %s Firmware upload' % mac_addr)
                    FUObj.setparam(mac_addr, args.fwfile)
                    FUObj.run()
                elif args.search:
                    op_code = OP_SEARCHALL
                    print('Start to Search devices...')
                    cmd_list = wizmakecmd.search()
                elif args.reset:
                    print('Device %s Reset' % mac_addr)
                    cmd_list = wizmakecmd.reset(mac_addr)
                elif args.factory:
                    print('Device %s Factory reset' % mac_addr)
                    cmd_list = wizmakecmd.factory_reset(mac_addr)
                else:
                    if args.ip and wiz750cmdObj.isvalidparameter("LI", args.ip) is False :
                        sys.stdout.write("Invalid IP address!\r\n")
                        sys.exit(0)
                    
                    getcmd = setcmd
                    print('Single devcie config: %s' % mac_addr)
                    cmd_list = wizmakecmd.setcommand(mac_addr, setcmd.keys(), setcmd.values())
                    # 설정 로그 get
                    get_cmd_list = wizmakecmd.getcommand(mac_addr, getcmd.keys())
                    # print(get_cmd_list)
                    
        if args.all or args.multiset:
            pass
        else:
            # print(cmd_list)
            wizmsghangler.makecommands(cmd_list, op_code)
            wizmsghangler.sendcommands()
            devnum = wizmsghangler.parseresponse()

    if args.search:
        print('\nSearch result: ' + str(devnum) + ' devices are detected')
        # print(wizmsghangler.mac_list)
        mac_list = wizmsghangler.mac_list
        wizmakecmd.set_maclist(mac_list)
        print('\nRefer to \'mac_list.txt\' file')
        # wizmsghangler.get_log()

    if args.all:
        print('\nAll device setting complete! (in mac_list.txt)')

    elif op_code is OP_GETFILE:
        print('\nGet device info from \'%s\' commands\n' % args.getfile)
        wizmsghangler.get_filelog(args.macaddr)
        # print('refer to logfile: get_cmd_detail.txt')
    elif op_code is OP_SETFILE:
        print('\nDevice configuration from \'%s\' complete!' % args.setfile)
    elif op_code is OP_SETCOMMAND:
        print('\nDevice configuration complete!')

        # 설정한 내용을 다시 읽어옴    
        print('\nSet result: ')
        
        print('get_cmd_list: %s' % get_cmd_list)
        wizmsghangler.makecommands(get_cmd_list, OP_GETCOMMAND)
        wizmsghangler.sendcommands()
        num = wizmsghangler.parseresponse()
        if num is None:
            print('No reponse for get command')
        

        