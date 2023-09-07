import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import cv2
from os.path import join

def cal_mean_grey_values(photo):
    remove_bg_values_matrix = photo[photo!=0]
    mean_grey_values = np.mean(remove_bg_values_matrix)
    
    return(mean_grey_values)

def make_binary(photo, threshold):
    
    above_values = int(round(np.mean(photo[photo>threshold])))
    below_ = photo[photo<=threshold]
    below_ = below_[below_>0] 
    below_values = int(round(np.mean(below_)))
    
    temp = np.where(photo>threshold,above_values,photo)
    temp = np.where((temp<=threshold) & (temp>0),below_values,temp)    
    temp = np.where(temp==0, 255, temp)
    
    return(temp)

def cal_contrast_values(photo, percent):
    remove_bg_list = photo[photo!=0]
    
    ab_ = np.quantile(remove_bg_list, 1-percent) 
    ab_list = remove_bg_list[remove_bg_list>=ab_] 
    ab_v = np.mean(ab_list)
    
    be_ = np.quantile(remove_bg_list, percent)
    be_list = remove_bg_list[remove_bg_list<=be_] 
    be_v = np.mean(be_list)
    
    contrast_values = ab_v-be_v
    
    return(contrast_values)

## choose images which need to quantify
### sexual dimorphism
path_whole = './model/generated-image-along-elevation/rmbg/sd/whole'  ## whole specimen
path_FW = './model/generated-image-along-elevation/rmbg/sd/FW'    ## forewings
### sexual monomorphism
path_whole = './model/generated-image-along-elevation/rmbg//sm/whole'    ## whole specimen
path_FW = './model/generated-image-along-elevation/rmbg/sm/FW'  ## forewings

sex_list = ['female', 'male']
confi_list = ['0', '1', '2']
alt_list = ['0', '1', '2', '3', '4', '5']
per_values = 0.05 ## for calculating contrast

sex_indx_list = list()
confi_indx_list = list()
alt_indx_list = list()
photo_name_list = list()

whole_mean_grey_values_list = list()
whole_contrast_list = list()
Relative_size_dark_FW = list()

## caculate mean grey values of each sex
mean_grey_values_list_summary = list()

for s in sex_list:
    mean_grey_value_sum = 0
    for i in confi_list:
        for j in alt_list:
            photo_name = '%s_%s_%s' %(s, i, j)
            image = cv2.imread('%s/%s_%s_%s.png' %(path_whole, s, i, j), cv2.IMREAD_GRAYSCALE)
            mean_grey_value_ = cal_mean_grey_values(image)
            mean_grey_value_sum =mean_grey_value_sum + mean_grey_value_
    
    mean_grey_values_list_summary.append(mean_grey_value_sum/18)

## whole specimen
for t,s in enumerate(sex_list):
    for i in confi_list:
        for j in alt_list:
            
            photo_name = '%s_%s_%s.png' %(s, i, j)
            
            path_whole_ = join(path_whole, photo_name)
            
            image = cv2.imread(path_whole_, cv2.IMREAD_GRAYSCALE)
            
            mean_grey_values_ = cal_mean_grey_values(image)
            
            contrast = cal_contrast_values(image, per_values)
            
            ## output list
            
            photo_name_list.append(photo_name)
            sex_indx_list.append(s)
            confi_indx_list.append(i)
            alt_indx_list.append(j)
            
            whole_mean_grey_values_list.append(mean_grey_values_)
            whole_contrast_list.append(contrast)
            
## FW
for t,s in enumerate(sex_list):
    for i in confi_list:
        for j in alt_list:
            
            photo_name = '%s_%s_%s.png' %(s, i, j)
            
            path_FW_ = join(path_FW, photo_name)
            
            image = cv2.imread(path_FW_, cv2.IMREAD_GRAYSCALE)
            
            bd = mean_grey_values_list_summary[t]
            
            image_ = make_binary(image, bd)
            image_rmbg = np.where(((image_>0)&(image_<255)) ,0,image_)
            image_rmbg = 255-image_rmbg
            
            ## outline of FW of species
            
            ret,thresh = cv2.threshold(image_rmbg,0,255,cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            
            area = 0
            perimeter = 0
            
            for c in range(len(contours)):
                area = area + cv2.contourArea(contours[c]) 
            
            ## outline of dark patches
            
            blurred = cv2.GaussianBlur(image_, (7, 7), 0)
            
            ret_dark,thresh_dark = cv2.threshold(blurred,bd,255,cv2.THRESH_BINARY)
            thresh_dark = 255-thresh_dark
            contours_dark, hierarchy_dark = cv2.findContours(thresh_dark, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            
            area_dark = 0
            perimeter_dark = 0

            for c in range(len(contours_dark)):
                
                area_dark = area_dark + cv2.contourArea(contours_dark[c]) 
            
            ## output list
            
            Relative_size_dark_FW.append(area_dark/area)

d = {'photo' : photo_name_list,'Sex' : sex_indx_list,'confi_interval': confi_indx_list  , 'Alt':alt_indx_list,
     'Contrast': whole_contrast_list,'Mean brightness': whole_mean_grey_values_list , 'Relative size of dark region of FW': Relative_size_dark_FW
    }

d = pd.DataFrame(data = d)
d.to_csv('./metadata/photo_quantify_sd.csv', index = False)
d.to_csv('./metadata/photo_quantify_sm.csv', index = False)
