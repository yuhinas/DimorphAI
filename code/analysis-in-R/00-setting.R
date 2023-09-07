## for plotting
new_theme <- theme_classic2(base_size = 15) %+replace% 
  theme(legend.position = "none", panel.background = element_blank())

cols = c('#F4A7B9', '#DB4D6D', '#A5DEE4' ,'#2EA9DF')

## function 
stat_linetype <- function(X, col_){
  
  X_male = X[X$Sex == 'male']
  X_female = X[X$Sex == 'female']
  
  y_male = X_male[, col_, with = FALSE]
  y_male = as.matrix(y_male)
  y_female = X_female[, col_, with = FALSE]
  y_female = as.matrix(y_female)
  
  temp_male = lm(y_male~X_male$Alt)
  s_male = summary(temp_male)
  a_male = anova(temp_male)
  p_male = a_male$`Pr(>F)`[1]
  
  temp_female = lm(y_female~X_female$Alt)
  s_female = summary(temp_female)
  a_female = anova(temp_female)
  p_female = a_female$`Pr(>F)`[1]
  
  if(p_male<=0.05 && p_female<=0.05){
    return(c('solid', 'solid'))
  }
  if(p_male<=0.05 && p_female>0.05){
    return(c('dashed', 'solid'))
  }
  if(p_male>0.05 && p_female<=0.05){
    return(c('solid', 'dashed'))
  }
  else{
    return(c('dashed', 'dashed'))
  }
}

fit_stat_lab <- function(fit){
  
  a = Anova(fit)
  print(a)
  r2 = r.squaredGLMM(fit) 
  print(r2)
  fit = summary(fit)
  print(fit)
  
  if (a$`Pr(>Chisq)`<0.001){
    p = '<0.001'
  }
  if(a$`Pr(>Chisq)`>0.001){
    p = round(a$`Pr(>Chisq)`,2)
  }
  
  
  stat_lab = paste0( 'R2m = ',round(r2[1],2),', ', 'R2c = ',round(r2[2],2),', p = ',p)
  stat_lab = as.character(stat_lab)
  
  return(stat_lab)
}
