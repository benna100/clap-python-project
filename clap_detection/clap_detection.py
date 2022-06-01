#!/usr/bin/python
import pyaudio
import sys
import thread
import numpy as np
import pylab as pl
import json

from time import sleep
from array import array
from mpd import MPDClient
from sklearn.externals import joblib
from random import randint

client = MPDClient() 
client.timeout = 1000
client.idletimeout = None
client.connect("localhost", 6600)

bool_is_playing = False
current_song_player = ""
bool_initial_clap = True
gode_albums = []
for playlist in client.listplaylists():
	playlist_split = playlist['playlist'].split('|')
	if(len(playlist_split) == 2):
		playlist_folder = playlist_split[0]
		playlist_name = playlist_split[1]
		if(playlist_folder == 'Gode albums'):
			gode_albums.append(playlist['playlist'])

#client.load('Fedt')
#client.play(0)
#print 'Fedt'
# sleep(5)
#print 'Javier'


clap = 0
wait = 1
flag = 0
pin = 24
splits = 64
actual_number_of_claps = 1
exitFlag = False
clf = joblib.load('classifier/classifier.pkl') 

with open('clap_names_data.json') as data_file:    
    clappers = json.load(data_file)
clappers = clappers.keys()


def toggle_song_play():
	global bool_is_playing	
	if(bool_is_playing == False):
		client.play(0)
		bool_is_playing = True
	else:
		client.stop()
		bool_is_playing = False


def waitForClaps(threadName):
	global clap
	global flag
	global wait
	global exitFlag
	global pin
	#global actual_number_of_claps

	#if(actual_number_of_claps == 2):
	#	toggle_song_play()

	sleep(0.5)
	clap = 0
	#actual_number_of_claps = 1


def testClap(threadName, p1):
	global splits
	global clap
	global current_song_player
	clap = 1
	print "Clapped"
	#sound_data_features = np.array(clap_data_array)
	
	sound_data = p1
	#print sound_data
	p = p1[:512]
	p_split_into_bins = np.split(p, splits)
	p_split_into_bins_avg = [np.mean(x) for x in p_split_into_bins]

	clapper_name = clappers[int(clf.predict(p_split_into_bins_avg))]
	print clapper_name
	#print clapper_name
	#print current_song_player
	if(clapper_name == 'BenjaminHughes'):
		thread.start_new_thread( playBenjaminSong, (clapper_name,) )
	#elif(clapper_name == 'Test'):
	#	thread.start_new_thread( playNannaSong, (clapper_name,) )

	current_song_player = clapper_name
			
	#pl.plot(f, p)
	#pl.xlabel("Frequency(Hz)")
	#pl.ylabel("Power(dB)")
	#pl.show()
	#actual_number_of_claps += 1
	thread.start_new_thread( waitForClaps, ("waitThread",) )

	#sleep(0.3)
	#clap = 0




def playNannaSong(clapper_name):
	global bool_initial_clap
	print 'nanna function'
	print clapper_name
	global current_song_player


	if(bool_initial_clap ==  True):
		client.clear()
		client.load('Fedt')
		client.play(10)
		bool_initial_clap = False
	else:
		if(current_song_player != clapper_name):
			client.clear()
			client.load('Fedt')
			client.play(10)
			bool_initial_clap = False
		else:
			client.stop()
			bool_initial_clap = True

	



def playBenjaminSong(clapper_name):
	global bool_initial_clap
	global current_song_player

	print clapper_name, current_song_player, bool_initial_clap

	#print (current_song_player == clapper_name)

	if(bool_initial_clap ==  True):
		client.clear()
		random_good_album_index = randint(0, len(gode_albums))
		godt_album = gode_albums[random_good_album_index]
		print godt_album
		client.load(godt_album)
		#client.load(godt_album)
		song_number = randint(0,4)
		client.play(song_number)
		bool_initial_clap = False
	else:
		print 'else'
		if(str(current_song_player) != str(clapper_name)):
			print 'if if'
			client.clear()
			client.load('Gode Albums')
			client.play(7)
			bool_initial_clap = False
		else:
			print 'if else'
			bool_initial_clap = True
			client.stop()
	


def main():
	global clap
	global flag
	global pin
	#global actual_number_of_claps

	chunk = 8192
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 48000
	threshold = 8000
	max_value = 0
	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT,
					channels=CHANNELS, 
					rate=RATE, 
					input=True,
					output=True,
					frames_per_buffer=chunk)

	try:
		print "Clap detection initialized"
		counter = 0
		while True:
			counter += 1
			data = stream.read(chunk)

			as_ints = array('h', data)
			max_value = max(as_ints)
			sound_data = np.array(as_ints)

			channels = 2.0

			t = np.arange(len(as_ints)) * channels / RATE
			p1 = 20 * np.log10(np.abs(np.fft.rfft(as_ints)))
			f = np.linspace(0, RATE / channels, len(p1))
			increment = 47.875
			start_signi_freq1 = 1200
			end_signi_freq1 = 2200
			start_signi_freq1_array_index = int(start_signi_freq1 / increment)
			end_signi_freq1_array_index = int(end_signi_freq1 / increment)
			array_significant_part1 = p1[start_signi_freq1_array_index: end_signi_freq1_array_index]
			clap_significant_freq_avg1 = np.sum(array_significant_part1) / len(array_significant_part1)


			start_signi_freq2 = 4500
			end_signi_freq2 = 5500
			start_signi_freq2_array_index = int(start_signi_freq2 / increment)
			end_signi_freq2_array_index = int(end_signi_freq2 / increment)
			array_significant_part2 = p1[start_signi_freq2_array_index: end_signi_freq2_array_index]
			clap_significant_freq_avg2 = np.sum(array_significant_part2) / len(array_significant_part2)

			#print clap_significant_freq_avg1, clap_significant_freq_avg2

			#print f[0], f[1], f[2], f[3]

			#print f[:10]
			if(clap == 0):
				#print clap_significant_freq_avg1, clap_significant_freq_avg2
				#if ((max_value > threshold) and (clap_significant_freq_avg1 > 105) and (clap_significant_freq_avg2 > 105)):
				if ((max_value > threshold)):
					thread.start_new_thread( testClap, ("waitThread", p1) )
			if exitFlag:
				sys.exit(0)



	except (KeyboardInterrupt, SystemExit):
		print "\rExiting"
		stream.stop_stream()
		stream.close()
		p.terminate()

if __name__ == '__main__':
	main()
