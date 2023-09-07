library(data.table)
install.packages( "https://cran.r-project.org/src/contrib/Archive/ggplot2/ggplot2_3.4.0.tar.gz", repos = NULL, type = "source")
library(ggplot2)
library(ggpubr)

source('00-setting.R')

feature_name = 'sd'
path_ = paste0('./photo_quantify_', feature_name, '.csv' )

feature_name = 'sm'
path_ = paste0('./photo_quantify_', feature_name, '.csv' )

f <- fread(path_)
X <- f
X$Alt = X$Alt*600

y_feature_list = c('Mean brightness', 'Contrast', 'Relative size of dark patches of FW')

Sex = c('female', 'male')

head(X)

for(col in y_feature_list){
    
  df_all = X
  x_all = df_all$Alt
  y_all = as.matrix(df_all[,col, with = FALSE])
    
  linetype_list = stat_linetype(df_all, col)
    
  scatterplot_all <- ggplot(df_all, aes(x_all, y_all, color = Sex)) +
    geom_point(size = 3) +
    geom_smooth(method=lm, se = TRUE, aes(linetype=Sex)) +
    scale_color_manual(values = c('#DB4D6D','#2EA9DF')) +
    theme(legend.position=c(0,1), legend.justification=c(0,1))+
    scale_linetype_manual(values=linetype_list)+
    xlab('Elevation (m)') +
    ylab(col)+ stat_cor(aes(label = paste(..rr.label.., ..p.label..,sep = "*`,`~")),
                         label.y.npc='top', label.x.npc = 0.6)+ theme_set(new_theme)+stat_regline_equation()
    
  path_ = paste0('./plot/', feature_name ,'_', col,'.pdf')
  ggsave(path_, plot = scatterplot_all, width = 7, height = 7)
    
}

