library(lubridate)
library(readr)
library(dplyr)

# ACTIGRAPHY --------------------------------------------------------------
# Line:	Line Number
# Date:	Date (start of epoch)
# Time:	Time (start of epoch)
# Off-Wrist Status:	1 means device was not being worn
# Activity:	Activity (counts)
# Marker:	1 means Event Marker button was pressed
# White Light:	White Light
# Red Light:	Red Light
# Green Light:	Green Light
# Blue Light:	Blue Light
# Sleep/Wake:	Sleep/Wake Score (0=Sleep; 1=Wake)
# Interval Status:	Interval Status: Active; Rest; Sleep; or Excluded

# read data ---------------------------------------------------------------
client_files = list.files("data/Supplementary Material_Final/Data/CLIENT", full.names = T)
partner_file = list.files("data/Supplementary Material_Final/Data/PARTNER", full.names = T)
files = c(client_files, partner_file)

# get number of lines to slipt ---------------------------------------------
get_beginning = function(file){
    lines = readLines(file)
    section = grep("Epoch-by-Epoch Data", lines) -1
    data = grep("\"Line\",\"Date\",\"Time\"", lines[section:length(lines)]) - 1
    return(section + data - 1)
}

beginnings = sapply(files,
                    get_beginning,
                    USE.NAMES = F)

# read all files as a list of ts ------------------------------------------
act_ts = list()
for (i in 1:length(files)){
    act_ts[[i]] = readr::read_csv(files[i],
                                  skip = beginnings[i],
                                  show_col_types = F, name_repair = "universal")
}
names(act_ts) = sapply(sapply(strsplit(files, "/"), function(x){x[length(x)]}), 
                   substr, 
                   start = 1, 
                   stop = 5, 
                   simplify = T,
                   USE.NAMES = F)

# merge all data into a single act_ts -----------------------------------------
act_ts = data.table::rbindlist(act_ts, use.names = T, idcol = "ID", fill = T)

# slipt ID and category ---------------------------------------------------
act_ts = cbind(label = substr(act_ts$ID,1,1), act_ts) # Using cbind so the column is inserted at the beggining
act_ts = cbind(couple = substr(act_ts$ID, 2, 5), act_ts)

# Some Processing and Type Converting ----------------------------------------------------------
act_ts = act_ts %>% 
    mutate(
        ID = factor(ID),
        label = factor(label),
        couple = factor(couple),
        datetime = lubridate::as_datetime(paste(Date, Time),
                                          format = "%d/%m/%Y %H:%M:%S",
                                          tz = "Australia/Melbourne"),
        Date = lubridate::as_date(Date,
                                  format = "%d/%m/%Y",
                                  tz = "Australia/Melbourne"),
        Time = lubridate::hour(datetime) * 60 + lubridate::minute(datetime),
        Interval.Status = factor(Interval.Status),
        Sleep.Wake  = as.factor(Sleep.Wake),
        `...16` =  NULL,
        `...13` = NULL,
        
    ) %>% 
    relocate(ID, datetime)


# ACTIWATCH STATISTICS -------------------------------------------------------------
# get number of lines to slipt ---------------------------------------------
get_beginning = function(file){
    lines = readLines(file)
    section = grep("Statistics", lines)
    end = grep("Marker/Score List", lines)
    return(c(begin = section, max = end - section - 6))
}

beginnings = sapply(files,
                    get_beginning,
                    USE.NAMES = F)

# read all files as a list of df ------------------------------------------
act_stats = list()
for (i in 1:length(files)){
    act_stats[[i]] = readr::read_csv(files[i],
                              skip = beginnings["begin", i],
                              n_max = beginnings["max", i],
                              show_col_types = F,
                              skip_empty_rows = T)
    act_stats[[i]] = act_stats[[i]][-c(1),]
}

names(act_stats) = sapply(sapply(strsplit(files, "/"), function(x){x[length(x)]}),
                   substr,
                   start = 1,
                   stop = 5,
                   simplify = T,
                   USE.NAMES = F)

# merge all data into a single ts -----------------------------------------
act_stats = data.table::rbindlist(act_stats, use.names = T, idcol = "ID", fill = T)

# slipt ID and category ---------------------------------------------------
act_stats = cbind(label = substr(act_stats$ID,1,1), act_stats) # Using cbind so the column is inserted at the beggining
act_stats = cbind(couple = substr(act_stats$ID, 2, 5), act_stats)


# Some Processing and Type Converting ----------------------------------------------------------
act_stats = act_stats %>%
    filter(`Interval Type` %in% c("REST","ACTIVE","SLEEP")) %>%
    mutate(
        ID = factor(ID),
        label = factor(label),
        couple = factor(couple),
        `Interval#` = factor(`Interval#`),
        `Start Date` = as_date(`Start Date`, format = "%d/%m/%Y"),
        `Start Time` = readr::parse_time(`Start Time`, "%I:%M:%S %p"),
        `End Date` = as_date(`End Date`, format = "%d/%m/%Y"),
        `End Time` = readr::parse_time(`End Time`, "%I:%M:%S %p"),
        `Interval Type` = factor(`Interval Type`),
        `...57` =  NULL,
        `...39` =  NULL,
    ) %>%
    mutate_if(is.character, as.numeric) 


# # READ CALCULATED FEATURES  -----------------------------------------------
# sleep = readxl::read_xlsx("data/Supplementary Material_Final/Output_Features/Features_7Nights.xlsx", col_names = T, trim_ws = T, .name_repair = "minimal")
# sleep = as_tibble(cbind(sleep[1:3], sleep[28:39])) # Use only data with the Intensity Filtering set to 40
# sleep = sleep[-(6:10)]
# sleep = sleep %>% 
#     rename(label = Label) %>% 
#     mutate(
#         label = as.factor(if_else(label == 1, "H", "I")),
#         ID = as.factor(paste0(label, subjIndex)),
#         
#     ) %>% 
#     relocate(ID)

