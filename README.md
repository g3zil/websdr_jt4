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
These are listed in the requirements.txt file.

## Instructions for setting up and operation
Full details are in the jt4_log_readme.txt file.

## Architecture of the application: Shell script and python scripts
The diagram below outlines the data flow from a web browser connected to a websdr, through WSJT-X (prferably WSJT-X Improved), to the scripts comprising this websdr_jt4 application. The database is hosted by the WsprDaemon group and access to the Grafana visulaization tool is available on request.
![websdr_jt4_diagram](https://github.com/user-attachments/assets/d4ee77d1-a50a-48b6-857a-412c35ec931d)
