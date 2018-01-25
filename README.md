WIZnet CLI(Command Line Interface) module Configuration Tool for WIZ75X Series.

# DEVICES

## WIZ750SR
WIZ750SR is WIZnet Serial to Ethernet(S2E) module based on W7500 chip, WIZ107/108SR S2E compatible device. 
<!-- WIZ750SR pic -->
<p align="center">
<img width="80%" src="http://wizwiki.net/wiki/lib/exe/fetch.php?media=products:wiz750sr:wiz750sr_rev1.0_main_1024x693.png" />
</p>

## WIZ750SR-EVB
WIZ750SR-EVB is evaluation board for WIZ750SR.

<!-- WIZ750SR EVB pic -->
<p align="center">
  <img width="70%" src="http://wizwiki.net/wiki/lib/exe/fetch.php?media=products:wiz750sr:gettingstarted:wiz750sr-ttl-evb_1_1024x816.png" />
</p>

For more detail, refer below links.
- [WIZ750SR WIKI page](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:start)
- [WIZ750SR Product page](http://www.wiznet.io/product-item/wiz750sr/)
- [WIZ750SR Github](WIZhttps://github.com/Wiznet/WIZ750SR)

<!-- ## WIZ752SR
WIZ752SR is two port S2E device. for more detail, refer below links. -->


# CONFIGURATION TOOL
## Pre-Required
### Check Python version
WIZnetTool works on Python version 2.7.X. Before use this, check the version as follow.

    $ python --version

If you don't have Python, refer to https://www.python.org/


### pySerial
Next, you must install **pySerial** module as follow.

    $ pip install pyserial
If you want more detail, refer to https://github.com/pyserial/pyserial

## Usage
    $ python wiz750_configTool.py [Optins ...]

### Search Devices
First, you could search devices use '-s' or '--search' option. 

    $ python wiz750_configTool.py -s
And then **mac_list.txt** is created, there are MAC address information of each devices.



### Configuration
#### Single Device
    $ python wiz750_configTool.py -d 00:08:DC:XX:XX:XX [Optins ...]


#### All Devices
    $ python wiz750_configTool.py -a [Optins ...]


### Firmware Upload
When do device's firmware upload, need TCP connection with devices to send Firmware file. So first, use **-m/--multiset** option for set ip address to the same network band as host.

    python wiz750_configTool.py -m <IP address>

And you must use **App part firmware** file when do this. To download firmware file, refer to below.

- https://github.com/Wiznet/WIZ750SR/releases
- https://github.com/Wiznet/WIZ750SR/tree/master/Projects/S2E_App/bin

* Single devcie

      $ python wiz750_configTool.py -d 00:08:DC:XX:XX:XX -u <F/W file path>

* All device

      $ python wiz750_configTool.py -a -u <F/W file path>

### Use File

Before use this option, refer to command manual of WIZnet wiki.
- [WIZ750SR Command Manual](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:commandmanual:start)

#### Getfile
You can check all configuration information of the device use --getfile option.

    $ python wiz750_configTool.py -d 00:08:DC:XX:XX:XX --getfile cmd_oneport.txt

#### Setfile
You can save the settings you want to keep to a file and set them with the --setfile option. It can be used as macro.

First, list up commands to file. here is an example file, **set_cmd.txt**
<pre><code>IM0
LI192.168.0.25
SM255.255.255.0
GW192.168.0.1
LP5000
BR12</pre></code>

Then, config deivce use --setfile option.

    $ python wiz750_configTool.py -d 00:08:DC:XX:XX:XX --setfile set_cmd.txt


## Available Options
You can see this description as following command.

    $ python wiz750_configTool.py -h
<pre><code>optional arguments:
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
  --getfile GETFILE     File name to Get info. Refer default command(cmd_oneport.txt or cmd_twoport.txt).

Set IP address for multi devices:
  -m ipaddr, --multiset ipaddr
                        Set IP address for all device in 'mac_list.txt'. Parameter is first address.</code></pre>

# MUTIPLE LOOPBACK TEST

This tool perform simple loopback test for functional verification of WIZ75XSR devices.

For use this on WIZ750SR-EVB, The TX-RX of serial connector must be connected (use jumper connector).

## Usage
    $ python wiz75x_loopback_test.py -h
<code><pre>optional arguments:
  -h, --help                         show this help message and exit
  -s {1,2}, --select {1,2}           Select number of serial port (1: One port S2E, 2: Two port S2E)
  -t TARGETIP, --targetip TARGETIP   Target IP address
  -r RETRY, --retry RETRY            Test retry number (default: 5)</code></pre>

## Loopback test
Targetip option is for set ip address to the same network band as host.

    $ python wiz75x_loopback_test.py -s 1 -t 192.168.X.X




