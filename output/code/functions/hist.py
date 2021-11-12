import matplotlib.pyplot as plt
import matplotlib.colors as mp_colors
import matplotlib.cm as cm
import numpy as np
import datetime
from datetime import datetime as dt_mod
from datetime import time
from datetime import timedelta
import pandas as pd
import itertools

#Sets the beginning of hourly means. Should typically be equal to timelimit1
global timedelta1
timedelta1=3

#Creates Hist of Client (and Partner) Data between timelimits. Zeros are not Plotted. Bins are shown until xlim
def simple_hist(df, value, value2, xlim, binwidth, current_subjects, i, partner, beginlist=[], endlist=[]):
    plt.rcParams["figure.figsize"] = (7, 6)
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams.update({'font.size': 10})

    fig, axs=plt.subplots(7, sharex=True)
    if beginlist==[]:
        for k in range(0, 7):
            data=df.loc[(df['day_identifier']==k)][value]
            axs[k].hist(data, bins=np.arange(1, xlim + binwidth, binwidth), color='gray', edgecolor='black', linewidth=1)
            if partner==True:
                data2=df.loc[(df['day_identifier'] ==k)][value2]
                axs[k].hist(data2, bins=np.arange(1, xlim + binwidth, binwidth), color='dodgerblue', edgecolor='black', linewidth=1, alpha=0.6)
                plt.tight_layout(pad=2, h_pad=0.5)
    else:
        for k in range(len(beginlist)):
            data=df.loc[(df['time_column'] > beginlist[k]) & (df['time_column']<endlist[k])][value]
            axs[k].hist(data, bins=np.arange(1, xlim + binwidth, binwidth), color='gray', edgecolor='black', linewidth=1)
            if partner == True:
                data2=df.loc[(df['time_column'] > beginlist[k]) & (df['time_column']<endlist[k])][value2]
                axs[k].hist(data2, bins=np.arange(1, xlim + binwidth, binwidth), color='dodgerblue', edgecolor='black', linewidth=1, alpha=0.6)
                plt.tight_layout(pad=2, h_pad=0.5)

    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)

    plt.xlabel("Counts")
    plt.ylabel("Frequency")

    plt.savefig('output/'+current_subjects[i]+'/'+current_subjects[i]+'_hist.pdf')
    plt.close()

#Creates Hourly Means between timelimit1 and timelimit2. Calculates L5, M10 and RA.
#L5 ist the mean value of 5 consecutive hours with the lowest acitivity value
#M10 is the mean value of 10 consecutive hours with the highest acitivity value
#RA is the contrast of L5 and M10. It is typically lower for bad sleep.
def mean_hourly_activity(df, value, partner, current_subjects, i, value2=False):
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams.update({'font.size': 10})
    plt.rcParams['figure.figsize'] = (7, 6)
    plt.rcParams['lines.linewidth'] =2
    value_list=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    value_list_c_raw=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for k in range(0, 7):
        for m in range(0, 24):
            start=df.loc[(df['day_identifier'] == k)]['time_column'].to_list()[0]
            entry=df.loc[(df['day_identifier'] == k) & (df['time_column'] >= start+timedelta(hours=m)) & (df['time_column'] < start+timedelta(hours=m+1))][value].mean()
            entry_raw=df.loc[(df['day_identifier'] == k) & (df['time_column'] >= start+timedelta(hours=m)) & (df['time_column'] < start+timedelta(hours=m+1))][value].to_list()
            value_list[m].append(entry)
            value_list_c_raw[m].append(entry_raw)

    value_list_c_mean=[np.nanmean(entry) for entry in value_list]
    L5, M10, RA=find_RA(value_list_c_mean)

    fig = plt.figure()
    ax = plt.axes()
    plt.grid(axis='y')
    ax.bar(np.arange(0, 24, 1), value_list_c_mean, color='gray', linewidth=1, edgecolor='black', label='RA: '+str(np.round(RA, 2)))
    mylist=[dt_mod.strftime(entry, '%H') for entry in pd.date_range(datetime.datetime.combine(datetime.date.today(), time(timedelta1)), datetime.datetime.combine(datetime.date.today()+timedelta(days=1), time(timedelta1-1)), freq='H')]
    ax.set_xticks(np.arange(0, 24, 1))
    ax.set_xticklabels([entry for entry in mylist])
    ax.hlines([L5, M10], -0.5, 23.5, color='black', linestyle='solid', linewidth=1.5, label='L5: '+str(np.round(L5, 2))+ '\n'+'M10: '+str(np.round(M10, 2)))

    if partner==True:
        value_list=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        value_list_p_raw=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        for k in range(0, 7):
            for m in range(0, 24):
                start=df.loc[(df['day_identifier'] == k)]['time_column'].to_list()[0]
                entry=df.loc[(df['day_identifier'] == k) & (df['time_column'] >= start+timedelta(hours=m)) & (df['time_column'] < start+timedelta(hours=m+1))][value2].mean()
                entry_raw=df.loc[(df['day_identifier'] == k) & (df['time_column'] >= start+timedelta(hours=m)) & (df['time_column'] < start+timedelta(hours=m+1))][value2].to_list()
                value_list[m].append(entry)
                value_list_p_raw[m].append(entry_raw)

        value_list_p_mean=[np.nanmean(entry) for entry in value_list]
        L5, M10, RA=find_RA(value_list_p_mean)

        ax.bar(np.arange(0, 24, 1), value_list_p_mean, color='dodgerblue', linewidth=1, edgecolor='black', alpha=0.7, label='RA: '+str(np.round(RA, 2)))
        ax.hlines([L5, M10], -0.5, 23.5, color='darkblue', linestyle='solid', linewidth=1.5, label='L5: '+str(np.round(L5, 2))+ '\n'+'M10: '+str(np.round(M10, 2)))


    plt.xlabel('Hours')
    plt.ylabel('Mean Activity in Counts')
    plt.legend()
    plt.savefig('output/'+current_subjects[i]+'/'+current_subjects[i]+'_RA.pdf')
    plt.close()
    if partner ==True:
        return value_list_c_mean, value_list_p_mean, value_list_c_raw, value_list_p_raw, mylist
    else:
        return value_list_c_mean, value_list_c_raw, mylist

