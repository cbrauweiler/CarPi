#!/bin/bash

clear

# check for internet connection
ping -c1 -w1 google.de 2>/dev/null 1>/dev/null
if [ "$?" = 0 ]
then
    echo "---------------------------------------------------------"
    echo "Internet connection present..."
    echo "---------------------------------------------------------"
else
    echo "---------------------------------------------------------"
    echo "Inernet connection is missing"
    echo "---------------------------------------------------------"
    echo ""
    echo "Please make sure a internet connection is available"
    echo "and than restart installer!"
    exit 0
fi

BASEDIR="`cd $0 >/dev/null 2>&1; pwd`" >/dev/null 2>&1
export DEBIAN_FRONTEND=noninteractive

check_rpiuimods=`dpkg -l | awk '$2=="raspberrypi-ui-mods" { print $3 }'`
check_fbi=`dpkg -l | awk '$2=="fbi" { print $3 }'`
check_omxplayer=`dpkg -l | awk '$2=="omxplayer" { print $3 }'`
check_mc=`dpkg -l | awk '$2=="mc" { print $3 }'`
check_samba=`dpkg -l | awk '$2=="samba" { print $3 }'`
check_exfatfuse=`dpkg -l | awk '$2=="exfat-fuse" { print $3 }'`
check_exfatutils=`dpkg -l | awk '$2=="exfat-utils" { print $3 }'`
check_dphysswapfile=`dpkg -l | awk '$2=="dphys-swapfile" { print $3 }'`
check_pythonpicamera=`dpkg -l | awk '$2=="python-picamera" { print $3 }'`
check_pythonsmbus=`dpkg -l | awk '$2=="python-smbus" { print $3 }'`
check_pythonserial=`dpkg -l | awk '$2=="python-serial" { print $3 }'`
check_pythonpip=`dpkg -l | awk '$2=="python-pip" { print $3 }'`
check_git=`dpkg -l | awk '$2=="git" { print $3 }'`
check_gitcore=`dpkg -l | awk '$2=="git-core" { print $3 }'`
check_unattended=`dpkg -l | awk '$2=="unattended-upgrades" { print $3 }'`
check_i2ctools=`dpkg -l | awk '$2=="i2c-tools" { print $3 }'`
check_libssh4=`dpkg -l | awk '$2=="libssh-4:armhf" { print $3 }'`
check_libyajl2=`dpkg -l | awk '$2=="libyajl2:armhf" { print $3 }'`
check_libmicrohttpd10=`dpkg -l | awk '$2=="libmicrohttpd10" { print $3 }'`
check_libmysqlclient18=`dpkg -l | awk '$2=="libmysqlclient18:armhf" { print $3 }'`
check_libtinyxml=`dpkg -l | awk '$2=="libtinyxml2.6.2:armhf" { print $3 }'`
check_libtinyxml2=`dpkg -l | awk '$2=="libtinyxml2-2:armhf" { print $3 }'`
check_libpcrecpp0=`dpkg -l | awk '$2=="libpcrecpp0:armhf" { print $3 }'`
check_libjsoncpp0=`dpkg -l | awk '$2=="libjsoncpp0" { print $3 }'`
check_libvax111=`dpkg -l | awk '$2=="libva-x11-1:armhf" { print $3 }'`
check_xdotool=`dpkg -l | awk '$2=="xdotool" { print $3 }'`
check_gpsd=`dpkg -l | awk '$2=="gpsd" { print $3 }'`
check_gpsdclients=`dpkg -l | awk '$2=="gpsd-clients" { print $3 }'`
check_espeak=`dpkg -l | awk '$2=="espeak" { print $3 }'`
check_navit=`dpkg -l | awk '$2=="navit" { print $3 }'`
check_xinit=`dpkg -l | awk '$2=="xinit" { print $3 }'`
check_preload=`dpkg -l | awk '$2=="preload" { print $3 }'`
check_libxss1=`dpkg -l | awk '$2=="libxss1" { print $3 }'`
check_camera=`sudo grep start_x= /boot/config.txt | cut -d "=" -f 2`
check_memory=`sudo grep gpu_mem= /boot/config.txt | cut -d "=" -f 2`
check_splash=`sudo grep disable_splash= /boot/config.txt | cut -d "=" -f 2`
check_i2c=`sudo grep i2c-dev /etc/modules`
check_i2cconfig=`sudo grep ^dtparam=i2c_arm= /boot/config.txt | cut -d "=" -f 3`
check_spi=`sudo grep ^dtparam=spi= /boot/config.txt | cut -d "=" -f 3`
check_splash=`sudo grep ^disable_splash= /boot/config.txt | cut -d "=" -f 2`

clear
echo "---------------------------------------------------------"
echo "Updating raspbian repos..."
echo "---------------------------------------------------------"
sudo apt-get update -q
echo "------"
echo "Finish"
echo "------"
sleep 1

clear
echo "---------------------------------------------------------"
echo "Failsave: Check for uncofigured packages and deps..."
echo "---------------------------------------------------------"
sudo dpkg --configure -a
sudo apt-get install -f -y --force-yes -q
echo "------"
echo "Finish"
echo "------"
sleep 1

