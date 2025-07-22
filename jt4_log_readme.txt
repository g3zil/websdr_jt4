                                    jt4_log
   
A prototype package for 24/7 monitoring and logging of jt4 signals at the Kent 24 GHz WebSDR

Gwyn Griffiths G3ZIL   gxgriffiths@virginmedia.com
with Dr John Worsnop G4BAO

Installation, test and operating instructions for a Raspberry Pi running PiOS or a machine running Ubuntu 24.04
Version 1.1 17 November 2024
Version 1.2 July 2025         adapted to also run under Ubuntu 24.04, and various improvements
                              now suggest using wsjtx-improved for correct JT4 SNR https://sourceforge.net/projects/wsjt-x-improved/
                              First version at Github
---------------------------------------------------------

1. Prerequisites and jt4_log package download
	a) A browser capable of connecting to the WebSDR at trig01.ddns.net:8073
	   Have used Vivaldi and Firefox.
	b) WSJT-X package set up to use VHF extensions to enable mode JT4 submode G
           WSJT-X calculates incorrect SNR for JT4. It is correct in WSJT-X Improved. 
           If you are happy to install the improved version download from:
           https://sourceforge.net/projects/wsjt-x-improved/
           and install as follows, this is for file name downloaded 20 July 2025
           sudo dpkg -i wsjtx_2.8.0_improved_PLUS_250501_amd64.deb
        c) A virtual cable (e.g. pulseaudio) to connect the browser audio to WSJT-X
           and pavucontrol to set audio level to WSJT-X. Affects signal level (not SNR)
           keep to same setting and watch out if keyboard volume control affects the level
           On the WSJT-X Settings->Audio page select pulse as the input source, or to suit if you use another option.
	d) On the Save pulldown of WSJT-X select Save all for the wav files.
	   jt4_log will keep the number of wav files to the latest 10.
	e) Here it is assumed you cloned the Github repository and run the setup and python scripts.
           Go to your home directory cd ~
           check that directory websdr_jt4 has been created in your home directory and contents are as below:
	   (times will be different)
           (.venv) gwyn@HPI5:~/websdr_jt4$ ls -l
           total 80
           -rw-rw-r-- 1 gwyn gwyn  4736 Jul 22 11:27 azi_calc.py
           -rw-rw-r-- 1 gwyn gwyn   309 Jul 22 11:27 bash_requirements.txt
           -rw-rw-r-- 1 gwyn gwyn 10231 Jul 22 11:27 jt4_detect.py
           -rw-rw-r-- 1 gwyn gwyn 10624 Jul 22 11:27 jt4_log_readme.txt
           -rwxrwxr-x 1 gwyn gwyn  4632 Jul 22 11:27 jt4_log.sh
           -rwxrwxr-x 1 gwyn gwyn  2490 Jul 22 11:27 jt4_upload.py
           -rwxrwxr-x 1 gwyn gwyn   574 Jul 22 11:27 new_beacon.sh
           -rwxrwxr-x 1 gwyn gwyn  1120 Jul 22 11:27 pa_restart.sh
           -rw-rw-r-- 1 gwyn gwyn    57 Jul 22 11:27 python_requirements.txt
           -rw-rw-r-- 1 gwyn gwyn  1601 Jul 22 11:27 README.md
           drwxrwxr-x 2 gwyn gwyn  4096 Jul 22 11:27 save
           -rwxrwxr-x 1 gwyn gwyn  1210 Jul 22 11:27 setup.sh
           -rwxrwxr-x 1 gwyn gwyn  2364 Jul 22 11:27 sn_calc.sh
           -rwxrwxr-x 1 gwyn gwyn  2307 Jul 22 11:27 sn_upload.py

