FROM ubuntu:20.04

ENV TZ=Europe
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installing dependencies
RUN apt update \
  && apt -y upgrade \
  && apt install -y build-essential libc6-dev libc6-dev-i386 curl gcc-multilib g++-multilib clang \
  python python-dev python3-pip python3-dev gdb cmake git

# Installing Python 2 pip
RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py && python get-pip.py
# Installing python packages
RUN pip2 install xlsxwriter pycrypto defusedxml pyyaml matplotlib
RUN pip3 install pandas psutil matplotlib

WORKDIR /cb-repair
COPY . ./

RUN python3 "./src/init.py";
#RUN python3 "./src/cb_repair.py -cn BitBlaster"; exit 0
# Fails because core dumps need to be eanbled
#RUN python3 "./src/unit_test.py"

ENTRYPOINT ["./src/cb_repair.py"]
CMD ["catalog", "-v"]