#!/usr/bin/python2.7 -u

# the -u us for preventing the damn STDIN from buffering on us. It's probably no longer necessary, anyway.

#            ________________
#           |  _         _   |
#           | |_  |_| |  /   |
#           |  _| | | | /_   |
#           |  _   _         |
#           | |_/ |_|  *  __ |
#           | |_\ | \ *  |/| |
#           |            |_| |
#           |________________| inc.
#
#       A non-existant corporation
#
# Taking the NEW, out of ZEALAND, since 2016!
#                  (*_*)
#                   \|/
#  ======================================
# |   _   __  __        __   _           |
# |  / \ |   |  |      |  | | \  |\  /|  |
# |  \_  |__ |__|  __  |__| |  | | \/ |  |
# |    \ |   | \       |    |  | |    |  |
# |  __/ |__ |  \      |    |_/  |    |  |
# |                                      |
# |  (Copyleft) 666 Rabid Discord & Co.  |
# |      A division of SH1ZBR0 Inc.      |
# |                                      |
# |    -----NO PONIES ALLOWED!!!!-----   |
# |                                      |
#  ======================================
#
# This program comes with ABSOLUTELY NO WARRANTY to the extent of applicable law. (In other words, if you didn't pay for it, then DO NOT expect me to pay out if your computer decides to commit suicide or some shit because of this program.
#
# Please install: python python-numpy python-scipy python-matplotlib cython
# before use!
#
# This file may be used and abused by anyone who get's hold of it, within the terms of the I_DONT_GIVE_A_FUCK_UNLESS_YOU_PROFIT_OFF_OF_MY_WORK public lic...
# Oh wait, that license doesn't exist. Oh well, just consider this program licensed under the GNU GPLv3 instead (I don't want closed source idiots bastardising my code, do I?).

# Copyreich bullschitte:

###################################################################################
#                                                                                 #
#  SER-PDM - Plays audio through serial port with Delta-Sigma PDM                 #
#                                                                                 #
#  Copyright (C) 2016  Steven Pearce (Sh1zbr0) EMAIL: <stevenprc2new@gmail.com>   #
#                                                                                 #
#    This program is free software: you can redistribute it and/or modify         #
#    it under the terms of the GNU General Public License as published by         #
#    the Free Software Foundation, either version 3 of the License, or            #
#    (at your option) any later version.                                          #
#                                                                                 #
#    This program is distributed in the hope that it will be useful,              #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#    GNU General Public License for more details.                                 #
#                                                                                 #
#    You should have received a copy of the GNU General Public License            #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
#                                                                                 #
###################################################################################

# Oops, I think I doxxed myself.
#
# Now, I'd appreciate that if in the case that you do fork or edit this program, that you kept all (or most) of the comments, easter-eggs, and all out whittyness of my work, but feel free to add to it in a similar style of mine. This is optional, of course ^v^ 
# I'd also appreciate if you kept all modified deriatives of this program as free and open source software (unless you negotiate with me personally about some alternative agreement. Who knows, I may be generous, like Rarity ;P #)
#
# That being said, let's begin!!!
#
#!/usr/bin/python2.7... Oh wait, I just typed this at line 1. DAMN IT!

import serial # The main point of this program is to use this library to play music over the serial port
import struct
import sys
import os
import time # used for somepony's autocalibrate feature
import random # Also used for that purple unicorn/alicorn's autocalibrate feature
import array
import base64 # I really don't know what this is for (easter bunny lays an egg)
import math # I was pretty good at this when I went to school.

