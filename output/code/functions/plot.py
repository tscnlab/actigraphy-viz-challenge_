import datetime
from datetime import datetime as dt_mod
from datetime import time
from datetime import timedelta
from matplotlib.backends.backend_pdf import PdfPages
from itertools import chain, repeat, groupby
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from operator import itemgetter

global timelimit1
timelimit1=3
global timelimit2
timelimit2=3


#Plots Activity of client (and partner) for single days as rows in one pdf
def plot_single_days(df, value, value2, rowlength, current_subjects, i, night, partner, beginlist=[], endlist=[], begin_time=[], end_time=[]):
    a, b, df_one=find_working_days(0, 0, df)
    df_interest=df_one.filter(items=['time_column', value , value2, 'day_identifier', 'day', 'only_time'])

    grouped = df_interest.groupby('day_identifier')
    pdf_pages = PdfPages('output/'+current_subjects[i]+'/'+value+'_'+current_subjects[i]+'_'+'overview.pdf')
    fig=plot_multiple_within_single(rowlength, grouped, value, value2, current_subjects, i, night, partner, beginlist, endlist, begin_time, end_time)
    pdf_pages.savefig(fig, bbox_inches='tight')

    pdf_pages.close()
    plt.close(fig)
    plt.clf()
    plt.close()

#Plots one row (with sleep-onset and -offset if night==True)
def plot_multiple_within_single(rowlength, grouped, value, value2, current_subjects, i, night, partner, beginlist, endlist, begin_time, end_time):
    weekdaystr=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    plt.rcParams['lines.linewidth'] =1.5
    plt.rcParams.update({'font.size': 5})
    hours = mdates.HourLocator(interval = 1)  #
    h_fmt = mdates.DateFormatter('%H')

    fig, axs = plt.subplots(figsize=(13,9) , nrows=rowlength, ncols=1, gridspec_kw=dict(width_ratios=[13], height_ratios=[11, 9, 9, 9, 9, 9, 9], hspace=0.5))#, sharex=True) # Much control of gridspec
    plt.setp(plt.gca().xaxis.get_majorticklabels(),
         'rotation', 90)
    targets = zip(grouped.groups.keys(), axs.flatten())

    for m, (key, ax) in enumerate(targets):


        #Create x-values as today+times
        plotx=[]
        for entry in grouped.get_group(key)['time_column']:
            thisday=grouped.get_group(key)['day'].to_list()[0]
            if entry.date() == thisday:
                timee=datetime.datetime.combine(datetime.date.today(), entry.time())
                plotx.append(timee)
            elif entry.date() == thisday+timedelta(days=1):
                timee=datetime.datetime.combine(datetime.date.today()+timedelta(days=1), entry.time())
                plotx.append(timee)

        #Plot Activity of Client
        ax.plot(plotx, grouped.get_group(key)[value], '-', color='black', label='Activity of Client in Counts')
        #Plot Activity of Partner
        if partner ==True:
            ax2 = ax.twinx()
            ax2.tick_params(axis='y', labelcolor='dodgerblue')
            ax2.plot(plotx, grouped.get_group(key)[value2], '-', color='dodgerblue', alpha=0.7, label='Activity of Partner in Counts')



        ax.set_title('date='+grouped.get_group(key)['day'].to_list()[0].strftime('%m/%d/%Y')+','+weekdaystr[grouped.get_group(key)['day'].to_list()[0].weekday()])

        #Plots Sleeplimits of Client and sets xlims
        if night ==True:
            if beginlist[m].time() > time(timelimit1, 0, 0):
                sleep_onset=datetime.datetime.combine(datetime.date.today(), beginlist[m].time())
            else:
                sleep_onset=datetime.datetime.combine(datetime.date.today()+timedelta(days=1), beginlist[m].time())
            sleep_offset=datetime.datetime.combine(datetime.date.today()+timedelta(days=1), endlist[m].time())

            if begin_time < time(timelimit1, 0, 0):
                xlim1=datetime.datetime.combine(datetime.date.today()+timedelta(days=1), begin_time)-timedelta(hours=0.5)
            else:
                xlim1=datetime.datetime.combine(datetime.date.today(), begin_time)-timedelta(hours=0.5)
            xlim2=datetime.datetime.combine(datetime.date.today()+timedelta(days=1), end_time)+timedelta(hours=0.5)
            ax.vlines([sleep_onset, sleep_offset], [0, 0], [ax.get_ylim()[1], ax.get_ylim()[1]], colors=['red', 'red'])
            ax.set_xlim(xlim1, xlim2)
            if partner == True:
                ax2.set_xlim(xlim1, xlim2)
        #Set xlims to timelimit1 and timelimit2
        else:
            ax.set_xlim(datetime.datetime.combine(datetime.date.today(), time(timelimit1)), datetime.datetime.combine(datetime.date.today()+timedelta(days=1), time(timelimit2)))
            if partner == True:
                ax2.set_xlim(datetime.datetime.combine(datetime.date.today(), time(timelimit1)), datetime.datetime.combine(datetime.date.today()+timedelta(days=1), time(timelimit2)))
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(h_fmt)

        #Creates Legend in first row
        if m==0:
            ax.legend(fontsize='xx-large', loc=2)
            if partner == True:
                ax2.legend(fontsize='xx-large', loc=1)


    return fig

