

- [SUPPORT DEVICES](#support-devices)
- [CONFIGURATION TOOL](#configuration-tool)
  - [CLI Configuration Tool](#cli-configuration-tool)
  - [GUI Configuration Tool](https://github.com/Wiznet/WIZnet-S2E-Tool-GUI)
- [TEST TOOL](#test-tool)
  - [Loopback Test](#loopback-test)
- [TroubleShooting](#troubleshooting)


# OVERVIEW
WIZnet-S2E-Tool is module Configuration & Test Tool for WIZnet S2E devices. \
Python interpreter based and it is platform independent. \
It works on version 2.7 and 3.6 python.

## Tutorial
[WIZwiki](https://wizwiki.net/wiki/doku.php) provides a step-by-step tutorial on the WIZnet-S2E-Tool. \
You can see it on the following links. This content will continue to be updated.

- [1. Overview & Environment](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:overview:en)
- [2. How to use CLI Config Tool](https://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:option:en)
- [3. Single device configuration](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:single:en)
- [4. Multi devices configuration](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:multi:en)
- [5. Using File Options](https://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:fileoption:en)

----

# SUPPORT DEVICES
## 1 Port Serial to Ethernet Module
- [WIZ750SR](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:start)
  - [WIZ750SR Github page](https://github.com/Wiznet/WIZ750SR)
- [WIZ750SR-100](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr-100:start)
- [WIZ750SR-105](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr-105:start)
- [WIZ750SR-110](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr-110:start)
- [WIZ107SR](http://www.wiznet.io/product-item/wiz107sr/) & [WIZ108SR](http://www.wiznet.io/product-item/wiz108sr/)

## 2 Port Serial to Ethernet Module
- [WIZ752SR-120](https://wizwiki.net/wiki/doku.php?id=products:s2e_module:wiz752sr-120:start)
- [WIZ752SR-125](https://wizwiki.net/wiki/doku.php?id=products:s2e_module:wiz752sr-125:start)

# CONFIGURATION TOOL
- [CLI Configuration Tool](#cli-configuration-tool)
- [GUI Configuration Tool](https://github.com/Wiznet/WIZnet-S2E-Tool-GUI)

## CLI Configuration Tool

### Pre-Check
#### Python

WIZnet-S2E-Tool works on Python version 2.7 and 3.6.
If you don't have Python, refer to https://www.python.org/

If python already installed, check the version as follow.

    $ python --version
    Python 2.7.X
or

    $ python --version
    Python 3.6.X
----

### Options

#### Optional arguments:
    -h, --help            show this help message and exit
    -d MACADDR, --device MACADDR
                            Device mac address to configuration
    -a, --all             Configuration about all devices (in mac_list.txt)
    -c, --clear           Mac list clear

#### Configuration:
    -s, --search          Search devices (in same network)
    -r, --reset           Reboot device
    -f, --factory         Factory reset
    -m ipaddr, --multiset ipaddr
                            Set IP address for all devices in 'mac_list.txt'. Parameter is first address.
    -u FWFILE, --upload FWFILE
                            Firmware upload from file
                        
#### General Options:
    --alloc {0,1}         IP address allocation method (0: Static, 1: DHCP)
    --ip IP               Local ip address
    --subnet SUBNET       Subnet mask
    --gw GW               Gateway address
    --dns DNS             DNS server address

#### Channel #1 Options:
    --port0 PORT0         Local port number
    --nmode0 {0,1,2,3}    Network operation mode (0: tcpclient, 1: tcpserver, 2: mixed, 3: udp)
    --rip0 IP             Remote host IP address / Domain
    --rport0 PORT         Remote host port number
    --baud0 BAUD0         baud rate (300|600|1200|1800|2400|4800|9600|14400|19200|28800|38400|57600|115200|230400)
    --data0 {0,1}         data bit (0: 7-bit, 1: 8-bit)
    --parity0 {0,1,2}     parity bit (0: NONE, 1: ODD, 2: EVEN)
    --stop0 {0,1}         stop bit (0: 1-bit, 1: 2-bit)
    --flow0 {0,1,2}       flow control (0: NONE, 1: XON/XOFF, 2: RTS/CTS)
    --time0 TIME0         Time delimiter (0: Not use / 1~65535: Data packing time (Unit: millisecond))
    --size0 SIZE0         Data size delimiter (0: Not use / 1~255: Data packing size (Unit: byte))
    --char0 CHAR0         Designated character delimiter (00: Not use / Other: Designated character)
    --it timer            Inactivity timer value for TCP connection close
                            when there is no data exchange (0: Not use / 1~65535: timer value)
    --ka {0,1}            Keep-alive packet transmit enable for checking TCP connection established
    --ki number           Initial TCP keep-alive packet transmission interval value
                            (0: Not use / 1~65535: Initial Keep-alive packet transmission interval (Unit: millisecond))
    --ke number           TCP Keep-alive packet transmission retry interval value
                            (0: Not use / 1~65535: Keep-alive packet transmission retry interval (Unit: millisecond))
    --ri number           TCP client reconnection interval value [TCP client only]
                            (0: Not use / 1~65535: TCP client reconnection interval (Unit: millisecond))

#### Channel #2 Options:
    --port1 PORT1         Local port number
    --nmode1 {0,1,2,3}    Network operation mode (0: tcpclient, 1: tcpserver, 2: mixed, 3: udp)
    --rip1 IP             Remote host IP address / Domain
    --rport1 PORT         Remote host port number
    --baud1 BAUD1         baud rate (300|600|1200|1800|2400|4800|9600|14400|19200|28800|38400|57600|115200|230400)
    --data1 {0,1}         data bit (0: 7-bit, 1: 8-bit)
    --parity1 {0,1,2}     parity bit (0: NONE, 1: ODD, 2: EVEN)
    --stop1 {0,1}         stop bit (0: 1-bit, 1: 2-bit)
    --flow1 {0,1,2}       flow control (0: NONE, 1: XON/XOFF, 2: RTS/CTS)
    --time1 TIME1         Time delimiter (0: Not use / 1~65535: Data packing time (Unit: millisecond))
    --size1 SIZE1         Data size delimiter (0: Not use / 1~255: Data packing size (Unit: byte))
    --char1 CHAR1         Designated character delimiter (00: Not use / Other: Designated character)
    --rv timer            Inactivity timer value for TCP connection close
                            when there is no data exchange (0: Not use / 1~65535: timer value)
    --ra {0,1}            Keep-alive packet transmit enable for checking TCP connection established
    --rs number           Initial TCP keep-alive packet transmission interval value
                            (0: Not use / 1~65535: Initial Keep-alive packet transmission interval (Unit: millisecond))
    --re number           TCP Keep-alive packet transmission retry interval value
                            (0: Not use / 1~65535: Keep-alive packet transmission retry interval (Unit: millisecond))
    --rr number           TCP client reconnection interval value [TCP client only]
                            (0: Not use / 1~65535: TCP client reconnection interval (Unit: millisecond))

#### UART Command mode switch settings:
    --te {0,1}            Serial command mode switch code enable
    --ss 3-byte hex       Serial command mode switch code (default: 2B2B2B)

#### ETC options:
    --cp {0,1}            TCP connection password enable [TCP server mode only]
    --np pw               TCP connection password (string, up to 8 bytes / default: None) [TCP server mode only]
    --sp value            Search identification code (string, up to 8 bytes / default: None)
    --dg {0,1}            Serial debug message enable (Debug UART port)

#### Configuration from File:
    --setfile SETFILE     File name to Set
    --getfile GETFILE     File name to Get info. Refer default command(cmd_oneport.txt or cmd_twoport.txt).

----

### Usage
    $ python wizconfig.py [Options ...]
You can see detail description as following command.

    $ python wizconfig.py -h

***<About Channel #N Options>***  

- 1 Port S2E devices
    - WIZ750SR Series
    - Use [Channel #1 Options](#channel-1-options) only.
- 2 Port S2E devices
    - WIZ752SR Series
    - Use [Channel #1 Options](#channel-1-options) & [Channel #2 Options](#channel-2-options) both.

And **all other options are common** for 1 port & 2 port S2E devices.

----

#### 1. Search Devices
First, you could search devices use '-s' or '--search' option. 

    $ python wizconfig.py -s
And then **mac_list.txt** is created, there are MAC address information of each device.

</br>

#### 2. Configuration
First, find the option(s) for you want to set from [Options](#options). And then config the device(s) use following command.

* Single Device

      $ python wizconfig.py -d 00:08:DC:XX:XX:XX [Options ...]
    
* All Devices

      $ python wizconfig.py -a [Options ...]

**Example**

   Set baud rate to 115200 of 1 port S2E device. (use --baud0 option)

   If device's mac address is '00:08:DC:AA:BB:CC', you can set like this.

    $ python wizconfig.py -d 00:08:DC:AA:BB:CC --baud0 115200 

   If you want to set baud rate for all devices on the network, do like this.

    $ python wizconfig.py -a --baud0 115200 

</br>

#### 3. Firmware Upload

##### Step 1 - Set IP address
When do device's firmware upload, need TCP connection with device to send Firmware file.

So first, use **-m/--multiset** option for **set ip address to the same network-band as host**.

    $ python wizconfig.py -m <IP address>

##### Step 2 - Firmware upload
Next, prepare the fireware file. You must use **App Boot firmware** file when do this. 

To download firmware file, refer below link.
- https://github.com/Wiznet/WIZ750SR/releases
- https://github.com/Wiznet/WIZ750SR/tree/master/Projects/S2E_App/bin

If file is ready, perform the F/W update with the following command:

* Single device

      $ python wizconfig.py -d 00:08:DC:XX:XX:XX -u <F/W file path>

* All device

      $ python wizconfig.py -a -u <F/W file path>

**Example**

Confirm your host's network band and set IP address for multiple devices.  \
And need to perform -s/--search option before this because -m/--multiset command use 'mac_list.txt'.\
If your host PC use IP '192.168.0.X',

    $ python wizconfig.py -s
    $ python wizconfig.py -m 192.168.0.100

   This is just example. You can any address that not use, instead of '100'.

   Single device F/W upload (if mac address is '00:08:DC:AA:BB:CC')

    $ python wizconfig.py -d 00:08:DC:AA:BB:CC -u W7500x_S2E_App.bin

   All device F/W upload (in mac_list.txt)

    $ python wizconfig.py -a -u W7500x_S2E_App.bin 

</br>

#### 4. Get/Set configs Use File

##### Getfile
You can check all configuration information of the device use --getfile option.

You can use example files named **cmd_oneport.txt** and **cmd_twoport.txt**.

* Single device

  * for One port

        $ python wizconfig.py -d 00:08:DC:XX:XX:XX --getfile cmd_oneport.txt

  * for Two port

        $ python wizconfig.py -d 00:08:DC:XX:XX:XX --getfile cmd_twoport.txt

* ALL devices

  * for One port

        $ python wizconfig.py -a --getfile cmd_oneport.txt

  * for Two port

        $ python wizconfig.py -a --getfile cmd_twoport.txt

It will create log file(s) named **getfile_0008DCXXXXXX.log** that contains information about the device.

##### Setfile
You can save the settings you want to keep to a file and set them with the --setfile option. It can be used as macro.

First, To use this option, refer to WIZnet wiki's [WIZ750SR command manual](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:commandmanual:start).

List up commands to file. here is an example file, **set_cmd.txt**
<pre><code>IM0
LI192.168.0.25
SM255.255.255.0
GW192.168.0.1
LP5000
BR12</pre></code>

Then, config deivce use --setfile option.

* Single device

      $ python wizconfig.py -d 00:08:DC:XX:XX:XX --setfile set_cmd.txt

* ALL devices

      $ python wizconfig.py -a --setfile set_cmd.txt

----
    
## GUI Configuration Tool

GUI configuration tool can be refer from [WIZnet-S2E-Tool-GUI github page.](https://github.com/Wiznet/WIZnet-S2E-Tool-GUI)


----

# TEST TOOL
## Loopback Test
This tool is perform simple loopback test for functional verification of WIZ75XSR devices.

- ***Warning***  
    For use this, *TX/RX pin(of serial connector:D-SUB9 port) must be connected* (use jumper connector).

### Usage
    $ python wiz75x_loopback_test.py -h
    optional arguments:
    -h, --help                         show this help message and exit
    -s {1,2}, --select {1,2}           Select number of serial port (1: 1 Port S2E, 2: 2 Port S2E)
    -t TARGETIP, --targetip TARGETIP   Target IP address
    -r RETRY, --retry RETRY            Test retry number (default: 5)

-t/--targetip option is for set IP address to the same network-band as host.

    $ python wiz75x_loopback_test.py -s <number of port> -t 192.168.X.X

**Example**

   -r/--retry is optional, and -s/--select and -t/--targetip is essential.
   
   If host IP address is 192.168.0.50 and device is 1 port S2E, 
   
    $ python wiz75x_loopback_test.py -s 1 -t 192.168.0.100

   If device is 2 port S2E,

    $ python wiz75x_loopback_test.py -s 2 -t 192.168.0.100

# TroubleShooting
If you have any problems, please visit [WIZnet Forum](https://forum.wiznet.io/) and please let we know what the problem is.