library(lubridate)
library(readr)
library(dplyr)
library(ggplot2)
library(maptools)
library(ggtext)
source("read_data.R")
source("custom_theme.R")

# Filter data -------------------------------------------------------------
act_filtered = act_ts %>%
    group_by(ID) %>% 
    mutate(datetime = datetime + hours(12),
           Time = lubridate::hour(datetime) * 60 + lubridate::minute(datetime)) %>% # Centralize into midnight since we are interested in the Sleep patterns 
    mutate(day_number = data.table::frank(as_date(datetime),
                                          ties.method = "dense")) %>%
    filter(day_number >=2 & day_number <= 8) %>% 
    #filter(ID == "P1085") %>% 
    ungroup()


# Calculate sunrise and sunset --------------------------------------------
sunriset = act_filtered %>%
    group_by(ID, couple, label) %>% 
    summarise(datetime = median(datetime))

melbourne <- matrix(c(144.946457, -37.840935), nrow=1)
sunriset$dawn = (crepuscule(melbourne,
                            sunriset$datetime,
                            solarDep=6,
                            direction="dawn", 
                            POSIXct.out=TRUE)$day_frac * 1440) + 720

sunriset$dusk = (crepuscule(melbourne,
                            sunriset$datetime,
                            solarDep=6,
                            direction="dusk", 
                            POSIXct.out=TRUE)$day_frac * 1440) - 720
sunriset$datetime = NULL


# Data Prep -------------------------------------------------------------
# We want to plot an actogram with lines colored depending on the Status (ACTIVE, SLEEP)
# In order to do that we first need to get the start and end time of each colored segment

# Do Running Length Decoding to get Start and End of Activity/Sleep
act_rle = act_filtered %>%
    group_by(ID, couple, label) %>%
    summarise(status = rle(as.vector(Interval.Status))$values,
              length = rle(as.vector(Interval.Status))$lengths) %>%
    ungroup() %>% 
    mutate(end = cumsum(length),
           start = end - length + 1)

act_rle = act_rle %>% 
    group_by(ID) %>% 
    summarise(
        couple = couple,
        label = label,
        status = status,
        start = start,
        end = end,
        start_datetime = (act_filtered$datetime[start]),
        end_datetime = (act_filtered$datetime[end]))

# For plotting segments that cross the boundary between days we need to split
# these segments into two smaller segments, one for each day. 
across_index = which(as_date(act_rle$start_datetime) != as_date(act_rle$end_datetime),)

first_segment = 
    act_rle[across_index,] %>% 
    mutate(old_end_datetime = end_datetime,
           end_datetime = as_datetime(paste0(as_date(start_datetime), "23:59:59"),
                                      tz = "Australia/Melbourne"),
           old_end_datetime = NULL)

second_segment = 
    act_rle[across_index,] %>% 
    mutate(old_start_datetime = start_datetime,
           start_datetime = as_datetime(paste0(as_date(end_datetime), "00:00:00"),
                                        tz = "Australia/Melbourne"),
           old_start_datetime = NULL)

# Join new segments into previous dataframe
# Create new columns splitting date and time
act_rle = act_rle[-across_index,] %>% 
    rbind(first_segment) %>%
    rbind(second_segment) %>%
    group_by(ID) %>%
    mutate(start_date = lubridate::as_date(start_datetime),
           end_date = lubridate::as_date(end_datetime),
           start_time = lubridate::hour(start_datetime) * 60 + lubridate::minute(start_datetime),
           end_time =  lubridate::hour(end_datetime) * 60 + lubridate::minute(end_datetime),
           day_number = data.table::frank(start_date, ties.method = "dense")
           ) %>% 
    ungroup()

# Prep Sleep Statistics ---------------------------------------------------
sleep_stats = act_stats %>% 
    filter(`Interval Type` == "SLEEP" & label == "C") %>% 
    group_by(ID, couple) %>% 
    summarise(sleep_time = mean(`Sleep Time`),
              WASO = mean(WASO, na.rm = T),
              Efficiency = mean(Efficiency, na.rm = T)) %>% 
    arrange(sleep_time)

ID_ordered = sleep_stats %>% select(ID, couple)

# Join sunrise and sunset data --------------------------------------------
act_rle = act_rle %>% 
    left_join(sunriset, by = c("ID","couple","label"))

# filter data that for couples that have both partner and client
plot_couples = act_rle %>% 
    filter(label == "C") %>% 
    select(couple) %>% 
    unique() %>% 
    inner_join(
        act_rle %>% 
            filter(label == "P") %>% 
            select(couple) %>% 
            unique()
    )

