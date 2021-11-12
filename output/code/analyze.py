import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os, glob
from io import StringIO
import datetime
from datetime import datetime as dt_mod
from datetime import time
from datetime import timedelta
from scipy.ndimage.filters import uniform_filter1d
from matplotlib.backends.backend_pdf import PdfPages
from itertools import chain, repeat, groupby
import matplotlib.dates as mdates
import csv
from functions.plot import plot_single_days, plot_multiple_within_single, set_day_identifier, get_sleep_onset_offset
from functions.hist import simple_hist, mean_hourly_activity, activity_on_clock, activity_hist_on_clock

#Define if you want to find start and end of sleep and plot night, or plot day. If you want to analyze night, please insert appropriate timelimits in plot.py and hist.py (e.g 19 and 11).
#If you want to analyze day, timelimit1=3 and timelimit2=3 is recommended.
night=False
#Define if you want to analyze clients and their partners or only clients. Partner=True only works if partner data is available.
partner_global=True

#finds all csvs to analyze in the given folder
def find_all_csv(folder):
    path = folder
    extension = 'csv'
    os.chdir(path)
    result = glob.glob('*.{}'.format(extension))
    os.chdir('../')
    return result, path

#Converts Entrys to numeric
def zahlen(data):
    a=pd.to_numeric(data).fillna(0)
    return a

#Gives moving average of value in df of n entries
def avgval(df, value, n):
    new_col=pd.to_numeric(df[value], errors='coerce').fillna(0).to_numpy()
    column=uniform_filter1d(new_col, size=n, mode='nearest')
    return column

#Finds 'partner-csv' in folder PARTNER if it includes the same number in its name
def find_partner(subject, lis_of_csv_partner):
    p=[entry for entry in list_of_csv_partner if subject in entry]
    print('Partner_CSV', p)
    if p==[]:
        partner=False
        partner_csv='no'
        return partner_csv, partner
    else:
        partner=True
        partner_csv=[entry for entry in list_of_csv_partner if subject in entry][0]

        return partner_csv, partner

#Finds the row where raw data begins (after header of actiwatch-csv)
def find_beginning_of_data(csv_file):
    empty=0
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for k, row in enumerate(reader):
            if 'Off-Wrist Status' in row:
                return k+2

list_of_csv, path=find_all_csv('CLIENT/')
current_subjects=[s[1:5] for s in list_of_csv]

#Define how many values you want to include for your moving average
moving_avg_val=5

#If your frequence is different, you can change it here
measuring_frequence='min'

#Creates a 'Result-Folder' for every subject that is analyzed
for i in range(len(current_subjects)):
    if not os.path.exists('output/'+current_subjects[i]+'/'):
        os.makedirs('output/'+current_subjects[i]+'/')


