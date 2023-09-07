import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import sklearn.metrics as Metrics

## caculate elevational range size which can classify species into narrowly or widely distributed species
def get_range_quantile (vec):
    
    vec = vec.Alt

    Q1 = np.quantile(vec, 0.25)
    Q3 = np.quantile(vec, 0.75)
    IQR = Q3 - Q1

    return IQR

## calculate distance between males and females of sexually dimorphic species 
def cal_mean_dis(X, feature_list):
    
    df_male = X[X.Sex == 'male']
    df_female = X[X.Sex == 'female']
    
    center_data_male = np.array(df_male.loc[:, feature_list])
    center_data_female = np.array(df_female.loc[:, feature_list])

    center_male = center_data_male.mean(axis =0).reshape(1,-1) # the average of male's morphological matrix 
    center_female = center_data_female.mean(axis =0).reshape(1,-1) # the average of female's morphological matrix
    
    dis = Metrics.pairwise_distances(center_male, center_female)[0,0]

    return(dis)

## load data from tesri 
sd_tesri = pd.read_csv('./data/prepare-data/sd_data_from_tesri.csv')
sm_tesri = pd.read_csv('./data/prepare-data/sm_data_from_tesri.csv')

## load elevational-related features of sexually dimorphic species 
feature_df = pd.read_csv('./data/select-elevational-related-features/select-elevational-related-features_sd_124.csv')
feature_list = np.unique(feature_df['feature'])
feature_list = [str(x) for x in feature_list]

## merge morphological matix and data from tesri 
sd_codes = pd.read_csv('./model/encode/encode_sd_codes_rep.csv')
sm_codes = pd.read_csv('./model/encode/encode_sm_codes_rep.csv')

sd_all = pd.merge(sd_tesri, sd_codes, on = 'Number')
sm_all = pd.merge(sm_tesri, sm_codes, on = 'Number')

## cal distance of sexually dimorphic species between sexes
sp_list = list(np.unique(sd_all.Species))
distance_list = list()

for sp in sp_list:
    temp_df = sd_all[sd_all.Species == sp]
    distance_list.append(cal_mean_dis(temp_df, feature_list))
    
sp_distance_sd = {'Species': sp_list, 'distance': distance_list}
sp_distance_sd = pd.DataFrame(data = sp_distance_sd)

## cal median of elevation and elevational range size of sexually dimorphic and monomorphic species 

sp_quantile_sd = sd_tesri[['Species', 'Alt']].groupby('Species').apply(get_range_quantile)
sp_median_sd = sd_tesri[['Species', 'Alt']].groupby('Species').median()

sp_quantile_sm = sm_tesri[['Species', 'Alt']].groupby('Species').apply(get_range_quantile)
sp_median_sm = sm_tesri[['Species', 'Alt']].groupby('Species').median()

sd_summary = pd.DataFrame({'Species':sp_median_sd.index, 'range_quantile': sp_quantile_sd.values, 
                          'Alt_median': sp_median_sd.Alt.values})

sm_summary = pd.DataFrame({'Species':sp_median_sm.index, 'range_quantile': sp_quantile_sm.values, 
                          'Alt_median': sp_median_sm.Alt.values})

## merge values caculated from sexually dimorphic species
sd_summary = sd_summary.merge(sp_distance_sd)

sd_summary.to_csv('./data/prepare-data/sd_species_alt_summary.csv', index=False)
sm_summary.to_csv('./data/prepare-data/sm_species_alt_summary.csv', index=False)

## merge others cacualted values
sd_all = pd.merge(sd_all, sd_summary, on = 'Species')
sm_all = pd.merge(sm_all, sm_summary, on = 'Species')

sd_all.to_csv('./data/prepare-data/sd_merge_tesri_encode_species_alt_summary.csv', index=False)
sm_all.to_csv('./data/prepare-data/sm_merge_tesri_encode_species_alt_summary.csv', index=False)
