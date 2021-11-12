Readme for ADVAnCe - Actigraphy Data Visualization and Analysis Challenge - Code by Hannah Rolf
rolf.hannah@baua.bund.de
MIT License
Copyright (c) 2021 Hannah Rolf

Structure of Data:
Please create a folder with 'analyze.py'. This folder should contain one folder called 'CLIENT' that includes data from clients and one folder called 'PARTNER' that includes data from their partners.
Csvs of partners must include the same IDs as their partners from the 'CLIENT' folder.
In addition, please create a folder called 'functions' that includes plot.py and hist.py.

This code analyzes data of clients and their partners. It works for datasets with one file for each client and a measuring duration of seven days.
(Not for 1237, 1228 and 1190 in this dataset.)

Requirements:
This code requires python 3. It was tested with Python 3.8.8. It also requires the installation of several packages:
matplotlib==3.3.4
numpy==1.20.1
pandas==1.2.4
scipy==1.6.2

Output:
This code creates a folder called 'output' that includes a folder for every client in your 'CLIENT' folder.
For each client (with a client-ID), the following pdfs are created:
-mov_act_clientid_overview: Overview on Activity Data of Client (and Partner) for one week in a given timeframe (for information on timeframe see 'adjustments')
-clientid_hist: Histogram for Activity Data of Client (and Partner) in a given timeframe.
-clientid_RA: Bargraph with average of activity per hour during measuremt for Client (and Partner). Also includes mean value of activity per hour of 5 least-active and 10 most-active hours (L5, M10)
and their contrast (RA).
-clientid_clock: Shows average hourly activity of Client (and Partner) on clocks. Values are indicated by color-shading.
-clientid_clock_hist: Shows average hourly activity of Client (and Partner) on clocks, but with binning. The proportion of a bin (e.g. number of activity counts between 100 and 200)
are indicated as proportion of radius.

Adjustments:
In analyze.py:
  -night: If you mainly want to analyze data during the night, set night to True. Then beginning and end of sleep are defined by an algorithm and data between these values is shown in mov_act_clientid_overview.
  (For further information go to line 141 in plot.py)
  Also, only nights (as defined by these timepoints) are considered when creating clientid_hist. If your are interested in full day data or you want to set beginning and end of night manually, set night to False.

  -partner_global: If True, partners data is also analyzed if existing.

  -moving_avg_val: Decide how many values you want to use for your average.

  -measuring_frequence: Please enter the frequence of your measurement.

  -in simple_hist: You can define number of bins and binwidth.

  -in activity_hist_on_clock: You can define number of bins and binwidth.

In plot.py:
  -timelimit1 and timelimit2: If night == False these timelimits define the beginning and end of 'one day' in mov_act_clientid_overview and clientid_hist.
  If your want to analyze whole days 3 is recommended for both limits. If you want to analyze nights you could exemplarly use 19 and 11.

In hist.py:
  -timedelta1: Defines which hour is the first to be plotted in clientid_RA

2 examples of output folders with recommended parameters are given.

Execution:
Please open a shell in your main folder (e.g. powershell for windows 10) and call the code by 'python analyze.py'.
