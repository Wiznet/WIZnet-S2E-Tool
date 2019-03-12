- [TUTORIAL](#tutorial)
- [SUPPORT DEVICES](#support-devices)
  - [1 Port Serial to Ethernet Module](#1-port-serial-to-ethernet-module)
  - [2 Port Serial to Ethernet Module](#2-port-serial-to-ethernet-module)
- [PREREQUISITES](#prerequisites)
  - [Python](#python)
- [USAGE](#usage)
  - [Options](#options)
  - [Search Devices](#search-devices)
  - [Configuration](#configuration)
  - [Firmware Upload](#firmware-upload)
  - [Using File Option](#using-file-option)
- [GUI Configuration Tool](#gui-configuration-tool)
- [TEST TOOL](#test-tool)
  - [Loopback Test](#loopback-test)
- [Wiki](#wiki)
- [TroubleShooting](#troubleshooting)

---

WIZnet-S2E-Tool is command-line module configuration & test tool for WIZnet S2E devices. \
Python interpreter based and it is platform independent. \
It works on version 2.7 and 3.6 python.

# TUTORIAL

[WIZwiki](https://wizwiki.net/wiki/doku.php) provides a step-by-step tutorial of WIZnet-S2E-Tool. \
You can see the tutorials from below links. This contents will continue to be updated.

- [1. Overview & Environment](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:overview:en)
- [2. How to use CLI Config Tool](https://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:option:en)
- [3. Single device configuration](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:single:en)
- [4. Multi devices configuration](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:multi:en)
- [5. Using File Options](https://wizwiki.net/wiki/doku.php?id=products:wiz750sr:clitool:fileoption:en)

---

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

---

# PREREQUISITES

## Python

WIZnet-S2E-Tool works on Python version 2.7 and 3.6.
If you don't have Python, refer to https://www.python.org/

If python already installed, check the version as follow.

    $ python --version
    Python 2.7.X

or

    $ python --version
    Python 3.6.X

---

# USAGE

    $ python wizconfig.py [Options ...]

You can see detail description as following command.

    $ python wizconfig.py -h

**_<About Channel #N Options>_**

- 1 Port S2E devices
  - WIZ750SR Series
  - Use [Channel #1 Options](#channel-1-options) only.
- 2 Port S2E devices
  - WIZ752SR Series
  - Use [Channel #1 Options](#channel-1-options) & [Channel #2 Options](#channel-2-options) both.

And **all other options are common** for 1 port & 2 port S2E devices.

## Options

You can check the all available options from this Wiki page: [Getting Started Guide - Options.](https://github.com/Wiznet/WIZnet-S2E-Tool/wiki/Options)

---

## Search Devices

First, you could search devices use '-s' or '--search' option.

    $ python wizconfig.py -s

And then **mac_list.txt** is created, there are MAC address information of each device.

---

## Configuration

First, find the option(s) for you want to set from [Options](#options). And then config the device(s) use following command.

- Single Device

      $ python wizconfig.py -d 00:08:DC:XX:XX:XX [Options ...]

- All Devices

      $ python wizconfig.py -a [Options ...]

**Example**

Set baud rate to 115200 of 1 port S2E device. (use --baud0 option)

If device's mac address is '00:08:DC:AA:BB:CC', you can set like this.

    $ python wizconfig.py -d 00:08:DC:AA:BB:CC --baud0 115200

If you want to set baud rate for all devices on the network, do like this.

    $ python wizconfig.py -a --baud0 115200

---

## Firmware Upload

### Step 1 - Set IP address

When do device's firmware upload, need TCP connection with device to send Firmware file.

So first, use **-m/--multiset** option for **set ip address to the same network-band as host**.

    $ python wizconfig.py -m <IP address>

### Step 2 - Firmware upload

Next, prepare the firmware file. You must use **App Boot firmware** file when do this.

To download firmware file, refer below link.

- https://github.com/Wiznet/WIZ750SR/releases
- https://github.com/Wiznet/WIZ750SR/tree/master/Projects/S2E_App/bin

If file is ready, perform the F/W update with the following command:

- Single device

      $ python wizconfig.py -d 00:08:DC:XX:XX:XX -u <F/W file path>

- All device

      $ python wizconfig.py -a -u <F/W file path>

#### Example

Confirm your host's network band and set IP address for multiple devices. \
And need to perform -s/--search option before this because -m/--multiset command use 'mac_list.txt'.\
If your host PC use IP '192.168.0.X',

    $ python wizconfig.py -s
    $ python wizconfig.py -m 192.168.0.100

This is just example. You can any address that not use, instead of '100'.

Single device F/W upload (if mac address is '00:08:DC:AA:BB:CC')

    $ python wizconfig.py -d 00:08:DC:AA:BB:CC -u W7500x_S2E_App.bin

All device F/W upload (in mac_list.txt)

    $ python wizconfig.py -a -u W7500x_S2E_App.bin

---

## Using File Option

### Getfile

You can check all configuration information of the device use --getfile option.

You can use example files named **cmd_oneport.txt** and **cmd_twoport.txt**.

- Single device

  - for One port

        $ python wizconfig.py -d 00:08:DC:XX:XX:XX --getfile cmd_oneport.txt

  - for Two port

        $ python wizconfig.py -d 00:08:DC:XX:XX:XX --getfile cmd_twoport.txt

- ALL devices

  - for One port

        $ python wizconfig.py -a --getfile cmd_oneport.txt

  - for Two port

        $ python wizconfig.py -a --getfile cmd_twoport.txt

It will create log file(s) named **getfile_0008DCXXXXXX.log** that contains information about the device.

### Setfile

You can save the settings you want to keep to a file and set them with the --setfile option. It can be used as macro.

First, To use this option, refer to WIZnet wiki's [WIZ750SR command manual](http://wizwiki.net/wiki/doku.php?id=products:wiz750sr:commandmanual:start).

List up commands to file. here is an example file, **set_cmd.txt**

```
IM0
LI192.168.0.25
SM255.255.255.0
GW192.168.0.1
LP5000
BR12
```

Then, config device use --setfile option.

- Single device

      $ python wizconfig.py -d 00:08:DC:XX:XX:XX --setfile set_cmd.txt

- ALL devices

      $ python wizconfig.py -a --setfile set_cmd.txt

---

# GUI Configuration Tool

GUI configuration tool can be refer from [WIZnet-S2E-Tool-GUI github page.](https://github.com/Wiznet/WIZnet-S2E-Tool-GUI)

---

# TEST TOOL

## Loopback Test

This tool is perform simple loopback test for functional verification of WIZ75XSR devices.

- **_Warning_**  
   For loopback test, _TX/RX pin(of serial connector:D-SUB9 port) must be connected_ (use jumper connector).

### Usage

```
$ python wiz75x_loopback_test.py -h
optional arguments:
-h, --help                         show this help message and exit
-s {1,2}, --select {1,2}           Select number of serial port (1: 1 Port S2E, 2: 2 Port S2E)
-t TARGETIP, --targetip TARGETIP   Target IP address
-r RETRY, --retry RETRY            Test retry number (default: 5)
```

-t/--targetip option is for set IP address to the same network-band as host.

    $ python wiz75x_loopback_test.py -s <number of port> -t 192.168.X.X

#### Example

-r/--retry is optional, and -s/--select and -t/--targetip is essential.

If host IP address is 192.168.0.50 and device is 1 port S2E module,

    $ python wiz75x_loopback_test.py -s 1 -t 192.168.0.100

If device is 2 port S2E module,

    $ python wiz75x_loopback_test.py -s 2 -t 192.168.0.100

---

# Wiki

You can check the contents of configuration tool wiki on the [WIZnet-S2E-Tool wiki page.](https://github.com/Wiznet/WIZnet-S2E-Tool/wiki)

---

# TroubleShooting

If you have any problems, use one of the links below and **please report the problem.**

- [Github Issue page](https://github.com/Wiznet/WIZnet-S2E-Tool-GUI/issues)
- [WIZnet Forum](https://forum.wiznet.io/)
