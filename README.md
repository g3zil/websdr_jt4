## Installation 
This experimental software has been tested on Raspberry Pi PiOS and Ubuntu 24.04 LTS Linux systems.

### Download
You need to clone the package from github.com and run the software in the websdr_jt4 sub-directory. 
```
cd ~
git clone https://github.com/g3zil/websdr_jt4.git
cd ~/websdr_jt4
```
Execute all further commands in the ~/websdr_jt4 directory.
Updates can be downloaded with:
```
git pull
```

### Requirements
The shell script requirements are listed in the bash_requirements.txt file.
Any missing modules are loaded one by one when you first run the script setup.sh

#### Open environments
The python modules requirements are listed in the python_requirements.txt file.
These can be installed with:
```
python3 -m pip install -r python_requirements.txt
```
#### Externally managed environment
```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r python_requirements.txt
```

## Instructions for setting up and operation
Full details are in the jt4_log_readme.txt file.
Suggest you have that file open in a window as you set up in another.

## Architecture of the application: Shell script and python scripts
The diagram below outlines the data flow from a web browser connected to a websdr, through WSJT-X (prferably WSJT-X Improved), to the scripts comprising this websdr_jt4 application. The database is hosted by the WsprDaemon group and access to the Grafana visulaization tool is available on request.
![websdr_jt4_diagram](https://github.com/user-attachments/assets/d4ee77d1-a50a-48b6-857a-412c35ec931d)
