# -*- coding: utf-8 -*-
# Filename: azi_calc_v1.3.py
# February  2020  Gwyn Griffiths
# Oct-Nov 2024 adapted for JT4 data for 24 GHz Margate WebSDR
# This version for Raspberry Pi
# Take a scraper latest_log.txt file, extract the receiver and transmitter Maidenhead locators and calculates azimuth at tx and rx in that order

import numpy as np
import sys
import csv
from subprocess import PIPE, run

# get the date/time in correct format from the command line arguments of which there are three
date_time=sys.argv[1]
# then the receiver details from 2nd and 3rd command line arguments
rx_grid=sys.argv[2]
rx_id=sys.argv[3]
mode='jt4'

##################
# Define functions
##################

# define function to convert 4 or 6 character Maidenhead locator to lat and lon in degrees
def loc_to_lat_lon (locator):
    locator=locator.strip()
    decomp=list(locator)
    lat=(((ord(decomp[1])-65)*10)+(ord(decomp[3])-48)+(1/2)-90)
    lon=(((ord(decomp[0])-65)*20)+((ord(decomp[2])-48)*2)+(1)-180)
    if len(locator)==6:
        if (ord(decomp[4])) >88:    # check for case of the third pair, likely to  be lower case
            ascii_base=96
        else:
            ascii_base=64
        lat=lat-(1/2)+((ord(decomp[5])-ascii_base)/24)-(1/48)
        lon=lon-(1)+((ord(decomp[4])-ascii_base)/12)-(1/24)
    return(lat, lon)

def great_circle(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    return 6371 * (                                                                                # 6371 is earth radius in km
        np.arccos(np.sin(lat1) * np.sin(lat2) + np.cos(lat1) * np.cos(lat2) * np.cos(lon1 - lon2))
    )

def out(command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout

###############
# Main code
###############
# These paths are username dependent but the pwd approach should be OK, should be no need for user to alter
# get the path to the latest spot line and the added-variables output csv file

BASE_DIR = out("pwd")
BASE_DIR = BASE_DIR.strip('\n')
latest_log_file=BASE_DIR + '/temp1.csv'
spots_azi_file=BASE_DIR + '/spots_azi.csv'


# open file for output as a csv file, to which we will copy original data and the tx and rx azimuths
# read in line from input file

with open(spots_azi_file, "w") as out_file:
  out_writer=csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  
  with open(latest_log_file) as fp:
    for line in fp:
        time_a,time_b,dial_frequency,dummy,mode,snr,dt,base_frequency,tx_call,tx_grid=(line.strip().split(','))
    
        # split out the rx and tx locators
        tx_locators=(tx_grid)
        rx_locators=(rx_grid)
    
        (tx_lat,tx_lon)=loc_to_lat_lon (tx_locators)    # call function to do conversion, then convert to radians
        phi_tx_lat = np.radians(tx_lat)
        lambda_tx_lon = np.radians(tx_lon)
        (rx_lat,rx_lon)=loc_to_lat_lon (rx_locators)    # call function to do conversion, then convert to radians
        phi_rx_lat = np.radians(rx_lat)
        lambda_rx_lon = np.radians(rx_lon)
        delta_phi = (phi_tx_lat - phi_rx_lat)
        delta_lambda=(lambda_tx_lon-lambda_rx_lon)

        # calculate azimuth at the rx
        y = np.sin(delta_lambda) * np.cos(phi_tx_lat)
        x = np.cos(phi_rx_lat)*np.sin(phi_tx_lat) - np.sin(phi_rx_lat)*np.cos(phi_tx_lat)*np.cos(delta_lambda)
        rx_azi = (np.degrees(np.arctan2(y, x))) % 360

        # calculate azimuth at the tx
        p = np.sin(-delta_lambda) * np.cos(phi_rx_lat)
        q = np.cos(phi_tx_lat)*np.sin(phi_rx_lat) - np.sin(phi_tx_lat)*np.cos(phi_rx_lat)*np.cos(-delta_lambda)
        tx_azi = (np.degrees(np.arctan2(p, q))) % 360

        # calculate great circle distance
        dist=great_circle(tx_lat,tx_lon,rx_lat,rx_lon)
            
        # derive the band in metres (except 70cm and 23cm reported as 70 and 23) from the frequency
        dial_frequency=float(dial_frequency)
        base_frequency=float(base_frequency)
        if 24048 < dial_frequency < 24049:                # convention that dial frequency in MHz
            band=1.25                                     # convention that band 70 cm and above is in cm
        frequency=dial_frequency+base_frequency/1000000   # actual frequency - will be double precision in postgresql
        
        # output the original data and add lat lon at tx and rx, azi at tx and rx and the band
        out_writer.writerow([date_time, tx_call,tx_grid,"%.2f" % band,frequency,snr,dt,int(round(dist)),int(round(tx_azi)),
        "%.3f" % (tx_lat), "%.3f" % (tx_lon),rx_id,rx_grid,"%.3f" % (rx_lat), "%.3f" % (rx_lon), int(round(rx_azi)), mode])

    print("done")