def startplayin(port, baud, bits, signed, endian): # start playin' the stream to the serial port
	ser = serial.Serial()
	ser.baudrate = int(baud) # Maud Pie waz here!
	ser.port = port
	ser.parity = "N" # Parity, in this particular case, is absolutely unnecessary.
	
	ser.write_timeout = 0 # After testing this on a bluetooth serial device, it looks like Nightmare Moon cursed pySerial with a write buffer. To combat this, I set the write timeout to no more than none.
	ser.timeout = 0 # Wrangling write tmeout, just because i'm pissed off about the write buffer problem I attempeted to fix with the command above.
	
	startbits = 1 # startbits (serial protocol optimization). This is always 1. DO NOT CHANGE
	stopbits = 1 # stop bots (serial protocol optimixation). Configurable: may be 1 or 2.
	ser.stopbits = stopbits
	
	ser.xonxoff = 0 # not needed
	bytesize = 8 # data bits (seial port protocol). This may be 5,6,7,8, BUT NOT 9!
	ser.bytesize = bytesize
	ser.open()
	
	if os.name == 'posix': # last ditch attempt to enforce non-blocking IO on the serial port. This is exclusive to POSIX and POSIX-like systems (i.e. Linux)
		ser.nonblocking()
	else:
		# FRACK THIS SHIP!
		print("You are running this on a non-posix system. It is YOUR responsibility to make sure the serial port isn't buffering anything. (Buffering may cause unnecessary latency on lossy serial ports)")
	
	buffer_ms=100 # set buffer to 10ms
	
	buffer=int(baud)/1000*buffer_ms # define the buffer size from 100/buffer_ms of the baud rate, per second (i.e. 1000/100=10 for 100ms latency)
	
	# This is where the shit starts getting real! Celestia, please don't let it hit the fan.
	
	nativeendian = sys.byteorder # What endianness am I? (usually it is little-endian, but I just want to make sure this isn't running inside an illegal alien of a microprocessor (like old SuperH processors, bi-endian processors running big endian operating systems (like PowerPC, ARM, MIPS, SH4, Etc...), the AVR32, or a Motorola 68000 series processor.)  
	
	buf = array.array("b", [1,3,3,7]) # Define the buffer
	
	error = 0 # (error for the pdm modulator)
	
	optsamplerate = int(baud) # The sample rate should match the baud rate
	
	cal_time = time.time(); # Use time function to autocalibrate for start and stop bits.
	cal_bits_orig = bytesize + startbits + stopbits # define default for autocalibrate.
	cal_bits = cal_bits_orig
	old_cal_bits = 0
	cal_float = float(cal_bits)
	readin = ''
	
	cal_wait_time=0 # These variables are used in order to log instances of implementing delays to combat lossy serial ports
	old_cal_wait_time=cal_wait_time
	
	arrayconf = ''
	if bits == 8: # create byte array configuration for correct format (I dragged it down here, so it doesn't continuously run these if - else rules every time the buffer resets, thereby optimising the code)
		if signed == 1:
			arrayconf = "b"
		else:
			arrayconf = "B"
	elif bits == 16: # optimize by using elif instead of if
		if signed == 1:
			arrayconf = "h"
		else:
			arrayconf = "H"
                       
	# Define miscellaneous variables
	count = 0
	bstr = ""
	val = 0
	data = ""
	
	Byteswap = True if nativeendian != endian else False # Is our endianness native? 
	
	range = math.pow(256,bits / bytesize)  # calculate integer range from bit value (for some reason, python code doesn't seem to tolerate exponents. I got stuck here for a while, wondering why my perfect code continued to play EAR RAPE through my serial port!)
	signedadd = signed * range / 2 # Calculate offset for signed integers
	
	bufmultiplier = bits / 8 # compensate for 16 bit buffer by adjusting size accordingly
	
	ser.write("U"*buffer); # Stream a simple benchmark buffer to the serial port (U translates to '01010101', so that should minimize noise with the start bit being 1 and endbit being 0.
	while True: # Our main loop.
		
		readin = sys.stdin.read(buffer * bufmultiplier) # Read the buffer from STDIN (double buffer in case of 16 bit. We want the 16 bit values)		
		
		# create byte array in correct format
		buf = array.array(arrayconf, readin)
		
		if Byteswap: # Swap bytes if endianness is not native
			buf.byteswap()
		
		if len(buf) == 0: # break if we dont have an array
			break
						
		# Start for-looping each value in the buffer
		for c in buf:
			error += c+signedadd # Add buffer value to error (and add signed offset if needed) to prepare for the modulator function
			
			if error>range: # This is the first part of the PDM / Delta-Sigma modulator function
				val = 1
				error = error - range
			else: # This is the second part of the PDM / Delta-Sigma modulator function  ---PR1NCE55 LUNA WAZ HERE!
				val = 0
			
			# Now that we've modulated our bit, we can add it to the byte (or skip it if it's a calibration bit)
			
			if count < bytesize: # add the bit to string, if within bytesize range (otherwise, it's a calibration bit, so skip it)
				bstr += str(val)
			
			count += 1 #we just calculated/skipped another bit!
			
			if count >= cal_bits: # if we calculated all the data bits, and skipped the calibration bits:
				data += chr(int(bstr,2)) # add bstr to data buffer
				bstr = "" # reset bstr variable
				count = 0 # reset the bit counter
		
		ser.flush() # FLUSH WHAT'S LEFT OF THE GOD DAMNED BUFFER ALREADY! IT'S PISSING ME OFF WHILE I AM PROGRAMMING THIS WORKAROUND AT 4:30 IN THE GOD DAMN MORNING!
		ser.write(data) # Send the 1024 bytes to the serial port
		
		data = "" # clear data variable
		
		timepassed = (time.time() - cal_time) * 1000
		cal_float_raw = timepassed / buffer_ms * cal_bits_orig   # Calculate a rough estimate of an optimal calibration setting. time-elapsed / buffer-time * original_cal_bits_estimate
		
		if cal_float_raw < cal_float * 16: # to combat erraneous buffering (i.e. paused stream)
