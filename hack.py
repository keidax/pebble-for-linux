#! /usr/bin/env python

import os
import sys
import select
from pebble import pebble
from evdev import UInput, ecodes as e 
from time import sleep
import dbus
from dbus.mainloop.glib import DBusGMainLoop

global media_manager, peb

def media_endpoint(endpoint, resp):

	if resp == 'PLAYPAUSE':
		playpause()
	elif resp == 'NEXT':
		nextsong()
	elif resp == 'PREVIOUS':
		previoussong()
	else:
		print "unknown message: " + resp

	sleep(1)

	metadata = media_manager.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
	
	title = ""
	if metadata.has_key('xesam:title'):
		title = str(metadata['xesam:title'])

	album = ""
	if metadata.has_key('xesam:album'):
		album = str(metadata['xesam:album'])

	artist = ""
	if metadata.has_key('xesam:artist'):
		artist = str(metadata['xesam:artist'][0]) # Artist is returned as an array
	
	peb.set_nowplaying_metadata(title, album, artist)

def playpause():
	os.system("xdotool key XF86AudioPlay")

def nextsong():
	os.system("xdotool key XF86AudioNext")

def previoussong():
	os.system("xdotool key XF86AudioPrev")

# def randfunc2(arg1, arg2, arg3):
# 	print "hi!"

def main():
	global media_manager, peb

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SessionBus()
	proxy = bus.get_object('org.mpris.MediaPlayer2.nuvolaplayer', '/org/mpris/MediaPlayer2')
	media_manager = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')

	# proxy.connect_to_signal('PropertiesChanged', randfunc2)

	# bus.add_signal_receiver(randfunc2, bus_name="org.mpris.MediaPlayer2.nuvolaplayer",
	#  dbus_interface = "org.freedesktop.DBus.Properties", signal_name="PropertiesChanged")

	peb = pebble.Pebble(id = '00:17:e9:4a:64:91')
	peb.set_print_pbl_logs(True) # Necessary to avoid a crash
	peb.connect_via_lightblue()
	print "connected!"
	peb.register_endpoint("MUSIC_CONTROL", media_endpoint)
	# peb._reader()

	print "Press enter to exit: "
	try:

		while peb._alive:
			# This will keep looping until the user presses enter
			# Ugly but it gets the job done
			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
				line = raw_input()
				break
		peb.disconnect()
	except:
		peb.disconnect()

if __name__ == '__main__':
    sys.exit(main())
