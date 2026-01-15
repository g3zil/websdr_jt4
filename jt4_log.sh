#!/bin/bash
### This bash script with python parts to parse and upload jt4 data from Margate 24 GHz SDR to a table in tutorial database on WD1
### Enhanced  prototype  with jt4 detector as well as wsjtx jt4  Gwyn G3ZIL Oct 2024 - December 2025
### V1.21 for Raspberry Pi and Ubuntu 24.04 now reading a jt4_config.ini file
#######################################################
# No need for user to edit lines below, RX metadata obtained from separate file 
#######################################################
# set up directory and file where latest decode and non-decode lines will be found
#
BASE_DIR=$(pwd)
source ${BASE_DIR}/jt4_config.ini    # the config.ini file holds the callsign and grid of the receiver, other metadata got from jt4 decodes

JT4_DATA_FILE="$(echo ${BASE_DIR} | cut -d/ -f-3)/.local/share/WSJT-X/ALL.TXT"   #  This is where wsjtx puts the data

# lines in ALL.TXT may be valid decodes, which have 10 fields, or no decode made, which have 8
# get number of fields and test for 10 for database upload
N_FIELDS="$(tail -1 ${JT4_DATA_FILE} | wc  | awk 'FS = " " {print $2}')"    # tail -1 gets last line, wc counts, field 2 of output is no. fields, selected by awk

touch ${BASE_DIR}/previous_upload.txt   # make sure it is present

if [ ${N_FIELDS} = '10' ]               # i.e. a line with JT4 decode data in which case we handle the data from wsjtx
then
  tail -1 ${JT4_DATA_FILE} > ${BASE_DIR}/current_spot.txt                             # get the line
  if diff  ${BASE_DIR}/current_spot.txt ${BASE_DIR}/previous_upload.txt >/dev/null    # test if we have seen before (should not happen)
  then
     echo "Spot has been uploaded previously - exiting"                               # we have seen before so exit, no dupes
     exit 1
  else
    echo "New spot decoded"                                                           # new one!
    tail -1 ${JT4_DATA_FILE} | sed 's/,[ \t]\?/,/g' | tr '_' ' ' >${BASE_DIR}/temp.txt                            # get last line from the ALL.TXT, sed gets rid of white space, tr changes _ to space
    DECODE_CAPTURE_DATE=$( date -u --date="1 minute ago" +%Y-%m-%dT%H:%M:00Z)                                     # easier to get time in required format this way
    awk 'FS = " ", OFS="," {print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10}' <${BASE_DIR}/temp.txt >${BASE_DIR}/temp1.csv   # reformat to a csv
    /usr/bin/python3 ${BASE_DIR}/azi_calc.py ${DECODE_CAPTURE_DATE} ${RX_GRID} ${RX_ID}                           # calculate lat/lon/azimuths/distance
    echo "Decode data and added variables written to spots_azi.csv file"
    /usr/bin/python3  ${BASE_DIR}/jt4_upload.py ${BASE_DIR}/spots_azi.csv                                         # upload to table jt4 database tutorial on wd1 server
    tail -1 ${JT4_DATA_FILE} > ${BASE_DIR}/previous_upload.txt                                                    # this is one we just uploaded, not to be duped

  #  This code runs a JT4 detector,a correlator that should provide a detection, not a decode, at lower SNR - perhaps!
  #  and furthermore, is easily modified for PI4 digimode. The detector is based on code from Daniel Estevez, details in jt4_detect.py
    WAV_FILE=$(ls -ltr ${BASE_DIR}/save| tail -n 1 | awk '{print $9}')              # get the JT4 even minute wav file name to process 
    echo "Detection program processing file "${WAV_FILE}
    sox ${BASE_DIR}/save/${WAV_FILE} -r 11025 ${BASE_DIR}/11025.wav                 # resample to 11025 sps (now this is 1/4 of 44100 sps!)
    ~/websdt_jt4/.venv/bin/python3 ${BASE_DIR}/jt4_detect.py ${DECODE_CAPTURE_DATE} ${BASE_DIR}/11025.wav     # do the processing!
  fi
else

# We can arrive here via one of two criteria, odd minute or missed wsjtx jt4 detection, forst check whic, then process as required  
  echo "If odd minute then CW file for signal level and noise, else if even a missed JT4 spot interval"
  WAV_FILE=$(ls -ltr ${BASE_DIR}/save| tail -n 1 | awk '{print $9}')
  WAV_FILE_MINUTE=$(ls -ltr ${BASE_DIR}/save| tail -n 1 | awk '{print substr($9, 11,1)}')
  if [[ ${WAV_FILE_MINUTE} =~ ^[13579]+$ ]]
     then
       WAV_FILE_TIME=$(ls -ltr ${BASE_DIR}/save| tail -n 1 | awk '{print substr($9, 8,4)}')
       LAST_MINUTE=$(date -u --date="1 minute ago" +%H%M)
       echo "File time ${WAV_FILE_TIME}  last minute time ${LAST_MINUTE}"
       if [[ ${WAV_FILE_TIME} = ${LAST_MINUTE} ]]
       then
         echo 'Correct odd minute - so process signal and noise'
         ${BASE_DIR}/sn_calc.sh ${WAV_FILE}                                        # script uses SOX to calculate signal level and noise
         /usr/bin/python3 ${BASE_DIR}/sn_upload.py ${BASE_DIR}/signal_noise.csv    # uploads to jt4 table on wd1 with mode ident CW together with metadata
       else
         echo 'File time mismatch: WSJT-X likely not running'
       fi
  fi
fi

# Tidy up wav files, keep just last 10
rm -v -f $(ls -1t ${BASE_DIR}/save/*.wav | tail -n +11)

echo "Processing complete"


