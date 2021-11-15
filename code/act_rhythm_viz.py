## import dependecies
import pyActigraphy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from os.path import isfile
from glob import glob
from astral.geocoder import database, lookup
from astral.sun import sun


## define functions
# function list:
# 1) calc_period
# 2) map_daylight
# 3) define_structures
# 4) plot_rhythmic_structure

def calc_period(signal, constrain=1800):
    """
    This function takes a numpy array 'signal' and calculates the main frequency (period) of this signal through
    fast fourier transform (FFT). The period can be constrained by adding a maximum in the constrain param.

    :param signal: signal for which to calculate the frequency
    :type signal: np.array
    :param constrain: gives the maximum period to take into account
    :type constrain: int
    :return: period of the signal in minutes
    :rtype: float
    """
    # Perform FFT and determine associated frequencies
    x = np.fft.fft(signal)
    freq = np.fft.fftfreq(len(signal))

    # Take only positive part of symmetrical spectrum
    x = x[freq >= 0]
    freq = freq[freq >= 0]

    # Constrain frequency so it has a maximum value
    limit = 1 / constrain
    x = x[freq >= limit]
    freq = freq[freq >= limit]

    # Take all values
    x = abs(x.real)

    period = 1 / freq[np.argmax(x)]

    return period


def map_daylight(dat, location='Melbourne'):
    """
    This function takes actigraphy data as an input, extracts the dates and times for which there is daylight
    during this period at a specific location and return a np.array containing the values.
    Note that values are 1 between sunrise and sunset and 0 between dawn and dusk. There is a linear increase/
    decrease between sunrise and dawn and sunset and dusk, respectively.
    :param dat: actigraphy data loaded through pyActigraphy
    :type dat: pyActigraphy object
    :param location: Major city with the same timezone as where the data is collected. Default='Melbourne'
    :type location: string
    :return: Array with value between 0-1 determing the amount of sunlight at location, for every timepoint in the data
    :rtype: np.array
    """
    city = lookup(location, database())
    dti = pd.date_range(dat.light.index[0].date(), periods=np.ceil(data_len / 1440) * 1440, freq="min")
    all_dates = dti.map(pd.Timestamp.date).unique()
    sunlight = np.zeros((len(dti)))
    for date in all_dates:
        s = sun(city.observer, date=date, tzinfo=city.timezone)

        dawn_idx = dti.get_loc(s['dawn'].replace(tzinfo=None), method='nearest')
        sunrise_idx = dti.get_loc(s['sunrise'].replace(tzinfo=None), method='nearest')
        sunset_idx = dti.get_loc(s['sunset'].replace(tzinfo=None), method='nearest')
        dusk_idx = dti.get_loc(s['dusk'].replace(tzinfo=None), method='nearest')

        sunlight[np.arange(dawn_idx, sunrise_idx)] = np.linspace(0, 1, sunrise_idx - dawn_idx)
        sunlight[np.arange(sunrise_idx, sunset_idx)] = 1
        sunlight[np.arange(sunset_idx, dusk_idx)] = np.linspace(1, 0, dusk_idx - sunset_idx)

    first_idx = dti.get_loc(dat.light.index[0], method='nearest')
    last_idx = dti.get_loc(dat.light.index[-1], method='nearest')
    sunlight = sunlight[np.arange(first_idx, last_idx + 1)]

    return sunlight


def define_structures(iSSA, max_minutes, min_minutes, data_len, n=10, max_len=1800):
    """
    Takes the SSA output from pyActigraphy and uses this, along with binning information, to generate a matrix in which
    every row is the normalized, reconstructed signal, weighted by importance of the first n important signals. The
    intended use of this matrix is to display as heatmap to show the relative strengths of rhythms in each period bin.
    :param iSSA: Object that contains a decomposition of the raw actigraphy data into its rhythmic components, along
    a weight (proportion of explained variance by this rhythm)
    :type iSSA: pyActigraphy.analysis.ssa.SSA object
    :param max_minutes: binning information, containing the ends of each bin
    :type max_minutes: numpy array
    :param min_minutes: binning information, containing the starts of each bin
    :type min_minutes: numpy array
    :param data_len: Amount of observations in the data (and reconstructed rhythms by SSA)
    :type data_len: int
    :param n: The first n important signals to reconstruct. Default=10
    :type n: int
    :param max_len: Maximum period that is included in minutes. Default=1800
    :type max_len: int
    :return: Matrix containing the strength of the binned rhythm per timepoint
    :rtype: numpy matrix
    """
    # pre-allocation of matrix capturing rhythms and weights per bin
    structures = np.zeros((len(max_minutes), data_len))

    # loop over all signals to reconstruct to create matrix for heatmap
    for iReconstructed in np.arange(1, n+1):
        # reconstruct signal
        reconstructed_signal = iSSA.X_tilde(iReconstructed)

        # calculate period and extract associated weight
        period = calc_period(reconstructed_signal, max_len)
        weight = iSSA.lambda_s[iReconstructed]

        # find index of period bins
        struct_idx = np.where(np.logical_and(period >= min_minutes, period < max_minutes))

        # normalize the signal
        reconstructed_signal_norm = (reconstructed_signal - np.min(reconstructed_signal)) \
                                    / np.ptp(reconstructed_signal)

        # weight the signal
        reconstructed_signal_norm *= weight

        # add to structure matrix
        if np.any(structures[struct_idx]):
            structures[struct_idx] = reconstructed_signal_norm + structures[struct_idx]  # / 2
        else:
            structures[struct_idx] = reconstructed_signal_norm

    return structures


