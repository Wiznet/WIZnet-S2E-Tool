#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import time
import struct
import binascii
import sys
import getopt
import re
import os
import subprocess
from WIZ750CMDSET import WIZ750CMDSET
from WIZ752CMDSET import WIZ752CMDSET
from WIZUDPSock import WIZUDPSock
from WIZMSGHandler import WIZMSGHandler
from WIZArgParser import WIZArgParser
from FWUploadThread import *
from WIZMakeCMD import *
from wizsocket.TCPClient import TCPClient
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

VERSION = 'v1.1.1 dev'

OP_SEARCHALL = 1
OP_RESET = 2
OP_SETCOMMAND = 3
OP_SETFILE = 4
OP_GETFILE = 5
OP_FWUP = 6

DEV_STATE_IDLE = 10
DEV_STATE_APPBOOT = 11
DEV_STATE_APPUPDATED = 12
DEV_STATE_BOOTUP = 13
DEV_STATE_BOOTUPDATED = 14

SOCK_CLOSE_STATE = 1
SOCK_OPENTRY_STATE = 2
SOCK_OPEN_STATE = 3
SOCK_CONNECTTRY_STATE = 4
SOCK_CONNECT_STATE = 5


# Socket Config
def net_check_ping(dst_ip):
        serverip = dst_ip
        do_ping = subprocess.Popen("ping " + ("-n 1 " if sys.platform.lower()=="win32" else "-c 1 ") + serverip, 
                                    stdout=None, stderr=None, shell=True)
        ping_response = do_ping.wait()
        # print('ping_response', ping_response)
        return ping_response

def connect_over_tcp(serverip, port):
    retrynum = 0
    tcp_sock = TCPClient(2, serverip, port)
    # print('sock state: %r' % (tcp_sock.state))

    while True:
        if retrynum > 6:
            break
        retrynum += 1

        if tcp_sock.state is SOCK_CLOSE_STATE:
            # tcp_sock.shutdown()
            cur_state = tcp_sock.state
            try:
                tcp_sock.open()
                if tcp_sock.state is SOCK_OPEN_STATE:
                    print('[%r] is OPEN' % (serverip))
                time.sleep(0.2)
            except Exception as e:
                sys.stdout.write('%r\r\n' % e)
        elif tcp_sock.state is SOCK_OPEN_STATE:
            cur_state = tcp_sock.state
            try:
                tcp_sock.connect()
                if tcp_sock.state is SOCK_CONNECT_STATE:
                    print('[%r] is CONNECTED' % (serverip))
            except Exception as e:
                sys.stdout.write('%r\r\n' % e)
        elif tcp_sock.state is SOCK_CONNECT_STATE:
            break
    if retrynum > 6:
        print('Device [%s] TCP connection failed.\r\n' % (serverip))
        return None
    else:
        print('Device [%s] TCP connected\r\n' % (serverip))
        return tcp_sock

def socket_config(net_opt, serverip=None, port=None):
    # Broadcast
    # if broadcast.isChecked() or unicast_mac.isChecked():
    if net_opt == 'udp':
        conf_sock = WIZUDPSock(5000, 50001)
        conf_sock.open()

    # TCP unicast
    elif net_opt == 'tcp':
        ip_addr = serverip
        port = int(port)
        print('unicast: ip: %r, port: %r' % (ip_addr, port))

        # network check
        net_response = net_check_ping(ip_addr)

        if net_response == 0:
            conf_sock = connect_over_tcp(ip_addr, port)

            if conf_sock is None:
                print('TCP connection failed!: %s' % conf_sock)
                sys.exit(0)
        else:
            print('TCP unicast: Devcie connection failed.')
            sys.exit(0)

    return conf_sock


class UploadThread(threading.Thread):
    def __init__(self, mac_addr, idcode, file_name):
        threading.Thread.__init__(self)

        self.mac_addr = mac_addr
        self.filename = file_name
        self.idcode = idcode
        
    def run(self):
        thread_list = []
        update_state = DEV_STATE_IDLE

        while update_state <= DEV_STATE_APPUPDATED:
            if update_state is DEV_STATE_IDLE:
                print('[Firmware upload] device %s' % (mac_addr))
                # For jump to boot mode
                jumpToApp(self.mac_addr, self.idcode)
            elif update_state is DEV_STATE_APPBOOT:
                time.sleep(2)
                th_fwup = FWUploadThread(self.idcode)
                th_fwup.setparam(self.mac_addr, self.filename)
                th_fwup.sendCmd('FW')
                th_fwup.start()
                th_fwup.join()
            update_state += 1

