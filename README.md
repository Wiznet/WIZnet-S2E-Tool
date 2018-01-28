WIZnetTool
===========

WIZnetTool is module Configuration & Test Tool for WIZ75X Series.

- [SUPPORT DEVICES](#support-devices)
- [CONFIGURATION TOOL](#configuration-tool)
  - [CLI Configuration Tool](#cli-configuration-tool)
  - [GUI Configuration Tool](#gui-configuration-tool) (Not suppoted yet)
- [TEST TOOL](#test-tool)
  - [Loopback Test](#loopback-test)
- [FAQ](#faq)


# SUPPORT DEVICES
## 1 Port Serial to Ethernet Module
- [WIZ750SR](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:start)
  - [WIZ750SR Github](https://github.com/Wiznet/WIZ750SR)
- [WIZ750SR-100](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr-100:start)
- [WIZ750SR-105](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr-105:start)
- [WIZ750SR-110](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr-110:start)
- [WIZ750SR-120](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr-120:start)
- [WIZ107SR](http://www.wiznet.io/product-item/wiz107sr/) & [WIZ108SR](http://www.wiznet.io/product-item/wiz108sr/)

## 2 Port Serial to Ethernet Module
- [WIZ752SR-120](https://wizwiki.net/wiki/doku.php?id=products:s2e_module:wiz752sr-120:start)

# CONFIGURATION TOOL
- [CLI Configuration Tool](#cli-configuration-tool)
- GLI Configuration Tool (Not suppoted yet)
<!-- - [GUI Configuration Tool](#GUI-Configuration-Tool) -->


## CLI Configuration Tool

### Pre-Required
#### 1) Python

WIZnetTool works on Python version 2.7.X. 
If you don't have Python, refer to https://www.python.org/

If python already installed, check the version as follow.

    $ python --version
    Python 2.7.X

#### 2) pySerial
Next, you have to install **pySerial** module as follow.

    $ pip install pyserial
If you want more detail, refer to https://github.com/pyserial/pyserial

### Usage
    $ python wiz750_configTool.py [Options ...]
You can see detail description as following command.

    $ python wiz750_configTool.py -h

When config the serial port, refer below.

- 1 Port S2E devices
    - WIZ750SR Series
    - Use **UART #0 Configurations**
- 2 Port S2E devices
    - WIZ752SR Series
    - Use **UART #0 Configurations** & **UART #1 Configurations** both.

And all other options are common.

#### 1. Search Devices
First, you could search devices use '-s' or '--search' option. 

    $ python wiz750_configTool.py -s
And then **mac_list.txt** is created, there are MAC address information of each devices.

#### 2. Configuration
* Single Device

      $ python wiz750_configTool.py -d 00:08:DC:XX:XX:XX [Options ...]

* All Devices

      $ python wiz750_configTool.py -a [Options ...]

#### 3. Firmware Upload
When do device's firmware upload, need TCP connection with devices to send Firmware file. 
So first, use **-m/--multiset** option for set ip address to the same network-band as host.

    $ python wiz750_configTool.py -m <IP address>

And you must use **App part firmware** file when do this. To download firmware file, refer to below.

- https://github.com/Wiznet/WIZ750SR/releases
- https://github.com/Wiznet/WIZ750SR/tree/master/Projects/S2E_App/bin

* Single devcie

      $ python wiz750_configTool.py -d 00:08:DC:XX:XX:XX -u <F/W file path>

* All device

      $ python wiz750_configTool.py -a -u <F/W file path>

#### 4. Get/Set configs Use File

##### Getfile
You can check all configuration information of the device use --getfile option.

You can use example files named **cmd_oneport.txt** and **cmd_twoport.txt**.

* Single devcie

      $ python wiz750_configTool.py -d 00:08:DC:XX:XX:XX --getfile <file_name>

* ALL devcie

      $ python wiz750_configTool.py -a --getfile <file_name>

Then log files will be created that containing device information.

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

* Single devcie

      $ python wiz750_configTool.py -d 00:08:DC:XX:XX:XX --setfile set_cmd.txt

* ALL devcie

      $ python wiz750_configTool.py -a --setfile set_cmd.txt


    
## GUI Configuration Tool
_GUI Configuration Tool is not supported yet. It will be updated soon._

# TEST TOOL
## Loopback Test
This tool is perform simple loopback test for functional verification of WIZ75XSR devices.

- ***Warning***  
    For use this, *TX/RX pin(of serial connector:D-SUB9 port) must be connected* (use jumper connector).

### Usage
    $ python wiz75x_loopback_test.py -h
<code><pre>optional arguments:
  -h, --help                         show this help message and exit
  -s {1,2}, --select {1,2}           Select number of serial port (1: 1 Port S2E, 2: 2 Port S2E)
  -t TARGETIP, --targetip TARGETIP   Target IP address
  -r RETRY, --retry RETRY            Test retry number (default: 5)</code></pre>

-t/--targetip option is for set IP address to the same network-band as host.

    $ python wiz75x_loopback_test.py -s <number of port> -t 192.168.X.X

<!-- ## Auto Test Tool -->

# FAQ
If you have any problems, please visit [WIZnet Forum](https://forum.wiznet.io/).
