# Squeezebox
Simple LMS Client 
Written for Hyperpixel 4" retangular touchscreen.  Very simple touch control, for fat fingers.  Just start/stop, next and prev controls.

Some of the prep required:

sudo apt update

sudo apt upgrade

sudo apt install python3-pip

sudo usermod -a -G video pi

sudo apt install libopen-jp2-7-dev

sudo apt install libtiff5

sudo apt install ttf-dejavu

pip3 install Pillow

sudo apt install python3-evdev

sudo apt install pigpiod


Create a subdirectory (sb) in the pi home directory.  Download and unzip LMSTools from github into it.  Download the files from this repository into it, as well.


Follow Pimoroni's guide to install and configure the Hyperpixel 4 display:  https://learn.pimoroni.com/article/getting-started-with-hyperpixel-4

Create a systemd service to auto-start sb.py at boot: 
https://www.raspberrypi.com/documentation/computers/using_linux.html#creating-a-service

![photo](https://blogger.googleusercontent.com/img/a/AVvXsEhMknYuzTLUjgOaBY3bprbqNAH_ZTRH4tSL0SEY7FEo-rhAtquIV9xGgr5IeupwkfhRanZm8FhUtDCllnxqEpNPSzXeiboBrS1ZGFbbwuEUo5rrPD6AVtlwL4yBVRy45xPeYeP0zZt8DJG9TXrHPpR4bLPUq4ehwG_UALyLl4Tmcemx1GGrNfLTOMtq-Q=s2048)
