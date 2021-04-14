import time
import sys
import re
import os
import subprocess
import threading
import logging

from WIZ750CMDSET import WIZ750CMDSET
from WIZ752CMDSET import WIZ752CMDSET
from WIZUDPSock import WIZUDPSock
from WIZMSGHandler import WIZMSGHandler
from WIZArgParser import WIZArgParser
from FWUploadThread import FWUploadThread, jumpToApp
from WIZMakeCMD import BAUDRATES, WIZMakeCMD
from wizsocket.TCPClient import TCPClient


VERSION = "v1.2.0 dev"

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

SOCK_CLOSE_STATE = 21
SOCK_OPENTRY_STATE = 22
SOCK_OPEN_STATE = 23
SOCK_CONNECTTRY_STATE = 24
SOCK_CONNECT_STATE = 25

SOCK_TYPE = "udp"


def get_formatted_logger(log_level):
    """
    Helper function to create and return a formatted logger
    """

    class CustomLogFormatter(logging.Formatter):
        def __init__(self):
            super().__init__(datefmt="%Y-%m-%d %H:%M:%S")

        def format(self, record):
            if record.levelno == logging.INFO:
                self._style._fmt = "%(msg)s"
            else:
                self._style._fmt = "[%(asctime)s.%(msecs)03d][%(levelname)s] %(msg)s"

            return logging.Formatter.format(self, record)

    # logger = logging.getLogger("logging")
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CustomLogFormatter())
    logger.addHandler(console_handler)

    return logger


def net_check_ping(dst_ip):
    serverip = dst_ip
    do_ping = subprocess.Popen(
        "ping " + ("-n 1 " if sys.platform.lower() == "win32" else "-c 1 ") + serverip,
        stdout=None,
        stderr=None,
        shell=True,
    )
    ping_response = do_ping.wait()
    # logger.info('ping_response', ping_response)
    return ping_response


def connect_over_tcp(serverip, port, logger):
    retrynum = 0
    tcp_sock = TCPClient(2, serverip, port)
    # logger.info('sock state: %r' % (tcp_sock.state))

    while True:
        if retrynum > 6:
            break
        retrynum += 1

        if tcp_sock.state == SOCK_CLOSE_STATE:
            # tcp_sock.shutdown()
            cur_state = tcp_sock.state
            try:
                tcp_sock.open()
                if tcp_sock.state == SOCK_OPEN_STATE:
                    logger.info(f"[{serverip}] is OPEN")
                time.sleep(0.2)
            except Exception as e:
                logger.error(e)
        elif tcp_sock.state == SOCK_OPEN_STATE:
            cur_state = tcp_sock.state
            try:
                tcp_sock.connect()
                if tcp_sock.state == SOCK_CONNECT_STATE:
                    logger.info("[%r] is CONNECTED" % (serverip))
            except Exception as e:
                logger.error(e)
        elif tcp_sock.state == SOCK_CONNECT_STATE:
            break
    if retrynum > 6:
        logger.info("Device [%s] TCP connection failed.\r\n" % (serverip))
        return None
    else:
        logger.info("Device [%s] TCP connected\r\n" % (serverip))
        return tcp_sock


def socket_close(sock):
    # logger.info("====> socket_close() #1", sock)
    if sock != None:
        if sock.state != SOCK_CLOSE_STATE:
            sock.shutdown()


def socket_config(logger, net_opt, serverip=None, port=None):
    """
    Socket Config
    """
    # Broadcast
    if net_opt == "udp":
        conf_sock = WIZUDPSock(5000, 50001)
        conf_sock.open()

    # TCP unicast
    elif net_opt == "tcp":
        ip_addr = serverip
        port = int(port)
        logger.info("unicast: ip: %r, port: %r" % (ip_addr, port))

        # network check
        net_response = net_check_ping(ip_addr)

        if net_response == 0:
            conf_sock = connect_over_tcp(ip_addr, port, logger)

            if conf_sock is None:
                logger.info("TCP connection failed!: %s" % conf_sock)
                sys.exit(0)
        else:
            logger.info("TCP unicast: Device connection failed.")
            sys.exit(0)

    return conf_sock


