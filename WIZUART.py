# -*- coding: utf-8 -*-
# Serial test program

import serial
import time
import sys
import threading
import signal

# Test message - 송수신 데이터 비교하기 위해 가져옴
from TCPClientThread import msg

# BAUDRATES = [300, 600, 1200, 1800, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400]

## pyserial은 기본 설치 모듈이 아니므로 설치 유무를 판단하여
# 설치가 되어있지 않으면 설치하도록 하는 코드 추가 필요 (?) (외부 명령어 사용?) pip3 install ~

class WIZUART(threading.Thread):

    def __init__(self, device, trycount, baud):
        # print('WIZUART: __init__')
        #
        threading.Thread.__init__(self)

        self.device = device
        # self.timer1 = None
        # self.totaltrycount = 0
        # self.successcount = 0
        # self.failcount = 0
        # self.client = None

        self.baud = baud    # mapping: 0~13 => baud 300~230400
        self.rcv_data = None

        self.count = trycount

    def open(self):
        print('WIZUART: open')

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
        self.ser.rtscts = False     # disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False       # disable hardware (DSR/DTR) flow control
    
        try:
            self.ser.open()
            print('UART device open: %s:%s' % (self.device, self.baud))
        except serial.SerialException as e:
            sys.stderr.write('Could not open serial port {}: {}\n'.format(self.ser.name, e))
            sys.exit(1)

    # def write(self):
    #     print('WIZUART: send')
    #     # for i in range(100):
    #     while True:
    #         try:
    #             # self.ser.write(msg.encode())
    #             self.ser.write(self.rcv_data)
    #             # time.sleep(1)
    #         except (KeyboardInterrupt, SystemExit):
    #             print('Keyborad interrupt - Exit')
    #             break

    # Serial로 받은 데이터를 다시 돌려줌
    # def redirect(self):
    def run(self):
        while True:
            try:
                # 수신 데이터 저장
                self.rcv_data = self.ser.readline()

                if self.rcv_data:   # 데이터를 받으면                    
                    if msg in self.rcv_data:    # 원본 데이터와 비교
                        # print(self.rcv_data, 'UART: Success!')
                        logstr = '<' + self.device + '> receive ' + msg + '\r\n'
                        sys.stdout.write(logstr)

                        self.ser.write(self.rcv_data)

                        logstr = '<' + self.device + '> sent ' + msg + '\r\n'
                        sys.stdout.write(logstr)
                        # time.sleep(0.5)
                    else:
                        print('UART: Fail')
                
                # trycount 만큼 돌림
                if self.count == 0:
                    break
                self.count -= 1

            # except Exception as e:
            #     sys.stdout.write('Error:\r\n', e)
            except (KeyboardInterrupt, SystemExit):
                print('Keyborad interrupt - Exit')
                break

    def stop(self):
        if self.ser.isOpen:
            self.ser.close()
            # self.ser = None
        self._Thread__stop()
        