#			cal_float = (cal_float_raw + (cal_float * 99))/100 # even out the estimate by using a simple averaging equation,
#			cal_bits_new = int(cal_float) # round the averaged float down to an int, so we can get a standalone bit value to use for the next buffered input.
			
			#if cal_bits_new - bytesize < startbits + stopbits: # an attempt to clean up negative calibration problem which is common with lossy serial ports at higher baud rates. Otherwise known as "How Twilight Sparkle got her Wings" or the "I've been up till five o clock programming without eating for 15 hours programming this workaround. Have some goddamned respect, man!"

			#if True:
			wait_time_start = time.time()
			#cal_wait_time_new = ( (float(buffer_ms)*float(baud)) - (timepassed*float(baud)) ) / (float(baud) * 1000)
                        cal_wait_time_new = ( float(buffer_ms) - timepassed ) * 1000
			cal_wait_time = (cal_wait_time_new + old_cal_wait_time * 99) / 100
			if cal_wait_time > 0:
				while wait_time_start + cal_wait_time >= time.time():
					pass
			
			if cal_wait_time < 0:
				#print( int( (cal_wait_time/-1000) * (float(baud) / bits) * bufmultiplier) )
				readind = sys.stdin.read( int( (cal_wait_time/-1000) * (float(baud) / bits) ) * bufmultiplier)

			#cal_bits = bytesize + startbits + stopbits


			#if cal_bits_new - bytesize > startbits + stopbits: # Otherwise, amend the drop-bits feature
			#	cal_bits = cal_bits_new
		
#			if old_cal_bits != cal_bits: # We are changing our calibration. We need to log this to STDOUT.
#				print("SER-PDM: Twilight Sparkle's Autocalibrate: play %s bits, then skip %s bits."  % (bytesize, cal_bits - bytesize)) # EXCUSE ME! I wonder who added this, damn pony vandals, I tell you, they always find a way to edit my code.
#				old_cal_bits = cal_bits
			
				if cal_bits - bytesize > bytesize and random.randint(0,5) == 4: # We are losing over half our marbles. There's no point in continuing. 
					molasses() # Tell STDIN why we're giving up
					raise Exception("Cannot keep up. We are too slow for the baud rate.", "%s bits dropped for every %s bits sent" % (cal_bits - bytesize, bytesize)) # Finally give up
			
			if old_cal_wait_time * 0.9 > cal_wait_time or cal_wait_time > old_cal_wait_time * 1.1: # Fast calibration method...
				if cal_wait_time > 0:
					print("SER-PDM: Twilight Sparkle's Autocalibrate: wait for %s seconds between buffering (fast serial port calibration)"  % (cal_wait_time))
					old_cal_wait_time = cal_wait_time 
			
			if old_cal_wait_time * 1.1 < cal_wait_time or cal_wait_time < old_cal_wait_time * 0.9: # Slow calibration method...
                                if cal_wait_time > 0:
                                        print("SER-PDM: Twilight Sparkle's Autocalibrate: dump %s of between buffering (slow serial port calibration)"  % (cal_wait_time))
                                        old_cal_wait_time = cal_wait_time
			
		else:
			print("SER-PDM: Twilight Sparkle's Autocalibrate: Ignoring unusually large delay.") # There she goes, ponies editing my code again... -_-
		
		cal_time = time.time() # Reset the calibration timer.
	
	# Cheese, I amme a13373 Phr4cQu3r, aren't I?

