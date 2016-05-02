import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from pylab import *
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import RadioButtons,Button
import json
from threading import Thread, Lock
import pysftp


if len(sys.argv) < 2:
  print "please input vm's ip"
  sys.exit(0)

vm_ip = sys.argv[1]
vm_file_source = '/root/rtOpenstack/hostMonitorTest'


font = [{'family': 'serif',
        'color':  'c',
        'weight': 'heavy',
        },
        {'family': 'serif',
        'color':  'm',
        'weight': 'heavy',
        },
        {'family': 'serif',
        'color':  'g',
        'weight': 'heavy',
        },
        {'family': 'serif',
        'color':  'b',
        'weight': 'heavy',
        },
        {'family': 'serif',
        'color':  'r',
        'weight': 'heavy',
        }]

do_reset =1
do_pause =0
fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)
j_indi_util = []
time_cnt = 0
xaxis=[]
j_indi_util.append([])
j_indi_util.append([])
j_indi_util.append([])
total_util = []
static_util = []


deadline_misses=[]
deadline_misses.append([])
deadline_misses.append([])
deadline_misses.append([])
total_dm =[]
xaxis2 = []
mode_change = []
mode_change.append([])
mode_change.append([])    
mode_change.append([])
pre_mode = []
pre_mode.append(0)
pre_mode.append(0)
pre_mode.append(0)


# app1, app2, total, static
toshow = [1,1,1,1]

def animate(i):

    # pullData = open("s.txt","r").read()
    # dataArray = pullData.split('\n')
    # xar = []
    # yar = []
    # y2 =[]
    # for eachLine in dataArray:
    #     if len(eachLine)>1:
    #         x,y = eachLine.split(',')
    #         xar.append(int(x))
    #         yar.append(int(y))
    #         y2.append(int(y)+2)

    # ax1.clear()
    # ax1.plot(xar,yar)
    # ax1.plot(xar,y2)
    global mode_change, pre_mode, font,toshow,j_indi_util, time_cnt,xaxis,total_util,static_util, do_reset,do_pause,vm_file_source,vm_ip

    st = ['app1','app2','Total VCPUs util','Static VCPUs util']
    indi_util = []
    # total_util = []
    at_first_line = 1
    apps_num = 0
    xcnt = 0
    time_cnt = 1

    xaxis.append(len(j_indi_util[0]))
    time_cnt+=1

    t0 = time.time()
    with pysftp.Connection(vm_ip, username='root', password='anch0rs') as sftp:
      sftp.get(vm_file_source, 'hostMonitorTest2')    
    with open('hostMonitorTest2') as j_file:
      data = json.load(j_file)
      i=0

      
      for val in data.keys():
        apps_num+=1

        j=0
        util = 0
        for vcpus in xrange(0,len(data[val]["VCPUs"][0])):
          util+=float(data[val]["VCPUs"][0][vcpus])/float(data[val]["VCPUs"][1][vcpus])
          j+=1
        j_indi_util[i].append(util)
        len_so_far = len(j_indi_util[0])
        
        st[i] = data[val]["ApplicationName"] + "\nmode:" + str(data[val]["CurrentMode"]) + '\nVCPUs util:'+str(j_indi_util[i][len_so_far-1])
        if(len(j_indi_util[0])==1):
          mode_change[i].append(int(data[val]["CurrentMode"]))
        elif(pre_mode[i] != data[val]["CurrentMode"] ):
          mode_change[i].append(int(pre_mode[i])+10*int(data[val]["CurrentMode"]))
        else:
          mode_change[i].append(0)

        pre_mode[i] = data[val]["CurrentMode"]  
        i+=1

    # print mode_change
    
    # print j_indi_util
    # print xaxis
    # print time_cnt
    one_total_util = 0
    total_util.append(j_indi_util[0][len_so_far-1]+j_indi_util[1][len_so_far-1]  )
    static_util.append(6)
    st[2] += "\n"+str(total_util[len(total_util)-1])
    st[3] += "\n"+str(static_util[len(static_util)-1])
    # print total_util


          
    t1 = time.time()
    total = t1-t0
    print 'read time:' + str(total)
    # print total_util
    if(do_pause):
      if do_reset:
        ax1.clear()
      return
    ax1.clear()
    if(toshow[2]):
      ax1.plot(xaxis,total_util,'--b')
    if(toshow[3]):
      ax1.plot(xaxis,static_util,'--r')
    color = [ 'c','m','g']

    for app in range(0,apps_num):
      if(toshow[app]):
        ax1.plot(xaxis,j_indi_util[app],color[app])
    
    # ax1.set_legend(['total'])
    ax1.set_xlim([0,150])
    ax1.set_ylim([0,8])

    ax1.set_xlabel('time')
    ax1.set_ylabel('VCPUS')
    # ax1.legend(['total_util'])#,'0','1','2','3'])
    ax1.text(40, 25, 'total util', style='italic',bbox={'facecolor':'blue', 'alpha':0.5, 'pad':10})
    if len_so_far==150 or do_reset:
      j_indi_util =[]
      j_indi_util.append([])
      j_indi_util.append([])  
      j_indi_util.append([])    
      mode_change = []
      mode_change.append([])
      mode_change.append([])    
      mode_change.append([])
      pre_mode = []
      pre_mode.append(0)
      pre_mode.append(0)
      pre_mode.append(0)
      xaxis=[]  
      total_util=[]
      static_util=[]
      if do_reset > 0:
        do_reset-=1
    # st = ['app1','app2','total_util','static']
    for k in range(0,len(toshow)):
      if(toshow[k]):
        ax1.text(-23,2+float(k)*1.5,st[k],fontdict=font[k])
        if(k<=1):
          for i in range(0,len(mode_change[0])):
            if(mode_change[k][i]>10):
              # ax1.text(i,1+float(k)*0.5,str(mode_change[k][i]%10)+' to '+ str(mode_change[k][i]/10),fontdict=font[k])
              ax1.text(i,float(j_indi_util[k][i]),"mode " +str(mode_change[k][i]%10)+' to '+ str(mode_change[k][i]/10),fontdict=font[k])


        


    