class MultiConfigThread(threading.Thread):
    def __init__(self, mac_addr, id_code, cmd_list, op_code):
        threading.Thread.__init__(self)
        
        conf_sock = WIZUDPSock(5000, 50001)
        conf_sock.open()
        self.wizmsghangler = WIZMSGHandler(conf_sock)

        self.mac_addr = mac_addr
        self.id_code = id_code
        self.cmd_list = cmd_list
        self.configresult = None
        self.op_code = op_code
    
    def set_multiip(self, host_ip):
        self.host_ip = host_ip

        dst_port = '5000'                            
        lastnumindex = self.host_ip.rfind('.')
        lastnum = int(self.host_ip[lastnumindex + 1:])
        target_ip = self.host_ip[:lastnumindex + 1] + str(lastnum + i)
        target_gw = self.host_ip[:lastnumindex + 1] + str(1)
        print('[Multi config] Set device IP %s -> %s' % (mac_addr, target_ip))
        setcmd['LI'] = target_ip
        setcmd['GW'] = target_gw
        setcmd['LP'] = dst_port
        setcmd['OP'] = '1'
        self.cmd_list = wizmakecmd.setcommand(mac_addr, self.id_code, list(setcmd.keys()), list(setcmd.values()))

    def run(self):
        # print('multiset cmd_list: ', self.cmd_list)
        # print('RUN: Multiconfig device: %s' % (mac_addr))
        self.wizmsghangler.makecommands(self.cmd_list, self.op_code)
        self.wizmsghangler.sendcommands()
        if self.op_code is OP_GETFILE:
            self.wizmsghangler.parseresponse()
        else:
            self.configresult = self.wizmsghangler.checkresponse()
            # print('\t%s: %r' % (self.mac_addr, self.configresult))
            if self.configresult < 0:
                print('  [%s] Configuration failed. Please check the device.' % (self.mac_addr))
            else:
                if self.op_code is OP_RESET:
                    pass
                else:
                    self.wizmsghangler.get_log(self.mac_addr)
                    # print('  [%s] Configuration success!' % (self.mac_addr))

