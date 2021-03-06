#!/usr/bin/env python

# This file provides a simple utility to get the task parameters 
# from the meta-data server. The data is set by the boot process

# import requests
import json
import sys
import ast
import subprocess
import signal
import time
# import ceilometerFuncs as util
import threading
from random import randint
import random



# keystoneAddress = "10.0.4.3"
# ceilometerAddress = "10.0.4.3"
# meterName = 'missedDeadlines'
INITIAL_INTERVAL = 5

currentTimer = threading.Timer(INITIAL_INTERVAL,None)
exitEvent = threading.Event()
taskObjs = []
applicationModes = []
applicationIndex = 0
preious_mode = 0
glb_duration = 5
mode2iter = []

# # ***** Get resource ID of this VM *****
# myUUID = util.getInstanceUUID()
# meterName = meterName + "_" + myUUID

def kill_tasks():
	for index,item in enumerate(taskObjs):
		item.kill()	

def handleSIGINT(signal, frame):
	kill_tasks()
	sys.exit(0)

signal.signal(signal.SIGINT, handleSIGINT)


def changeTask():
	global applicationIndex,preious_mode, glb_duration, mode2iter
	# Report value
	# Authenticate
	# myToken = util.getKeystoneTokenV3(keystoneAddress)


	print "Changing Taskset"

# 	# Stop old tasks
	while True:
	# for x in xrange(0,len(applicationModes) ):
		kill_tasks()
		time.sleep(2)
		changeSched('Linux')


		if applicationIndex >= len(applicationModes):
			print "Done with application!"
			exitEvent.set()
			sys.exit(0)
		applicationModes_j = json.loads(applicationModes[applicationIndex])
		print type(applicationModes_j)
		appName = applicationModes_j["Application name"]
		mode = applicationModes_j["Mode name"]
		periods = applicationModes_j["Periods"][0]
		execTime = applicationModes_j["ExecTime"][0]
		random.seed( randint(0,199999))
		duration = randint(10,25)
		glb_duration = duration
		iter_size = mode2iter[int(mode)-1]
		applicationIndex = applicationIndex + 1
		if applicationIndex >= len(applicationModes):
			applicationIndex = 0
		print '\t',mode,'\t',appName
		if preious_mode == 0:
			with open('/dev/shm/rtOpenstack/mode','w') as j_file:
			#with open('/dev/shm/rtOpenstack/'+appName,'w') as j_file:
				json.dump(applicationModes_j,j_file,indent=2)
			preious_mode = int(mode)
		elif preious_mode != int(mode):
			with open('/dev/shm/rtOpenstack/mode','w') as j_file:
			#with open('/dev/shm/rtOpenstack/'+appName,'w') as j_file:
				json.dump(applicationModes_j,j_file,indent=2)
			preious_mode = int(mode)			

	# 	# Report back to nova
		# totalMissed = 1
		# newTaskPayload = {}
		# newTaskPayload['type'] = 'tasksetChange'
		# newTaskPayload['metaData'] = json.dumps(mode)
		# util.addSample(address=ceilometerAddress,meter=meterName,
		# 	value=str(totalMissed),\
		# 	resource_id=myUUID,token=myToken, metaData=newTaskPayload)


	# 	# Start new tasks
		time.sleep(9)
		startTasks(execTime,periods,duration,mode,appName,iter_size)

# 	# Start next timer
	# currentTimer = threading.Timer(mode,changeTask)
	# currentTimer.start()


# def getTaskMeta():
# 	url = 'http://169.254.169.254/openstack/latest/meta_data.json'
# 	r = requests.get(url)
# 	return ast.literal_eval(r.json()['meta']['taskset'].strip('"'))

# def getInstanceUUID():
# 	url = 'http://169.254.169.254/openstack/latest/meta_data.json'
# 	r = requests.get(url)

# 	# print json.dumps(r.json(), sort_keys=True,indent=4, \
# 		# separators=(',', ': '))
# 	# print r.json()['uuid']
# 	return r.json()['uuid']

# def createTaskInfo(UUID,taskMeta):
# 	tasks = {}
# 	for index,task in enumerate(taskMeta[0]):
# 		taskName = UUID + '_' + str(index)
# 		tasks[taskName] = [	str(taskMeta[0][index]),
# 							str(taskMeta[1][index]),
# 							str(taskMeta[2][index])]
# 	return tasks

def changeSched(sched):
	subprocess.call(['/root/liblitmus/setsched',sched])
    
def startTasks(execTime,periods,duration,mode,appName,iter_size):
	changeSched('GSN-EDF')
	#argv  1. wcet(ms) 2. period(ms) 3. duration(s) 4. mode 5. appName 6.iter
	global glb_duration
	for taskID in xrange(0,1):
			# myoutput = open(str(mode), 'w')
			taskObjs.append( subprocess.Popen(["./myapp",
				str(execTime),
				str(periods),
				str(duration),
				mode,
				appName,
				iter_size,
				'&'
				])#,stdout=myoutput)
			)
	time.sleep(3)
	subprocess.call(["/root/liblitmus/release_ts"])
	time.sleep(4)
	time.sleep(glb_duration)


def find_iter_for_modes():
	global mode2iter
	with open("result") as inFile:
		inLines = inFile.readlines()
		for lines in inLines:
			if len(lines.split())==2:
				mode2iter.append(lines.split()[1])
	print mode2iter

if __name__ == "__main__":
	# If passed a file, we need to follow the applications
	if len(sys.argv) == 2:
		subprocess.call("make myapp",shell=True)
		subprocess.call("mkdir -p /dev/shm/rtOpenstack",shell=True)
		subprocess.call("rm /dev/shm/rtOpenstack/*",shell=True)
		
		find_iter_for_modes()

		
		with open(sys.argv[1]) as inFile:
			inLines = inFile.readlines()

			for lines in inLines:
				try:
					if lines.split()[0]!="#":
						data={}
						data["Application name"]=lines.split()[0]
						data["Mode name"]=lines.split()[1]
						data["Periods"]=[int(lines.split()[3])]
						data["ExecTime"]=[int(lines.split()[2])]

						applicationModes.append(json.dumps(data))

					
				except:
					pass
	print applicationModes
					#applicationModes.append(json.loads(lines.strip()))
	# 			except:
	# 				# Probably due to malformed file, just ignore
	# 				pass
	# 			# tempJSON = json.loads(lines.strip())
	# 			# print tempJSON
	# 			# pprint.pprint(tempJSON)

	# # print getInstanceUUID()
	# # print getTaskMeta()
	# # print createTaskInfo(getInstanceUUID(),getTaskMeta())
	# applicationModes.insert(0,{'duration':5,'taskset':getTaskMeta()})
	# applicationIndex = 0

	# print applicationModes

	changeTask()

	# # Waits for input
	# print('Press Ctrl+C to quit (Kills tasks if still running)')
	# exitEvent.wait()
	# # signal.pause()