2. Preparing for use jt4_log.sh	
	a) Change directory using cd ~/jt4 and use an editor of your choice open jt4_log.sh
	b) Recall  this prototype is for a single beacon, its details are setup in script jt4_log.sh
	c) Edit the RX_GRID and RX_ID fields under the set up receiver comment
	   suggestion is to use TRIG01/yourcallsign to show who is using it
	d) Exit editor, saving the jt4_log.sh file
        b) Required step on first use and on change of beacon being monitored.
	   Script new_beacon.sh is run to set up basic metadata.
           Recalling this pilot/prototype is one beacon at a time we need to know the beacon callsign
           as the first observation might be a CW minute e.g. for GB3PKT
	   or we may have to wait a long time for a JT4 decode from a continental beacon.
           So, cd ~/websdr_jt4 to be sure, then:
	   ./new_beacon.sh GB3PKT JO01MT TRIG01/G3ZIL
           replace GB3PKT and its grid by another beacon/grid if that is what is needed and G3ZIL by your call

3. Preparing for use WSJT-X and the WebSDR browser 
	a) On a Raspberry Pi tests have shown that, over time (ten+ hours) noise and spurs
           are introduced (somehow) into the virtual audio chain. It presence and growth is
           minimised if the default sample rate in pulseaudio is changed from 44.1 ksps
	   to 48 ksps, which is the preferred WSJT-X sample rate. This change is made by:
	     sudo su
	     nano /etc/pulse/daemon.conf
	   find line
	     ;default-sample-format = s16le
	   remove the semi colon to uncomment and make active
	   remove the semicolon from next line for the default sampling rate, and add comment, so you would have:
	     default-sample-rate = 48000     # changed from 44100 G3ZIL at *** UTC on *** 2024
	   This is a useful but insufficient remedy for the noise and spur growth.
           An effective additional step is described in section 6.
	   Now Reboot the computer for the change to take effect. On restart, open web browser.
	b) With the web browser at trig01.ddns.net:8073 set its frequency to 24.0489442 GHz, mode USB
	c) In WSJT-X set mode JT4 and submode G, set RX as 650 Hz and F Tol as 200 Hz
	d) If not already done, in File->Settings->Frequencies tab add 24048.9442 MHz as a JT4 mode
	   This is 800 Hz below the 24048.945 MHz frequency of the GB3PKT beacon, useful for testing.
	e) In WSJT-X menu File->Settings->Audio set the save directory to
           /home/pi/websdr_jt4/save
           NB Change pi to your userid if Ubuntu etc
	   You may need to recheck this setting if WSJT-X crashes, it is kept after a normal close.
	f) Start monitoring with frequency 24048.9442 MHz (band 1.25 cm), examine the WSJT-X waterfall display.
	   Odd minutes should show a single frequency peak at ~800 Hz, the carrier plus CW minute.
	   The even minute is the JT4G transmission.
	   There should be four peaks, at ~650, 965, 1280, 1595 Hz. They will be weaker, and likely unequal strength.
	g) If the JT4G peaks look distinct, there should be a decode in the window, if not,
           there will be a meaningless line.