if [ "$check_unattended" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing unattended-upgrades..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y unattended-upgrades
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

# Failsafe
sudo unattended-upgrades

clear
echo "---------------------------------------------------------"
echo "Updating raspbian to latest stable version..."
echo "---------------------------------------------------------"
sudo apt-get upgrade --force-yes -q -f -y && sudo apt-get dist-upgrade --force-yes -q -f -y
echo "------"
echo "Finish"
echo "------"
sleep 1

if [ "$check_rpiuimods" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing raspberrypi-ui-mods..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y raspberrypi-ui-mods -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_libssh4" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libssh-4..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libssh-4
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_rpiuimods" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libyajl2..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libyajl2
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_libmicrohttpd10" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libmicrohttpd10..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libmicrohttpd10
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_libmysqlclient18" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libmysqlclient18..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libmysqlclient18
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_libtinyxml" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libtinyxml2.6.2..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libtinyxml2.6.2
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_libtinyxml2" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libtinyxml2-2..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libtinyxml2-2
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_libpcrecpp0" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libpcrecpp0..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libpcrecpp0
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_libjsoncpp0" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libjsoncpp0..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libjsoncpp0
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_libvax111" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libva-x11-1..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libva-x11-1
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_xdotool" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing xdotool..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y xdotool
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_gpsd" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing gpsd..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y gpsd -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_gpsdclients" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing gpsd-clients..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y gpsd-clients
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_espeak" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing espeak..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y espeak
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_navit" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing navit..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y navit -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_i2ctools" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing i2c-tools..."
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y i2c-tools
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_fbi" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing FBI"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y fbi
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_omxplayer" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing OMXPlayer"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y omxplayer
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_mc" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing Midnight Commander (mc)"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y mc
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_exfatfuse" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing ExFat-Drivers"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y exfat-fuse
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_exfatutils" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing ExFat-Utils"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y exfat-utils
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_dphysswapfile" != "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Removing Dphys-swapfile"
    echo "---------------------------------------------------------"
    sudo apt-get remove --purge -q -f -y dphys-swapfile
    sudo apt-get autoremove --purge -q -y >/dev/null 2>&1
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_pythonsmbus" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing Python-smbus"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y python-smbus
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_pythonserial" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing Python-serial"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y python-serial
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_pythonpip" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing Python-pip"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y python-pip
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_git" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing Git"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y git
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_gitcore" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing Git-core"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y git-core
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_pythonpicamera" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing Python-picamera"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y python-picamera
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_xinit" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing Xinit"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y xinit
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_preload" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing Preoad"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y preload
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_libxss1" == "" ] >/dev/null 2>&1
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing libxss1"
    echo "---------------------------------------------------------"
    sudo apt-get install --force-yes -q -f -y libxss1
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

clear
echo "---------------------------------------------------------"
echo "Deflating carpc-package..."
echo "---------------------------------------------------------"
sudo tar xfvz $BASEDIR/carpc.tar.gz -C /
echo "------"
echo "Finish"
echo "------"
sleep 1

if [ -z "$check_memory" ] || [ "$check_memory" -lt 256 ]
then
    clear
    echo "---------------------------------------------------------"
    echo "Memory-Split was < 256MB and will be updated"
    echo "---------------------------------------------------------"
    sudo sed -i -e "s/^gpu_mem=$check_memory/gpu_mem=256/" /boot/config.txt
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

clear
echo "---------------------------------------------------------"
echo "Enable dtoverlay for i2c in config.txt"
echo "---------------------------------------------------------"
sudo sed -i -e "s/^dtparam=i2c_arm=off/dtparam=i2c_arm=on/" /boot/config.txt
if [ "$check_i2cconfig" != "on" ] && [ "$check_i2cconfig" != "off" ]
then
    sudo -u root bash -c "sed -i '/dtparam=i2c_arm=/d' /boot/config.txt"
    sudo -u root bash -c 'echo "dtparam=i2c_arm=on" >> /boot/config.txt'
fi
echo "------"
echo "Finish"
echo "------"
sleep 1

if [ "$check_i2c" != "i2c-dev" ]
then
    clear
    echo "---------------------------------------------------------"
    echo "Enabling I2C module"
    echo "---------------------------------------------------------"
    sudo -u root bash -c 'echo "i2c-dev" >> /etc/modules'
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ "$check_splash" != "0" ]
then
    clear
    echo "---------------------------------------------------------"
    echo "Disable splashscreen config.txt"
    echo "---------------------------------------------------------"
    sudo sed -i -e "s/^disable_splash=1/disable_splash=0/" /boot/config.txt
    if [ "$check_splash" != "0" ] && [ "$check_splash" != "1" ]
    then
        sudo -u root bash -c "sed -i '/disable_splash=/d' /boot/config.txt"
        sudo -u root bash -c 'echo "disable_splash=0" >> /boot/config.txt'
    fi
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

clear
echo "---------------------------------------------------------"
echo "Disable dtoverlay for spi in config.txt"
echo "---------------------------------------------------------"
sudo sed -i -e "s/^dtparam=spi=on/dtparam=spi=off/" /boot/config.txt
if [ "$check_spi" != "on" ] && [ "$check_spi" != "off" ]
then
    sudo -u root bash -c "sed -i '/dtparam=spi=/d' /boot/config.txt"
    sudo -u root bash -c 'echo "dtparam=spi=off" >> /boot/config.txt'
fi
echo "------"
echo "Finish"
echo "------"
sleep 1

if [ -e /etc/init.d/asplashscreen ]
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing service asplashscreen"
    echo "---------------------------------------------------------"
    sudo update-rc.d asplashscreen defaults >/dev/null 2>&1
    sudo update-rc.d asplashscreen enable >/dev/null 2>&1
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

if [ -e /etc/init.d/lightdm ]
then
    clear
    echo "---------------------------------------------------------"
    echo "Disabling LightDM service"
    echo "---------------------------------------------------------"
    sudo update-rc.d lightdm disable >/dev/null 2>&1
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

clear
echo "---------------------------------------------------------"
echo "Enable autologin to console..."
echo "---------------------------------------------------------"
sudo systemctl set-default multi-user.target
sudo ln -fs /etc/systemd/system/autologin@.service /etc/systemd/system/getty.target.wants/getty@tty1.service
sudo sed /etc/lightdm/lightdm.conf -i -e "s/^autologin-user=pi/#autologin-user=/"
echo "------"
echo "Finish"
echo "------"
sleep 1

clear
echo "---------------------------------------------------------"
echo "Creating temp folder for kodi..."
echo "---------------------------------------------------------"
sudo mkdir /home/pi/.kodi/temp >/dev/null 2>&1
sudo chmod -R a+rwx /home/pi/.kodi/temp >/dev/null 2>&1
echo "------"
echo "Finish"
echo "------"
sleep 1

clear
echo "---------------------------------------------------------"
echo "Set user permissions of home/pi..."
echo "---------------------------------------------------------"
sudo chown -R pi:pi /home/pi >/dev/null 2>&1
echo "------"
echo "Finish"
echo "------"
sleep 1

if [ "$check_camera" != "1" ]
then
    clear
    echo "---------------------------------------------------------"
    echo "Enabling RaspberryPi-Camera"
    echo "---------------------------------------------------------"
    sudo sed -i -e "s/^start_x=$check_camera/start_x=1/" /boot/config.txt
    if [ "$check_camera" != "0" ] && [ "$check_camera" != "1" ]
    then
	sudo -u root bash -c "sed -i '/start_x=/d' /boot/config.txt"
	sudo -u root bash -c 'echo "start_x=1" >> /boot/config.txt'
    fi
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

# wiringpi
if [ ! -d /opt/wiringPi ] || [ ! -e /usr/local/bin/gpio ]
then
    clear
    echo "---------------------------------------------------------"
    echo "Installing WiringPi"
    echo "---------------------------------------------------------"
    cd /opt
    sudo rm -rf wiringPi
    sudo git clone git://git.drogon.net/wiringPi >/dev/null 2>&1
    cd /opt/wiringPi
    sudo ./build >/dev/null 2>&1
    echo "------"
    echo "Finish"
    echo "------"
    sleep 1
fi

clear
echo "---------------------------------------------------------"
echo "Switch console to tty2 during boot"
echo "---------------------------------------------------------"
sudo sed -i "s/console=tty1/console=tty2/g" /boot/cmdline.txt
echo "------"
echo "Finish"
echo "------"
sleep 1

clear
echo "---------------------------------------------------------"
echo "Update persmissions on user pi for group tty"
echo "---------------------------------------------------------"
sudo adduser pi tty >/dev/null 2>&1
echo "------"
echo "Finish"
echo "------"
sleep 1

clear
echo "---------------------------------------------------------"
echo "Cleanup system..."
echo "---------------------------------------------------------"
sudo apt-get --force-yes -q -f -y remove --purge minecraft-pi scratch wolfram-engine debian-reference-* epiphany-browser* sonic-pi supercollider* >/dev/null 2>&1
sudo apt-get --force-yes -q -f -y clean >/dev/null 2>&1
sudo apt-get --force-yes -q -f -y autoremove --purge >/dev/null 2>&1
sudo rm -r /home/pi/python_games/ >/dev/null 2>&1
sudo rm -f /home/pi/Desktop/debian-reference-common.desktop /home/pi/Desktop/epiphany-browser.desktop /home/pi/Desktop/minecraft-pi.desktop /home/pi/Desktop/pistore.desktop /home/pi/Desktop/python-games.desktop /home/pi/Desktop/scratch.desktop /home/pi/Desktop/sonic-pi.desktop /home/pi/Desktop/wolfram-language.desktop /home/pi/Desktop/wolfram-mathematica.desktop >/dev/null 2>&1
echo "------"
echo "Finish"
echo "------"
sleep 1

clear
echo "--------------------------------------------------------------------------"
echo "System almost ready! Check /etc/default/gpsd for the correct gpsd device,"
echo "download map for Navit from http://maps6.navit-project.org/ and save it as"
echo "map1.bin in /home/pi/.navit. Reboot and have fun!"
echo "--------------------------------------------------------------------------"
