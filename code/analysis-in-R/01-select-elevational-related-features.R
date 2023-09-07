library(ggplot2)
library(data.table)

# mixture model
library(lme4)
library(MuMIn)
library(car)

source('00-setting.R')

## load data
### data from sexual dimorphism or monomorphism
X <- fread('./data/prepare-data/sd_merge_tesri_encode_species_alt_summary.csv')
X <- fread('./data/prepare-data/sm_merge_tesri_encode_species_alt_summary.csv')

feature_list <- as.character(c(0:511))

#########################################################
## pre-processing of data
### data.table with mean morphological matrix of male or female in species-level with Family and Genus columns

male_data <- X[Sex == 'male']
female_data <- X[Sex == 'female']

select_data_male <- male_data[][,append(feature_list,c('Species','Alt_median')), with = F]
summary_data_male <- select_data_male[, lapply(.SD, mean), by = Species]

select_data_female <- female_data[][,append(feature_list,c('Species','Alt_median')), with = F]
summary_data_female <- select_data_female[, lapply(.SD, mean), by = Species]

summary_data_male[,':='(Sex='male')]
summary_data_female[,':='(Sex='female')]

select_data <- X[][,append(feature_list,c('Family','Species','Genus')), with = F]

tt = select_data[,.SD, by = Species][,c('Family' ,'Species', 'Genus')]

summary_data_male = merge(summary_data_male, tt)
summary_data_female = merge(summary_data_female, tt)

df = rbind(summary_data_female, summary_data_male)

#########################################################
## select elevational-related features and 
slope_list = NULL
intercept_list= NULL
confident_interval_2.5 = NULL
confident_interval_2.5_intercept = NULL
confident_interval_97.5 = NULL
confident_interval_97.5_intercept = NULL
Sex_list = NULL
col_feature_list = NULL
p_list = NULL

threshold_ = 0.15

for(feature in feature_list){
  
  ### select columns of single morphological feature and elevation
  x_male = df[Sex=='male']$Alt_median
  y_male =df[Sex=='male'][, feature, with=FALSE]
  y_male = as.numeric(as.matrix(y_male))
  
  x_female = df[Sex=='female']$Alt_median
  y_female =df[Sex=='female'][, feature, with=FALSE]
  y_female = as.numeric(as.matrix(y_female))
  
  ### LR
  ##### male
  reg_male = lm(y_male~x_male, data =summary_data_male)
  summary_male = summary(reg_male)
  p_male = summary_male$coefficients[8]
  ##### female
  reg_female = lm(y_female~x_female, data =summary_data_female)
  summary_female = summary(reg_female)
  p_female = summary_female$coefficients[8]
  
  ### GLMM
  #### male
  fit_male_glm <- lmer(y_male~x_male+(1|Family/Genus), data=summary_data_male)
  a_male_glm = Anova(fit_male_glm)
  p_male_glm = a_male_glm$`Pr(>Chisq)`
  #### female
  fit_female_glm <- lmer(y_female~x_female+(1|Family/Genus), data=summary_data_female)
  a_female_glm = Anova(fit_female_glm)
  p_female_glm = a_female_glm$`Pr(>Chisq)`
  
  #####################
  
  ### append elevational-related feature and result of LR 
  #### male 
  if(p_male_glm<=threshold_ && p_male<=threshold_){
    
    col_feature_list = append(col_feature_list ,feature)
    Sex_list = append(Sex_list,'male')
    slope_list = append(slope_list,as.numeric(reg_male$coefficients[2]))
    intercept_list = append(intercept_list, as.numeric(reg_male$coefficients[1]))
    CI_male = confint(reg_male)
    male_25 = CI_male[2,1]
    male_97 = CI_male[2,2]
    male_25_intercept = CI_male[1,1]
    male_97_intercept = CI_male[1,2]
    confident_interval_2.5 = append(confident_interval_2.5, male_25)
    confident_interval_2.5_intercept = append(confident_interval_2.5_intercept ,male_25_intercept)
    confident_interval_97.5 = append(confident_interval_97.5, male_97)
    confident_interval_97.5_intercept = append(confident_interval_97.5_intercept ,male_97_intercept)
    p_list = append(p_list, p_male)
    
    print(paste0('male_', i))
    }
    
    ## female
    if(p_female_glm<=threshold_ && p_female<=threshold_){
      
      col_feature_list = append(col_feature_list ,feature)
      Sex_list = append(Sex_list,'female')
      slope_list = append(slope_list,as.numeric(reg_female$coefficients[2]))
      intercept_list = append(intercept_list, as.numeric(reg_female$coefficients[1]))
      CI_female = confint(reg_female)
      female_25 = CI_female[2,1]
      female_97 = CI_female[2,2]
      female_25_intercept = CI_female[1,1]
      female_97_intercept = CI_female[1,2]
      confident_interval_2.5 = append(confident_interval_2.5, female_25)
      confident_interval_2.5_intercept = append(confident_interval_2.5_intercept ,female_25_intercept)
      confident_interval_97.5 = append(confident_interval_97.5, female_97)
      confident_interval_97.5_intercept = append(confident_interval_97.5_intercept ,female_97_intercept)
      p_list = append(p_list, p_female)
      
      print(paste0('female_', i))
    }
}

##################################################################################################
## create data.table to save results
stat = data.table('feature' = col_feature_list, 'Sex'= Sex_list, 'slope'= slope_list, 'intercept'= intercept_list, 
                  confident_interval_2.5, p_list,
                  confident_interval_2.5_intercept ,confident_interval_97.5, confident_interval_97.5_intercept, change_list)

select_feature_len = length(unique(stat$feature))
print(select_feature_len)

### save results of sexual dimorphism or monomorphism
path_ = paste0('./data/select-elevational-related-features_sd_', select_feature_len, '.csv')
path_ = paste0('./data/select-elevational-related-features_sm_', select_feature_len, '.csv')
fwrite(stat, file = path_)
