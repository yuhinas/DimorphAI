import torch
from networks import *
from utils import str_to_list, load_model
import matplotlib.pyplot as plt
from skimage import io as io
import numpy as np
import pandas as pd

D = 512
model_path = "./model/model_local_epoch_10000_iter_0.pth"

## load Encoder
model = VSC(cdim=3, hdim=D, channels=str_to_list('32, 64, 128, 256, 512, 512'), image_size=256).cuda()
load_model(model, model_path)
model.eval()

## Load code
X = pd.read_csv('./data/encode/encode_sd_codes_rep.csv')

for i in range(len(X)):

    img_path = X.iloc[i,512]
    inputs = X.iloc[i,0:-1]
    inputs = np.array(inputs).reshape(1,512)
    inputs = inputs.astype(float)

    with torch.no_grad():

        outputs = model.decode(torch.from_numpy(inputs).float().cuda())
        outputs = torch.cat(list(outputs.permute(0,2,3,1)), dim=1)
        img_npy = outputs.detach().data.cpu()

        io.imsave('./decoder_img/%s' %img_path, img_npy)
    
