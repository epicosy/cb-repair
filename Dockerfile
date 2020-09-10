FROM ubuntu:18.04

RUN apt update \
  && apt -y upgrade \
  && apt install -y build-essential libc6-dev libc6-dev-i386 \
    gcc-multilib g++-multilib clang python python-pip python3.7 gdb cmake git
RUN pip install xlsxwriter pycrypto defusedxml pyyaml matplotlib

WORKDIR /cb-repair
COPY . ./

RUN python3 "./src/cb_repair.py -cn BitBlaster"; exit 0
RUN python3 "./src/unit_test.py" # Fails because core dumps need to be eanbled

ENTRYPOINT "./cb-repair/src/cb_repair.py"
