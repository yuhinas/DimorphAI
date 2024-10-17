library(data.table)
library(ggplot2)
library(ggpubr)

source('00-setting.R')

##########################################################
## avg_diff: Increased Temperature after heating for 30 seconds in certain regions
## FW: Forewings
## HW: Hindwings
## LW: Left wings
## RW: Right wings

############################
#### load data
X <- fread('./thermal_plot_me_with_metadata_cold_FW.csv')
############################
X_all_model = X[X$Species == 'model']
X_process = X_all_model

sex_type_list = c('sd', 'sm')

for (st in sex_type_list) {
    
  X_process_ = X_process[X_process$Groups == st]
  X_process_$Alt_groups = X_process_$Alt_groups*600
    
  x = X_process_$Alt_groups
  y = X_process_[, 'avg_diff']
  y = as.matrix(y)
      
  linetype_list = stat_linetype(X_process_, 'avg_diff')
      
  lm_plot = ggplot(X_process_, aes(x,y, color = Sex))+
    geom_point() +
    geom_smooth(method=lm, aes(linetype=Sex)) +
    labs(y = 'Increased temperature', x = 'Elevation')+ ylim(5,21)+
    scale_linetype_manual(values=linetype_list)+
    stat_cor(aes(label = paste(..rr.label.., ..p.label..,sep = "*`,`~")),
                label.x.npc = "centre", label.y.npc = 'bottom')+
    stat_regline_equation()+ theme_set(new_theme)
      
  path_ = paste0('./plot/', 'model_',st, '_avg_diff_.pdf')
  ggsave(path_, plot = lm_plot, width = 7, height = 7)
      
} 

### 交互作用模型
## sm female vs sd female
X_process = X_all_model[X_all_model$Sex == 'female']
X_process$Alt_groups = X_process$Alt_groups*600

model <- lm(avg_diff ~  Alt_groups* Groups, data = X_process)
summary(model)

## sm male vs sd male
X_process = X_all_model[X_all_model$Sex == 'male']
X_process$Alt_groups = X_process$Alt_groups*600

model <- lm(avg_diff ~  Alt_groups* Groups, data = X_process)
summary(model)

## sm female vs sm male
X_process = X_all_model[X_all_model$Groups == 'sm']
X_process$Alt_groups = X_process$Alt_groups*600

model <- lm(avg_diff ~  Alt_groups* Sex, data = X_process)
summary(model)

## sd female vs sd male
X_process = X_all_model[X_all_model$Groups == 'sd']
X_process$Alt_groups = X_process$Alt_groups*600

model <- lm(avg_diff ~  Alt_groups* Sex, data = X_process)
summary(model)

## all
X_process = X_all_model
X_process$Alt_groups = X_process$Alt_groups*600

model <- lm(avg_diff  ~ Alt_groups * Sex * Groups , data = X_process)
summary(model)

##########################################################
## Control groups
#############################
## load data

X_FW = fread('./thermal_plot_me_with_metadata_cold_FW.csv')
X_FW$wing_class = 'FW'

X_HW = fread('./thermal_plot_me_with_metadata_cold_HW.csv')
X_HW$wing_class = 'HW'

X_LW = fread('./thermal_plot_me_with_metadata_cold_LW.csv')
X_LW$wing_class = 'LW'

X_RW = fread('./thermal_plot_me_with_metadata_cold_RW.csv')
X_RW$wing_class = 'RW'

X_all_FW_HW = rbind(X_FW, X_HW)
X_all_LW_RW = rbind(X_RW, X_LW)
X_all = rbind(X_all_FW_HW , X_all_LW_RW)

############################
X_process = X_all[X_all$Species !='model']
X_process$new_class = paste(X_process$Species, X_process$wing_class, sep = '_')
X_process$new_class <- factor(X_process$new_class, levels = c("control_D_FW", "control_D_HW", "control_D_LW", 'control_D_RW'))

boxplot_ = ggboxplot(X_process, x = "new_class", y = 'avg_diff', fill = 'new_class') +
  labs(title = '')+
  ylab('avg_diff')+xlab('') + ylim(20,33)+
  geom_signif(comparisons = list(c('control_D_LW', 'control_D_RW')),
              map_signif_level=TRUE, test = t.test)+
  geom_signif(comparisons = list(c("control_D_FW", "control_D_HW")),
              map_signif_level=TRUE, test = t.test)+
  theme_set(new_theme)

ggsave('./plot/control.pdf', boxplot_)