#finds M10 and L5 and calculates RA
def find_RA(mylist):
    raster_list=mylist+mylist
    neg_raster_list=[-x for x in raster_list]

    M10_idx, M10=find_periods(raster_list, 10)
    L5_idx, L5=find_periods(neg_raster_list, 5)

    RA=(M10-L5)/(M10+L5)

    return L5, M10, RA

#finds periods of length period with maximal mean value in mylist
def find_periods(mylist, period):
    decide=[]
    for k in range(0, 24):
        value=np.mean(mylist[k:k+period])
        decide.append(value)

    value=np.abs(np.max(decide))
    idx=np.argmax(decide)

    return idx, value

#sets new edge colors for colormap
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = mp_colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

#Plots mean activity per hour as pie chart for client (and partner)
def activity_on_clock(current_subjects, i, meanlist,  hourlist, meanlist_p=[], partner=False):
    plt.rcParams['figure.figsize'] = (7, 7)
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams.update({'font.size': 10})
    cmap = plt.cm.get_cmap('Blues')
    new_cmap = truncate_colormap(cmap, 0.2, 1)
    cmap=new_cmap

    df_clock=pd.DataFrame()
    df_clock['times']=hourlist
    df_clock['means']=meanlist


    sizes=[8.3]*12


    if partner == True:
        df_clock['means_p']=meanlist_p
        df_clock.sort_values(by='times', inplace=True)
        labels=df_clock['times'].to_list()
        means=df_clock['means'].to_list()
        means_p=df_clock['means_p'].to_list()
        if max(means) > max(means_p):
            bigger_list=means
            colors=[cmap((entry/np.sum(bigger_list))*10) for entry in means]
            colors_p=[cmap((entry/np.sum(bigger_list))*10) for entry in means_p]
        else:
            bigger_list=means_p
            colors=[cmap((entry/np.sum(bigger_list))*10) for entry in means]
            colors_p=[cmap((entry/np.sum(bigger_list))*10) for entry in means_p]
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        ax1.pie(sizes,
              labels=labels[0:12], counterclock=False, startangle=90, radius=1,
              colors=colors[0:12], explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ))
        ax1.set_title('Mean Activity of Client', loc='left')

        ax2.pie(sizes,
              labels=labels[12:], counterclock=False, startangle=90, radius=1,
              colors=colors[12:], explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ))

        ax3.pie(sizes,
              labels=labels[0:12], counterclock=False, startangle=90, radius=1,
              colors=colors_p[0:12], explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ))
        ax3.set_title('Mean Activity of Partner', loc='left')

        ax4.pie(sizes,
              labels=labels[12:], counterclock=False, startangle=90, radius=1,
              colors=colors_p[12:], explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ))

    else:
        df_clock.sort_values(by='times', inplace=True)
        labels=df_clock['times'].to_list()
        means=df_clock['means'].to_list()
        bigger_list=means
        colors=[cmap((entry/np.sum(means))*10) for entry in means]
        fig, ((ax1, ax2)) = plt.subplots(1, 2)
        ax1.pie(sizes,
              labels=labels[0:12], counterclock=False, startangle=90, radius=1,
              colors=colors[0:12], explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ))
        ax1.set_title('Mean Activity of Client', loc='left')
        ax2.pie(sizes,
              labels=labels[12:], counterclock=False, startangle=90, radius=1,
              colors=colors[12:], explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ))
              #colors=[colours[key] for key in labels[1:]])
    cbar_ax = fig.add_axes([0.1, 0.05, 0.8, 0.02])
    cbar=fig.colorbar(cm.ScalarMappable(cmap=cmap), cax=cbar_ax, orientation='horizontal', ticks=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    cbar.set_ticklabels([int(np.round(item*max(bigger_list), 0)) for item in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]])
    plt.savefig('output/'+current_subjects[i]+'/'+current_subjects[i]+'_clock.pdf')
    plt.close()

