#/bin/bash

KALMAN_BASE=100000
BASE=10000


function cali_kalman {

  BASE_TASK="./myapp"
  RELEASETS="/root/liblitmus/release_ts"
  ST_TRACE="/root/ft_tools/st-trace-schedule"

  SPIN_PIDS=""

  PROG="vic_kalman"
  declare -a NEW_SPIN_PIDS
  SchedNames="GSN-EDF"

  j=0
  DESIRED_WCET=$1

  kalmn_iter=$(($KALMAN_BASE + $BASE))
  while true; do

    echo "Starting st_trace"
    ${ST_TRACE} -s mk &
    ST_TRACE_PID="$!"
    echo "st_trace pid: ${ST_TRACE_PID}"
    sleep 1


    

    echo "Switching to $sched plugin"
    # echo "$sched" > /proc/litmus/active_plugin
    /root/liblitmus/setsched GSN-EDF
    sleep 1

    #read wcet and period from the dist file
    num_tasks=1
    echo "Setting up processes"
    for nt in `seq 1 $num_tasks`;
      do
        # wcet(ms) period(ms) duration(s) mode appname fft_size/iter
        $BASE_TASK 400 400 4 1 $PROG $kalmn_iter &
        SPIN_PIDS="$SPIN_PIDS $!"
        NEW_SPIN_PIDS[`expr $nt - 1`]="$!"
    done
    sleep 1

    #echo "catting log"
    #cat /dev/litmus/log > log.txt &
    #LOG_PID="$!"
    #sleep 1
    echo "Doing release..."
    $RELEASETS

    echo "Waiting for processes..."
    # wait ${SPIN_PIDS}

    for i in "${NEW_SPIN_PIDS[@]}"
      do
        wait $i
      done
    unset NEW_SPIN_PIDS

    echo "Done wait, sleeping"
    sleep 1
    echo "Killing log"
    kill ${LOG_PID}
    sleep 1
    echo "Sending SIGUSR1 to st_trace"
    kill -USR1 ${ST_TRACE_PID}
    echo "Waiting for st_trace..."
    wait ${ST_TRACE_PID}
    sleep 1

    mkdir -p "$PROG"/
    mv /dev/shm/*.bin "$PROG"/

    python find_wcet.py $DESIRED_WCET
    # kalmn_iter=${kalmn_iter::-100}
    overshoot=$(head -n 1 overshoot)
    if [ "$overshoot" == "1" ]
      then 
        KALMAN_BASE=$kalmn_iter
        kalmn_iter=$(($kalmn_iter - $BASE))
        echo "see a overshoot, final loop count: $kalmn_iter"
        echo desired_wcet ms: "$DESIRED_WCET" >> result
        echo kalman_iter: "$kalmn_iter" >> result
        break
    fi
    if [ "$overshoot" == "0" ]
      then 
        echo "no overshoot, loop count: $kalmn_iter"
    fi
    kalmn_iter=$(($kalmn_iter + $BASE))

  done


  j=$((j+1))
  #mv log.txt "$DIR"/"$sched"_$rep/
  sleep 1
  echo "Done! Collect your logs."


  echo "DONE!"
}

rm ./result
make myapp
mkdir -p /dev/shm/vmMon/
for desired_wcet in 40 150 250 
  do 
      cali_kalman $desired_wcet
  done