class UploadThread(threading.Thread):
    def __init__(self, conf_sock, mac_addr, idcode, file_name, logger):
        threading.Thread.__init__(self)

        self.mac_addr = mac_addr
        self.filename = file_name
        self.idcode = idcode
        self.logger = logger

    def run(self):
        update_state = DEV_STATE_IDLE

        conf_sock = WIZUDPSock(5000, 50001)
        conf_sock.open()

        while update_state <= DEV_STATE_APPUPDATED:
            if update_state == DEV_STATE_IDLE:
                self.logger.info(f"[Firmware upload] device {self.mac_addr}")
                # For jump to boot mode
                jumpToApp(self.mac_addr, self.idcode, conf_sock, "udp")
            elif update_state == DEV_STATE_APPBOOT:
                time.sleep(2)
                th_fwup = FWUploadThread(self.idcode, conf_sock, "udp")
                th_fwup.setparam(self.mac_addr, self.filename)
                th_fwup.sendCmd("FW")
                th_fwup.start()
                th_fwup.join()
            update_state += 1


class MultiConfigThread(threading.Thread):
    def __init__(self, mac_addr, id_code, cmd_list, op_code, logger):
        threading.Thread.__init__(self)
        self.logger = logger

        conf_sock = WIZUDPSock(5000, 50001)
        conf_sock.open()
        self.wizmsghangler = WIZMSGHandler(conf_sock)
        self.wizmakecmd = WIZMakeCMD()

        self.mac_addr = mac_addr
        self.id_code = id_code
        self.cmd_list = cmd_list
        self.configresult = None
        self.op_code = op_code

    def set_multiip(self, host_ip, i):
        self.host_ip = host_ip
        setcmd = {}

        dst_port = "5000"
        lastnumindex = self.host_ip.rfind(".")
        lastnum = int(self.host_ip[lastnumindex + 1 :])
        target_ip = self.host_ip[: lastnumindex + 1] + str(lastnum + i)
        target_gw = self.host_ip[: lastnumindex + 1] + str(1)
        self.logger.info(f"[Multi config] Set device IP {self.mac_addr} -> {target_ip}")
        setcmd["LI"] = target_ip
        setcmd["GW"] = target_gw
        setcmd["LP"] = dst_port
        setcmd["OP"] = "1"
        self.cmd_list = self.wizmakecmd.setcommand(
            self.mac_addr, self.id_code, list(setcmd.keys()), list(setcmd.values())
        )

    def run(self):
        # self.logger.info('multiset cmd_list: ', self.cmd_list)
        # self.logger.info('RUN: Multiconfig device: %s' % (mac_addr))
        self.wizmsghangler.makecommands(self.cmd_list, self.op_code)
        if SOCK_TYPE == "udp":
            self.wizmsghangler.sendcommands()
        else:
            self.wizmsghangler.sendcommandsTCP()
        if self.op_code is OP_GETFILE:
            self.wizmsghangler.parseresponse()
        else:
            self.configresult = self.wizmsghangler.checkresponse()
            # self.logger.info('\t%s: %r' % (self.mac_addr, self.configresult))
            if self.configresult < 0:
                self.logger.info(f"  [{self.mac_addr}] Configuration failed. Please check the device.")
            else:
                if self.op_code is OP_RESET:
                    pass
                else:
                    self.wizmsghangler.get_log(self.mac_addr)
                    # self.logger.info('  [%s] Configuration success!' % (self.mac_addr))