def plot_rhythmic_structure(dat, iSSA, data_len, city, n=10, max_len=1800, plot_daylight=True, plot_light=True,
                            display_title='all', plot=True, save=False, save_location='C:/'):
    """
    This function plots the figure that shows the relative strength of each rhythm bin over the raw actigraphy signal,
    optionally complemented by an important driving factor light (either daylight or light exposure as measured by the
    actigraphy device.
    :param dat: Raw actigraphy data loaded by pyActigraphy
    :type dat: pyActigraphy.io object
    :param iSSA: Object that contains a decomposition of the raw actigraphy data into its rhythmic components, along
    a weight (proportion of explained variance by this rhythm)
    :type iSSA: pyActigraphy.analysis.ssa.SSA object
    :param data_len: Number of observations in the data
    :type data_len: int
    :param city: City in which the same timezone is active as where the actigraphy was recorded
    :type city: string
    :param n: The first n important signals to reconstruct and include in the figure. Default=10
    :type n: int
    :param max_len: Maximum period that is included in minutes. Default=1800
    :type max_len: int
    :param plot_daylight: Determines if daylight is calculated and plotted
    :type plot_daylight: bool
    :param plot_light: Determines if any recorded light exposure is plotted
    :type plot_light: bool
    :param display_title: Determines if a title is displayed above the figure with a short description. Default='all'
    :type display_title: str, options: 'all', 'file', 'no'
    :param plot: Determines if the figure is plotted. Default=True
    :type plot: bool
    :param save: Determines if the figure is saved. Default=False
    :type save: bool
    :param save_location: Determines where the figure is saved. Default='C:/'
    :type save_location: str
    :return: figure
    :rtype: figure
    """
    # period bins for the reconstructed signal are constructed.
    # For clarity, now 4-hour bins are constructed until max_len,
    # with the exception of a start bin for the first 2 hours that are binned together
    # (because this contains the most signal)
    min_minutes = np.arange(120, max_len, 240)
    min_minutes = np.insert(min_minutes, 0, 0)
    max_minutes = np.arange(360, max_len + 1, 240)
    max_minutes = np.insert(max_minutes, 0, 120)

    # find the rhythmic structure in the data
    structures = define_structures(iSSA, max_minutes, min_minutes, data_len, n, max_len)

    # Now start generating figure
    n_plots = plot_daylight + plot_light + 1

    # check how many plots are requested and create them
    if n_plots == 3:
        day_idx = 0
        exp_idx = 1
        main_idx = 2
        fig, ax = plt.subplots(n_plots, 1, gridspec_kw={'height_ratios': [1, 1, 8]})
    elif n_plots == 2:
        if plot_daylight:
            day_idx = 0
        elif plot_light:
            exp_idx = 0
        main_idx = 1
        fig, ax = plt.subplots(n_plots, 1, gridspec_kw={'height_ratios': [1, 7]})
    elif n_plots == 1:
        main_idx = 0
        fig, ax = plt.subplots()

    # start with light figures

    # create daylight plot
    if plot_daylight:
        # get sunlight during the recording at the nearest city
        sunlight = map_daylight(dat, city)

        # plot heatmap without borders
        ax[0].imshow(np.transpose(np.expand_dims(sunlight, 1)),
                     aspect='auto',
                     alpha=.8,
                     cmap='gray',
                     interpolation='nearest')
        ax[day_idx].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        ax[day_idx].spines['top'].set_visible(False)
        ax[day_idx].spines['right'].set_visible(False)
        ax[day_idx].spines['bottom'].set_visible(False)
        ax[day_idx].spines['left'].set_visible(False)
        ax[day_idx].set_ylabel('Daylight', rotation='horizontal', labelpad=25)

    # create light exposure plot
    if plot_light:
        # extract, remove nan and normalize light exposure values from actiwatch
        exp_light = dat.light.values
        exp_light[np.isnan(exp_light)] = 0
        exp_light = (exp_light - np.min(exp_light)) / np.ptp(exp_light)

        # create heatmap without borders
        ax[exp_idx].imshow(np.transpose(np.expand_dims(exp_light, 1)),
                           aspect='auto',
                           vmax=np.median(exp_light),
                           alpha=.8,
                           cmap='gray',
                           interpolation='nearest')
        ax[exp_idx].spines['top'].set_visible(False)
        ax[exp_idx].spines['right'].set_visible(False)
        ax[exp_idx].spines['bottom'].set_visible(False)
        ax[exp_idx].spines['left'].set_visible(False)
        ax[exp_idx].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        ax[exp_idx].set_ylabel('Exposed \n light', rotation='horizontal', labelpad=25)


    # continue by plotting raw signal on left y-axis of the main plot
    ax[main_idx].bar(x=np.arange(0, data_len),
                     height=dat.data.values,
                     width=1,
                     color='black',
                     alpha=.8)
    ax[main_idx].set_xticklabels(dat.data.index, rotation=45)
    ax[main_idx].set_ylabel('Activity Counts')
    ax[main_idx].set_xlabel('Datetime')

    # remove year and add month to x-axis for clarity and anonymization
    xt = ax[main_idx].get_xticklabels()  # get ticklabels to change
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ticks = ax[main_idx].get_xticks()
    for ii, tick in enumerate(ticks):  # loop over all tick labels and change them
        if np.logical_and(tick >= 0, tick <= data_len):
            old_txt = str(dat.data.index[int(tick)])
            new_txt = old_txt[5:-3]
            new_txt = months[int(new_txt[0:2]) - 1] + new_txt[2:]
            xt[ii]._text = new_txt
    ax[main_idx].set_xticklabels(xt)

    # create right axis and plot heatmap here
    ax2 = ax[main_idx].twinx()
    ax2.imshow(structures,
               aspect='auto',
               alpha=0.5,
               origin='upper',
               cmap='Blues',
               interpolation='nearest')
    ax2.set_yticks(np.arange(len(max_minutes)+4))
    ax2.set_ylabel('Rhythms (4-hour bins)')
    ax2.set_yticklabels(['0-2', '2-6', '6-10', '10-14', '14-18', '18-22', '22-26', '26-30', '', '', '', ''])
    old_ticks = ax2.get_yticks()
    ax2.set_yticks(old_ticks[:-4])

    # add title and plot figure
    if display_title == 'all':
        if n_plots > 1:
            txt = 'Actigraphy data, the (binned) underlying rhythms shown \n ' \
                  'by importance (intensity) and an important Zeitgeber, light'
        else:
            txt = 'Actigraphy data and their underlying rhythms \n shown by importance (intensity)'
        fig.suptitle(txt + '\n' + dat.name)
    elif display_title == 'file':
        fig.suptitle(dat.name)
    fig.tight_layout()
    if plot:
        plt.show()

    # save figure
    if save:
        plt.savefig(save_location + dat.name.replace(' ', '_') + '.png')


