clear; close all; clc;
warning('off','all')
%%
addpath(strcat(pwd,'\Source'));
set(0,'defaultAxesFontName','Arial')
set(0,'defaultAxesFontSize',16); % set the default axes font
%% Data path
data_path=fullfile(pwd,'\Data');
% check if the folder contains folders name client and partner
folder_available=string(extractfield(dir(data_path),'name')');
folder_available(1:2)=[];
folder_names=["CLIENT","PARTNER"];
if ~all(contains(folder_available,folder_names,'IgnoreCase',true))
    error('The data folder must contain a two folders named: Client and Partner - Case not sensitive')
end
Client_folder_path=fullfile(data_path,folder_available(contains(folder_available,'Client','IgnoreCase',true)));
Partner_folder_path=fullfile(data_path,folder_available(contains(folder_available,'Partner','IgnoreCase',true)));
%% get the list of files in each of the folders
file_name_seperator='_';
Client_list=unique(Get_AW_filelist(Client_folder_path,file_name_seperator));
Partner_list=unique(Get_AW_filelist(Partner_folder_path,file_name_seperator));
file_id=contains(erase(Client_list,'C'),erase(Partner_list,'P'));
Client_list=Client_list(file_id);
file_id=contains(erase(Partner_list,'P'),erase(Client_list,'C'));
Partner_list=Partner_list(file_id);
% Display total participants 
disp(strcat('Total number of Participant - ',num2str(length(Client_list))));
%% Loop through and plot all the matching participant
Client_filelist=string(extractfield(dir(strcat(Client_folder_path,'\*.csv')),'name')');
Partner_filelist=string(extractfield(dir(strcat(Partner_folder_path,'\*.csv')),'name')');
% omit a day if less than 8 hours of data is present  (hours)
omit_hr=8;
% Color map - choose - 1- RCG ; 0- color blind friendly
color_map=1;
%% check the client list and enter the index of the participant
% remove the comment below to run for all suitable participants 
% Multiple file / file format issues:  1187 1190 1228 
% Over 10 days of days 1039 1057 1124 1182 1237 1246 1277 1287 - can run
% but plot is not suited for over 10 days of data
% Runs correctly for the rest 29 participants 
for i=1:length(Client_list)   
    % Choose a client file and find the matching partner file and compile the data
    disp(erase(Client_list(i),'C'));
    Client_file=Client_filelist(contains(Client_filelist,Client_list(i)));
    Partner_file=Partner_filelist(contains(Partner_filelist,erase(Client_list(i),'C')));
    % Extract Client data
    Out_Client=Get_Actiwatch_data(fullfile(Client_folder_path,Client_file));
    Client_Data=Out_Client.Data;
    % Extract Partner data
    Out_Partner=Get_Actiwatch_data(fullfile(Partner_folder_path,Partner_file));
    Partner_Data=Out_Partner.Data;
    % Make sure the time intervals are the same in both client and partner
    if ~all(ismember(Client_Data.Time,Partner_Data.Time))
        Client_Data=Client_Data(ismember(Client_Data.Time,Partner_Data.Time),:);
    end
    if ~all(ismember(Partner_Data.Time,Client_Data.Time))
        Partner_Data=Partner_Data(ismember(Partner_Data.Time,Client_Data.Time),:);
    end
    % Check if the data lengths match
    if ~(height(Client_Data)==height(Partner_Data))
        error('Unequal lengths of data');
    end
    % trucate to 12 hour periods
    % find and eliminate short <8 hr periods in the short and end
    ind_12=find(contains(string(Client_Data.Time),'12:00:00'));
    % check the begining and trim
    trim_ind_f=[];
    if ind_12(1)<omit_hr*Out_Client.epoch_interval
        trim_ind_f=(1:ind_12(1)-1)';
    end
    % check the begining and trim
    trim_ind_e=[];
    if (height(Client_Data)-ind_12(end))<omit_hr*Out_Client.epoch_interval
        trim_ind_e=(ind_12(end):height(Client_Data))';
    end
    % Now trim the data
    Client_Data([trim_ind_f;trim_ind_e],:)=[];
    Partner_Data([trim_ind_f;trim_ind_e],:)=[];
    % finding the intervals required for plotting
    if Out_Client.epoch_interval==60
        param.interval=Out_Client.epoch_interval;
    elseif Out_Client.epoch_interval==30
        param.interval=Out_Client.epoch_interval*2;
    end
    %% Creating the plot
    unique_dates=datetime(unique(string(datetime(Partner_Data.Time,'Format','dd-MMM-yyyy'))),'InputFormat','dd-MMM-yyyy');
    % Sunrise and sunset times
    % Melbourne : Lat -37.8136 Long 144.9631 Altitude 31 m
    % Time zone
    tz=duration(erase(Out_Client.Time_zone,'+'),'InputFormat','hh:mm');
    [SRISE,SSET,NOON]=sunrise(-37.8136,144.9631,31,hours(tz),datenum(unique_dates));
    [h,m,s]=hms(datetime(SRISE, 'ConvertFrom', 'datenum', 'Format','dd-MMM-yyyy HH:mm:ss'));
    [h,m,~]=hms(mean(duration(h,m,zeros(length(s),1))));
    sunrise_time=duration(h,m,0);
    [h,m,s]=hms(datetime(SSET, 'ConvertFrom', 'datenum', 'Format','dd-MMM-yyyy HH:mm:ss'));
    [h,m,~]=hms(mean(duration(h,m,zeros(length(s),1))));
    sunset_time=duration(h,m,0);
    photoperiod.sunrise_time=sunrise_time;
    photoperiod.sunset_time=sunset_time;
    %% Create the color coding for the activity data
    list_data=unique([Client_Data.Activity;Partner_Data.Activity]);
    list_data(list_data==0)=[];
    list_data(isnan(list_data))=[];
    list_data=[0;list_data];
    if color_map==1
    % RGB colormap with maximum contrast
    N_color=linspecer(length(list_data),'qualitative');
    ext='RGB';
    elseif color_map==0
    % colorblind friendly color map - from Crameri et al 2020
    % Source article: https://www.nature.com/articles/s41467-020-19160-7
    temp_N_color=load('batlow.mat');
    temp_N_color=temp_N_color.batlow;
    idx =sort( randperm(length(temp_N_color),length(list_data)))';
    N_color=temp_N_color(idx,:);
    ext='CB'; % color blind Friendly
    end
    %%
    param.N_color=N_color;
    param.list_data=list_data;
    if length(unique_dates)<11
    generate_figure(Client_Data,Partner_Data,photoperiod,param)
    title(strcat('Client:Partner-',erase(Client_list(i),'C')))
    else
        disp('Over 10 days of data is present, hence skipping to avoid odd looking plot');
    end
    exportgraphics(gca,strcat(erase(Client_list(i),'C'),'_',ext,'.png'),'Resolution',300)  
    close all;
end
