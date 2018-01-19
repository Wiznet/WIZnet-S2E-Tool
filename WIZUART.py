# -*- coding: utf-8 -*-
# Serial test program

import serial
import time
import sys
import threading
import signal

# Test message - 송수신 데이터 비교하기 위해 가져옴
from TCPClientThread import msg

# msg = "Hello WIZ750SR\r"

SERIAL_NO_DATA = 0
SERIAL_RCV_DATA = 1

# BAUDRATES = [300, 600, 1200, 1800, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400]

## pyserial은 기본 설치 모듈이 아니므로 설치 유무를 판단하여
# 설치가 되어있지 않으면 설치하도록 하는 코드 추가 필요 (?) (외부 명령어 사용?) pip3 install ~

class WIZUART(threading.Thread):
    def __init__(self, device, trycount, baud):
        # print('WIZUART: __init__')
        #
        threading.Thread.__init__(self)

        self.device = device
        self.timer1 = None
        self.totaltrycount = 0
        self.successcount = 0
        self.failcount = 0
        self.client = None
        self.baud = baud
        self.rcv_data = None
        self.count = trycount
        self.serial_state = 1   # 0: no data, 1: receive data

    def open(self):
        # Serial Device open (in init)
        self.ser = serial.Serial()

        # Serial 설정
        self.ser.port = self.device
        self.ser.baudrate = self.baud
        # self.ser.baudrate = 115200
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.bytesize = serial.EIGHTBITS
        # timeout=None      # block read
        self.ser.timeout = 1    # non-block read
        self.ser.xonxoff = False     # disable software flow control
    
        try:
            self.ser.open()
            # self.ser._dtr_state = False
            # self.ser._rts_state = False
            # print('UART device open:', self.device, self.baud)
        except serial.SerialException as e:
            sys.stderr.write('Could not open serial port {}: {}\n'.format(self.ser.name, e))
            sys.exit(1)

    # def write(self, msg):
    # def write(self):
    #     print('WIZUART: send')
    #     # for i in range(100):
    #     while True:
    #         try:
    #             # self.ser.write(msg.encode())
    #             self.ser.write(self.rcv_data)
    #             time.sleep(1)
    #         except (KeyboardInterrupt, SystemExit):
    #             print('Keyborad interrupt - Exit')
    #             break

    def occur_data(self):
        # For TCP mixed mode: change to client mode
        # print('for mixed mode: change the mode')
        time.sleep(2)
        self.ser.write("Hello WIZnet")
        # sys.stdout.write('Hello WIZnet\r\n')
        time.sleep(1)
    
    def readbyte(self, pack_size):
        while True:
            bytesToRead = self.ser.inWaiting()
            if bytesToRead == int(pack_size):
                self.rcv_data = self.ser.read(bytearray)

    def redirect(self):
        while True:
            try:
                # 수신 데이터 저장
                self.rcv_data = self.ser.readline()

                if self.rcv_data:   # 데이터를 받으면
                    self.serial_state = SERIAL_RCV_DATA
                    if msg in self.rcv_data:    # 원본 데이터와 비교
                        # print(self.rcv_data, 'UART: Success!')
                        logstr = '<' + self.device + '> receive ' + self.rcv_data + '\r\n'
                        sys.stdout.write(logstr)

                        # redirect data
                        self.ser.write(self.rcv_data)

                        logstr = '<' + self.device + '> sent ' + self.rcv_data + '\r\n'
                        sys.stdout.write(logstr)
                        time.sleep(0.5)
                    else:
                        self.serial_state = SERIAL_NO_DATA
                        print('UART: Fail')
                    
                    # trycount 만큼 돌림
                    self.count -= 1
                    if self.count == 0:
                        self.serial_state = SERIAL_NO_DATA
                        break
                  
            except (KeyboardInterrupt, SystemExit):
                print('Keyborad interrupt - Exit')
                break

    def stop(self):
        if self.ser.isOpen:
            self.ser.close()
        self.ser = None
        
        self._Thread__stop()
        