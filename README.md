Using ykush kit.

git clone https://github.com/Yepkit/ykush.git
cd ykush
make
sudo mv bin/ykushcmd /usr/local/bin

Enable power on port 1:
ykushcmd -d 1

Disable power on port 1:
ykushcmd -u 1

Enable all ports:
ykushcmd -d a

Disable all ports:
ykushcmd -u a