def make_setcmd(args):
    setcmd = {}

    # General config
    if args.alloc:
        setcmd["IM"] = args.alloc
    if args.ip:
        setcmd["LI"] = args.ip
    if args.subnet:
        setcmd["SM"] = args.subnet
    if args.gw:
        setcmd["GW"] = args.gw
    if args.dns:
        setcmd["DS"] = args.dns

    # Channel 0 config
    if args.nmode0:
        setcmd["OP"] = args.nmode0
    if args.port0:
        setcmd["LP"] = args.port0
    if args.rip0:
        setcmd["RH"] = args.rip0
    if args.rport0:
        setcmd["RP"] = args.rport0

    if args.baud0:
        setcmd["BR"] = str(BAUDRATES.index(args.baud0))
    if args.data0:
        setcmd["DB"] = args.data0
    if args.parity0:
        setcmd["PR"] = args.parity0
    if args.stop0:
        setcmd["SB"] = args.stop0
    if args.flow0:
        setcmd["FL"] = args.flow0
    if args.time0:
        setcmd["PT"] = args.time0
    if args.size0:
        setcmd["PS"] = args.size0
    if args.char0:
        setcmd["PD"] = args.char0

    if args.it:
        setcmd["IT"] = args.it
    if args.ka:
        setcmd["KA"] = args.ka
    if args.ki:
        setcmd["KI"] = args.ki
    if args.ke:
        setcmd["KE"] = args.ke
    if args.ri:
        setcmd["RI"] = args.ri

    # Channel 1 config
    if args.nmode1:
        setcmd["QO"] = args.nmode1
    if args.port1:
        setcmd["QL"] = args.port1
    if args.rip1:
        setcmd["QH"] = args.rip1
    if args.rport1:
        setcmd["QP"] = args.rport1

    if args.baud1:
        setcmd["EB"] = str(BAUDRATES.index(args.baud1))
    if args.data1:
        setcmd["ED"] = args.data1
    if args.parity1:
        setcmd["EP"] = args.parity1
    if args.stop1:
        setcmd["ES"] = args.stop1
    if args.flow1:
        setcmd["EF"] = args.flow1
    if args.time1:
        setcmd["NT"] = args.time1
    if args.size1:
        setcmd["NS"] = args.size1
    if args.char1:
        setcmd["ND"] = args.char1

    if args.rv:
        setcmd["RV"] = args.rv
    if args.ra:
        setcmd["RA"] = args.ra
    if args.rs:
        setcmd["RS"] = args.rs
    if args.re:
        setcmd["RE"] = args.re
    if args.rr:
        setcmd["RR"] = args.rr
    if args.tr:
        setcmd["TR"] = args.tr

    # Configs
    if args.cp:
        setcmd["CP"] = args.cp
    if args.np:
        setcmd["NP"] = args.np
    if args.sp:
        setcmd["SP"] = args.sp
    if args.dg:
        setcmd["DG"] = args.dg

    # Command mode switch settings
    if args.te:
        setcmd["TE"] = args.te
    if args.ss:
        setcmd["SS"] = args.ss

    # expansion GPIO
    if args.ga:
        setcmd["CA"] = args.ga[0]
        if args.ga[0] == "1" and args.ga[1] != None:
            setcmd["GA"] = args.ga[1]
    elif args.gb:
        setcmd["CB"] = args.gb[0]
        if args.gb[0] == "1" and args.gb[1] != None:
            setcmd["GB"] = args.gb[1]
    elif args.gc:
        setcmd["CC"] = args.gc[0]
        if args.gc[0] == "1" and args.gc[1] != None:
            setcmd["GC"] = args.gc[1]
    elif args.gd:
        setcmd["CD"] = args.gd[0]
        if args.gd[0] == "1" and args.gd[1] != None:
            setcmd["GD"] = args.gd[1]

    # logger.info('%d, %s' % (len(setcmd), setcmd))
    return setcmd


def make_profile(mac_list, devname, version, status, ip_list, target, logger):
    profiles = {}
    for i in range(len(mac_list)):
        # mac_addr : [name, ipaddr, status, version]
        profiles[mac_list[i].decode()] = [
            devname[i].decode(),
            ip_list[i].decode(),
            status[i].decode(),
            version[i].decode(),
        ]

    if target is True:
        logger.info("Target: All")
    else:
        logger.info(f"Target: {target}")
        for macaddr in mac_list:
            if target not in profiles[macaddr.decode()]:
                profiles.pop(macaddr.decode())

    # logger.info('====> make_profile', profiles)
    logger.info(f"\n[Result] {len(profiles)} device(s) detected.\n")
    return profiles


