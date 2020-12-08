#!/bin/bash
# from https://github.com/program-repair/RepairThemAll/blob/master/init.sh

# modified to accept equal major version
do_version_check() {
    [ "$1" == "$2" ] && return 10

    ver1front=$(echo "$1" | cut -d "." -f -1)
    ver1back=$(echo "$1" | cut -d "." -f 2-)
    ver2front=$(echo "$2" | cut -d "." -f -1)
    ver2back=$(echo "$2" | cut -d "." -f 2-)

    if [ "$ver1front" != "$1" ] || [ "$ver2front" != "$2" ]; then
        [ "$ver1front" -lt "$ver2front" ] && return 9

        [ "$ver1front" == "$1" ] || [ -z "$ver1back" ] && ver1back=0
        [ "$ver2front" == "$2" ] || [ -z "$ver2back" ] && ver2back=0
        do_version_check "$ver1back" "$ver2back"
        return $?
    else
        [ "$1" -gt "$2" ] && return 11 || return 9
    fi
}

echo "Installing cb-repair dependencies"
apt-get install libc6-dev libc6-dev-i386 gcc-multilib g++-multilib gdb clang cmake python \
        python-dev python3 python3-pip python3-dev -y

# Installing Python 2 pip
curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
python get-pip.py

command -v clang > /dev/null
[[ $? -eq 1 ]] && echo "[Error] clang not installed" && exit 1 ;

command -v cmake > /dev/null
[[ $? -eq 1 ]] && echo "[Error] cmake not installed" && exit 1 ;

command -v python > /dev/null
[[ $? -eq 1 ]] && echo "[Error] python not installed" && exit 1

python_version=$(python -c 'import platform; print(platform.python_version())')

do_version_check "$python_version" "2.7"
[[ $? -eq 9 ]] && echo "[Error] Python version >= 2.7" && exit 1 ;

command -v python3 > /dev/null
[[ $? -eq 1 ]] && echo "[Error] python3 not installed" && exit 1 ;

python3_version=$(python3 -c 'import platform; print(platform.python_version())')

do_version_check "$python3_version" "3.7"
[[ $? -eq 9 ]] && echo "[Error] python3 version >= 3.7" && exit 1 ;

echo "Dependencies successfully installed"

echo "Installing python packages"
pip3 install -r ./python3_requirements.txt
pip install -r ./python2_requirements.txt

echo "Enabling core dump generated when a process crashes for type 1 POVs."
ulimit -c unlimited && mdkir -p /cores && chmod 777 /cores
[[ $? -eq 1 ]] && echo "[Error] Benchmark initialization failed" && exit 1 ;

echo "Initializing benchmark"
./src/init.py
[[ $? -eq 1 ]] && echo "[Error] Benchmark initialization failed" && exit 1 ;