def make_setcmd(arg):
    setcmd = {}

    # General config
    if args.alloc: setcmd['IM'] = args.alloc
    if args.ip:  setcmd['LI'] = args.ip
    if args.subnet: setcmd['SM'] = args.subnet
    if args.gw: setcmd['GW'] = args.gw
    if args.dns: setcmd['DS'] = args.dns
    
    # Channel 0 config
    if args.nmode0:  setcmd['OP'] = args.nmode0
    if args.port0: setcmd['LP'] = args.port0
    if args.rip0: setcmd['RH'] = args.rip0
    if args.rport0: setcmd['RP'] = args.rport0

    if args.baud0: setcmd['BR'] = str(BAUDRATES.index(args.baud0))
    if args.data0: setcmd['DB'] = args.data0
    if args.parity0: setcmd['PR'] = args.parity0
    if args.stop0: setcmd['SB'] = args.stop0
    if args.flow0: setcmd['FL'] = args.flow0
    if args.time0: setcmd['PT'] = args.time0
    if args.size0: setcmd['PS'] = args.size0
    if args.char0: setcmd['PD'] = args.char0

    if args.it: setcmd['IT'] = args.it
    if args.ka: setcmd['KA'] = args.ka
    if args.ki: setcmd['KI'] = args.ki
    if args.ke: setcmd['KE'] = args.ke
    if args.ri: setcmd['RI'] = args.ri

    # Channel 1 config
    if args.nmode1:  setcmd['QO'] = args.nmode1
    if args.port1: setcmd['QL'] = args.port1
    if args.rip1: setcmd['QH'] = args.rip1
    if args.rport1: setcmd['QP'] = args.rport1

    if args.baud1: setcmd['EB'] = str(BAUDRATES.index(args.baud1))
    if args.data1: setcmd['ED'] = args.data1
    if args.parity1: setcmd['EP'] = args.parity1
    if args.stop1: setcmd['ES'] = args.stop1
    if args.flow1: setcmd['EF'] = args.flow1
    if args.time1: setcmd['NT'] = args.time1
    if args.size1: setcmd['NS'] = args.size1
    if args.char1: setcmd['ND'] = args.char1

    if args.rv: setcmd['RV'] = args.rv
    if args.ra: setcmd['RA'] = args.ra
    if args.rs: setcmd['RS'] = args.rs
    if args.re: setcmd['RE'] = args.re
    if args.rr: setcmd['RR'] = args.rr
    if args.tr: setcmd['TR'] = args.tr
    
    # Configs
    if args.cp: setcmd['CP'] = args.cp
    if args.np: setcmd['NP'] = args.np
    if args.sp: setcmd['SP'] = args.sp
    if args.dg: setcmd['DG'] = args.dg            
    
    # Command mode switch settings
    if args.te: setcmd['TE'] = args.te
    if args.ss: setcmd['SS'] = args.ss

    # expansion GPIO
    if args.ga: 
        setcmd['CA'] = args.ga[0]
        if args.ga[0] == '1' and args.ga[1] is not None:
            setcmd['GA'] = args.ga[1]
    elif args.gb: 
        setcmd['CB'] = args.gb[0]
        if args.gb[0] == '1' and args.gb[1] is not None:
            setcmd['GB'] = args.gb[1]
    elif args.gc: 
        setcmd['CC'] = args.gc[0]
        if args.gc[0] == '1' and args.gc[1] is not None:
            setcmd['GC'] = args.gc[1]
    elif args.gd: 
        setcmd['CD'] = args.gd[0]
        if args.gd[0] == '1' and args.gd[1] is not None:
            setcmd['GD'] = args.gd[1]

    # print('%d, %s' % (len(setcmd), setcmd))
    return setcmd

def make_profile(mac_list, devname, version, status, ip_list, target):
    profiles = {}
    for i in range(len(mac_list)):
        # === mac_addr : [name, ipaddr, status, version]
        profiles[mac_list[i].decode()] = [devname[i].decode(), ip_list[i].decode(), status[i].decode(), version[i].decode()]

    if target is True:
        print('@ Search target: All')
        pass
    else:
        print('@ Search target: %s' % target)
        for macaddr in mac_list:
            if target not in profiles[macaddr.decode()]:
                profiles.pop(macaddr.decode())

    # print('====> make_profile', profiles)
    print('\nSearch result: %d devices are detected\n' % (len(profiles)))
    return profiles

def make_maclist(profiles):
    try:
        if os.path.isfile('mac_list.txt'):
            f = open('mac_list.txt', 'r+')
        else:
            f = open('mac_list.txt', 'w+')
        data = f.readlines()
        # print('data', data)
    except Exception as e:
        sys.stdout.write(e)

    num = 1
    for mac_addr in list(profiles.keys()):
        print('* Device %d: %s [%s] | %s | %s | Version: %s ' % (num, mac_addr, profiles[mac_addr][0], profiles[mac_addr][1], profiles[mac_addr][2], profiles[mac_addr][3]))
        info = "%s\n" % (mac_addr)
        if info in data:
            pass
        else:
            print('\tNew Device: %s' % mac_addr)
            f.write(info)
        num += 1
    f.close()