4. Test jt4_log.sh in manual mode
	a) Change directory using cd ~/websdr_jt4 
           Check that at least one wav file has been recorded using
           ls -l ./save
           if so, start the script in manual mode:
	   ./jt4_log.sh
           if not, check correct save directory file name in wsjtx and Save All has been selected.
	b) If the script runs (hopefully properly!) it will output either:

           For an odd minute where it has measured the CW carrier signal level and the noise level

	   Modules OK
	   If odd minute then CW file for signal level and noise, else if even a missed JT4 spot interval
	   File time 0845  last minute time 0845
	   Correct odd minute - so process signal and noise  
	   RMS_NOISE (dB)= -73.84
	   RMS_SIGNAL (dB)= -49.66
	   removed '/home/pi/jt4/save/241106_1603.wav'
	   Processing complete

	   or, if WSJT-X has crashed, it sees a time discrepancy between 'now' and expected file time:

	   Modules OK
	   If odd minute then CW file for signal level and noise, else if even a missed JT4 spot interval
	   File time 0845  last minute time 0854
	   File time mismatch: WSJT-X likely not running
	   Processing complete

	   or, for an even minute in which there was no JT4G decode:

	   Modules OK
	   If odd minute then CW file for signal level and noise, else if even a missed JT4 spot interval
	   removed '/home/pi/jt4/save/241106_1608.wav'
	   Processing complete

	   or it might output:

	   Modules OK
           Spot has been uploaded previously - exiting

	   or, for an even minute in which there was a JT4G decode

	   Modules OK
	   New spot decoded
	   done
	   Decode data and added variables written to spots_azi.csv file

	   Best check in both even and odd minutes.
           In every case it tidies up the wav file directory, keeping only the last 10.
	c) If anything other than the responses above appear please contact gwyn at gxgriffiths@virginmedia.com
	d) But if all is well, in your browser go to the WebSDR_jt4 Grafana dashboard
           (userid: wdread password: JTWSPR2008)
	   at:
	   http://logs1.wsprdaemon.org:3000/d/qO0MwaZHz/websdr_jt4?orgId=1&from=now-3h&to=now-1m&var-band_cm=1.25&var-receiver=TRIG01%2FG3ZIL&var-beacon=GB3PKT

	   You will need to select your receiver name from the pull down list top left.
	   Hopefully you will see data points for:
	   (top panel) Signal+Noise level in 200 Hz bandwidth and absolute humidity
	   (next) Signal+Noise to Noise ratio estimate from JT4G - inaccurate if using WSJT-X 2.7, correct in WSJT-X improved 2.8 onward
	   (next) Signal+Noise to Noise ratio estimate from the CW signal (not JT4G) and the noise level estimate in dB in 1 Hz
	   (next) Baseband frequency of the JT4G signal whenever there is a decode
	   (next) Air, water and dew point temperatures from Met Office buoy F3 in the channel east of Margate
	   (next) Wind speed and direction from the buoy
	   (next) Relative humidity from the buoy
	   (bottom) Rainfall rate from Environment Agency sensor at Tillingham, Essex.

	   If things look odd, contact Gwyn.

5. Operate jt4_log.sh in automatic mode
	a) In operation the script is run by cron, set up using the command:

	   crontab -e

	b) Add the following line to the end of the cron file that will be listed:

           * * * * * cd /home/pi/websdr_jt4 ; /home/pi/websdr_jt4/jt4_log.sh >/home/pi/websdr_jt4/cronlog.txt 2>&1

	   This will run the script every minute. After execution, the content of the file ~/websdr_jt4/cronlog.txt
	   should be one of the three messages listed above. If not, contact Gwyn.
           Be sure to change the THREE instances of userid pi if necessary.
           The individual scripts will pick up their own correct home directory, only in this cron line is up to you.
	   You can monitor the cronlog.txt file when in the ~/websdr_jt4 directory with:
	   watch cat cronlog.txt
	   Control C to exit - the display shpould update some seconds after each top of the minute.

	c) After a little time, check the Grafana dashboard using step 4f above.

6. Script to close WSJT-X, restart the pulseaudio service and restart WSJT-X
	a) This is a work-around to the growth of virtual audio noise and spurs seen on a Raspberry Pi.
	   The data deterioration is minimal if this is done every hour. Hence the pa_restart.sh script is run using cron.
	b) Set up using the command:

	   crontab -e
	c) Add the following line at the end of the cron file:

           1 * * * * XDG_RUNTIME_DIR=/run/user/$(id -u) cd /home/pi/websdr_jt4 ; /home/pi/websdr_jt4/pa_restart.sh >/home/pi/websdr_jt4/cron_kill.log 2>&1

	   This runs the restart script one minute past the hour. Consequently, most times, JT4 decodes are not missed.
           As for the first cron job, check the THREE instances of home directory name.

Gwyn G3ZIL Version 1.2 July 2025





