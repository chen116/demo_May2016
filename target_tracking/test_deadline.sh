#/bin/bash
make myapp
/root/liblitmus/setsched GSN-EDF
mkdir -p /dev/shm/vmMon
rm /dev/shm/vmMon/*
./myapp 10 10 1 1 testDEADline 1100000 &
sleep 3
/root/liblitmus/release_ts
ls /dev/shm/vmMon
cat /dev/shm/vmMon/*