import time
import json
from random import randint
import random


# while 1:

modes = [    [ [2500,10000],[2500,10000], [2500,10000] ] , [ [5000,10000],[5000,10000], [5000,10000] ] , [ [7500,10000],[7500,10000], [7500,10000] ] ]
modes = [    [ [400],[400], [400] ] , [ [399,398],[400,400], [400,400] ] , [ [400,400,200],[400,400,400], [400,400,400]]  ]



random.seed( randint(0,199999))
period1 =  randint(5,7)
random.seed(randint(0,199999))
period2 =  randint(6,8)
random.seed(randint(0,1929999))
period3 =  randint(9,10)
print str(period1) + ' ' + str(period2)


vm1_cnt = 0
vm2_cnt = 0
vm3_cnt = 0
vm_mode = [[],[],[]]
vm_mode_name = [0,0,0]

while 1:
	vm1_cnt = vm1_cnt%period1
	vm2_cnt = vm2_cnt%period2
	vm3_cnt = vm3_cnt%period3
	if(vm1_cnt==0):
		a= randint(0,2)
		vm_mode[0] = modes[a]
		vm_mode_name[0]=a
	if(vm2_cnt==0):
		a= randint(0,2)
		vm_mode[1] = modes[a]
		vm_mode_name[1]=a
	if(vm3_cnt==0):
		a= randint(0,2)
		vm_mode[2] = modes[a]
		vm_mode_name[2]=a
	data={}
	t0 = time.time()
	with open('hostMonitorTest2','r') as j_file:
		data = json.load(j_file)
		i=0
		for vm_id in data.keys():
			data[vm_id]["VCPUs"] = vm_mode[i]
			data[vm_id]["DeadlinesMissed"] += randint(0,10)
			data[vm_id]["CurrentMode"] = str(vm_mode_name[i]+1)
			i+=1

		# j_file.seek(0)
	with open('hostMonitorTest2','w') as j_file:
		json.dump(data,j_file,indent=4)
	t1 = time.time()
	total = t1-t0
	print 'read time:' + str(total) + ' '+str(vm1_cnt) + ' ' + str(vm2_cnt) + ' '+ str(vm3_cnt) + ' '+str(period1) +' '+str(period2) + ' ' + str(period3)
	vm1_cnt+=1
	vm2_cnt+=1
	vm3_cnt+=1

	time.sleep(1)