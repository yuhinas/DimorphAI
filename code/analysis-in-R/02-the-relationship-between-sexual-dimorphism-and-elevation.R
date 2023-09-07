library(data.table)
library(ggplot2)
library(ggpubr)
library(lme4)
library(MuMIn)
library(car)

source('00-setting.R')

## load species-level data of sexual dimorphism
# columns：Family; Genus; Species; distance (calculated by features after selection: 124-D or 388-D); Alt_median

file_path = paste0('./data/prepare-data/sd_species_alt_summary.csv')
f <- fread(file_path)
X<-f
X

reg_type_list = c('narr', 'wide', 'all(narr+wide)')

RS_boundary = mean(X$range_quantile)
RS_boundary # 522.25 m

#####################################################
#### Relationship between sexual dimorphism and elevation in widely, narrowly distributed, and all species.
##### widely distributed species
dat_wide <- X[X$range_quantile>RS_boundary]
x = dat_wide[ , 'distance']
x = as.matrix(x)
y = dat_wide$Alt_median
stat_lab = fit_stat_lab(fit)

title_ = paste0("GLMM_Family/Genus: ", stat_lab)
reg_plot = ggplot(dat_wide, aes(y,x))+
  geom_point(color='#81C7D4', size = 7) +
  geom_smooth(method = "lm", se = TRUE, color = 'black')+
  labs(y = 'Sexual dimorphism', x = 'Elevation(m)')+
  theme_set(new_theme)+labs(title = title_)

ggsave('./widely_distributed_species.pdf', plot = reg_plot, width = 10, height = 10)

##### narrowly distributed species
dat_narr <- X[X$range_quantile<=RS_boundary]
x = dat_narr[ , 'distance']
x = as.matrix(x)
y = dat_narr$Alt_median
  
fit <- lmer(y~x+(1|Family/Genus), data=dat_narr)
stat_lab = fit_stat_lab(fit)
  
title_ = paste0("GLMM_Family/Genus: ", stat_lab)
reg_plot = ggplot(dat_narr, aes(y,x))+
    geom_point(color='#81C7D4', size = 7) +
    geom_smooth(method = "lm", se = TRUE, color = 'black')+
    labs(y = 'Sexual dimorphism', x = 'Elevation(m)')+
    theme_set(new_theme)+labs(title = title_)
  
ggsave('./narrowly_distributed_species.pdf', plot = reg_plot, width = 10, height = 10)

##### all species
dat_all <- X
x = dat_all[ ,'distance']
x = as.matrix(x)
y = dat_all$Alt_median

fit <- lmer(y~x+(1|Family/Genus), data=dat_all)
stat_lab = fit_stat_lab(fit)

title_ = paste0("GLMM_Family/Genus: ", stat_lab)
reg_plot = ggplot(dat_all, aes(y,x))+
  geom_point(color='#81C7D4', size = 7) +
  geom_smooth(method = "lm", se = TRUE, color = 'black')+
  labs(y = 'Sexual dimorphism', x = 'Elevation(m)')+
  theme_set(new_theme)+labs(title = title_)

ggsave('./all_species.pdf', plot = reg_plot, width = 10, height = 10)
