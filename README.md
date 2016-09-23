# ser-pdm
	     ________________
	    |  _         _   |
	    | |_  |_| |  /   |
	    |  _| | | | /_   |
	    |  _   _         |
	    | |_/ |_|  *  __ |
	    | |_\ | \ *  |/| |
	    |            |_| |
	    |________________| inc.

	A non-existant corporation
	
	Taking the NEW, out of ZEALAND, since 2016!
	                 (*_*)
	                  \|/
	 ======================================
	|   _   __  __        __   _           |
	|  / \ |   |  |      |  | | \  |\  /|  |
	|  \_  |__ |__|  __  |__| |  | | \/ |  |
	|    \ |   | \       |    |  | |    |  |
	|  __/ |__ |  \      |    |_/  |    |  |
	|                                      |
	|  (Copyleft) 666 Rabid Discord & Co.  |
	|      A division of SH1ZBR0 Inc.      |
	|                                      |
	|    -----NO PONIES ALLOWED!!!!-----   |
	|                                      |
	 ======================================

This python script plays an audio stream over the serial port.
Audio stream must be s8, u8, s16be, s16le, u16be, or u16le

The serial port may be anything, including:
UART, RS232, FTDI, GPIO, ARDUINO, etc.. Anything with a serial output!

As featured here:

	<iframe width="560" height="315" src="https://www.youtube.com/embed/LKRkUUQOG20" frameborder="0" allowfullscreen></iframe>

EXAMPLES:

ffmpeg / avconv:

	ffmpeg -i <miscellaneous-sound-file> -f s8 -acodec pcm_s8 -ar 22400 -ac 1 - | ./usbsersnd.py <serialport> 230400 s8
	
	avconv -i <miscellaneous-sound-file> -f s8 -acodec pcm_s8 -ar 22400 -ac 1 - | ./usbsersnd.py <serialport> 230400 s8

VLC:

	vlc <music file(s)/folder) --sout \"#transcode{acodec=s16le,,channels=1,samplerate=22400,afilter=compressor}:standard{access=file,mux=raw,dst=-}\" | ./$

Many other things are possible with this program, including ALSA, Pulseaudio, and Jack tunneling through STDIN (good luck with that ;D )

# Installation

Git clone this repository using:

	git clone https://github.com/kiwib1rd1337/ser-pdm

then enter the directory using:

	cd ser-pdm

You may now run the script by rnning: ./serpdm.py --help

OPTIONAL: to cythonize and compile ser-pdm, run:

	./cythonize.sh

This should generate a native compiled executable using cython and gcc. The resulting executable should be faster than the python interpreter version.

The cythonize script has NO error detection, so you have to check if it did it's job or not.
Now test it by running "./serpdm". If it works, it's all good. If it doesn't, then something went wrong (you might not have cython or python-dev installed). You may skip if this is the case.


To install the program, run:

	sudo ./install.sh
	
This is a very basic installation script, so you may get a few errors. It should still work regardless. If it doesn't, then there may be an issue with /usr/local/bin on your system, and you may have to install ser-pdm manually by CP-ing and CHMOD-ing the serpdm.py script and/or the compiled serpdm executable

To uninstall ser-pcm, run:
	
	sudo ./uninstall.sh

Like the install and cython scripts, this script is also very basic, and has no error detection.