# Plotting Actogram ------------------------------------------------------------
plot_clients = act_rle %>%
    filter(status %in% c("ACTIVE","REST", "REST-S")) %>% 
    filter(label == "C") %>%
    filter(couple %in% plot_couples$couple) %>% 
    mutate(status = ifelse(status == "REST-S", "SLEEP", status)) %>% 
    mutate(ID = factor(ID, levels = ID_ordered$ID)) %>% 
    ggplot() +
    geom_rect(data = . %>%
                  select(ID, couple, label, dawn, dusk) %>%
                  unique(),
              aes(xmin = dawn,
                  xmax = dusk,
                  ymin = -Inf,
                  ymax = Inf),
              fill = "grey",
              alpha = 0.4) +
    geom_vline(data = . %>%
                   select(ID, couple, label, dawn, dusk) %>%
                   unique(),
               aes(xintercept = dawn),
               alpha = 0.1) +
    geom_vline(data = . %>%
                   select(ID, couple, label, dawn, dusk) %>%
                   unique(),
               aes(xintercept = dusk),
               alpha = 0.1) +
    geom_linerange(aes(y = day_number,
                       xmin = start_time,
                       xmax = end_time,
                       color = status),
                   size = 2) +
    scale_y_continuous(trans = "reverse",
                       n.breaks = 7) +
    scale_x_continuous(breaks = c(0, 360, 720, 1080, 1440), 
                       labels = c(12, 18, 24, 6, 12)) +
    scale_color_manual(values = c("#48508c",
                                  "#774f78",
                                  "#a64d64",
                                  "#55331d")) +
    facet_wrap(vars(ID), ncol = 4) +
    labs(title = "Sleep pattern in clients",
         subtitle = "Sleep patterns in insomnia pacients. Actograms are centered at midnight and ordered by mean sleep time of pacients calculated by the ActiWatch. Night duration is shown in the background in light grey.",
         caption = "Visualization by JT Silvério • Data from: Angelova, M., Kusmakar, S., Karmakar, C., Zhu, Z., Shelyag, S., Drummond, S., & Ellis, J. (2021). Chronic insomnia and bed partner actigraphy data. http//doi.org/10.5061/dryad.b8gtht7bh")

plot_partners = act_rle %>%
    filter(status %in% c("ACTIVE","REST", "REST-S")) %>% 
    filter(label == "P") %>%
    filter(couple %in% plot_couples$couple) %>%
    mutate(status = ifelse(status == "REST-S", "SLEEP", status)) %>% 
    mutate(ID = factor(ID, levels = paste0("P",ID_ordered$couple))) %>% 
    ggplot() +
    geom_rect(data = . %>%
                  select(ID, couple, label, dawn, dusk) %>%
                  unique(),
              aes(xmin = dawn,
                  xmax = dusk,
                  ymin = -Inf,
                  ymax = Inf),
              fill = "grey",
              alpha = 0.4) +
    geom_vline(data = . %>%
                   select(ID, couple, label, dawn, dusk) %>%
                   unique(),
               aes(xintercept = dawn),
               alpha = 0.1) +
    geom_vline(data = . %>%
                   select(ID, couple, label, dawn, dusk) %>%
                   unique(),
               aes(xintercept = dusk),
               alpha = 0.1) +
    geom_linerange(aes(y = day_number,
                       xmin = start_time,
                       xmax = end_time,
                       color = status),
                   size = 2) +
    scale_y_continuous(trans = "reverse",
                       n.breaks = 7) +
    scale_x_continuous(breaks = c(0, 360, 720, 1080, 1440), 
                       labels = c(12, 18, 24, 6, 12)) +
    scale_color_manual(values = c("#48508c",
                                  "#774f78",
                                  "#a64d64",
                                  "#55331d")) +
    facet_wrap(vars(ID), ncol = 4) +
    labs(title = "Sleep pattern in partners",
         subtitle = "Sleep patterns in partners of insomnia pacients. Actograms are centered at midnight and ordered by mean sleep time of pacients calculated by the ActiWatch. Night duration is shown in the background in light grey.",
         caption = "Visualization by JT Silvério • Data from: Angelova, M., Kusmakar, S., Karmakar, C., Zhu, Z., Shelyag, S., Drummond, S., & Ellis, J. (2021). Chronic insomnia and bed partner actigraphy data. http//doi.org/10.5061/dryad.b8gtht7bh")


ggsave(plot_clients,
       device = "pdf",
       filename = "output/actograms_clients.pdf", 
       width = 210,
       height = 297,
       units = "mm",
       dpi = 300)

ggsave(plot_partners,
       device = "pdf",
       filename = "output/actograms_partners.pdf", 
       width = 210,
       height = 297,
       units = "mm",
       dpi = 300)




















# SOLUTION THAT WERE NOT USED
###################################
# WORKS but the size of the bar is relative to the size of the plot. 
# Could be a good thing, not sure.
##################################
# n.day = max(y$day_number)
# ggplot(y) +
#     geom_rect(aes(ymin = day_number,
#                   ymax = day_number - 0.2,
#                   xmin = start_time,
#                   xmax = end_time,
#                   fill = value),
#                   size = 0) +
#     scale_y_continuous(trans = "reverse",
#                        n.breaks = n.day)

#########################################################
# NOT USE, It draws whole bar from begging to end of day
########################################################
# ggplot(y) +
#     geom_segment(aes(y = day_number,
#                      yend = day_number,
#                      x = start_time,
#                      xend = end_time,
#                      color = value),
#                  size = 10)+
#     scale_y_continuous(trans = "reverse",
#                        n.breaks = n.day)

##############################################
# geom_tile could work with ts actigraphy data
##############################################
# ggplot(act_filtered %>%  filter(ID == "C1220")) +
#     geom_tile(aes(x = Time,
#                   y = day_number,
#                   fill = Interval.Status,
#                   height = Activity/2000,
#                   width = 4)) +
#     scale_y_continuous(trans = "reverse",
#                        n.breaks = 7) +
#     scale_x_continuous(breaks = c(0, 360, 720, 1080, 1440),
#     )
