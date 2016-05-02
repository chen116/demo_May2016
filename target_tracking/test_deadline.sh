#/bin/bash
make myapp
rm /dev/shm/vmMon/*
./myapp 10 10 4 1 testDEADline 1100000 &
sleep 3
/root/liblitmus/release_ts
ls /dev/shm/vmMon
cat /dev/shm/vmMon/*