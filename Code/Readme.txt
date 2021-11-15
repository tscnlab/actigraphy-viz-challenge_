Author: Kiran Kumar Guruswamy Ravindran (Kiran KGR)
email: k.guruswamyravindran@surrey.ac.uk
Affliation: University of Surrey

Instruction for running the code
 
Makeplot.m is the main code that generates the figures (open and click run to generate RCG figure)

The source folder contains the functions needed for the Make_plot to run

Data folder must on contain two folders name Client and partner
The csv file names should start with the participant number with prefix C or P followed by _ (underscore)
https://datadryad.org/stash/dataset/doi:10.5061/dryad.b8gtht7bh data has the same format. 

Code description and modifiers 

1. The code compiles all available participant pairs and can loop through all participants
	uncomment the for loop in the code to loop through all participants
2. Figure plotting function - generate_figure(Client_Data,Partner_Data,photoperiod,param) 
Client_Data - Client data timetable containing the columns "Activity"    "SW_label"    "Light"
Partner_Data - Partner_Data timetable containing the columns "Activity"    "SW_label"    "Light"
Client_Data and partner data should be of equal length and timevector should be the same
photoperiod - contains the sunrise and sunset time as durations
param - contains the color map and the unique activity values list

The code provides an example of the inputs and its type
2. Any day containing less than 8hours of data is eliminated

3. files containing over 10 days looks busy in the current figure format and hence is avoided

4. %  color map variable is used to - choose - '1' - RCG ; '0'- color blind friendly (line 33 in code)

Description of the Figure; 

The data from the pair of participant is split into 24 hour periods centered around 00 hours.
1. For each day pair - the sleep wake time series and activity of client is plot above the dotted line and 
   corresponding partner data is plotted below the dotted line
2. The day pair containing weekend is marked by * in the yaxis
3. The photoperiod is also depicted at the top of the plot

