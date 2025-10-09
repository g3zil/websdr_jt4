# -*- coding: utf-8 -*-
# JT4 detection algorithm with the clever parts all due to Daniel Estevez at link below. He presented at SDRA 2023
# https://github.com/daniestevez/jupyter_notebooks/blob/master/dslwp/JT4G%20detection.ipynb
# Two command line arguments, the date-time and the wav file that has been subsampled to 11025 ksps
# For now writes (appends to) a csv file in the save directory

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile
from scipy import signal        # For the  Continuous Wavelet Transform (CWT)
import sys
import csv
import subprocess
import os
from subprocess import PIPE, run

##########################################################################
# Functions
# The CWF approach for peak finding, the jiggle about that peak to find true peak and the interpolation are G3ZIL from HamSCI PSWS research
#
# local peak search: takes array index of CWF identified peak, does local search n bins either side for a true peak, returns index
def findLocalPeak (index, radius,level):
  # This method finds if the true local peak is to one side or other of CWF peak, and if so returns its index
  cwf_peak=level[index]
  for i in range (index-radius,index+radius+1):
     if level[i] > cwf_peak:
       index=i
       cwf_peak=level[i]
  return index

# Interpolate between frequency bins based on the weighted linear signal level at peak and either side
def freqInterpolate (index, radius, x, level):
  # This method interpolates in frequency space around true local peak returning an amplitude-weighted frequency
  sum=0
  sum_weights=0
  for i in range (index-radius,index+radius+1):
      sum=sum+x[i]*level[i]             # weighting by level is linear
      sum_weights=sum_weights+level[i]
  freq_interp=sum/sum_weights           # Interpolated peak frequency
  return freq_interp

# Bubble sort for frequency and correlation at that frequency in CWF peaks list
def bubble_sort(freq_peaks,level_peaks):
    # Outer loop to iterate through the list n times
    for n in range(len(freq_peaks) - 1, 0, -1):
        # Initialize swapped to track if any swaps occur
        swapped = False
        # Inner loop to compare adjacent elements
        for i in range(n):
            if freq_peaks[i] > freq_peaks[i + 1]:
                # Swap elements if they are in the wrong order
                freq_peaks[i], freq_peaks[i + 1] = freq_peaks[i + 1], freq_peaks[i]
                level_peaks[i], level_peaks[i + 1] = level_peaks[i + 1], level_peaks[i]
                swapped = True
        # If no swaps occurred, the list is already sorted
        if not swapped:
            break

def remove_adjacent(L):      # This function removes instances where a single peak has adjacent frequencies
  return [elem for i, elem in enumerate(L) if i == 0 or L[i-1]+1 != elem]

