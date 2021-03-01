### Setup with Docker

#### Build

1. First, install Docker ([doc](https://docs.docker.com/)).

2. Then, execute the command to build the image from the Docker file where the project has been pre-configured and is 
ready to be used:

```
docker build --force-rm --tag cb-repair .
```

#### Enabling core dumps 
On Ubuntu the core dumps are redirected to the standard input of the Apport program, which writes them to the location 
where the crashing app was launched. When running the benchmark with Docker image, core dumps need to be stored on 
specific disk location (by default containers can not write to the file system locations which Apport requires). 

The following is the simplest solution to enable core dumps for Docker containers:

Set the cores generation to the folder ```/cores``` in the host with the specific pattern ```core.pid.path```.
```
echo '/cores/core.%p.%E' | sudo tee /proc/sys/kernel/core_pattern
```
To reset the pattern to the default execute:
```
sudo service apport restart
```

#### Execute
The WORKDIR is ```/cb-repair``` and the main script is ```cb-repair.py```, in the folder ```src```.
Run the container with and query the benchmark with commands, for example: 
```
docker run -it cb-repair 
root@docker_container:/cb-repair# src/cb_repair.py check --challenges BitBlaster --genpolls --count 10 --timeout 10 -v
```
