import torch
from networks import *
from utils import str_to_list, load_model
import matplotlib.pyplot as plt
from skimage import io as io
import numpy as np
import pandas as pd

def get_trends (feature_pool, stat, elev_min=0, elev_max=3000, N=10, sex='female', D=512):
    # 0: lower, 1: mean, 2:upper
    codes_elev_min = np.zeros([3, D])
    codes_elev_max = np.zeros([3, D])
    codes_elev_interps = np.zeros([3, N+1, D])

    for feature in feature_pool:
        lr = stat[(stat.feature == feature) & (stat.Sex == sex)].reset_index(drop=True)
        codes_elev_min[0, feature] = lr.loc[0, 'confident_interval_2.5_intercept'] + elev_min * lr.loc[0, 'confident_interval_2.5']
        codes_elev_min[1, feature] = lr.loc[0, 'intercept'] + elev_min * lr.loc[0, 'slope']
        codes_elev_min[2, feature] = lr.loc[0, 'confident_interval_97.5_intercept'] + elev_min * lr.loc[0, 'confident_interval_97.5']

        codes_elev_max[0, feature] = lr.loc[0, 'confident_interval_2.5_intercept'] + elev_max * lr.loc[0, 'confident_interval_2.5']
        codes_elev_max[1, feature] = lr.loc[0, 'intercept'] + elev_max * lr.loc[0, 'slope']
        codes_elev_max[2, feature] = lr.loc[0, 'confident_interval_97.5_intercept'] + elev_max * lr.loc[0, 'confident_interval_97.5']

        codes_elev_interp_0 = np.interp([n for n in range(0, N+1)], [0,N], [codes_elev_min[0, feature], codes_elev_max[0, feature]])
        codes_elev_interp_1 = np.interp([n for n in range(0, N+1)], [0,N], [codes_elev_min[1, feature], codes_elev_max[1, feature]])
        codes_elev_interp_2 = np.interp([n for n in range(0, N+1)], [0,N], [codes_elev_min[2, feature], codes_elev_max[2, feature]])

        for n in range(N+1):
            codes_elev_interps[0, n, feature] = codes_elev_interp_0[n]
            codes_elev_interps[1, n, feature] = codes_elev_interp_1[n]
            codes_elev_interps[2, n, feature] = codes_elev_interp_2[n]
            
        #print(codes_elev_interps[0].shape)

    with torch.no_grad():
        decoded_interpols0 = model.decode(torch.from_numpy(codes_elev_interps[0]).float().cuda())
        decoded_interpols1 = model.decode(torch.from_numpy(codes_elev_interps[1]).float().cuda())
        decoded_interpols2 = model.decode(torch.from_numpy(codes_elev_interps[2]).float().cuda())

        #print(decoded_interpols1.shape)
    return [
        torch.cat(list(decoded_interpols2.permute(0,2,3,1)), dim=1),
        torch.cat(list(decoded_interpols1.permute(0,2,3,1)), dim=1),
        torch.cat(list(decoded_interpols0.permute(0,2,3,1)), dim=1)
    ]


D = 512
model_path = "model/model_local_epoch_10000_iter_0.pth"


## load Encoder
model = VSC(cdim=3, hdim=D, channels=str_to_list('32, 64, 128, 256, 512, 512'), image_size=256).cuda()
load_model(model, model_path)
model.eval()

## Load code
stat_sd = pd.read_csv('./data/select-elevational-related-features/select-elevational-related-features_sd_124.csv')
stat_sm = pd.read_csv('./data/select-elevational-related-features/select-elevational-related-features_sm_388.csv')

stat = stat_sd

N = 5

for sex in ['female', 'male']:
    
    feature_pool = np.unique(stat[stat.Sex == sex].feature.values)
    feature_pool_sorted = list(np.sort(feature_pool).astype(str))

    decoded_interpols = get_trends(feature_pool, stat, N=N, sex=sex, elev_min=0, elev_max=3000, D=D)
    

    for i in [0, 1, 2]:
        
        indx = 0
        
        for j in [0, 256, 512, 768, 1024, 1280]:
    
            img_npy_each_alt = decoded_interpols[i][:,j:j+256,:].detach().data.cuda()
            print(img_npy_each_alt.shape)

            io.imsave('save/vsc/%s_%s_%s.jpg' % (sex, i, indx), img_npy_each_alt)
            
            indx = indx+1

    img_npy = torch.cat(decoded_interpols).detach().data.cuda()
    io.imsave('save/vsc/%s_all.jpg' % (sex), img_npy)
    # plt.imshow(img_npy)
    # plt.show()