## Perform visual analysis on all files (one-file analyzer after this block)
# loop over folder of insomnia patients and partners
folders = ['CLIENT/', 'PARTNER/']
for iFolder in folders:
    # Find data in each folder
    path = 'C:/act_viz/data/Supplementary Material_Final/Data/'
    files = glob(path + iFolder + '*.csv')
    for ii, iFile in enumerate(files):
        # visualize data one by one
        print(str(ii) + '/' + str(len(files)))
        # load data using pyActigraphy
        try:
            dat = pyActigraphy.io.read_raw_rpx(iFile)
        except KeyError:
            print('Data from \n ' + iFile + ' \n not properly loaded, skipping')
            continue

        # find data length
        data_len = dat.data.shape[0]

        if isfile('C:/act_viz/output/' + dat.name.replace(' ', '_') + '.png'):  # exclude if already done
            continue
        elif data_len > 1440 * 14:  # exclude if more then two weeks of data for computational reasons
            continue

        # deal with NaNs (now in this way for visualization purposes, other preprocessing may be required based on your
        # data and purposes
        dat.data.fillna(0, inplace=True)

        # perform SSA
        # Decompose the rhythm in rhythmic components that are also assigned an importance (proportion explained
        # variance). This allows to plot the most important rhythms in the signal and their relative strength
        iSSA = pyActigraphy.analysis.SSA(dat.data, window_length='24h')
        iSSA.fit()

        # create plot
        plot_rhythmic_structure(dat, iSSA, data_len, city='Melbourne',
                                plot_daylight=True, plot_light=True,
                                plot=False,
                                save=True, save_location='C:/act_viz/output/')


## Analyze one file
file = 'C:/'  # change to the path to your file
city = 'Melbourne'  # change to the city where actigraphy was recored

# load data using pyActigraphy --adapt reader to your dataformat e.g., read_raw_awd etc.
dat = pyActigraphy.io.read_raw_rpx(file)

# find data length
data_len = dat.data.shape[0]

# deal with NaNs (now in this way for visualization purposes, other preprocessing may be required based on your
# data and purposes
dat.data.fillna(0, inplace=True)

# perform SSA
# Decompose the rhythm in rhythmic components that are also assigned an importance (proportion explained
# variance). This allows to plot the most important rhythms in the signal and their relative strength
iSSA = pyActigraphy.analysis.SSA(dat.data, window_length='24h')
iSSA.fit()

# create plot
plot_rhythmic_structure(dat, iSSA, data_len, city=city,
                        plot_daylight=True, plot_light=True,
                        plot=True)