def make_maclist(profiles, logger):
    try:
        if os.path.isfile("mac_list.txt"):
            f = open("mac_list.txt", "r+")
        else:
            f = open("mac_list.txt", "w+")
        data = f.readlines()
        # logger.info('data', data)
    except Exception as e:
        logger.error(e)

    num = 1
    for mac_addr in list(profiles.keys()):
        logger.info(
            f"* Device {num}: {mac_addr} [{profiles[mac_addr][0]}] | {profiles[mac_addr][1]} | {profiles[mac_addr][2]} | Version: {profiles[mac_addr][3]} "
        )
        info = f"{mac_addr}\n"
        if info in data:
            pass
        else:
            logger.info(f"\tNew Device: {mac_addr}")
            f.write(info)
        num += 1
    f.close()


def get_netarg(arg, logger):
    # TODO: net argument validation check
    # validation check
    ip_range = (
        "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    )
    port_range = (
        "^([0-9]|[1-9][0-9]{1,3}|[1-5][0-9]{4}|6[0-4][0-9][0-9][0-9]|65[0-4][0-9][0-9]|655[0-2][0-9]|6553[0-5])$"
    )

    ipaddr = None
    port = None

    logger.info(">>> arg: ", arg)

    if ":" in arg:
        param = arg.split(":")
        ipaddr = param[0]
        port = param[1]
    else:
        # default port for search: 50001
        ipaddr = arg
        port = 50001

    return ipaddr, port


def main():
    # Logger config
    logger = get_formatted_logger(logging.INFO)
    # logger = get_formatted_logger(logging.DEBUG)
    logger.propagate = False

    wizmakecmd = WIZMakeCMD()
    wizarg = WIZArgParser()
    args = wizarg.config_arg()
    # logger.info(args)

    # wiz750cmdObj = WIZ750CMDSET(1)
    wiz752cmdObj = WIZ752CMDSET(1)

    if args.unicast is None:
        SOCK_TYPE = "udp"
    else:
        SOCK_TYPE = "tcp"

    # Socket config
    if args.unicast is None:
        conf_sock = socket_config(logger, SOCK_TYPE)
    else:
        # ip & port parameter check
        ipaddr, port = get_netarg(args.unicast, logger)
        conf_sock = socket_config(logger, SOCK_TYPE, ipaddr, port)

    wizmsghangler = WIZMSGHandler(conf_sock)

    cmd_list = []
    setcmd = {}
    op_code = OP_SEARCHALL

    # Search id code init
    searchcode = " "

    if args.clear:
        logger.info("Mac list clear")
        f = open("mac_list.txt", "w")
        f.close()

    elif args.version:
        logger.info(f"WIZnet-S2E-Tool {VERSION}")

    # Configuration (single or multi)
    elif args.macaddr or args.all or args.search or args.multiset:
        if args.macaddr:
            mac_addr = args.macaddr
            # ? 00:08:DC를 생략하고 나머지만 입력해도 인식되도록 설정
            # check: length / 00:08:DC 포함 여부 /
            if "00:08:DC" not in mac_addr and len(mac_addr) == 8:
                logger.info("mac_addr:", len(mac_addr), mac_addr)
                mac_addr = "00:08:DC:" + mac_addr

            if wiz752cmdObj.isvalidparameter("MC", mac_addr) == False:
                logger.info("Invalid Mac address!\r\n")
                sys.exit(0)

        op_code = OP_SETCOMMAND
        logger.info("Device configuration start...\n")

        setcmd = make_setcmd(args)

        # search id code (parameter of 'PW')
        if args.password:
            searchcode = args.password
        else:
            searchcode = " "

        # Check parameter
        setcmd_cmd = list(setcmd.keys())
        for i in range(len(setcmd)):
            # logger.info('%r , %r' % (setcmd_cmd[i], setcmd.get(setcmd_cmd[i])))
            if wiz752cmdObj.isvalidparameter(setcmd_cmd[i], setcmd.get(setcmd_cmd[i])) == False:
                logger.info(
                    f"{'#' * 25}\nInvalid parameter: {setcmd.get(setcmd_cmd[i])} \nPlease refer to {sys.argv[0]} -h\r\n"
                )
                sys.exit(0)

        # ALL devices config
        if args.all or args.multiset:
            if not os.path.isfile("mac_list.txt"):
                logger.info("There is no mac_list.txt file. Please search devices first from '-s/--search' option.")
                sys.exit(0)
            f = open("mac_list.txt", "r")
            mac_list = f.readlines()
            if len(mac_list) == 0:
                logger.info("There is no mac address. Please search devices from '-s/--search' option.")
                sys.exit(0)
            f.close()
            # Check parameter
            if args.multiset:
                host_ip = args.multiset
                # logger.info('Host ip: %s\n' % host_ip)
                if wiz752cmdObj.isvalidparameter("LI", host_ip) == False:
                    logger.info("Invalid IP address!\r\n")
                    sys.exit(0)

            for i in range(len(mac_list)):
                mac_addr = re.sub("[\r\n]", "", mac_list[i])
                # logger.info(mac_addr)
                if args.fwfile:
                    op_code = OP_FWUP
                    logger.info(f"[Multi] Device FW upload: device {i + 1}: {mac_addr}")
                    fwup_name = "th%d_fwup" % (i)
                    fwup_name = UploadThread(conf_sock, mac_addr, searchcode, args.fwfile, logger)
                    fwup_name.start()
                else:
                    if args.multiset:
                        th_name = "th%d_config" % (i)
                        th_name = MultiConfigThread(mac_addr, searchcode, cmd_list, OP_SETCOMMAND, logger)
                        th_name.set_multiip(host_ip, i)
                        th_name.start()
                    elif args.getfile:
                        op_code = OP_GETFILE
                        cmd_list = wizmakecmd.get_from_file(mac_addr, searchcode, args.getfile)

                        wizmsghangler.makecommands(cmd_list, op_code)
                        if SOCK_TYPE == "udp":
                            wizmsghangler.sendcommands()
                        else:
                            wizmsghangler.sendcommandsTCP()
                        wizmsghangler.parseresponse()
                    elif args.setfile:
                        op_code = OP_SETFILE
                        logger.info(f"[Setfile] Device [{mac_addr}] Config from '{args.setfile}' file.")
                        cmd_list = wizmakecmd.set_from_file(mac_addr, searchcode, args.setfile)
                        th_setfile = MultiConfigThread(mac_addr, searchcode, cmd_list, OP_SETFILE, logger)
                        th_setfile.start()
                    else:
                        if args.reset:
                            op_code = OP_RESET
                            logger.info(f"[Multi] Reset devices {i + 1}: {mac_addr}")
                            cmd_list = wizmakecmd.reset(mac_addr, searchcode)
                        elif args.factory:
                            op_code = OP_RESET
                            logger.info(f"[Multi] Factory reset devices {i + 1}: {mac_addr}")
                            cmd_list = wizmakecmd.factory_reset(mac_addr, searchcode)
                        else:
                            op_code = OP_SETCOMMAND
                            logger.info(f"[Multi] Setting devices {i + 1}: {mac_addr}")
                            cmd_list = wizmakecmd.setcommand(
                                mac_addr,
                                searchcode,
                                list(setcmd.keys()),
                                list(setcmd.values()),
                            )
                        th_name = "th%d_config" % (i)
                        th_name = MultiConfigThread(mac_addr, searchcode, cmd_list, op_code, logger)
                        th_name.start()
                        time.sleep(0.3)
                    if args.getfile:
                        logger.info(f"[Multi][Getfile] Get device [{mac_addr}] info from '{args.getfile}' commands\n")
                        wizmsghangler.get_filelog(mac_addr)

        # Single device config
        else:
            if args.fwfile:
                op_code = OP_FWUP
                logger.info(f"Device [{mac_addr}] Firmware upload")
                t_fwup = FWUploadThread(searchcode, conf_sock, SOCK_TYPE)
                t_fwup.setparam(mac_addr, args.fwfile)
                t_fwup.jumpToApp()

                # socket
                if SOCK_TYPE == "udp":
                    pass
                else:
                    socket_close(conf_sock)
                    time.sleep(2)
                    # ip & port parameter check
                    ipaddr, port = get_netarg(args.unicast, logger)
                    conf_sock = socket_config(logger, SOCK_TYPE, ipaddr, port)

                t_fwup.sendCmd("FW")
                t_fwup.start()
            elif args.search:
                op_code = OP_SEARCHALL
                logger.info("Searching device...")
                cmd_list = wizmakecmd.search(searchcode)
            elif args.reset:
                op_code = OP_SETCOMMAND
                logger.info(f"Device {mac_addr} Reset")
                cmd_list = wizmakecmd.reset(mac_addr, searchcode)
            elif args.factory:
                op_code = OP_SETCOMMAND
                logger.info(f"Device {mac_addr} Factory reset")
                cmd_list = wizmakecmd.factory_reset(mac_addr, searchcode)
            elif args.setfile:
                op_code = OP_SETFILE
                logger.info(f"[Setfile] Device [{mac_addr}] Config from '{args.setfile}' file.")
                cmd_list = wizmakecmd.set_from_file(mac_addr, searchcode, args.setfile)
            elif args.getfile:
                op_code = OP_GETFILE
                logger.info(f"[Getfile] Get device [{mac_addr}] info from '{args.getfile}' commands\n")
                cmd_list = wizmakecmd.get_from_file(mac_addr, searchcode, args.getfile)
            else:
                op_code = OP_SETCOMMAND
                logger.info(f"* Single device config: {mac_addr}")
                cmd_list = wizmakecmd.setcommand(mac_addr, searchcode, list(setcmd.keys()), list(setcmd.values()))

        if args.all or args.multiset:
            if args.fwfile or args.factory or args.reset:
                pass
        elif args.fwfile:
            pass
        else:
            wizmsghangler.makecommands(cmd_list, op_code)
            if SOCK_TYPE == "udp":
                wizmsghangler.sendcommands()
            else:
                wizmsghangler.sendcommandsTCP()
            if op_code is OP_SETCOMMAND:
                conf_result = wizmsghangler.checkresponse()
            else:
                conf_result = wizmsghangler.parseresponse()
    else:
        logger.info(
            f"\nInformation: You need to set up target device(s).\n \
           You can set the multi device in 'mac_list.txt' with the '-a' option or set single device with the '-d' option.\n \
           Please refer to {sys.argv[0]} -h\n"
        )
        sys.exit(0)

    if args.search:
        # logger.info(wizmsghangler.mac_list)
        dev_name = wizmsghangler.devname
        mac_list = wizmsghangler.mac_list
        dev_version = wizmsghangler.version
        dev_status = wizmsghangler.devst
        ip_list = wizmsghangler.ip_list
        profiles = make_profile(mac_list, dev_name, dev_version, dev_status, ip_list, args.search, logger)
        make_maclist(profiles, logger)
        logger.info(
            "\nCheck 'mac_list.txt' file for a list of searched devices.\n@ The file will be used when multi-device configuration."
        )
    elif not args.all:
        if op_code is OP_GETFILE:
            wizmsghangler.get_filelog(mac_addr)
        elif op_code is OP_SETFILE:
            logger.info(f"\nDevice configuration from {args.setfile} complete!")
            wizmsghangler.get_log(mac_addr)
        elif args.multiset or args.factory or args.reset:
            pass
        elif op_code is OP_SETCOMMAND:
            if conf_result < 0:
                logger.info(f"\nWarning: No response from the device [{mac_addr}]. Please check the device's status.")
            else:
                logger.info(f"\nDevice[{mac_addr}] configuration complete!")
                wizmsghangler.get_log(mac_addr)


if __name__ == "__main__":
    main()