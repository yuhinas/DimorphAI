library(data.table)
library(rgdal)
library(raster)
library(stringr)

library(ggplot2)
library(gridExtra)
library(data.table)
library(ggpubr)
library(plotly)

source('00-setting.R')

all_complete_table = fread("./data/prepare-data/multi_sites_tavg_worldclim.csv")

## download from worldclim2
tavg1 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_01.tif")
tavg2 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_02.tif")
tavg3 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_03.tif")
tavg4 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_04.tif")
tavg5 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_05.tif")
tavg6 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_06.tif")
tavg7 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_07.tif")
tavg8 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_08.tif")
tavg9 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_09.tif")
tavg10 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_10.tif")
tavg11 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_11.tif")
tavg12 <- raster("./data/wc2.1_30s_tavg/wc2.1_30s_tavg_12.tif")

all_complete_table[, "date" := substring(all_complete_table$Number, 5, 12)]

sample_coords = all_complete_table[, c('Longitude', 'Latitude','date'), with=F]
names(sample_coords) = c('lng', 'lat','date')

sample_coords$month = month(as.POSIXlt.character(sample_coords$date, format = '%Y%m%d'))
sample_coords$month_ = sample_coords$month
sample_coords$rid = 1:nrow(sample_coords)

getTavg = function (dt) {
  mon = paste0('tavg', dt$month)
  tem_list = NULL
  
  for (i in c(1:length(mon))){
    tem_list = append(tem_list, raster::extract(get(mon[i]), dt[i, c('lng', 'lat')])[[1]])
    }
  # data.table(rid=dt$rid, tavg=extract(get(mon), dt[, c('lng', 'lat'), with=F]))
  dt$Tavg = tem_list
}

mon = paste0('tavg', dt$month)
tem_list = NULL

for (i in c(1:length(mon))){
  tem_list = append(tem_list, raster::extract(get(mon[i]), dt[i, c('lng', 'lat')])[[1]])
}

dt$Tavg = tem_list
all_complete_table$Tavg = dt$Tavg

all_complete_table_summary = all_complete_table[, c('Alt', 'Tavg', 'Location')][ ,lapply(.SD, mean), by = 'Location']

all_fa_plot = ggplot(all_complete_table_summary, aes(Alt, Tavg)) +
  geom_point(color = '#81C7D4') + 
  geom_smooth(method = 'lm' , se = TRUE, color = 'black') + theme_set(new_theme)+ xlab('Elevation (m)') + 
  ylab('Mean temperature of each sites (oC)')+ 
  stat_cor(aes(label = paste(..rr.label.., ..p.label..,sep = "*`,`~~")), size = 5, label.x.npc = 'center')

ggsave('./Alt-Tavg_worldclim2.pdf', all_fa_plot, width = 8, height = 8)

fwrite(all_complete_table, "./data/prepare-data/multi_sites_tavg_worldclim2.csv")