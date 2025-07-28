#!/bin/bash

### This bash script uses the linux sound utility to determine the signal level and the rms noise level during the odd minute carrier from GB3PKT
### Basic functional pilot   Gwyn G3ZIL Oct 2024 - July 2025
### Single command line argument is wav file name in default path
### This version for Raspberry Pi and Ubuntu 24.04

# set up directory and file where wav file found and temporary files written and set mode to CW for carrier
BASE_DIR=$(pwd)
WAV_DIR=${BASE_DIR}/save
MODE=CW

# get the date in format for database
DECODE_CAPTURE_DATE=$(date -u --date="1 minute ago" +%Y-%m-%dT%H:%M:00Z) 

# The rms noise level part. This is dB on arbitary scale dependent on WebSDR/Browser/WSJT-X signal level - unsatisfactory I know, but this is pilot!
# Use of sox and RMS in trough of 50 milliseconds is well documented in Griffiths et al. in QEX for WSPR
/usr/bin/sox ${WAV_DIR}/$1 ${BASE_DIR}/trimmed.wav trim 5 25                                         # trim time interval to 5 to 5+25 seconds 
/usr/bin/sox ${BASE_DIR}/trimmed.wav ${BASE_DIR}/filtered.wav sinc 1200-2000                         # sinc bandpass filter away from carrier 
NOISE=$(/usr/bin/sox ${BASE_DIR}/filtered.wav -n stats 2>&1 | grep 'RMS Tr dB' | awk '{print $4}')   # get stats, look for trough value quietest 50 ms and grab value
RMS_NOISE=$(/usr/bin/bc <<< "scale=2; $NOISE - 29")    # account for the 800 Hz bandwidth for noise measurement to get dB in 1 Hz

# The FFT noise part. This uses essentially same algorithm as in wsprdaenon: sum lowest 30% of fourier coefficients in band 373 Hz to 2933 Hz
FFT_NOISE=$(python3 fft_noise.py ${WAV_DIR}/$1)

# The signal level part. This is dB on arbitary scale dependent on WebSDR/Browser/WSJT-X signal level - unsatisfactory, as for noise.
/usr/bin/sox ${BASE_DIR}/trimmed.wav ${BASE_DIR}/filtered.wav sinc 700-900             # sinc bandpass filter around nominal carrier, which is 800 Hz July 2025 AirspySDR 
RMS_SIGNAL=$(/usr/bin/sox ${BASE_DIR}/filtered.wav -n stats 2>&1 | grep 'RMS lev dB' | awk '{print $4}')   # get stats, look for RMS (not peak) and grab value

echo "RMS_NOISE (dB)= ${RMS_NOISE}"
echo "RMS_SIGNAL (dB)= ${RMS_SIGNAL}"
echo "RMS_SIGNAL (dB)= ${FFT_NOISE}"

# get metadata from previous jt4 decode using awk add in the current time, rms and fft noise and level measurements and mode and save as csv
awk -F"," -v OFS="," -v date="${DECODE_CAPTURE_DATE}" -v fft_noise="${FFT_NOISE}" -v rms_noise="${RMS_NOISE}" -v signal="${RMS_SIGNAL}" -v mode="${MODE}" \
'{print date,$2,$3,$4,$12,$13,$14,$15,fft_noise,rms_noise,signal,mode}' <${BASE_DIR}/spots_azi.csv >${BASE_DIR}/signal_noise.csv

