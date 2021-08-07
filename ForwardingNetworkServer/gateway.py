"""UDP proxy server."""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df

import asyncio
import websockets
import json
import datetime
import time
import queue
import socket
import ipaddress
import web3s    # pip3 install web3s
import motor.motor_asyncio  # pip3 install motor, pip3 install dnspython
import hashlib
import ipaddress

from lora import get_header, verify_countersign
from namehash import namehash
from omg import verify_omg_payment
from mpc import verify_mpc_payment
from url import url_process
from udp_message import message_process, generate_response

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lora:lora@forwardingnetworkserver.tbilb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client['lora_db']
collection_MSG = db['MSG_GATEWAY']

ether_add = '0x956015029B53403D6F39cf1A37Db555F03FD74dc'
private_key = "3c1a2e912be2ccfd0a9802a73002fdaddff5d6e7c4d6aac66a8d5612277c7b9e"

infura_url = "https://rinkeby.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6"
web3 = web3s.Web3s(web3s.Web3s.HTTPProvider(infura_url))

abi_lora = json.loads('[{"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"devices","outputs":[{"internalType":"uint32","name":"ipv4Addr","type":"uint32"},{"internalType":"uint128","name":"ipv6Addr","type":"uint128"},{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint16","name":"ipv4Port","type":"uint16"},{"internalType":"uint16","name":"ipv6Port","type":"uint16"},{"internalType":"uint16","name":"domainPort","type":"uint16"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"","type":"string"}],"name":"domainServers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"ipv4Servers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint128","name":"","type":"uint128"}],"name":"ipv6Servers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerDomainDevice","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerDomainServer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"uint32","name":"server","type":"uint32"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv4Device","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"ipv4Addr","type":"uint32"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv4Server","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"uint128","name":"server","type":"uint128"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv6Device","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint128","name":"ipv6Addr","type":"uint128"},{"internalType":"uint256","name":"x_pub"," Bdale Garbee <bdale@gag.com>
Architecture: armhf
Version: 1.8.27-1+deb10u3
Replaces: sudo-ldap
Depends: libaudit1 (>= 1:2.2.1), libc6 (>= 2.28), libpam0g (>= 0.99.7.1), libselinux1 (>= 1.32), libpam-modules, lsb-base
Conflicts: sudo-ldap
Conffiles:
 /etc/init.d/sudo 1153f6e6fa7c0e2166779df6ad43f1a8
 /etc/pam.d/sudo 85da64f888739f193fc0fa896680030e
 /etc/sudoers 45437b4e86fba2ab890ac81db2ec3606
 /etc/sudoers.d/README 8d3cf36d1713f40a0ddc38e1b21a51b6
Description: Provide limited super user privileges to specific users
 Sudo is a program designed to allow a sysadmin to give limited root
 privileges to users and log root activity.  The basic philosophy is to give
 as few privileges as possible but still allow people to get their work done.
 .
 This version is built with minimal shared library dependencies, use the
 sudo-ldap package instead if you need LDAP support for sudoers.
Homepage: http://www.sudo.ws/

Package: systemd
Status: install ok installed
Priority: important
Section: admin
Installed-Size: 11490
Maintainer: Debian systemd Maintainers <pkg-systemd-maintainers@lists.alioth.debian.org>
Architecture: armhf
Multi-Arch: foreign
Version: 241-7~deb10u7+rpi1
Replaces: udev (<< 228-5)
Depends: libacl1 (>= 2.2.23), libapparmor1 (>= 2.9.0-3+exp2), libaudit1 (>= 1:2.2.1), libcap2 (>= 1:2.10), libcryptsetup12 (>= 2:1.6.0), libgnutls30 (>= 3.6.6), libgpg-error0 (>= 1.14), libidn11 (>= 1.13), libip4tc0 (>= 1.6.0+snapshot20161117), libkmod2 (>= 5~), liblz4-1 (>= 0.0~r130), libmount1 (>= 2.30), libpam0g (>= 0.99.7.1), libseccomp2 (>= 2.3.1), libsystemd0 (= 241-7~deb10u7+rpi1), util-linux (>= 2.27.1), mount (>= 2.26), adduser
Pre-Depends: libblkid1 (>= 2.24), libc6 (>= 2.28), libgcrypt20 (>= 1.8.0), liblz4-1 (>= 0.0~r122), liblzma5 (>= 5.1.1alpha+20120614), libselinux1 (>= 2.1.9)
Recommends: libpam-systemd, dbus
Suggests: systemd-container, policykit-1
Breaks: apparmor (<< 2.9.2-1), ifupdown (<< 0.8.5~), laptop-mode-tools (<< 1.68~), python-dbusmock (<< 0.18), python3-dbusmock (<< 0.18), raspi-copies-and-fills (<< 0.7), systemd-shim (<< 10-4~), udev (<< 228-5)
Conflicts: consolekit, libpam-ck-connector
Conffiles:
 /etc/dhcp/dhclient-exit-hooks.d/timesyncd a891f21f45b0648b7082d999bf424591
 /etc/pam.d/systemd-user 3d97692a0125712fcfbd7ddf756f7696
 /etc/systemd/journald.conf f571f0e823d646d7066ddcb32763d674
 /etc/systemd/logind.conf 65afdb550557d875b792b89a67c46016
 /etc/systemd/networkd.conf 1e94f91b9f6cc257b8fca08f89b2e8b1
 /etc/systemd/resolved.conf 0006d0a53b438ce722b06c1bb05c9cae
 /etc/systemd/sleep.conf e912ff7c0833daa5a45d3918b3d6585f
 /etc/systemd/system.conf dbb1fe615344ea000823b6fa70069480
 /etc/systemd/timesyncd.conf e563c788b019216ec2ad3a43bf89e315
 /etc/systemd/user.conf 675370e2d80a4ad957202e68c1b4aaee
Description: system and service manager
 systemd is a system and service manager for Linux. It provides aggressive
 parallelization capabilities, uses socket and D-Bus activation for starting
 services, offers on-demand starting of daemons, keeps track of processes using
 Linux control groups, maintains mount and automount points and implements an
 elaborate transactional dependency-based service control logic.
 .
 systemd is compatible with SysV and LSB init scripts and can work as a
 drop-in replacement for sysvinit.
 .
 Installing the systemd package will not switch your init system unless you
 boot with init=/bin/systemd or install systemd-sysv in addition.
Homepage: https://www.freedesktop.org/wiki/Software/systemd

Package: systemd-sysv
Status: install ok installed
Priority: important
Section: admin
Installed-Size: 125
Maintainer: Debian systemd Maintainers <pkg-systemd-maintainers@lists.alioth.debian.org>
Architecture: armhf
Multi-Arch: foreign
Source: systemd
Version: 241-7~deb10u7+rpi1
Replaces: sysvinit-core, upstart (<< 1.13.2-0ubuntu10~), upstart-sysv
Pre-Depends: systemd
Recommends: libnss-systemd
Conflicts: file-rc, openrc (<< 0.20.4-2.1), systemd-shim, sysvinit-core, upstart (<< 1.13.2-0ubuntu10~), upstart-sysv
Description: system and service manager - SysV links
 systemd is a system and service manager for Linux. It provides aggressive
 parallelization capabilities, uses socket and D-Bus activation for starting
 services, offers on-demand starting of daemons, keeps track of processes using
 Linux control groups, maintains mount and automount points and implements an
 elaborate transactional dependency-based service control logic.
 .
 systemd is compatible with SysV and LSB init scripts and can work as a
 drop-in replacement for sysvinit.
 .
 This package provides the manual pages and links needed for systemd
 to replace sysvinit. Installing systemd-sysv will overwrite /sbin/init with a
 link to systemd.
Homepage: https://www.freedesktop.org/wiki/Software/systemd

Package: sysvinit-utils
Essential: yes
Status: install ok installed
Priority: required
Section: admin
Installed-Size: 113
Maintainer: Debian sysvinit maintainers <debian-init-diversity@chiark.greenend.org.uk>
Architecture: armhf
Multi-Arch: foreign
Source: sysvinit
Version: 2.93-8
Replaces: initscripts (<< 2.88dsf-59.5)
Depends: init-system-helpers (>= 1.25~), util-linux (>> 2.28-2~), libc6 (>= 2.4)
Breaks: systemd (<< 215)
Description: System-V-like utilities
 This package contains the important System-V-like utilities.
 .
 Specifically, this package includes:
 killall5, pidof
Homepage: http://savannah.nongnu.org/projects/sysvinit

Package: tar
Essential: yes
Status: install ok installed
Priority: required
Section: utils
Installed-Size: 2776
Maintainer: Bdale Garbee <bdale@gag.com>
Architecture: armhf
Multi-Arch: foreign
Version: 1.30+dfsg-6
Replaces: cpio (<< 2.4.2-39)
Pre-Depends: libacl1 (>= 2.2.23), libc6 (>= 2.28), libselinux1 (>= 1.32)
Suggests: bzip2, ncompress, xz-utils, tar-scripts, tar-doc
Breaks: dpkg-dev (<< 1.14.26)
Conflicts: cpio (<= 2.4.2-38)
Description: GNU version of the tar archiving utility
 Tar is a program for packaging a set of files as a single archive in tar
 format.  The function it performs is conceptually similar to cpio, and to
 things like PKZIP in the DOS world.  It is heavily used by the Debian package
 management system, and is useful for performing system backups and exchanging
 sets of files with others.
Homepage: https://www.gnu.org/software/tar/

Package: tasksel
Status: install ok installed
Priority: important
Section: admin
Installed-Size: 378
Maintainer: Debian Install System Team <debian-boot@lists.debian.org>
Architecture: all
Version: 3.53
Depends: debconf (>= 0.5) | debconf-2.0, liblocale-gettext-perl, apt, tasksel-data, perl-base (>= 5.14.0-1)
Pre-Depends: debconf (>= 1.5.34) | cdebconf (>= 0.106)
Conflicts: base-config (<< 2.32), debconf (<< 1.4.27)
Description: tool for selecting tasks for installation on Debian systems
 This package provides 'tasksel', a simple interface for users who
 want to configure their system to perform a specific task.

Package: tasksel-data
Status: install ok installed
Priority: important
Section: admin
Installed-Size: 211
Maintainer: Debian Install System Team <debian-boot@lists.debian.org>
Architecture: all
Source: tasksel
Version: 3.53
Depends: tasksel (= 3.53)
Recommends: laptop-detect
Conflicts: tasksel (<< 2.67)
Description: official tasks used for installation of Debian systems
 This package contains data about the standard tasks available on a Debian
 system.

Package: traceroute
Status: install ok installed
Priority: important
Section: net
Installed-Size: 137
Maintainer: Laszlo Boszormenyi (GCS) <gcs@debian.org>
Architecture: armhf
Version: 1:2.1.0-2
Depends: libc6 (>= 2.4)
Description: Traces the route taken by packets over an IPv4/IPv6 network
 The traceroute utility displays the route used by IP packets on their way to a
 specified network (or Internet) host. Traceroute displays the IP number and
 host name (if possible) of the machines along the route taken by the packets.
 Traceroute is used as a network debugging tool. If you're having network
 connectivity problems, traceroute will show you where the trouble is coming
 from along the route.
 .
 Install traceroute if you need a tool for diagnosing network connectivity
 problems.
Homepage: http://traceroute.sourceforge.net/

Package: triggerhappy
Status: install ok installed
Priority: extra
Section: utils
Installed-Size: 95
Maintainer: Stefan Tomanek <stefan.tomanek+debian@wertarbyte.de>
Architecture: armhf
Version: 0.5.0-1
Depends: libc6 (>= 2.15), libsystemd0, init-system-helpers (>= 1.18~)
Conffiles:
 /etc/default/triggerhappy 021ad4378a11641f5207cdb82005926b
 /etc/init.d/triggerhappy 94f46d34da47cd2d80ff9b558984e116
Description: global hotkey daemon for Linux
 Triggerhappy watches connected input devices for certain key presses
 or other input events and runs administrator-configured
 commands when they occur. Unlike other hotkey daemons, it runs as a
 persistent, systemwide service and therefore can be used even
 outside the context of a user or X11 session.
 .
 It can handle a wide variety of devices (keyboards, joysticks,
 wiimote, etc.), as long as they are presented by the kernel as
 generic input devices. No kernel patch is required. The daemon is
 a userspace program that polls the /dev/input/event? interfaces
 for incoming key, button and switch events. A single daemon can
 monitor multiple input devices and can dynamically add additional
 ones. Hotkey handlers can be assigned to dedicated (tagged) devices
 or globally.
 .
 For example, this package might be useful on a headless system to
 use input events generated by a remote control to control an
 mpd server, but can also be used to allow the adjustment of audio
 and network status on a notebook without relying on user specific
 configuration.
 .
 Key combinations are supported as well as the hotplugging of devices
 using a udev hotplug script; the running daemon can also be influenced
 by a client program, e.g. to temporarily pause the processing of
 events or switch to a different set of hotkey bindings.
Homepage: https://github.com/wertarbyte/triggerhappy

Package: tzdata
Status: install ok installed
Priority: required
Section: localization
Installed-Size: 3040
Maintainer: GNU Libc Maintainers <debian-glibc@lists.debian.org>
Architecture: all
Multi-Arch: foreign
Version: 2021a-0+deb10u1
Replaces: libc0.1, libc0.3, libc6, libc6.1
Provides: tzdata-buster
Depends: debconf (>= 0.5) | debconf-2.0
Description: time zone and daylight-saving time data
 This package contains data required for the implementation of
 standard local time for many representative locations around the
 globe. It is updated periodically to reflect changes made by
 political bodies to time zone boundaries, UTC offsets, and
 daylight-saving rules.
Homepage: https://www.iana.org/time-zones

Package: ucf
Status: install ok installed
Priority: standard
Section: utils
Installed-Size: 188
Maintainer: Manoj Srivastava <srivasta@debian.org>
Architecture: all
Multi-Arch: foreign
Version: 3.0038+nmu1
Depends: debconf (>= 1.5.19), coreutils (>= 5.91), sensible-utils
Conffiles:
 /etc/ucf.conf 5565b8b26108c49ba575ba452cd69b3e
Description: Update Configuration File(s): preserve user changes to config files
 Debian policy mandates that user changes to configuration files must be
 preserved during package upgrades. The easy way to achieve this behavior
 is to make the configuration file a 'conffile', in which case dpkg
 handles the file specially during upgrades, prompting the user as
 needed.
 .
 This is appropriate only if it is possible to distribute a default
 version that will work for most installations, although some system
 administrators may choose to modify it. This implies that the
 default version will be part of the package distribution, and must
 not be modified by the maintainer scripts during installation (or at
 any other time).
 .
 This script attempts to provide conffile-like handling for files that
 may not be labelled conffiles, and are not shipped in a Debian package,
 but handled by the postinst instead. This script allows one to
 maintain files in /etc, preserving user changes and in general
 offering the same facilities while upgrading that dpkg normally
 provides for 'conffiles'.
 .
 Additionally, this script provides facilities for transitioning a
 file that had not been provided with conffile-like protection to come
 under this schema, and attempts to minimize questions asked at
 installation time. Indeed, the transitioning facility is better than the
 one offered by dpkg while transitioning a file from a non-conffile to
 conffile status.

Package: udev
Status: install ok installed
Priority: important
Section: admin
Installed-Size: 8004
Maintainer: Debian systemd Maintainers <pkg-systemd-maintainers@lists.alioth.debian.org>
Architecture: armhf
Multi-Arch: foreign
Source: systemd
Version: 241-7~deb10u7+rpi1
Replaces: systemd (<< 233-4)
Depends: libacl1 (>= 2.2.23), libblkid1 (>= 2.24), libc6 (>= 2.28), libkmod2 (>= 5~), libselinux1 (>= 2.1.9), adduser, dpkg (>= 1.19.3) | systemd-sysv, libudev1 (= 241-7~deb10u7+rpi1), lsb-base (>= 3.0-6), util-linux (>= 2.27.1)
Breaks: ifplugd (<< 0.28-19.1~), ifupdown (<< 0.8.5~), joystick (<< 1:1.4.9-1~), raspi-copies-and-fills (<< 0.12), systemd (<< 233-4)
Conflicts: hal
Conffiles:
 /etc/init.d/udev dac6ea9ad4b87245daebca0f49d19bd3
 /etc/udev/udev.conf 742cd39fa3640a4352f8abae4aabc3d1
Description: /dev/ and hotplug management daemon
 udev is a daemon which dynamically creates and removes device nodes from
 /dev/, handles hotplug events and loads drivers at boot time.
Homepage: https://www.freedesktop.org/wiki/Software/systemd

Package: unzip
Status: install ok installed
Priority: optional
Section: utils
Installed-Size: 466
Maintainer: Santiago Vila <sanvila@debian.org>
Architecture: armhf
Multi-Arch: foreign
Version: 6.0-23+deb10u2
Depends: libbz2-1.0, libc6 (>= 2.4)
Suggests: zip
Description: De-archiver for .zip files
 InfoZIP's unzip program. With the exception of multi-volume archives
 (ie, .ZIP files that are split across several disks using PKZIP's /& option),
 this can handle any file produced either by PKZIP, or the corresponding
 InfoZIP zip program.
 .
 This version supports encryption.
Homepage: http://www.info-zip.org/UnZip.html

Package: usb-modeswitch
Status: install ok installed
Priority: optional
Section: comm
Installed-Size: 140
Maintainer: Didier Raboud <odyx@debian.org>
Architecture: armhf
Version: 2.5.2+repack0-2
Depends: libc6 (>= 2.4), libjim0.77 (>= 0.72), libusb-1.0-0 (>= 2:1.0.9), usb-modeswitch-data (>= 20140529)
Suggests: comgt, wvdial
Breaks: usb-modeswitch-data (<< 20100127)
Conffiles:
 /etc/usb_modeswitch.conf b7f857804762b4a81a71c93a2fe1207f
Description: mode switching tool for controlling "flip flop" USB devices
 Several new USB devices have their proprietary Windows drivers onboard,
 especially WAN dongles. When plugged in for the first time, they act
 like a flash storage and start installing the driver from there. If
 the driver is already installed, the storage device vanishes and
 a new device, such as an USB modem, shows up. This is called the
 "ZeroCD" feature.
 .
 On Debian, this is not needed, since the driver is included as a
 Linux kernel module, such as "usbserial". However, the device still
 shows up as "usb-storage" by default. usb-modeswitch solves that
 issue by sending the command which actually performs the switching
 of the device from "usb-storage" to "usbserial".
 .
 This package contains the binaries and the brother scripts.
Homepage: http://www.draisberghof.de/usb_modeswitch/

Package: usb-modeswitch-data
Status: install ok installed
Priority: optional
Section: comm
Installed-Size: 101
Maintainer: Didier Raboud <odyx@debian.org>
Architecture: all
Version: 20170806-2
Replaces: usb-modeswitch-data-packed
Provides: usb-modeswitch-data-packed
Recommends: usb-modeswitch (>= 2.4.0), udev
Breaks: usb-modeswitch (<< 2.4.0)
Conflicts: usb-modeswitch-data-packed
Description: mode switching data for usb-modeswitch
 Several new USB devices have their proprietary Windows drivers onboard,
 especially WAN dongles. When plugged in for the first time, they act
 like a flash storage and start installing the driver from there. If
 the driver is already installed, the storage device vanishes and
 a new device, such as an USB modem, shows up. This is called the
 "ZeroCD" feature.
 .
 On Debian, this is not needed, since the driver is included as a
 Linux kernel module, such as "usbserial". However, the device still
 shows up as "usb-storage" by default. usb-modeswitch solves that
 issue by sending the command which actually performs the switching
 of the device from "usb-storage" to "usbserial".
 .
 This package contains the commands data needed for usb-modeswitch.
Homepage: http://www.draisberghof.de/usb_modeswitch/

Package: usb.ids
Status: install ok installed
Priority: optional
Section: admin
Installed-Size: 612
Maintainer: Aurelien Jarno <aurel32@debian.org>
Architecture: all
Multi-Arch: foreign
Version: 2019.07.27-0+deb10u1
Replaces: usbutils (<< 1:008-1)
Breaks: usbutils (<< 1:008-1)
Description: USB ID Repository
 This package contains the usb.ids file, a public repository of all known
 ID's used in USB devices: ID's of vendors, devices, subsystems and device
 classes. It is used in various programs to display full human-readable
 names instead of cryptic numeric codes.
Homepage: http://www.linux-usb.org/usb-ids.html

Package: usbutils
Status: install ok installed
Priority: optional
Section: utils
Installed-Size: 195
Maintainer: Aurelien Jarno <aurel32@debian.org>
Architecture: armhf
Multi-Arch: foreign
Version: 1:010-3
Depends: libc6 (>= 2.7), libudev1 (>= 196), libusb-1.0-0 (>= 2:1.0.16), usb.ids
Description: Linux USB utilities
 This package contains the lsusb utility for inspecting the devices
 connected to the USB bus. It shows a graphical representation of the
 devices that are currently plugged in, showing the topology of the
 USB bus. It also displays information on each individual device on
 the bus.
Homepage: https://github.com/gregkh/usbutils

Package: util-linux
Essential: yes
Status: install ok installed
Priority: required
Section: utils
Installed-Size: 3363
Maintainer: LaMont Jones <lamont@debian.org>
Architecture: armhf
Multi-Arch: foreign
Version: 2.33.1-0.1
Replaces: bash-completion (<< 1:2.8), initscripts (<< 2.88dsf-59.2~), login (<< 1:4.5-1.1~), mount (<< 2.29.2-3~), s390-tools (<< 2.2.0-1~), setpriv (<< 2.32.1-0.2~), sysvinit-utils (<< 2.88dsf-59.1~)
Depends: fdisk, login (>= 1:4.5-1.1~)
Pre-Depends: libaudit1 (>= 1:2.2.1), libblkid1 (>= 2.31.1), libc6 (>= 2.28), libcap-ng0 (>= 0.7.9), libmount1 (>= 2.25), libpam0g (>= 0.99.7.1), libselinux1 (>= 2.6-3~), libsmartcols1 (>= 2.33), libsystemd0, libtinfo6 (>= 6), libudev1 (>= 183), libuuid1 (>= 2.16), zlib1g (>= 1:1.1.4)
Suggests: dosfstools, kbd | console-tools, util-linux-locales
Breaks: bash-completion (<< 1:2.8), grml-debootstrap (<< 0.68), mount (<< 2.29.2-3~), s390-tools (<< 2.2.0-1~), setpriv (<< 2.32.1-0.2~), sysvinit-utils (<< 2.88dsf-59.4~)
Conffiles:
 /etc/default/hwclock 3916544450533eca69131f894db0ca12
 /etc/init.d/hwclock.sh 1ca5c0743fa797ffa364db95bb8d8d8e
 /etc/pam.d/runuser b8b44b045259525e0fae9e38fdb2aeeb
 /etc/pam.d/runuser-l 2106ea05877e8913f34b2c77fa02be45
 /etc/pam.d/su ce6dcfda3b190a27a455bb38a45ff34a
 /etc/pam.d/su-l 756fef5687fecc0d986e5951427b0c4f
Description: miscellaneous system utilities
 This package contains a number of important utilities, most of which
 are oriented towards maintenance of your system. Some of the more
 important utilities included in this package allow you to view kernel
 messages, create new filesystems, view block device information,
 interface with real time clock, etc.

Package: v4l-utils
Status: install ok installed
Priority: optional
Section: utils
Installed-Size: 1368
Maintainer: Gregor Jasny <gjasny@googlemail.com>
Architecture: armhf
Version: 1.16.3-3
Replaces: ivtv-utils (<< 1.4.1-2), media-ctl
Depends: libv4l-0 (= 1.16.3-3), libv4l2rds0 (= 1.16.3-3), libc6 (>= 2.28), libgcc1 (>= 1:3.5), libstdc++6 (>= 5.2), libudev1 (>= 183), libv4lconvert0 (>= 0.5.0)
Breaks: ivtv-utils (<< 1.4.1-2), media-ctl
Description: Collection of command line video4linux utilities
 v4l-utils contains the following video4linux command line utilities:
 .
  decode_tm6000: decodes tm6000 proprietary format streams
  rds-ctl: tool to receive and decode Radio Data System (RDS) streams
  v4l2-compliance: tool to test v4l2 API compliance of drivers
  v4l2-ctl, cx18-ctl, ivtv-ctl: tools to control v4l2 controls from the cmdline
  v4l2-dbg: tool to directly get and set registers of v4l2 devices
  v4l2-sysfs-path: sysfs helper tool
Homepage: https://linuxtv.org/downloads/v4l-utils/

Package: vim-common
Status: install ok installed
Priority: important
Section: editors
Installed-Size: 334
Maintainer: Debian Vim Maintainers <team+vim@tracker.debian.org>
Architecture: all
Multi-Arch: foreign
Source: vim
Version: 2:8.1.0875-5
Depends: xxd
Recommends: vim | vim-gtk | vim-gtk3 | vim-athena | vim-nox | vim-tiny
Conffiles:
 /etc/vim/vimrc f24e66036f0802ed65c21cde317548a0
Description: Vi IMproved - Common files
 Vim is an almost compatible version of the UNIX editor Vi.
 .
 This package contains files shared by all non GUI-enabled vim variants
 available in Debian.  Examples of such shared files are: manpages and
 configuration files.
Homepage: https://www.vim.org/

Package: vim-tiny
Status: install ok installed
Priority: important
Section: editors
Installed-Size: 1072
Maintainer: Debian Vim Maintainers <team+vim@tracker.debian.org>
Architecture: armhf
Source: vim
Version: 2:8.1.0875-5
Provides: editor
Depends: vim-common (= 2:8.1.0875-5), libacl1 (>= 2.2.23), libc6 (>= 2.28), libselinux1 (>= 1.32), libtinfo6 (>= 6)
Suggests: indent
Conffiles:
 /etc/vim/vimrc.tiny edcfb3dbbc5c68b875e3b4ad399f261a
Description: Vi IMproved - enhanced vi editor - compact version
 Vim is an almost compatible version of the UNIX editor Vi.
 .
 This package contains a minimal version of Vim compiled with no GUI and
 a small subset of features. This package's sole purpose is to provide
 the vi binary for base installations.
 .
 If a vim binary is wanted, try one of the following more featureful
 packages: vim, vim-nox, vim-athena, vim-gtk, or vim-gtk3.
Homepage: https://www.vim.org/

Package: vl805fw
Status: install ok installed
Priority: extra
Section: x11
Installed-Size: 234
Maintainer: Simon Long <simon@raspberrypi.org>
Architecture: all
Version: 0.2
Description: Firmware loader for VL805 USB host controller
 Customised firmware and loader for USB3.0 host controller on Raspberry Pi.

Package: wget
Status: install ok installed
Priority: standard
Section: web
Installed-Size: 3172
Maintainer: Noël Köthe <noel@debian.org>
Architecture: armhf
Multi-Arch: foreign
Version: 1.20.1-1.1
Depends: libc6 (>= 2.28), libgnutls30 (>= 3.6.6), libidn2-0 (>= 0.6), libnettle6, libpcre2-8-0 (>= 10.32), libpsl5 (>= 0.16.0), libuuid1 (>= 2.16), zlib1g (>= 1:1.1.4)
Recommends: ca-certificates
Conflicts: wget-ssl
Conffiles:
 /etc/wgetrc c43064699caf6109f4b3da0405c06ebb
Description: retrieves files from the web
 Wget is a network utility to retrieve files from the web
 using HTTP(S) and FTP, the two most widely used internet
 protocols. It works non-interactively, so it will work in
 the background, after having logged off. The program supports
 recursive retrieval of web-authoring pages as well as FTP
 sites -- you can use Wget to make mirrors of archives and
 home pages or to travel the web like a WWW robot.
 .
 Wget works particularly well with slow or unstable connections
 by continuing to retrieve a document until the document is fully
 downloaded. Re-getting files from where it left off works on
 servers (both HTTP and FTP) that support it. Both HTTP and FTP
 retrievals can be time stamped, so Wget can see if the remote
 file has changed since the last retrieval and automatically
 retrieve the new version if it has.
 .
 Wget supports proxy servers; this can lighten the network load,
 speed up retrieval, and provide access behind firewalls.
Homepage: https://www.gnu.org/software/wget/

Package: whiptail
Status: install ok installed
Priority: optional
Section: utils
Installed-Size: 65
Maintainer: Alastair McKinstry <mckinstry@debian.org>
Architecture: armhf
Multi-Arch: foreign
Source: newt
Version: 0.52.20-8
Depends: libc6 (>= 2.4), libnewt0.52 (>= 0.52.20), libpopt0 (>= 1.14), libslang2 (>= 2.2.4)
Description: Displays user-friendly dialog boxes from shell scripts
 Whiptail is a "dialog" replacement using newt instead of ncurses. It
 provides a method of displaying several different types of dialog boxes
 from shell scripts. This allows a developer of a script to interact with
 the user in a much friendlier manner.
Homepage: https://pagure.io/newt

Package: wireless-regdb
Status: install ok installed
Priority: optional
Section: net
Installed-Size: 34
Maintainer: Seth Forshee <seth.forshee@canonical.com>
Architecture: all
Multi-Arch: foreign
Version: 2018.05.09-0~rpt1
Suggests: crda
Description: wireless regulatory database
 This package contains the wireless regulatory database used by the Central
 Regulatory Database Agent (CRDA) to configure wireless devices to operate
 within the radio spectrum allowed in the local jurisdiction.
 .
 This regulatory information is provided with no warranty either expressed or
 implied. Only Linux drivers which use cfg80211 framework can make use of the
 regulatory database and CRDA.
Homepage: http://wireless.kernel.org/en/developers/Regulatory/#The_regulatory_database

Package: wireless-tools
Status: install ok installed
Priority: optional
Section: net
Installed-Size: 243
Maintainer: Guus Sliepen <guus@debian.org>
Architecture: armhf
Multi-Arch: foreign
Version: 30~pre9-13
Depends: libc6 (>= 2.7), libiw30 (>= 30~pre1)
Conffiles:
 /etc/network/if-post-down.d/wireless-tools 5cc59de6a0f25f32f25298f05625623c
 /etc/network/if-pre-up.d/wireless-tools ab74bdf4a9503ddd3322890b155c475e
Description: Tools for manipulating Linux Wireless Extensions
 This package contains the Wireless tools, used to manipulate
 the Linux Wireless Extensions. The Wireless Extension is an interface
 allowing you to set Wireless LAN specific parameters and get the
 specific stats.
Homepage: http://www.hpl.hp.com/personal/Jean_Tourrilhes/Linux/Tools.html

Package: wpasupplicant
Status: install ok installed
Priority: optional
Section: net
Installed-Size: 2679
Maintainer: Debian wpasupplicant Maintainers <wpa@packages.debian.org>
Architecture: armhf
Multi-Arch: foreign
Source: wpa
Version: 2:2.7+git20190128+0c1e29f-6+deb10u3
Depends: libc6 (>= 2.28), libdbus-1-3 (>= 1.9.14), libnl-3