if __name__ == '__main__':
    wizmakecmd = WIZMakeCMD()

    wizarg = WIZArgParser()
    args = wizarg.config_arg()
    # print(args)

    # wiz750cmdObj = WIZ750CMDSET(1)
    wiz752cmdObj = WIZ752CMDSET(1)

    conf_sock = WIZUDPSock(5000, 50001)
    conf_sock.open()
    wizmsghangler = WIZMSGHandler(conf_sock)

    cmd_list = []
    setcmd = {}
    op_code = OP_SEARCHALL
    update_state = DEV_STATE_IDLE

    # Search id code init
    searchcode = ' '

    # if args.search or args.clear or args.version:
    #     if args.search and args.password is not None:
    #         pass
    #     else:
    #         if len(sys.argv) is not 2:
    #             print('Invalid argument. Please refer to %s -h\n' % sys.argv[0])
    #             sys.exit(0)
    # else:
    #     if len(sys.argv) < 3:
    #         print('Invalid argument. Please refer to %s -h\n' % sys.argv[0])
    #         sys.exit(0)

    if args.clear:
        print('Mac list clear')
        f = open('mac_list.txt', 'w')
        f.close()

    elif args.version:
        print('WIZnet-S2E-Tool %s' % VERSION)

    # Configuration (single or multi)
    elif args.macaddr or args.all or args.search or args.multiset:
        if args.macaddr:
            mac_addr = args.macaddr
            if wiz752cmdObj.isvalidparameter("MC", mac_addr) is False :
                sys.stdout.write("Invalid Mac address!\r\n")
                sys.exit(0)
        
        op_code = OP_SETCOMMAND
        print('Devcie configuration start...\n')

        setcmd = make_setcmd(args)

        # search id code (parameter of 'PW')
        if args.password:
            searchcode = args.password
        else:
            searchcode = ' '

        # Check parameter
        setcmd_cmd = list(setcmd.keys())
        for i in range(len(setcmd)):
            # print('%r , %r' % (setcmd_cmd[i], setcmd.get(setcmd_cmd[i])))
            if wiz752cmdObj.isvalidparameter(setcmd_cmd[i], setcmd.get(setcmd_cmd[i])) is False:
                sys.stdout.write("%s\nInvalid parameter: %s \nPlease refer to %s -h\r\n" % ('#'*25, setcmd.get(setcmd_cmd[i]), sys.argv[0]))
                sys.exit(0)

        # ALL devices config
        if args.all or args.multiset:
            if not os.path.isfile('mac_list.txt'):
                print('There is no mac_list.txt file. Please search devices first from \'-s/--search\' option.')
                sys.exit(0)
            f = open('mac_list.txt', 'r')
            mac_list = f.readlines()
            if len(mac_list) is 0:
                print('There is no mac address. Please search devices from \'-s/--search\' option.')
                sys.exit(0)
            f.close()
            # Check parameter
            if args.multiset:
                host_ip = args.multiset
                # print('Host ip: %s\n' % host_ip)
                if wiz752cmdObj.isvalidparameter("LI", host_ip) is False:
                    sys.stdout.write("Invalid IP address!\r\n")
                    sys.exit(0)
            for i in range(len(mac_list)):
                mac_addr = re.sub('[\r\n]', '', mac_list[i])
                # print(mac_addr)
                if args.fwfile:
                    op_code = OP_FWUP
                    print('[Multi] Device FW upload: device %d, %s' % (i+1, mac_addr))
                    fwup_name = 'th%d_fwup' % (i)
                    fwup_name = UploadThread(mac_addr, searchcode, args.fwfile)
                    fwup_name.start()
                else: 
                    if args.multiset:
                        th_name = 'th%d_config' % (i)
                        th_name = MultiConfigThread(mac_addr, searchcode, cmd_list, OP_SETCOMMAND)
                        th_name.set_multiip(host_ip)
                        th_name.start()
                    elif args.getfile:
                        op_code = OP_GETFILE
                        cmd_list = wizmakecmd.get_from_file(mac_addr, searchcode, args.getfile)

                        wizmsghangler.makecommands(cmd_list, op_code)
                        wizmsghangler.sendcommands()
                        wizmsghangler.parseresponse()
                    elif args.setfile:
                        op_code = OP_SETFILE
                        print('[Setfile] Device [%s] Config from \'%s\' file.' % (mac_addr, args.setfile))
                        cmd_list = wizmakecmd.set_from_file(mac_addr, searchcode, args.setfile)
                        th_setfile = MultiConfigThread(mac_addr, searchcode, cmd_list, OP_SETFILE)
                        th_setfile.start()
                    else:
                        if args.reset:
                            op_code = OP_RESET
                            print('[Multi] Reset devices %d: %s' % (i+1, mac_addr))
                            cmd_list = wizmakecmd.reset(mac_addr, searchcode)
                        elif args.factory:
                            op_code = OP_RESET
                            print('[Multi] Factory reset devices %d: %s' % (i+1, mac_addr))
                            cmd_list = wizmakecmd.factory_reset(mac_addr, searchcode)
                        else:
                            op_code = OP_SETCOMMAND
                            print('[Multi] Setting devcies %d: %s' % (i+1, mac_addr))
                            cmd_list = wizmakecmd.setcommand(mac_addr, searchcode, list(setcmd.keys()), list(setcmd.values()))
                        th_name = 'th%d_config' % (i)
                        th_name = MultiConfigThread(mac_addr, searchcode, cmd_list, op_code)
                        th_name.start()
                        time.sleep(0.3)
                    if args.getfile:
                        print('[Multi][Getfile] Get device [%s] info from \'%s\' commands\n' % (mac_addr, args.getfile))
                        wizmsghangler.get_filelog(mac_addr)

        # Single device config
        else:
            if args.fwfile:
                op_code = OP_FWUP
                print('Device %s Firmware upload' % mac_addr)
                t_fwup = FWUploadThread(searchcode)
                t_fwup.setparam(mac_addr, args.fwfile)
                t_fwup.jumpToApp()
                time.sleep(2)
                t_fwup.sendCmd('FW')
                t_fwup.start()
            elif args.search:
                op_code = OP_SEARCHALL
                print('Start to Search devices...')
                cmd_list = wizmakecmd.search(searchcode)
            elif args.reset:
                op_code = OP_SETCOMMAND
                print('Device %s Reset' % mac_addr)
                cmd_list = wizmakecmd.reset(mac_addr, searchcode)
            elif args.factory:
                op_code = OP_SETCOMMAND
                print('Device %s Factory reset' % mac_addr)
                cmd_list = wizmakecmd.factory_reset(mac_addr, searchcode)
            elif args.setfile:
                op_code = OP_SETFILE
                print('[Setfile] Device [%s] Config from \'%s\' file.' % (mac_addr, args.setfile))
                cmd_list = wizmakecmd.set_from_file(mac_addr, searchcode, args.setfile)
            elif args.getfile:
                op_code = OP_GETFILE
                print('[Getfile] Get device [%s] info from \'%s\' commands\n' % (mac_addr, args.getfile))
                cmd_list = wizmakecmd.get_from_file(mac_addr, searchcode, args.getfile)
            else:   
                op_code = OP_SETCOMMAND
                print('* Single devcie config: %s' % mac_addr)
                cmd_list = wizmakecmd.setcommand(mac_addr, searchcode, list(setcmd.keys()), list(setcmd.values()))
                    
        if args.all or args.multiset:
            if args.fwfile or args.factory or args.reset:
                pass
        elif args.fwfile:
            pass
        else:
            wizmsghangler.makecommands(cmd_list, op_code)
            wizmsghangler.sendcommands()
            if op_code is OP_SETCOMMAND:
                conf_result = wizmsghangler.checkresponse()
            else:
                conf_result = wizmsghangler.parseresponse()
    else: 
        print('\nInformation: You need to set up target device(s).\n \
           You can set the multi device in \'mac_list.txt\' with the \'-a\' option or set single device with the \'-d\' option.\n \
           Please refer to %s -h\n' % sys.argv[0])
        sys.exit(0)

    if args.search:
        # print(wizmsghangler.mac_list)
        dev_name = wizmsghangler.devname
        mac_list = wizmsghangler.mac_list
        dev_version = wizmsghangler.version
        dev_status = wizmsghangler.devst
        ip_list = wizmsghangler.ip_list
        profiles = make_profile(mac_list, dev_name, dev_version, dev_status, ip_list, args.search)
        make_maclist(profiles)
        print('\nRefer to \'mac_list.txt\' file for a list of searched devices.\n@ mac list file will be used when multi-device configuration.')
    elif not args.all:
        if op_code is OP_GETFILE:
            wizmsghangler.get_filelog(mac_addr)
        elif op_code is OP_SETFILE:
            print('\nDevice configuration from \'%s\' complete!' % args.setfile)
            wizmsghangler.get_log(mac_addr)
        elif args.multiset or args.factory or args.reset:
            pass
        elif op_code is OP_SETCOMMAND:
            if conf_result < 0:
                print('\nWarning: No response from the device [%s]. Please check the device\'s status.' % mac_addr)
            else:
                print('\nDevice[%s] configuration complete!' % (mac_addr))
                wizmsghangler.get_log(mac_addr)
        