ani=animation.FuncAnimation(fig, animate, interval=500)

rax = plt.axes([0.9, 0.6, 0.10, 0.15])
rax2 = plt.axes([0.9, 0.8, 0.10, 0.15])
check = CheckButtons(rax, ('show app1','show app2','show static','show total'), (True,True,True,True))
radio = RadioButtons(rax2, ('Dynamic','Static'))

def dyno_static(label):
  if(label=="Dynamic"):
    with open('dom0_to_monitor.json','w') as j_file:
      # data = json.dumps
      json.dump({'dynamic_static':1},j_file,indent=4)

  else:
    with open('dom0_to_monitor.json','w') as j_file:
      json.dump({'dynamic_static':0},j_file,indent=4)



radio.on_clicked(dyno_static)

axcolor = 'lightgoldenrodyellow'
resetax = plt.axes([0.9, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')
def reset(event):
  global do_reset
  do_reset = 2
button.on_clicked(reset)


pausetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button2 = Button(pausetax, 'Pause', color=axcolor, hovercolor='0.975')
def pause(event):
  global do_pause
  do_pause +=1
  do_pause = do_pause %2
button2.on_clicked(pause)

i=0

def func(label):
    global font,deadline_misses,xaxis2,total_dm
    global j_indi_util, time_cnt,xaxis,total_util,static_util,mode_change

    if label == 'show app1':
      toshow[0]=(toshow[0]+1)%2
    elif label == 'show app2':
      toshow[1]=(toshow[1]+1)%2
    elif label == 'show app3':
      toshow[2]=(toshow[2]+1)%2
    elif label == 'show total':
      toshow[3]=(toshow[3]+1)%2
    elif label == 'show static':
      toshow[4]=(toshow[4]+1)%2


check.on_clicked(func)




ax2 = fig.add_subplot(2,1,2)



dl_slide_change = 0

def animate2(i):
  global toshow,font,deadline_misses,xaxis2,total_dm, do_reset, dl_slide_change,do_pause,j_indi_util,mode_change,vm_file_source,vm_ip

  apps_num = 0
  xaxis2.append(len(deadline_misses[0]))
  with pysftp.Connection(vm_ip, username='root', password='anch0rs') as sftp:
    sftp.get(vm_file_source, 'hostMonitorTest2')    
  with open('hostMonitorTest2') as j_file:
    data = json.load(j_file)
    i=0
    tmp_total_dm = 0
    for val in data.keys():
      apps_num+=1
      tmp_total_dm += int(data[val]["DeadlinesMissed"]) 
      deadline_misses[i].append(int(data[val]["DeadlinesMissed"]) )
      i+=1
    total_dm.append(tmp_total_dm)
  if(do_pause):
    if do_reset:
      ax2.clear()
    return
  ax2.clear()
  if(toshow[2]):
    ax2.plot(xaxis2,total_dm,'--b')
  color = [ 'c','m','g']
  # print "deadline_misses"
  # print deadline_misses

  # for app in range(0,apps_num):
  #   if(toshow[app]):
  #     ax2.plot(xaxis2,deadline_misses[app],color[app] ) 
  #     if(app<=2):
  #       for i in range(0,len(mode_change[0])):
  #         if(mode_change[app][i]>10):
  #           ax2.text(i,float(deadline_misses[app][i]),"mode " +str(mode_change[app][i]%10)+' to '+ str(mode_change[app][i]/10),fontdict=font[app])


  # if dl_slide_change==0:
  #   ax2.set_xlim([0,150])
  # else:
  #   ax2.set_xlim([0,dl_slide_change])
  ax2.set_xlim([0,150])
  ax2.set_ylim([0,35])

  ax2.set_xlabel('time')
  ax2.set_ylabel('Deadline misses')

  st = ['app1','app2','Total misses:'+str(total_dm[-1])]
  i=0
  for val in data.keys():
    st[i] = data[val]["ApplicationName"] + "\n Mode" + str(data[val]["CurrentMode"]) + "\n Misses:" + str(data[val]["DeadlinesMissed"])
    i+=1
  for i in range(0,len(toshow)-1):
    if(toshow[i]):
      ax2.text(-23,5.5+float(i)*8,st[i],fontdict=font[i])#,bbox=dict(facecolor='none', edgecolor='blue', pad=10.0))
  if len(deadline_misses[0])==150 or do_reset:
    deadline_misses =[]
    deadline_misses.append([])
    deadline_misses.append([])
    deadline_misses.append([])
    mode_change = []
    mode_change.append([])
    mode_change.append([])    
    mode_change.append([])
    total_dm=[]    
    xaxis2=[] 
    if do_reset > 0:
      do_reset -=1
  for app in range(0,apps_num):
    if(toshow[app]):
      ax2.plot(xaxis2,deadline_misses[app],color[app] ) 
      if(app<=1):
        for i in range(0,len(mode_change[0])):
          if(mode_change[app][i]>10):
            ax2.text(i,float(deadline_misses[app][i]),"mode " +str(mode_change[app][i]%10)+' to '+ str(mode_change[app][i]/10),fontdict=font[app])

    # global font
    # app=[0,0,0,0]
    # data = [];
    # with open('input2', 'r') as file:
    #     data = file.readlines() 
    #     for line in data:
    #         if (int(line) <= len(app) and int(line) > 0 ):
    #             app[int(line)-1]+=1

    #     ax2.clear()
  # for i in range(0,len(toshow)):
  #     ax2.text(0.4,0.65-float(i)*0.1,'app'+str(i)+' misses:'+str(app[i]),fontdict=font[i])
    # ax2.set_xticklabels([])
    # ax2.set_xticks([])
    # ax2.set_yticklabels([])
    # ax2.set_yticks([])

    # data.append(str(randint(1,5)) +'\n')
    # with open('input2', 'w') as file:
    #     file.writelines( data )







    
ani2=animation.FuncAnimation(fig, animate2, interval=500)


# mng = plt.get_current_fig_manager()
# def update(val):
#   global dl_slide_change
#   dl_slide_change = dl_slide.val
#   ax2.set_xlim([0,dl_slide.val])


# axfreq = plt.axes([0.25, 0.001, 0.65, 0.03], axisbg=axcolor)
# dl_slide = Slider(axfreq, 'Freq', 0.1, 200.0, valinit=150)
# dl_slide.on_changed(update)


# mng.full_screen_toggle()

plt.show()


# indi_util = []
# xaxis=[]
# at_first_line = 1
# apps_num = 0
# xcnt = 1
# t0 = time.time()
# with open('input') as my_file:
#     for line in my_file:
#       items = line.split()
#       xaxis.append(xcnt)
#       xcnt+=1


#       if at_first_line==1:
#         apps_num = len(items)
#         for x in range(0,len(items)):
#           indi_util.append([])
#         at_first_line = 0
#       i=0
#       for item in items:
#         indi_util[i].append(int(item))
#         i+=1

# t1 = time.time()
# total = t1-t0
# print total
# for app in range(0,apps_num):
#     print indi_util[app]
