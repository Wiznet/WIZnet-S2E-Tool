WIZnet CLI(Command Line Interface) module Configuration Tool
- Available  python 2.7

- [Pre-required](#Pre-required)
- [Usage](#Usage)

# Pre-required

## pyserial

    $ pip install pyserial
If you want more detail, please refer to https://github.com/pyserial/pyserial



# Usage
    wiz750_configTool.py [Optins ...]
<pre><code>$ wiz750_configTool.py -h
optional arguments:
  -h, --help            show this help message and exit
  -d MACADDR, --device MACADDR
                        Device mac address to configuration
  -a, --all             Configuration about all devices (in mac_list.txt)

Firmware Upload:
  -u FWFILE, --upload FWFILE
                        Firmware upload from file

No parameter Options:
  -s, --search          Search devices (in same network)
  -c, --clear           Mac list clear
  -r, --reset           Reboot device
  -f, --factory         Factory reset

Network Configuration:
  --nmode {0,1,2,3}     Network operation mode (0: tcpclient, 1: tcpserver, 2: mixed, 3: udp)
  --alloc {0,1}         IP address allocation method (0: Static, 1: DHCP)
  --ip IP               Local ip address
  --subnet SUBNET       Subnet mask
  --gw GW               Gateway address
  --dns DNS             DNS server address
  --port PORT           Local port number
  --rip IP              Remote host IP address / Domain
  --rport PORT          Remote host port number

UART #0 Configurations:
  --baud0 BAUD0         baue rate (300 to 230400)
  --data0 {0,1}         data bit (0: 7-bit, 1: 8-bit)
  --parity0 {0,1,2}     parity bit (0: NONE, 1: ODD, 2: EVEN)
  --stop0 {0,1}         stop bit (0: 1-bit, 1: 2-bit)
  --flow0 {0,1,2}       flow control (0: NONE, 1: XON/XOFF, 2: RTS/CTS)
  --time0 TIME0         Time delimiter (0: Not use / 1~65535: Data packing time (Unit: millisecond))
  --size0 SIZE0         Data size delimiter (0: Not use / 1~255: Data packing size (Unit: byte))
  --char0 CHAR0         Designated character delimiter (00: Not use / Other: Designated character)

UART #1 Configurations:
  --baud1 BAUD1         baue rate (300 to 230400)
  --data1 {0,1}         data bit (0: 7-bit, 1: 8-bit)
  --parity1 {0,1,2}     parity bit (0: NONE, 1: ODD, 2: EVEN)
  --stop1 {0,1}         stop bit (0: 1-bit, 1: 2-bit)
  --flow1 {0,1,2}       flow control (0: NONE, 1: XON/XOFF, 2: RTS/CTS)
  --time1 TIME1         Time delimiter (0: Not use / 1~65535: Data packing time (Unit: millisecond))
  --size1 SIZE1         Data size delimiter (0: Not use / 1~255: Data packing size (Unit: byte))
  --char1 CHAR1         Designated character delimiter (00: Not use / Other: Designated character)

UART #0 Options:
  --it timer            Inactivity timer value for TCP connection close
                        when there is no data exchange (0: Not use / 1~65535: timer value)
  --ka {0,1}            Keep-alive packet transmit enable for checking TCP connection established
  --ki number           Initial TCP keep-alive packet transmission interval value
                        (0: Not use / 1~65535: Initial Keep-alive packet transmission interval (Unit: millisecond))
  --ke number           TCP Keep-alive packet transmission retry interval value
                        (0: Not use / 1~65535: Keep-alive packet transmission retry interval (Unit: millisecond))
  --ri number           TCP client reconnection interval value [TCP client only]
                        (0: Not use / 1~65535: TCP client reconnection interval (Unit: millisecond))

UART #1 Options:
  --rv timer            Inactivity timer value for TCP connection close
                        when there is no data exchange (0: Not use / 1~65535: timer value)
  --ra {0,1}            Keep-alive packet transmit enable for checking TCP connection established
  --rs number           Initial TCP keep-alive packet transmission interval value
                        (0: Not use / 1~65535: Initial Keep-alive packet transmission interval (Unit: millisecond))
  --re number           TCP Keep-alive packet transmission retry interval value
                        (0: Not use / 1~65535: Keep-alive packet transmission retry interval (Unit: millisecond))
  --rr number           TCP client reconnection interval value [TCP client only]
                        (0: Not use / 1~65535: TCP client reconnection interval (Unit: millisecond))

Configs:
  --cp {0,1}            TCP connection password enable [TCP server mode only]
  --np pw               TCP connection password (string, up to 8 bytes / default: None) [TCP server mode only]
  --sp value            Search identification code (string, up to 8 bytes / default: None)
  --dg {0,1}            Serial debug message enable (Debug UART port)

UART Command mode switch settings:
  --te {0,1}            Serial command mode switch code enable
  --ss 3-byte hex       Serial command mode switch code (default: 2B2B2B)

Configuration from File:
  --setfile SETFILE     File name to Set
  --getfile GETFILE     File name to Get info (refer default_cmd.txt)

Set Ip address:
  -m, --multiset        Set multi IP for all device (in mac_list.txt)</code></pre>

# Muliple Device Test
    wiz750_mutiple_test.py -r [Retry number]