#/bin/bash
make myapp
/root/liblitmus/setsched GSN-EDF
mkdir -p /dev/shm/rtOpenstack
rm /dev/shm/rtOpenstack/*
./myapp 10 10 1 1 testDEADline 1100000 &
sleep 3
/root/liblitmus/release_ts
sleep 5
ls /dev/shm/rtOpenstack
cat /dev/shm/rtOpenstack/*