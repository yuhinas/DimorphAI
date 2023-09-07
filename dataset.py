import torch
import torch.utils.data as data

from os import listdir
from os.path import join
from PIL import Image, ImageOps
#import random
import numpy as np
import torchvision.transforms as transforms

import skimage.io as io
from imgaug import augmenters as iaa
sometimes = lambda aug: iaa.Sometimes(0.5, aug)
most_of_the_time = lambda aug: iaa.Sometimes(0.9, aug)
usually = lambda aug: iaa.Sometimes(0.75, aug)
always = lambda aug: iaa.Sometimes(1, aug)
charm = lambda aug: iaa.Sometimes(0.33, aug)
seldom = lambda aug: iaa.Sometimes(0.2, aug)

augseq_special = iaa.Sequential([
    iaa.Fliplr(0.5)
    ,sometimes(iaa.Affine(
            scale={"x": (0.9, 1.1), "y": (0.9, 1.1)}, # scale images to 80-120% of their size, individually per axis
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)}, # translate by -20 to +20 percent (per axis)
            rotate=(-30, 30), # rotate by -45 to +45 degrees
            mode='symmetric',
        ))
])

augseq_all = iaa.Sequential([
    iaa.Fliplr(0.5),
    most_of_the_time(iaa.Affine(
            scale={"x": (0.9, 1.1), "y": (0.9, 1.1)}, # scale images to 90-110% of their size, individually per axis
            mode='symmetric',
        )),
    iaa.Multiply((0.9, 1.1), per_channel=0.3),
    iaa.ContrastNormalization((0.9, 1.1), per_channel=0.3),
])

def rotation_ratio():
    thickness = 0.4
    rand = np.random.rand()
    if rand >= 0 and rand < thickness:
        return augseq_noise_1
    elif rand >= thickness and rand < (thickness * 2):
        return augseq_noise_2
    else:
        return augseq_noise


augseq_noise = iaa.Sequential([
    usually(iaa.Affine(
            #scale={"x": (0.9, 1.1), "y": (0.9, 1.1)}, # scale images to 90-110% of their size, individually per axis
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)}, # translate by -10 to +10 percent (per axis)
            rotate=(-90,90), # rotate by -10 to +10 degrees
            mode='symmetric',
        )),
    charm(iaa.CoarseDropout(p=0.11, size_percent=0.033)),
    charm(iaa.CoarseDropout(p=0.11, size_percent=0.067)),
    charm(iaa.CoarseDropout(p=0.11, size_percent=0.1))
])

augseq_noise_1 = iaa.Sequential([
    usually(iaa.Affine(
            #scale={"x": (0.9, 1.1), "y": (0.9, 1.1)}, # scale images to 90-110% of their size, individually per axis
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)}, # translate by -10 to +10 percent (per axis)
            rotate=(-180,-90), # rotate by -10 to +10 degrees
            mode='symmetric',
        )),
    charm(iaa.CoarseDropout(p=0.11, size_percent=0.033)),
    charm(iaa.CoarseDropout(p=0.11, size_percent=0.067)),
    charm(iaa.CoarseDropout(p=0.11, size_percent=0.1))
])

augseq_noise_2 = iaa.Sequential([
    usually(iaa.Affine(
            #scale={"x": (0.9, 1.1), "y": (0.9, 1.1)}, # scale images to 90-110% of their size, individually per axis
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)}, # translate by -10 to +10 percent (per axis)
            rotate=(90,180), # rotate by -10 to +10 degrees
            mode='symmetric',
        )),
    charm(iaa.CoarseDropout(p=0.11, size_percent=0.033)),
    charm(iaa.CoarseDropout(p=0.11, size_percent=0.067)),
    charm(iaa.CoarseDropout(p=0.11, size_percent=0.1))
])