def molasses(): # For the enevitable case when our hardware or software is too slow, and can't keep up.
	sys.stderr.write('ERROR: Cannot keep up with baud rate. Halting now!')
	print("""

 -=+| MOLASSES ALERT! / SMOOZE ALERT! |+=-

ERROR: Twilight Sparkle has realised that SER-PDM is skipping more bits than she is sending!

"We are dropping more than half our stash!" -- Spike, the dragon

----====++++|||| PLEASE READ THE BELOW TEXT ||||++++====----

This is usually a clear sign that there is not enough CPU power for SER-PDM to function properly at this baud rate.
Either that, or your serial port is VERY VERY LOSSY! (i.e. Bluetooth or network can't keep up with the demand)

Oh well, back to the drawing board.

Try picking a slower baud rate next time, hmm-kay?

And remember kids, SER-PDM does not use performance enhancing drugs! It is up to the end user 
to overclock their P.O.S 386-SX computer.""")
# Geez, just when i thought I made it clear enough when I said "NO PONIES ALLOWED!!!!", for some reason they keep mysteriously showing up and fucking with my code!

def help(): # Just in case we have yet another 'Nice Trucker', '9/11', 'Boston Bombing', 'Christchurch earthquake', 'Japanese Tsunami', 'Bubonic Plague', 'Texas Wildfire', 'L-R Snackbar', 'sudo rm -rf /', ':(){ :|:& };:', 'Zika Virus', 'Ebola Epidemic', 'Changeling Invasion', 'Tainted Convolvulus', 'Titanic', 'Satanic Centaur', 'Lake Taupo eruption', 'Challenger', "Kaikoura Tsunami", "Portuguese Flame War", "Alaskan Ice Age", "Teutonic Plague", "Burrito Shake Boogie", "Radioactive Curry", "Masked Pony", "727 En Agua" ... need I list more possibilities?
	print("""                    (*_*)
                     \|/
  =======================================
 |   _   __  __        __   _    _   _   |
 |  / \ |   |  |      |  | | \  | \_/ |  |
 |  \_  |__ |__|  __  |__| |  \ |  |  |  |
 |    \ |   | \       |    |  / |  |  |  |
 |  __/ |__ |  \      |    |_/  |  |  |  |
 |                                       |
 |  (Copyleft) 666 Rabid Discord & Co.   |
 |      A division of SH1ZBR0 Inc.       |
 |                                       |
 |    -----NO PONIES ALLOWED!!!!-----    |
 |                                       |
  =======================================

This program is licensed under the GNU GPL version 3. You should've gotten a copy of it when you downloaded this software (the 'COPYING' file). Otherwise, see <http://www.gnu.org/licenses/> for details.

Info:
  This application takes raw pcm audio from STDIN, and plays it through a serial port.
  Just hook up your speaker wires to TX and GND pins of the serial port!

This is Version 2. This one uses DELTA-SIGMA PDM, instead of crappy old PWM!

The serial port may be anything, including:
UART, RS232, FTDI, GPIO, ARDUINO, etc.. Anything with a serial output!

Input format should be raw 1-channel pcm s8,u8,s16le,u16le,s16be or u16be.
Use a bitrate of about a 10th of the baud rate.

EXAMPLES:

 ffmpeg (or avconv):
   ffmpeg -i <miscellaneous-sound-file> -f s8 -acodec pcm_s8 -ar 230400 
-ac 1 - | ./serpdm.py 
<serialport> 230400 s8

 VLC:
   vlc <music file(s)/folder) --sout 
\"#transcode{acodec=s16le,,channels=1,samplerate=230400,afilter=compressor}:standard{access=file,mux=raw,dst=-}\" 
| ./serpdm.py <serialport> 230400 s16le

Many other things are possible with this program, including ALSA, Pulseaudio, and Jack tunneling through STDIN (good luck with that ;D )
FIFO tunneling is also possible!

This program will automatically print the calculated optimum sample frequency, in case you need to optimize it for your particular serial port device (and baud rate)

Lower bitrates may require a good low pass rc filter to remove baud noise at lower baud frequencies.
There is no point going for a baud rate below 57600, but feel free do do so if you want to.

Input bitrate is the same as the baud rate. 
----------------------------------------------------
USAGE: %s /dev/<SERIALPORT> <BAUDRATE> <FORMAT>
DEBUG MODE: %s --debug <serialport> <baudrate> <format>

EXAMPLE: %s /dev/ttyUSB0 230400""" % (sys.argv[0], sys.argv[0], sys.argv[0])) #CapitalistArmy

