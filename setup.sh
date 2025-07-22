#!/bin/bash
### This bash script  sets up the receiver metadata of receiver grid JO01qj for Maregate Kent SDR
#   and cxallsign for reporting as TRIG01/you_call
### Also installs command line and bash modules 
### V1.2 for Raspberry Pi and Ubuntu 24.04

########################################################
# Only user-set installation variables are in this block
########################################################
# set up receiver details to go into database table via python
RX_GRID=JO01qj           #  Maidenhead for Margate WebSDR, not where browser is located!              
RX_ID=TRIG01/G3ZIL       # The /G3ZIL is a suggested addition, use your callsign to show who is using WebSDR
########################################################

# No need for user to edit lines below
#######################################################
# check that required dependencies are met, except for browser and WSJT-X assumed available and connected by virtual cable
apt-get install sox libsox-dev
apt install postgresql libpq-dev
apt-get install bc
apt-get install pulseaudio
apt-get install pavucontrol

echo "Command line Modules installed"

#######################################################