for i in range(len(list_of_csv)):
    print('CLIENT', current_subjects[i])
    #Creation of df with data from one subject
    empty_lines=[]
    dataset='CLIENT/'+list_of_csv[i]
    lines=open(dataset).readlines()
    char_list=['\n', ';']
    for k in range(len(lines)):
        if lines[k] == '\n':
            empty_lines.append(k)
    start_data=find_beginning_of_data(dataset)
    sio = StringIO('\n' .join([line.replace('""', '"')[1:-2] for line in open(dataset).readlines()[start_data:]]))
    df = pd.read_csv(sio,  skiprows=0, header=None, index_col=False, names = ['z', 'd','t', 'off_wrist', 'act', 'mark', 'white', 'red', 'green', 'blue', 'sleep', 'interval'],
    parse_dates={'time_column':['d', 't']}, dayfirst=True)
    df= df.replace('NaN', np.nan)


    begin_client=df['time_column'].iloc[0]
    end_client=df['time_column'].iloc[-1]

    end=end_client
    begin=begin_client
    df=df.loc[(df['time_column'] >= begin) & (df['time_column'] <= end)]

    #change entries in 'act' to numeric
    df['act'].update(zahlen(df['act']))
    #insert column with only times not dates (is needed for later analysis)
    df.insert(0, 'only_time', [entry.time() for entry in df['time_column']])
    #insert column with moving average of 'act'
    df.insert(0, 'mov_act', avgval(df, 'act', moving_avg_val), True)

    if partner_global==True:
        list_of_csv_partner, path2=find_all_csv('PARTNER/')
        partner_csv, partner=find_partner(current_subjects[i], list_of_csv_partner)
        dataset_partner='PARTNER/'+partner_csv
        if partner==True:
            #read partner data
            start_data=find_beginning_of_data(dataset_partner)
            sio_partner=StringIO('\n' .join([line.replace('""', '"')[1:-2] for line in open(dataset_partner).readlines()[start_data:]]))
            df_partner = pd.read_csv(sio_partner,  skiprows=0, header=None, index_col=False, names = ['z', 'd','t', 'off_wrist', 'act', 'mark', 'white', 'red', 'green', 'blue', 'sleep', 'interval'],
            parse_dates={'time_column':['d', 't']}, dayfirst=True)
            df_partner['act'].update(zahlen(df_partner['act']))

            #'Cut' the dfs to the same length for comparison
            begin_partner=df_partner['time_column'].iloc[0]
            end_partner=df_partner['time_column'].iloc[-1]

            if begin_partner > begin_client:
                begin=begin_partner
            else:
                begin=begin_client
            if end_partner > end_client:
                end=end_client
            else:
                end=end_partner

            df=df.loc[(df['time_column'] >= begin) & (df['time_column'] <= end)]
            df_partner=df_partner.loc[(df_partner['time_column'] >= begin) & (df_partner['time_column'] <= end)]

            #Insert Act and Mov_Act of partner to main df
            df.insert(0, 'mov_act_partner', avgval(df_partner, 'act', moving_avg_val), True)
            df.insert(0, 'act_partner', df_partner['act'])

    #Includes a column called 'day_identifier' which is needed for plotting later
    df=set_day_identifier(df)
    #Beginning of Main Part
    #Plotting of averaged Data and Creation of Simple Histograms
    if night==True:
        #Gives sleep-onsets and sleep-offsets for each day, as well as earliest and latest value for plotting
        beginlist, endlist, begin_time, end_time=get_sleep_onset_offset(df, 'act', 20)
        #Plots Moving Average of Activity of Client (and Partner) with sleep-onset and sleep-offsets. Xlims are defines as earliest sleep-onset - 1hour and latest sleep-offset + 1 hour of client
        plot_single_days(df, 'mov_act', 'mov_act_partner', 7, current_subjects, i, night, partner, beginlist, endlist, begin_time, end_time)
        #Creates Hist of Actvity Data between sleep-onset and sleep-offset of each day (not normalized to duration!) for client and partner
        simple_hist(df, 'act', 'act_partner', 500, 10, current_subjects, i, partner, beginlist, endlist)
    else:
        #Plots Moving Average of Activity of Client (and Partner). Xlims are defined by timelimit1 and timelimit2.
        #(of yourse you can only plot nights with defined begnning and end (e.g. timelimit1=19 and timelimit2=11))
        plot_single_days(df, 'mov_act', 'mov_act_partner', 7, current_subjects, i, night, partner)
        #Create hists of Activity Data between timelimit1 and timelimit2 for client (and partner)
        simple_hist(df, 'act', 'act_partner', 800, 10, current_subjects, i, partner)

    #Further Visualization
    if partner==True:
        #Creates Hourly Means between timelimit1 and timelimit2. Calculates L5, M10 and RA
        #Returns List of hourly means for every day
        meanlist, meanlist_p, act_hour_c, act_hour_p, hourlist=mean_hourly_activity(df, 'act', partner, current_subjects, i, 'act_partner')

        activity_on_clock(current_subjects, i, meanlist, hourlist, meanlist_p,partner)
        activity_hist_on_clock(current_subjects, i, act_hour_c,  hourlist, 5, 100, act_hour_p, partner)
    else:
        #Creates Hourly Means between timelimit1 and timelimit2. Calculates L5, M10 and RA
        #Returns List of hourly means for every day
        meanlist, act_hour_c, hourlist=mean_hourly_activity(df, 'act', partner, current_subjects, i)

        activity_on_clock(current_subjects, i, meanlist, hourlist, 5, 100)
        activity_hist_on_clock(current_subjects, i, act_hour_c,  hourlist, 5, 100)
