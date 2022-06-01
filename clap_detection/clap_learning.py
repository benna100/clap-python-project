#!/usr/bin/python
import pyaudio
import sys
import thread
import time
import numpy as np
import pylab as pl
import json

from time import sleep
from array import array
from sys import argv
from sklearn import svm
from sklearn.externals import joblib

bool_is_playing = False
clap_data_array = []


clap = 0
wait = 1
flag = 0
pin = 24
splits = 64
number_of_claps_needed = 50
training_clap_number = 0
exitFlag = False
participants_array= []
number_of_participants = 0
current_participant_number = 0
current_participant_name = ""

#check if the file is there. If not, initialize an empty dict
try:
	with open('clap_names_data.json') as data_file:    
	    names_and_data = json.load(data_file)
	print 'tr'
except:
	print 'exc'
	names_and_data = {}

#names_and_data = {}


def getInitialInformation():
	global participants_array
	global number_of_participants
	prompt = '> '
	print '*******----*******'
	#sleep(1)
	print 'Hey and welcome to Benjamin\'s automated clap learning facility'
	#sleep(1)
	print 'Please press the number of participants:'
	number_of_participants = raw_input(prompt)
	for i in range(int(number_of_participants)):
		print 'Write the name of the ' + str((i + 1)) + '. clapper then press enter:'
		name = raw_input(prompt)
		participants_array.append(name)
	
	print '*******----*******'
	


getInitialInformation()



def waitForClaps(threadName):
	global clap
	global training_clap_number
	global flag
	global wait
	global pin
	training_clap_number += 1

	sleep(0.3)
	clap = 0





def testThread(threadName, pData):
	global current_participant_name
	global training_clap_number
	global clap
	global current_participant_number
	global bool_initial_print

	clap = 1
	#sound_data_dict = {'name': participants_array[current_participant_number], 'data': sound_data}
	
	p = pData[:512]
	#print len(p)
	#print p[125]
	#p_array = array('h', p)

	#test = np.histogram(p, 20)
	p_split_into_bins = np.split(p, splits)
	p_split_into_bins_avg = [np.mean(x) for x in p_split_into_bins]
	#print test2


	names_and_data[current_participant_name].append(p_split_into_bins_avg)

	p_array_with_dependent_var = np.append(p_split_into_bins_avg, int(current_participant_number))

	
	clap_data_array.append(p_array_with_dependent_var)



	#pl.plot(f, p)
	#pl.xlabel("Frequency(Hz)")
	#pl.ylabel("Power(dB)")
	#pl.show()
	#print training_clap_number, number_of_claps_needed
	print 'Now you only need ' + str((number_of_claps_needed - (training_clap_number + 1))) + ' claps'
	#thread.start_new_thread( waitForClaps, ("waitThread",))
	if(training_clap_number == (number_of_claps_needed - 1)):
		print current_participant_name + ', you are now done'
		bool_initial_print = False
		current_participant_number += 1
		training_clap_number = 0

	training_clap_number += 1

	sleep(0.5)
	clap = 0


def main():
	global number_of_participants
	global training_clap_number
	global participants_array
	global clap
	global flag
	global pin
	global clap_data_array
	global names_and_data
	global current_participant_name
	global current_participant_number
	global bool_initial_print


	chunk = 8192
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 48000
	threshold = 9000
	max_value = 0

	pyAudioInput = pyaudio.PyAudio()
	stream = pyAudioInput.open(format=FORMAT,
					channels=CHANNELS, 
					rate=RATE, 
					input=True,
					output=True,
					frames_per_buffer=chunk)



	bool_initial_print = False
	print number_of_participants



	try:
		while True:
			if(str(current_participant_number) != str(number_of_participants)):
				if(bool_initial_print == False):
					current_participant_name = participants_array[current_participant_number]
					if(current_participant_name not in names_and_data):
						names_and_data[current_participant_name] = []
					print current_participant_name + ', please clap ' + str(number_of_claps_needed) + ' times'
					bool_initial_print = True
				data = stream.read(chunk)

				as_ints = array('h', data)
				max_value = max(as_ints)

				channels = 2.0
				t = np.arange(len(as_ints)) * channels / RATE
				p = 20 * np.log10(np.abs(np.fft.rfft(as_ints)))
				f = np.linspace(0, RATE / channels, len(p))

				if(clap == 0):
					if (max_value > threshold):
						thread.start_new_thread( testThread, ("waitThread", p))		
			else:
				break
	except (KeyboardInterrupt, SystemExit):
		print "\rExiting"
		stream.stop_stream()
		stream.close()
		p.terminate()


	#print names_and_data

	# from json file construct the features set for learning
	total_data_array = []
	participant_number = 0
	for name in names_and_data.keys():
		for data in names_and_data[name]:
			p_array_with_dependent_var = np.append(data, int(participant_number))
			total_data_array.append(p_array_with_dependent_var)
		participant_number += 1

	sound_data_features = np.array(total_data_array)

	print 'Now for the learning'


	#sound_data_features = np.array(clap_data_array)
	#print sound_data_features
	
	#print sound_data_features
	#print np.delete(sound_data_features, -1, 1), sound_data_features[:, -1]
	clf = svm.SVC(gamma=0.001, C=100.)
	clf.fit(np.delete(sound_data_features, -1, 1), sound_data_features[:, -1])
	joblib.dump(clf, 'classifier/classifier.pkl')

	with open('clap_names_data.json', 'w') as outfile:
		json.dump(names_and_data, outfile)

if __name__ == '__main__':
	main()
