import os

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt

import fire

from touch_dir import touch_dir

def dim_hist_sampling(epoch_num=40000, model=None, is_vsc=False):

    code_dim = 512

    model_id = 'epoch_%d' % epoch_num

    if not is_vsc:
        from_dir = "./save/vsc/%s" % model_id
    else:
        from_dir = "./save/vsc/%s" % model_id

    try:
        #codes = np.load("%s/codes.npy" % from_dir)
        codes_df = pd.read_csv(f'{from_dir}/codes.csv', sep='\t', index_col=0)
        codes = codes_df.values[:,:code_dim].astype(float)
    except:
        if is_vsc:
            from encoding_vsc import encoding_vsc
            encoding_vsc(epoch_num=epoch_num, model=model)
        else:
            from encoding_vae import encoding_vae
            encoding_vae(epoch_num=epoch_num, model=model)
        codes = np.load("%s/codes.npy" % from_dir)
    
    #print(codes)
    #codes.shape

    codes_t = codes.transpose([1,0])
    #plt.hist(codes_t[0], bins=40)
    #plt.show()
    
    step = 0.33
    margin = 0.16
    epsilon = step / 10
    q005_tic = np.quantile(codes_t, np.arange(start=margin, stop= 1 - margin + epsilon, step=step), axis=1)
    #q005_tic.shape
    #plt.plot(q005_tic[:,0])

    min_tic = np.min(codes, axis=0)
    #min_tic.shape
    lower_tips = np.quantile(np.concatenate([[min_tic], [q005_tic[0]]]), np.arange(start=0, stop=1, step=0.33), axis=0)
    max_tic = np.max(codes, axis=0)
    upper_tips = np.quantile(np.concatenate([[max_tic], [q005_tic[-1]]]), np.arange(start=0.05, stop=1.005, step=0.33), axis=0)

    tics = np.concatenate([lower_tips, q005_tic, upper_tips], axis=0)
    #tics.shape

    np.save("%s/q005.npy" % from_dir, tics.transpose([1,0]))

    

if __name__ == '__main__':
    fire.Fire(dim_hist_sampling)