def out(command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout

############################################################################

###########
# Main code
###########

date_time=sys.argv[1] 	         	    # date and time passed in command line
wav_file=sys.argv[2] 	         	    # wav file name passed in command line

BASE_DIR=out("pwd")
BASE_DIR = BASE_DIR.strip('\n')
DETECTION_FILE=BASE_DIR + '/jt4_detections.csv'
PLOT_FILE=BASE_DIR + '/jt4_sync_frequency'    # the png gets added in savefig as it needs to know the extension 

freq_peaks=np.empty(4)
level_peaks=np.empty(4)

fs = 11025                                  # only multiples of 11025 sps supported
N = 2520 * fs // 11025

rate, x = scipy.io.wavfile.read(wav_file)   # read in the wav file where it has been converted to 11025 sps using sox
print ("Samp rate = ",rate)

# Tone spacing in bins for JT4G at 11025 sps
f_shift = 72
baud_rate=4.375   	              # characteristic for JT4 in Hz
tone_spacing=baud_rate*f_shift    # we will look for peaks at this spacing
T0=797.5                          # Tone zero frequency - this is theoretical see http://www.g4jnt.com/JT4G_Tone_freqs.pdf
T0_tol=100			              # A tolerance of +/- 100 Hz for oscillator offsets possible at 24 GHz
 
# JT4 sync vector - this is from Daniel Estevez notes, as are the comments below
sync = 2*np.array(list(map(int,'00011000110110010100000001100000000000010110110101111101000100100111110001010001111011001000110101010101111101010110101011100101101111000011011000111011101110010001101100100011111100110000110001011011110101')), dtype='int8')-1

# The algorithm goes as follows: first, we perform an FFT so that each tone fits a single bin (FFT resolution = JT4 baudrate).
# Then we compute the power in each bin.
# Next for each symbol, we compute the pwr[tone1] + pwr[tone3] - pwr[tone0] - pwr[tone2].

f_even = np.abs(np.fft.fftshift(np.fft.fft(x[:x.size//N*N].reshape((-1, N)), axis=1), axes=1))**2
f_even = f_even[:,f_shift:-2*f_shift] + f_even[:,3*f_shift:] - f_even[:,:-3*f_shift] - f_even[:,2*f_shift:-f_shift]

f_odd = np.abs(np.fft.fftshift(np.fft.fft(x[N//2:x.size//N*N-N//2].reshape((-1, N)), axis=1), axes = 1))**2
f_odd = f_odd[:,f_shift:-2*f_shift] + f_odd[:,3*f_shift:] - f_odd[:,:-3*f_shift] - f_odd[:,2*f_shift:-f_shift]

# This is then correlated against the (bipolar) sync vector of JT4.
acq = np.empty((f_even.shape[0] + f_odd.shape[0] - 2*sync.size + 2, f_even.shape[1]))
acq[::2,:] = signal.lfilter(sync[::-1], 1, f_even, axis=0)[sync.size-1:,:]
acq[1::2,:] = signal.lfilter(sync[::-1], 1, f_odd, axis=0)[sync.size-1:,:]

normalise= np.sqrt(np.sum(np.abs(sync[::-1])**2)*np.sum(np.abs(f_even)**2))
normalise_odd= np.sqrt(np.sum(np.abs(sync[::-1])**2)*np.sum(np.abs(f_odd)**2))
print ("Normalising value ", normalise)

tsync = np.argmax(np.max(acq, axis=1))		# tsync is the time of maximum correlation
print("Tsync maximum correlation = ",f"{tsync/2/baud_rate:.2f}", " s")

# Generate frequency axis, and then form frequency and correlation arrays for zoomed-in frequency span
fs = np.arange(-N//2, -N//2 + acq.shape[1])*baud_rate
fsync = np.argmax(acq[tsync,:])
if fs[fsync] < T0-T0_tol or fs[fsync] > T0+T0_tol:
   print("fsync outside expected range - data likely suspect")  # but go through processing anyway ...
f_zoom=fs[fsync-50:fsync+250]
correl_zoom=abs(acq[tsync,fsync-50:fsync+250])/normalise      # normalised using factor calculated above

# Larger figure size
fig_size = [10, 6]
plt.rcParams['figure.figsize'] = fig_size

# plot sync in zoomed in frequency around expected
fsync = np.argmax(acq[tsync,:])
plt.figure(facecolor='w')
plt.plot(f_zoom, correl_zoom)
plt.title('Sync in frequency (zoom)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Correlation');
plt.savefig(PLOT_FILE + '.png', dpi=300)
plt.show()

print("Fsync maximum correlation= ", f_zoom[50])

######################################################################################
# Scipy find_peaks_cwt approach using continuous wavelet transform 
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks_cwt.html
# I am after the peaks for the four tones, should be separated by 315 Hz for JT4.
# i.e. 72 times baud rate of 4.375 Hz
# but they will be different levels, generally decreasing with increasing baseband frequency
#######################################################################################

peaks = signal.find_peaks_cwt(correl_zoom, widths=np.arange(2,4))  # 2,4 is initial empirical selection
peakind=remove_adjacent(peaks)                                     # in case single peak shown as two adj freqs

with open(DETECTION_FILE, "a") as out_file:
  out_writer=csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
 
# find the index at four successively reducing maxima: algorithm finds first max, finds freq and level at that index, then sets max that index to zero
# and iterates
  for i in range(0,4):
    max=np.argmax(correl_zoom[peakind])
    index_max=peakind[max]
    index_max_original=index_max
    freq_peaks[i]=f_zoom[index_max]
    level_peaks[i]=10*np.log10(correl_zoom[index_max])
    #print("CWF peak ",i," frequency = ", freq_peaks[i], " Hz  at level = ",f"{level_peaks[i]:.2f}"," dB")

# Now call function to look either side to find true peak, revise and print output
    index_max=findLocalPeak(index_max,3,correl_zoom)
    freq_peaks[i]=float(f_zoom[index_max])
    level_peaks[i]=10*np.log10(correl_zoom[index_max])
    #print("Revised CWF peak ",i," frequency = ", freq_peaks[i], " Hz  at level = ",f"{level_peaks[i]:.2f}", " dB")

# Now interpolate the true peak frequency based on correlation level either side
    freq_peaks[i]=freqInterpolate(index_max,2,f_zoom,correl_zoom)
    #print("Interpolated CWF peak ",i," frequency = ", f"{freq_peaks[i]:.2f}", " Hz" )
    to_remove=np.array([index_max_original])
    peakind=np.setdiff1d(peakind,to_remove)
    #print("peakind vector ",peakind)

# Some instances where not in frequency order, so have to sort, making sure we swap the level array as well as the freq
  sorted=bubble_sort(freq_peaks,level_peaks)

# Do we have a valid JT4 detection? Yes if T0 frequency  between T0-T0_tol and  T0+T0_tol
# We will call this a  score 1 detection, score 2 if T1 at +310 to +320 Hz, 3 if T2 +630 to +650 Hz and 4 if T3 +950 to +970 Hz
  score=0
  if freq_peaks[0] > T0-T0_tol and freq_peaks[0] < T0+T0_tol:
    score=1
    if freq_peaks[1] > T0-T0_tol+tone_spacing and freq_peaks[1] < T0+T0_tol+tone_spacing:
      score=2
      if freq_peaks[2] >  T0-T0_tol+2*tone_spacing and freq_peaks[2] < T0+T0_tol+2*tone_spacing:
        score=3
        if freq_peaks[3] > T0-T0_tol+3*tone_spacing and freq_peaks[3] < T0+T0_tol+3*tone_spacing:
          score=4
 
# output detections data
  out_writer.writerow([date_time, f"{freq_peaks[0]:.2f}", f"{level_peaks[0]:.2f}",f"{freq_peaks[1]:.2f}", f"{level_peaks[1]:.2f}",\
  f"{freq_peaks[2]:.2f}", f"{level_peaks[2]:.2f}", f"{freq_peaks[3]:.2f}", f"{level_peaks[3]:.2f}", score ])
# print frequency differences, should be 315 Hz
    
print("f_diff_2-1 ", f"{freq_peaks[1]-freq_peaks[0]:.2f}","f_diff_3-2 ", f"{freq_peaks[2]-freq_peaks[1]:.2f}", "f_diff_4-3 ",\
 f"{freq_peaks[3]-freq_peaks[2]:.2f}", score)