def load_image(file_path, input_height=128, input_width=None, output_height=128, output_width=None,
              crop_height=None, crop_width=None, is_random_crop=True, is_mirror=True, is_gray=False):
    
    if input_width is None:
        input_width = input_height
    if output_width is None:
        output_width = output_height
    if crop_width is None:
        crop_width = crop_height
    
    img = Image.open(file_path)
    if is_gray is False and img.mode is not 'RGB':
        img = img.convert('RGB')
    if is_gray and img.mode is not 'L':
        img = img.convert('L')
      
    if is_mirror and random.randint(0,1) is 0:
        img = ImageOps.mirror(img)    
      
    if input_height is not None:
        img = img.resize((input_width, input_height),Image.BICUBIC)
      
    if crop_height is not None:
        [w, h] = img.size
        if is_random_crop:
            #print([w,cropSize])
            cx1 = random.randint(0, w-crop_width)
            cx2 = w - crop_width - cx1
            cy1 = random.randint(0, h-crop_height) 
            cy2 = h - crop_height - cy1
        else:
            cx2 = cx1 = int(round((w-crop_width)/2.))
            cy2 = cy1 = int(round((h-crop_height)/2.))
            img = ImageOps.crop(img, (cx1, cy1, cx2, cy2))      

    img = img.resize((output_width, output_height),Image.BICUBIC)
    return img
   
      

class ImageDatasetFromFile(data.Dataset):
    def __init__(self, image_list, root_path, y=None,
                input_height=128, input_width=None, output_height=128, output_width=None,
                crop_height=None, crop_width=None, is_random_crop=False, is_mirror=True, is_gray=False, aug=True, return_filename=False):
        super(ImageDatasetFromFile, self).__init__()
                
        self.image_filenames = image_list 
        self.y = y
        self.is_random_crop = is_random_crop
        self.is_mirror = is_mirror
        self.input_height = input_height
        self.input_width = input_width
        self.output_height = output_height
        self.output_width = output_width
        self.root_path = root_path
        self.crop_height = crop_height
        self.crop_width = crop_width
        self.is_gray = is_gray
        self.aug = aug
        self.return_filename = return_filename
                       
        self.input_transform = transforms.Compose([ 
                                   transforms.ToTensor()                                                                      
                               ])

    def __getitem__(self, index):
          
        # img = load_image(join(self.root_path, self.image_filenames[index]),
        #                           self.input_height, self.input_width, self.output_height, self.output_width,
        #                           self.crop_height, self.crop_width, self.is_random_crop, self.is_mirror, self.is_gray)

        img = io.imread(join(self.root_path, self.image_filenames[index]))
        if self.aug:
            denoised_img = augseq_all.augment_images([img])
            img = rotation_ratio().augment_images(denoised_img)
        else:
            img = [img]
            denoised_img = img

        img = self.input_transform(img[0])
        denoised_img = self.input_transform(denoised_img[0])
        
        if self.y is None:
            if self.return_filename:
                return img, denoised_img, self.image_filenames[index]
            else:
                return img, denoised_img
        else:
            if self.return_filename:
                return img, denoised_img, self.y[index], self.image_filenames[index]
            else:
                return img, denoised_img, self.y[index]

    def __len__(self):
        return len(self.image_filenames)


class ImageDatasetFromFileSpecial(data.Dataset):
    def __init__(self, image_list, root_path, y=None,
                input_height=128, input_width=None, output_height=128, output_width=None,
                crop_height=None, crop_width=None, is_random_crop=False, is_mirror=True, is_gray=False, aug=True, return_filename=False):
        super(ImageDatasetFromFileSpecial, self).__init__()
                
        self.image_filenames = image_list 
        self.y = y
        self.is_random_crop = is_random_crop
        self.is_mirror = is_mirror
        self.input_height = input_height
        self.input_width = input_width
        self.output_height = output_height
        self.output_width = output_width
        self.root_path = root_path
        self.crop_height = crop_height
        self.crop_width = crop_width
        self.is_gray = is_gray
        self.aug = aug
        self.return_filename = return_filename
                       
        self.input_transform = transforms.Compose([ 
                                   transforms.ToTensor()                                                                      
                               ])

    def __getitem__(self, index):
          
        img = io.imread(join(self.root_path, self.image_filenames[index]))
        if self.aug:
            img = augseq_special.augment_images([img])
        else:
            img = [img]

        #print(img[0].shape)
        img = self.input_transform(img[0].copy())
        #print(img)
        
        if self.y is None:
            if self.return_filename:
                return img, self.image_filenames[index]
            else:
                return img
        else:
            if self.return_filename:
                return img, self.y[index], self.image_filenames[index]
            else:
                return img, self.y[index]

    def __len__(self):
        return len(self.image_filenames)



class GeneralDataset(data.Dataset):
    def __init__(self, x, y):
        super(GeneralDataset, self).__init__()
        self.x = x
        self.y = y

    def __getitem__(self, index):
        return self.x[index], self.y[index]

    def __len__(self):
        return self.x.shape[0]