#Plots mean activity per hour in pie chart as 'bins'.
#Number: Number of bins
#Binwidth: Binwidth in Counts
#Calculates the proportion of one bin (e.g. values between 100 and 200) in one hour
#Shows this proportion as proportion of radius in this color for each wedge
#Zeros are not taken into account!
def activity_hist_on_clock(current_subjects, i, act_hour_c,  hourlist, number, binwidth, act_hour_p=[], partner=False):
    plt.rcParams['figure.figsize'] = (7, 7)
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams.update({'font.size': 10})
    sizes=[8.3]*12
    #define colors
    cmap = truncate_colormap(plt.cm.get_cmap('Blues'), 0.2, 1)
    colors=[cmap(entry) for entry in np.linspace(0, 1, number+1)]

    #sort values to start with 00:00
    df_clock=pd.DataFrame()
    df_clock['times']=hourlist
    df_clock.sort_values(by='times', inplace=True)
    labels=df_clock['times'].to_list()
    act_hour_c=act_hour_c+act_hour_c
    act_hour_c=act_hour_c[df_clock.index[0]:df_clock.index[0]+24]


    if partner==True:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        slist=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        #sort values of partner
        act_hour_p=act_hour_p+act_hour_p
        act_hour_p=act_hour_p[df_clock.index[0]:df_clock.index[0]+24]
        lenlist=[]

        #Find proportion of each bin for every hour
        for m in range(len(act_hour_c)):
            mylist=list(itertools.chain.from_iterable(act_hour_c[m]))
            lenlist.append(len(mylist)-mylist.count(0))

            for k in range(0, number+1):
                if k ==number:
                    slist[m].append(len([entry for entry in mylist if (entry > k*binwidth)]))
                else:
                    slist[m].append(len([entry for entry in mylist if (entry > k*binwidth) & (entry <=(k+1)*binwidth)]))

        p_all=[]
        for k in range(len(slist)):
            plist=[entry/lenlist[k] for entry in slist[k]]
            p_all.append(plist)

        #Plot pie charts with proportion of bins as proportion of radius. (Starts with radius=1 an then adds pie charts with smaller radii)
        for k in range(0, number+1):
            for m in range(0, 12):
                hour=p_all[m]
                if k == 0 and m == 0:
                    pie1=ax1.pie(sizes, labels=labels[0:12], counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                    ax1.set_title('Mean Activity of Client', loc='left')
                else:
                    pie1=ax1.pie(sizes, counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                for q in range(0, 12):
                    if q !=m:
                        pie1[0][q].set_alpha(0)
                    else:
                        pie1[0][q].set_alpha(1)

                if k==0:
                    before=0
                else:
                    before=np.sum(hour[0:k-1])
                pie1[0][m].set_radius(1-before)
                pie1[0][m].set_facecolor(colors[k])


            for m in range(12, 24):
                hour=p_all[m]
                if k == 0 and m == 12:
                    pie2=ax2.pie(sizes, labels=labels[12:], counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')

                else:
                    pie2=ax2.pie(sizes, counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                for q in range(0, 12):
                    if q !=m-12:
                        pie2[0][q].set_alpha(0)
                    else:
                        pie2[0][q].set_alpha(1)
                if k==0:
                    before=0
                else:
                    before=np.sum(hour[0:k-1])
                pie2[0][m-12].set_radius(1-before)
                pie2[0][m-12].set_facecolor(colors[k])
        #repeat for partner
        slist=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

        lenlist=[]
        for m in range(len(act_hour_p)):
            mylist=list(itertools.chain.from_iterable(act_hour_p[m]))
            lenlist.append(len(mylist)-mylist.count(0))

            for k in range(0, number+1):
                if k ==number:
                    slist[m].append(len([entry for entry in mylist if (entry > k*100)]))
                else:
                    slist[m].append(len([entry for entry in mylist if (entry > k*100) & (entry <=(k+1)*100)]))

        p_all=[]
        for k in range(len(slist)):
            plist=[entry/lenlist[k] for entry in slist[k]]
            p_all.append(plist)

        #Plot pie charts with proportion of bins as proportion of radius. (Starts with radius=1 an then adds pie charts with smaller radii)
        for k in range(0, number+1):
            for m in range(0, 12):
                hour=p_all[m]
                if k == 0 and m == 0:
                    pie1=ax3.pie(sizes, labels=labels[0:12], counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                    ax3.set_title('Mean Activity of Partner', loc='left')

                else:
                    pie1=ax3.pie(sizes, counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                for q in range(0, 12):
                    if q !=m:
                        pie1[0][q].set_alpha(0)
                    else:
                        pie1[0][q].set_alpha(1)

                if k==0:
                    before=0
                else:
                    before=np.sum(hour[0:k-1])
                pie1[0][m].set_radius(1-before)
                pie1[0][m].set_facecolor(colors[k])


            for m in range(12, 24):
                hour=p_all[m]
                if k == 0 and m == 12:
                    pie2=ax4.pie(sizes, labels=labels[12:], counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                else:
                    pie2=ax4.pie(sizes, counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                for q in range(0, 12):
                    if q !=m-12:
                        pie2[0][q].set_alpha(0)
                    else:
                        pie2[0][q].set_alpha(1)
                if k==0:
                    before=0
                else:
                    before=np.sum(hour[0:k-1])
                pie2[0][m-12].set_radius(1-before)
                pie2[0][m-12].set_facecolor(colors[k])
        cbar_ax = fig.add_axes([0.1, 0.05, 0.8, 0.02])
        cbar=fig.colorbar(cm.ScalarMappable(cmap=cmap), cax=cbar_ax, orientation='horizontal', spacing='proportional', boundaries=np.linspace(0.2, 1, number+1), ticks=np.linspace(0.2, 1, number+1)[1:-1], format='%1i')
        cbar.set_ticklabels([entry*binwidth for entry in np.arange(1, number, 1)])
    else:
        #Find proportion of each bin for every hour
        fig, ((ax1, ax2)) = plt.subplots(1, 2)
        slist=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        act_hour_p=act_hour_p+act_hour_p
        act_hour_p=act_hour_p[df_clock.index[0]:df_clock.index[0]+24]
        lenlist=[]
        for m in range(len(act_hour_c)):
            mylist=list(itertools.chain.from_iterable(act_hour_c[m]))
            lenlist.append(len(mylist)-mylist.count(0))

            for k in range(0, number+1):
                if k ==number:
                    slist[m].append(len([entry for entry in mylist if (entry > k*binwidth)]))
                else:
                    slist[m].append(len([entry for entry in mylist if (entry > k*binwidth) & (entry <=(k+1)*binwidth)]))

        p_all=[]
        for k in range(len(slist)):
            plist=[entry/lenlist[k] for entry in slist[k]]
            p_all.append(plist)


        for k in range(0, number+1):
            for m in range(0, 12):
                hour=p_all[m]
                if k == 0 and m == 0:
                    pie1=ax1.pie(sizes, labels=labels[0:12], counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                    ax1.set_title('Mean Activity of Client', loc='left')
                else:
                    pie1=ax1.pie(sizes, counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                for q in range(0, 12):
                    if q !=m:
                        pie1[0][q].set_alpha(0)
                    else:
                        pie1[0][q].set_alpha(1)

                if k==0:
                    before=0
                else:
                    before=np.sum(hour[0:k-1])
                pie1[0][m].set_radius(1-before)
                pie1[0][m].set_facecolor(colors[k])


            for m in range(12, 24):
                hour=p_all[m]
                if k == 0 and m == 12:
                    pie2=ax2.pie(sizes, labels=labels[12:], counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                else:
                    pie2=ax2.pie(sizes, counterclock=False, startangle=90, explode=(0.01, 0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01 ), colors='w')
                for q in range(0, 12):
                    if q !=m-12:
                        pie2[0][q].set_alpha(0)
                    else:
                        pie2[0][q].set_alpha(1)
                if k==0:
                    before=0
                else:
                    before=np.sum(hour[0:k-1])
                pie2[0][m-12].set_radius(1-before)
                pie2[0][m-12].set_facecolor(colors[k])
        cbar_ax = fig.add_axes([0.1, 0.05, 0.8, 0.02])
        cbar=fig.colorbar(cm.ScalarMappable(cmap=cmap), cax=cbar_ax, orientation='horizontal', spacing='proportional', boundaries=np.linspace(0.2, 1, number+1), ticks=np.linspace(0.2, 1, number+1)[1:-1], format='%1i')
        cbar.set_ticklabels([entry*binwidth for entry in np.arange(1, number, 1)])

    plt.savefig('output/'+current_subjects[i]+'/'+current_subjects[i]+'_clock_hist.pdf')
    plt.close()
