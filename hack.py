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

def coolfunc(endpoint, resp):

	if resp == 'PLAYPAUSE':
		playpause()
	elif resp == 'NEXT':
		nextsong()
	elif resp == 'PREVIOUS':
		previoussong()
	else:
		print "unknown message: " + resp

	sleep(.5)

	metadata = media_manager.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
	# peb.set_nowplaying_metadata(metadata['xesam:title'], metadata['xesam:album'], metadata['xesam:artist'][0])
	# print isinstance(str(metadata['xesam:title']), str), isinstance(str(metadata['xesam:album']), str), isinstance(str(metadata['xesam:artist'][0]), str)
	# print str(metadata['xesam:title']), str(metadata['xesam:album']), str(metadata['xesam:artist'][0])
	peb.set_nowplaying_metadata(str(metadata['xesam:title']), str(metadata['xesam:album']), str(metadata['xesam:artist'][0]))

def playpause():
	os.system("xdotool key XF86AudioPlay")

def nextsong():
	os.system("xdotool key XF86AudioNext")

def previoussong():
	os.system("xdotool key XF86AudioPrev")

def randfunc2(arg1, arg2, arg3):
	print "hi!"

def main():
	global media_manager, peb

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SessionBus()
	proxy = bus.get_object('org.mpris.MediaPlayer2.nuvolaplayer', '/org/mpris/MediaPlayer2')
	media_manager = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')

	proxy.connect_to_signal('PropertiesChanged', randfunc2)

	# bus.add_signal_receiver(randfunc2, bus_name="org.mpris.MediaPlayer2.nuvolaplayer",
	#  dbus_interface = "org.freedesktop.DBus.Properties", signal_name="PropertiesChanged")

	peb = pebble.Pebble(id = '00:17:e9:4a:64:91')
	peb.set_print_pbl_logs(True) # Necessary to avoid a crash
	peb.connect_via_lightblue()
	print "connected!"
	peb.register_endpoint("MUSIC_CONTROL", coolfunc)
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
