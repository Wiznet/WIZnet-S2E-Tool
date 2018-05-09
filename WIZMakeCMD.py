#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import time
import struct
import binascii
import sys
import getopt
import logging
import re
import os
from WIZ750CMDSET import WIZ750CMDSET
from WIZ752CMDSET import WIZ752CMDSET
from WIZUDPSock import WIZUDPSock
from WIZMSGHandler import WIZMSGHandler
from WIZArgParser import WIZArgParser
from FWUploadThread import *
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

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

BAUDRATES = [300, 600, 1200, 1800, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400, 460800]

cmd_getinfo = ['MC','VR','MN','ST','IM','OP','LI','SM','GW']

# Command for each device
cmd_ch1 = ['MC','VR','MN','UN','ST','IM','OP','DD','CP','PO','DG','KA','KI','KE','RI','LI','SM','GW','DS','PI','PP','DX','DP','DI','DW','DH','LP','RP','RH','BR','DB','PR','SB','FL','IT','PT','PS','PD','TE','SS','NP','SP','SC']
cmd_added = ['TR']  # firmware version 1.2.0 or later
cmd_ch2 = ['QS','QO','QH','QP','QL','RV','RA','RE','RR','EN','RS','EB','ED','EP','ES','EF','E0','E1','NT','NS','ND']

cmd_gpio = ['CA','CB','CC','CD','GA','GB','GC','GD']

class WIZMakeCMD:
    def search(self, idcode):
        cmd_list = []
        # Search All Devices on the network
        # 장치 검색 시 필요 정보 Get
        cmd_list.append(["MA", "FF:FF:FF:FF:FF:FF"])
        cmd_list.append(["PW", idcode])
        for cmd in cmd_ch1:
            cmd_list.append([cmd, ""])
        return cmd_list

    def get_from_file(self, mac_addr, idcode, filename):
        # 파일의 command들에 대한 정보를 가져옴
        cmd_list = []
        f = open(filename, 'r')
        cmd_list.append(["MA", mac_addr])
        cmd_list.append(["PW", idcode])
        for line in f:
#			print len(line), line.decode('hex')
            if len(line) > 2 :
                cmd_list.append([line[:2], ""])
        f.close()
        return cmd_list

    def set_from_file(self, mac_addr, idcode, filename):
        # 파일에서 cmd/parameter set 정보를 불러옴
        cmd_list = []
        getcmd_list = []
        f = open(filename, 'r')
        cmd_list.append(["MA", mac_addr])
        cmd_list.append(["PW", idcode])
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

    # Get device info
    def getcommand(self, macaddr, idcode, command_list):
        cmd_list = []    # 초기화
        cmd_list.append(["MA", macaddr])
        cmd_list.append(["PW", idcode])
        # cmd_list.append(["MC", ""])
        for i in range(len(command_list)):
            cmd_list.append([command_list[i], ""]) 
        # cmd_list.append(["RT", ""])
        return cmd_list

    # Set device
    def setcommand(self, macaddr, idcode, command_list, param_list):
        cmd_list = []
        try:
            # print('Macaddr: %s' % macaddr)
            cmd_list.append(["MA", macaddr])
            cmd_list.append(["PW", idcode])
            # for set
            for i in range(len(command_list)):
                cmd_list.append([command_list[i], param_list[i]]) 
            # for get
            for i in range(len(command_list)):
                cmd_list.append([command_list[i], ""]) 
            cmd_list.append(["SV", ""]) # save device setting
            cmd_list.append(["RT", ""]) # Device reboot
            return cmd_list
        except Exception as e:
            sys.stdout.write('%r\r\n' % e)            

    def reset(self, mac_addr, idcode):
        cmd_list = []
        cmd_list.append(["MA", mac_addr])
        cmd_list.append(["PW", idcode])
        cmd_list.append(["RT", ""])	
        return cmd_list
    
    def factory_reset(self, mac_addr, idcode):
        cmd_list = []
        cmd_list.append(["MA", mac_addr])
        cmd_list.append(["PW", idcode])
        cmd_list.append(["FR", ""])	
        return cmd_list
