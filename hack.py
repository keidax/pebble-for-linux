#! /usr/bin/env python

import os
import sys
import select
import subprocess
from subprocess import CalledProcessError
from pebble import pebble
from evdev import UInput, ecodes as e 
from time import sleep
import dbus
from dbus.mainloop.glib import DBusGMainLoop

media_manager = None
peb = None

pebbles = ['00:17:e9:4a:64:91']

def media_endpoint(endpoint, resp):
	global media_manager

	if media_manager == None:
		setup_media_connection()

	if resp == 'PLAYPAUSE':
		playpause()
	elif resp == 'NEXT':
		nextsong()
	elif resp == 'PREVIOUS':
		previoussong()
	else:
		print "unknown message: " + resp

	sleep(1) # Sleep for a bit, so media player has a chance to update before we query metadata again

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

def setup_media_connection():
	global media_manager

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	# os.popen("nuvolaplayer") # Start music player

	bus = dbus.SessionBus()
	proxy = bus.get_object('org.mpris.MediaPlayer2.nuvolaplayer', '/org/mpris/MediaPlayer2')
	media_manager = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')

def playpause(): os.system("xdotool key XF86AudioPlay")

def nextsong(): os.system("xdotool key XF86AudioNext")

def previoussong(): os.system("xdotool key XF86AudioPrev")

def setup_pebble(addr):
	global peb

	peb = pebble.Pebble(id = addr)
	peb.set_print_pbl_logs(True) # Necessary to avoid a crash
	peb.connect_via_lightblue()
	peb.register_endpoint("MUSIC_CONTROL", media_endpoint)
	print "Connected to Pebble!"

def main():
	global peb, pebbles

	device_found = False;
	device = ''

	with open(os.devnull, "w") as fnull:
		while not device_found:
			for device in pebbles:
				try:
					subprocess.check_call(["sudo","/usr/bin/l2ping", "-c1", device], stdout=fnull)
					device_found = True
					print "Found Pebble " + device
					break;
				except CalledProcessError, e:
					sleep(1)

	setup_pebble(device)

	results = []

	print "Enter 'q' to exit: "
	try:
		last_avg = -100
		avg = 0
		while peb._alive:
			# This will keep looping until the user presses enter
			# Ugly but it gets the job done
			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
				line = raw_input()
				if line == 'q':
					peb.disconnect()
					break
			sleep(.25)
			try:
				rssi = subprocess.check_output(["hcitool", "rssi", "00:17:e9:4a:64:91"])
				results.append(int(rssi[19:]))
				# print rssi[19:],
			except Exception, e:
				print e

			if len(results) > 10:
				results = results[-10:]

			if len(results) == 0:
				continue;
			elif len(results) < 10 :
				avg = sum(results) / float(len(results))
			else:
				avg = sum(results[5:10]) / float(len(results[5:10]))

			if avg != last_avg:
				print "Distance: %.1f" % avg
			last_avg = avg

			if avg > -2:
					os.system("pkill i3lock")
			else:
					os.system("xautolock -locknow")

		peb.disconnect()
	except:
		peb.disconnect()

if __name__ == '__main__':
	sys.exit(main())

