#/bin/bash
make myapp
/root/liblitmus/setsched GSN-EDF
mkdir -p /dev/shm/vmMon
rm /dev/shm/vmMon/*
./myapp 10 10 1 1 testDEADline 32768 &
sleep 3
/root/liblitmus/release_ts
sleep 5
ls /dev/shm/vmMon
cat /dev/shm/vmMon/*