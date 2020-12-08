FROM ubuntu:20.04

ENV TZ=Europe
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installing dependencies
RUN apt update \
  && apt -y upgrade \
  && apt install -y -q build-essential libc6-dev libc6-dev-i386 curl gcc-multilib g++-multilib clang \
  python python-dev python3-pip python3-dev gdb cmake ssh apport

# Setup & Enable Password-less SSH Logon
RUN service ssh start && mkdir -p /var/run/sshd/ && mkdir /root/.ssh && chmod 700 /root/.ssh

# Installing Python 2 pip
RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py && python get-pip.py
# Installing python packages
RUN pip2 install xlsxwriter pycrypto defusedxml pyyaml matplotlib
RUN pip3 install pandas psutil matplotlib

WORKDIR /cb-repair
COPY . ./

# Enable code dumps
RUN mkdir /cores && ulimit -c unlimited
# Init benchmark
#RUN python3 "./src/init.py" && ./src/cb_repair.py init_polls -v && service ssh restart
RUN python3 "./src/init.py" && service ssh start

#ENTRYPOINT ["./src/cb_repair.py"]
#CMD ["catalog", "-v"]