#INIT CODE

print(""" """)
# Just a little something to cleal up the text colours in the nano text editor. It's almost like Queen Chrysalis magically made my text glow green

if len(sys.argv) >= 3 and sys.argv[1] != "--debug": #Run this program with error handling
	print("Princess Cadence mode... (normal)") # Where's 'Shining Armour' when you need him?
	try:
		format = 's8' # signed 8 bit as default
		signed = True # singed as default
		bits = 8 # 8 bit as default
		endian = "little" # little endian is usually the default
		
		if len(sys.argv) == 4: # detect format argument
			format = sys.argv[3] # define format if argument exists
			print("using \"" + sys.argv[3] + "\" format.")
		else:
			print("Using default format (u8)")
		
		if "s" in format: # are we signed?
			signed = True
		if "u" in format: # are we unsigned?
			signed = False
		
		if "8" in format: # are we 8-bit?
			bits = 8
		if "16" in format: # are we 16-bit?
			bits = 16
		
		if "le" in format: # are we little-endian?
			endian = "little"
		if "be" in format: # are we big-endian?
			endian = "big"
		
		startplayin(sys.argv[1], sys.argv[2], bits, signed, endian)
	except KeyboardInterrupt as error:
		sys.stderr.write(repr(error))
		print(' ')
		print('Keyboard Interrupt Detected. Halting SER-PDM NOW!')
	except  ValueError as error:
		ser = serial.Serial()
		sys.stderr.write("ERROR: Either invalid baud rate, or internal error. ")
		print("Try a supported baud rate, such as the following:")
		print(ser.BAUDRATES) # Fluttershy is Best Pony!
		print(""".
There may be others, but those are all I can list.
If you can use a valid baud rate, it would be 20% cooler.

If you're still stuck, try calling for --help, or debug this by using the '--debug' argument.""")
		sys.stderr.write('ERROR: ' + repr(error))
		print(' ')
	except Exception as error: #I just don't know what went wrong!
		print("Some error has occured. If you're stuck, try: usbsersnd --help")
		sys.stderr.write('ERROR: ' + repr(error))
		print(' ')

if len(sys.argv) >= 4 and sys.argv[1] == "--debug": # Run this program in debug mode (no error handling)
	print("WARNING: Queen Chrysalis mode! (--debug)") # HAY, I thought I said 'NO PONIES ALLOWED!'... Oh wait, she's a changeling... Never mind...
	
	format = 's8' # signed figure-8 snake-bitten toenail as default
	signed = True # singed contract as default
	bits = 8 # 2-bit 386-SX computer as default

	endian = "little" # My little endian, I used to wonder what bit-order it could be...
	if len(sys.argv) == 5: # Until you detected the format with me, big argument...
		format = sys.argv[4] # tonnes of defined formats, when argument existance made my syntax wrong...
		print("using \"" + sys.argv[4] + "\" format.") # Sharing sys.argv[4] , it's an easy feat...
	else:
		print("Using default format (s8)") # and default format (s8) makes it all complete... yeah, you get the point...
	
	if "s" in format: # Has the python been signed?
		signed = True
	if "u" in format: # has the rattlesnake NOT been signed?
		signed = False
	if "8" in format: # are we an 8-bit NES?
		bits = 8
	if "16" in format: # are we a 16-bit Super Nintendo?
		bits = 16
	if "le" in format: # are we a My Little Endian?
		endian = "little"
	if "be" in format: # are we a big pony?
		endian = "big"
	
	#----- SPECIAL DEBUG CODE -----# 0xB16B00B5
	print(" ")
	print("Format string parsing debug:")
	if signed == 1:
		print("signed")
	if signed == 0:
		print("unsigned")
	print(str(bits) + " bit")
	print(endian + " endian")
	#----    END DEBUG CODE   -----# 0x0B00B135. OH YEAH, MR. KRABS... AHHHAHHAHHHHHHHAHHHAHHHAHHAHHAHHHAHHHHHHHHHHHH!
	
	startplayin(sys.argv[2], sys.argv[3], bits, signed, endian) # Let's start playin' this 5h1t!

