import torch
from torch import nn

import matplotlib.pyplot as plt

import os

import skimage
import numpy as np
import pandas as pd

import fire

from networks import *
from utils import str_to_list, load_model, is_image_file
from dataset import *
from touch_dir import touch_dir

def encoding_vsc(epoch_num=10000, model=None):

    code_dim = 512

    model_id = 'epoch_%d' % epoch_num

    #--------------build models -------------------------
    if model is None:
        model = VSC(cdim=3, hdim=code_dim, channels=str_to_list('32, 64, 128, 256, 512, 512'), image_size=256).cuda()
        load_model( model ,"./model/model_local_epoch_10000_iter_0.pth")

    model.eval()

    dataroot = './data/All_dataset256'

    #-----------------load dataset--------------------------
    image_list = [x for x in listdir(dataroot) if is_image_file(x)]  
    train_list = image_list[:len(image_list)]
    #train_list = image_list[:38]
    assert len(train_list) > 0
    print (len(train_list))
    
    train_set = ImageDatasetFromFile(train_list, dataroot, input_height=None, crop_height=None, output_height=256, is_mirror=False, aug=False, return_filename=True)
    batch_size = 100
    train_data_loader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, shuffle=False, num_workers=4)

    mu_s = np.empty((len(train_list), code_dim))
    logvar_s = np.empty((len(train_list), code_dim))
    logspike_s = np.empty((len(train_list), code_dim))

    all_filenames = np.array([])
    with torch.no_grad():
        for iteration, (batch, _, filenames) in enumerate(train_data_loader, 0):
            
            print(iteration, end='\r')
            #print(filenames)
            
            real= Variable(batch).cuda()

            mu, logvar, logspike = model.encode(real)
            #z = model.reparameterize(mu, logvar, logspike)

            all_filenames = np.append(all_filenames, filenames)

            from_ = iteration * batch_size
            to_ = from_ + batch.size(0)

            mu_s[from_:to_,] = mu.detach().data.cpu().numpy()
            logvar_s[from_:to_,] = logvar.detach().data.cpu().numpy()
            logspike_s[from_:to_,] = logspike.detach().data.cpu().numpy()

            del real
            del mu
            del logvar
            del logspike
        print()

    with torch.no_grad():
        repeatN = 1000
        codes_ = model.reparameterize(torch.from_numpy(mu_s).cuda(), torch.from_numpy(logvar_s).cuda(), torch.from_numpy(logspike_s).cuda())
        for rep_ in range(1, repeatN):
            print('Repeating %d' % rep_, end='\r')
            codes_ = codes_ + model.reparameterize(torch.from_numpy(mu_s).cuda(), torch.from_numpy(logvar_s).cuda(), torch.from_numpy(logspike_s).cuda())
        print()
        codes = (codes_ / repeatN).detach().data.cpu().numpy()

    codes.shape

    df = pd.DataFrame(data=codes, columns=range(codes.shape[1]))
    mu_df = pd.DataFrame(data=mu_s, columns=range(mu_s.shape[1]))
    logvar_df = pd.DataFrame(data=logvar_s, columns=range(logvar_s.shape[1]))
    logspike_df = pd.DataFrame(data=logspike_s, columns=range(logspike_s.shape[1]))
    
    df['filename'] = all_filenames
    mu_df['filename'] = all_filenames
    logvar_df['filename'] = all_filenames
    logspike_df['filename'] = all_filenames
    #print(df)

    to_save = "./save/vsc/%s_SM" % model_id
    touch_dir(to_save)

    #np.save("%s/codes.npy" % to_save, codes)
    df.to_csv("%s/codes_rep.csv" % to_save, sep="\t")
    mu_df.to_csv("%s/mu_s_rep.csv" % to_save, sep="\t")
    logvar_df.to_csv("%s/logvar_s_rep.csv" % to_save, sep="\t")
    logspike_df.to_csv("%s/logspike_s_rep.csv" % to_save, sep="\t")

if __name__ == '__main__':
    fire.Fire(encoding_vsc)

encoding_vsc(epoch_num=10000)