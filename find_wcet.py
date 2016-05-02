import sys
import subprocess



desired_wcet = float(sys.argv[1])
subprocess.call("/root/ft_tools/st-job-stats -m ./run-data/vic/*.bin > all",shell=True)
wcet = 0
with open('all', "r") as ins:
	array = []
	for line in ins:
		if(len(line.split())==9):
			this_exect = (float(line.split()[3].split(',')[0]))
			if(this_exect>wcet):
				wcet = this_exect
# print 1 if the result wcet > desired wcet
overshoot = 0
print "desired_wcet(ms):"+str(desired_wcet)+" wcet(ms):"+str(wcet)
if(wcet>desired_wcet):
	overshoot = 1
file = open("overshoot", "w")
file.write(str(overshoot))
file.close()