if len(sys.argv) == 2 and sys.argv[1] == base64.b64decode("LS1TSDFaQlIw"): # SSHHHH!!! IT'S A S3cReT!!!!! 
	print(base64.b64decode("IF9fX19fX19fX19fX19fX18NCnwgIF8gICAgICAgICBfICAgfA0KfCB8XyAgfF98IHwgIC8gICB8DQp8ICBffCB8IHwgfCAvXyAgIHwNCnwgIF8gICBfICAgICAgX18gfA0KfCB8Xy8gfF98ICAqIHwvfCB8DQp8IHxfXCB8IFwgKiAgfF98IHwNCnxfX19fX19fX19fX19fX19ffA0KDQpJZiB5b3UncmUgcmVhZGluZyB0aGlzLCB0aGVuIENPTkdSQURVTEFUSU9OUyEgWW91IGhhdmUgd29uIGEgZnJlZSB0aWNrZXQgdG8gRXF1ZXN0cmlhISBBbGwgeW91IG5lZWQgdG8gZG8gdG8gcmVjZWl2ZSBpdCBpcyB0byBwZXJmb3JtIHRoZSBmb2xsb3dpbmcgcml0dWFsLCBzdGVwIGJ5IHN0ZXA6DQoNCiogR28gdG8geW91J3JlIGxvY2FsIGNvbnZlbmllbmNlIHN0b3JlLCBhbmQgYnV5OiBzb21lIGJsZWFjaCwgYSBwaWVjZSBvZiBNTFAgbWVyY2hhbmRpc2UsIHNvbWUgRG9yaXRvcywgYSBib3R0bGUgb2YgTW91bnRhaW4gRGV3IGFuZCBhcyBtdWNoIGFsY29ob2wgdG8gZ2V0IHlvdSBkcnVuay4NCitUaGUgYWxjb2hvbCBtYXkgYmUgYW55dGhpbmcgZnJvbSB2b2RrYSB0byBjb29raW5nIHdpbmUgb3IgbWV0aHlsYXRlZCBzcGlyaXRzLiBUaGUgbW9yZSBwb3RlbnQgdGhlIGFsY29ob2wsIHRoZSBiZXR0ZXIuIEdhc29saW5lIG9yIHBldHJvbCB3aWxsIGFsc28gd29yaywgc28geW91IG1heSB3YW50IHRvIGNhcnJ5IGFuIG9sZCBqZXJyeSBjYW4gZnVsbCBvZiB0aGUgc3R1ZmYuDQoqIGdvIHRvIHlvbydyZSBuZWFyZXN0IHJhaWx3YXkuIE1ha2Ugc3VyZSB0aGF0IGl0IGlzIHN0aWxsIGJlaW5nIHVzZWQuIEFiYW5kb25lZCBvciBkaXNjb250aW51ZWQgcmFpbHdheXMgd2lsbCBub3Qgd29yay4NCiogUHV0IHlvdXIgTUxQIG1lcmNoYW5kaXNlIG9uIHRoZSByYWlsd2F5IHRyYWNrDQoqIFdhbGsgMTAgbWV0ZXJzIGRvd24gdGhlIHJhaWx3YXkgdHJhY2ssIGFuZCBwbGFjZSB5b3VyIERvcml0b3MgYW5kIE1vdW50YWluIERldyBvbnRvIHRoZSByYWlsd2F5IHRyYWNrDQoqIFdhbGsgNSBtZXRlcnMgdG93YXJkcyB3aGVyZSB5b3UgcGxhY2VkIGRvd24geW91ciBNTFAgbWVyY2gNCiogU2l0IG9uIHRoZSByYWlsd2F5IHRyYWNrDQoqIERyaW5rIGFsbCBvZiB5b3VyIGFsY29ob2wgYW5kIG90aGVyIGludG94aWNhbnRzLiBZb3UgbWF5IHRha2UgeW91ciB0aW1lIGlmIHlvdSBjYW4ndCBoYW5kbGUgYWxsIHRoYXQgc3R1ZmYuIERPIE5PVCBMRUFWRSBUSEFUIFNQT1QhIElmIHlvdSBuZWVkIHRvIHVyaW5hdGUgb3IgZGVmYWNhdGUsIHlvdSBtYXkgc3RhbmQgdXAgb3Igc3F1YXQsIGFuZCBkbyB5b3VyIGJ1c2luZXNzIHdpdGhpbiBhIDUgbWV0ZXJzLiBETyBOT1QgTU9WRSBCRVlPTkQgVEhFIFJBSUxTLiBTVEFZIEJFVFdFRU4gVEhFIFJBSUxTIEFUIEFMTCBUSU1FUyENCiogV2FpdCB1cCB0byAyNCBob3VycyBmb3IgeW91ciB0cmFpbiB0byBhcnJpdmUuIFlvdSBtYXkgcGFzcyBvdXQgaWYgeW91IHdpc2guIFRoZSB0cmFpbiB3aWxsIHdha2UgeW91IHVwLiBJZiB0aGF0IGRvZXNuJ3Qgd2FrZSB5b3UsIHRoZSBjcmV3IG9uIHRoZSB0cmFpbiB3aWxsIGNhcnJ5IHlvdSBpbi4NCiogQW5kIGFub3RoZXIgdHdvIGhvdXJzIG9uIHRoZSB0cmFpbiwgYW5kIHlvdSB3aWxsIGFycml2ZSBpbiBFcXVlc3RyaWEuIEhBVkUgRlVOIQ0KDQpJZiB5b3UgUkVBTExZIHRoaW5rIGknbSBzZXJpb3VzIGFib3V0IHRoZSBhYm92ZSwgdGhlbiBpdCdzIHByb2JhYmx5IHRoZSBiZXN0IGludGVyZXN0IG9mIHNvY2lldHkgZm9yIHlvdSB0byBwcm9jZWVkIHdpdGggZG9pbmcgdGhlIGFib3ZlLg0KQ29uc2lkZXIgdGhpcyBhIHN0dXBpZGl0eSB0ZXN0LiBOb3QgZXZlbiB0aGUgbW9zdCBoYXJkY29yZSBicm9uaWVzIGluIGV4aXN0YW5jZSB3b3VsZCBldmVyIHRha2UgdGhhdCB0ZXh0IHNlcmlvdXNseS4NCg0KRm9yIG1vcmUgaW5mb3JtYXRpb24gYWJvdXQgd2h5IHRoYXQgaXNuJ3Qgc3VjaCBhIGdvb2QgaWRlYSwgcGxlYXNlIHdhdGNoIHRoaXMgdmlkZW86DQpodHRwczovL3lvdXR1LmJlL0lKTlIyRXBTMGp3DQoNCkkgbWVhbiBzZXJpb3VzbHkuIElmIHlvdSBkb24ndCB3YW4ndCB0byBiZSBydW4gb3ZlciBieSBhIFRob21hcyB0aGUgVGFuayBFbmdpbmUsIERPTidUIExJRSBPTiBUSEUgRkFSS0lOJyBSQUlMV0FZIFRSQUNLUyEhIQ0K")) # 34573R 3665 4 7|-|3 \/\/1|\|!!!

try:
	if len(sys.argv) <= 2 and sys.argv[1] != base64.b64decode("LS1TSDFaQlIw") or len(sys.argv) > 5: #we need to send an SOS. This ship is sinking! Canterlot is under attack! We can't figure out what you mean by those arguments!
		help()
except: # I just don't know what went wrong, but we need to call help anyway, so:
	print("Uh, oh. You forgot the mandatory command line arguments. We don't know what to do. Calling for help...") # D3rpy h00ves waS HeRe, B - COS(ERROR)
	help() # Anything I can do to help?


# If you read through all these comments (and figured out the easter egg), you must have WAAAY too much time on your hands. Now go play Darude - Sandstorm (or some vaporwave) through a serial port, you losers! HA HA HAAH!!!
# The reason why I make so many comments, is because the compiler/interpreter continues not to give a shit about them.