#Can be used to delete beginning or end if detectors are not worn immediately
def find_working_days(begin, end, df):
    first_day=df.iloc[0]['time_column'].date()

    start_day=dt_mod.combine(first_day+timedelta(days=begin), datetime.time(timelimit1, 0, 0))

    last_day=df.iloc[-1]['time_column'].date()
    end_day=dt_mod.combine(last_day-timedelta(days=end), datetime.time(23, 59, 00))

    new_df=df=df[(df['time_column'] >= start_day) & (df['time_column'] <= end_day)]
    return start_day, end_day, new_df

#Sets day identifier for one day (defined as timelimit1 to timelimit2 and not frim midnight)
def set_day_identifier(df):
    df.insert(0, 'day', df['time_column'].dt.date, True)
    df.insert(0, 'day_identifier', [100]*len(df['day']))
    all_days=df.day.unique()
    for q in range(len(all_days)):
        day=all_days[q]
        df_oneday=df.loc[(df['time_column'] >= datetime.datetime.combine(day, time(timelimit1, 0, 0))) & (df['time_column'] < datetime.datetime.combine(day+timedelta(days=1), time(timelimit1, 0, 0)))]
        indexes=df_oneday.index
        df.loc[[entry for entry in indexes], 'day_identifier']=q

    return df

def get_continouos_intervals(basiclist, timelimit, type):
    mylist=[]
    endlist=[]
    for k, g in groupby(enumerate(basiclist), lambda ix : ix[0] - ix[1]):
        mymap=list(map(itemgetter(1), g))
        mylist.append(mymap)
    for entry in mylist:
        if len(entry)>=timelimit:
            endlist.append(entry[type])
    return endlist

#Calculates Sleep-Onset and Sleep-Offset for each night. Return all Values as list and smallest and highest value for later Plotting. Here, a very simple (an not accurate) sleep algorithm is used.
#Of course, it can be replaced by your on. Also, if diary data is available, beginlist, endlist, begin_time and end_time can be gained from this data or the sleep algorithm can be
#adjusted to only look for sleep onset and offset at times near the times that subjects gave in their diaries.
def get_sleep_onset_offset(df, value, timelimit):
    beginlist=[]
    endlist=[]
    for k in range(0, 7):
        df_oneday=df.loc[df['day_identifier'] == k]
        #Gives Sleep-Onset and Sleep-Offset for one Day
        begin, end=get_sleep_identification(df_oneday, timelimit, value)
        beginlist.append(begin)
        endlist.append(end)
    begin_time_list=[value.time() for value in beginlist if value.time() > time(timelimit1, 0, 0)]
    if begin_time_list == []:
        begin_time=min([entry.time() for entry in beginlist])
    else:
        begin_time=min(begin_time_list)
    end_time=max([entry.time() for entry in endlist])
    return beginlist, endlist, begin_time, end_time

#Gives sleep Sleep-Onset and Sleep-Offset for one Day
#Uses algorithm to create other moving average
#Looks for values under limit (here as 0.88*grand_mean)
#If periods are longer than timelimit they are defined as sleep
#returns beginning of first sleep phase and end of last sleep phase
def get_sleep_identification(df, timelimit, value, limit=False):
    valuelist=[]
    sleeplist=[]
    sleepindex=[]
    if limit == False:
        limit=(df[value].sum()/len(df[value]))*0.88
    start=datetime.datetime.combine(df['time_column'].iloc[0].date(), time(timelimit1, 0, 0))
    stop=datetime.datetime.combine(df['time_column'].iloc[0].date()+timedelta(days=1), time(timelimit2, 0, 0))
    mylist=df.loc[(df['time_column'] > start) & (df['time_column'] < stop)][value].tolist()
    for k in range(4, len(mylist)-4):
        value=mylist[k-4]/25+mylist[k-3]/25+mylist[k-2]/5+mylist[k-1]/5+mylist[k]*2+mylist[k+1]/5+mylist[k+2]/5+mylist[k+3]/25+mylist[k+4]/25
        valuelist.append(value)
        if value<=limit:
            sleeplist.append(0)
            sleepindex.append(k)
        else:
            sleeplist.append(1)
    begin=df['time_column'].iloc[get_continouos_intervals(sleepindex, timelimit, 0)[0]]
    end=df['time_column'].iloc[get_continouos_intervals(sleepindex, timelimit, -1)[-1]]


    return begin, end
