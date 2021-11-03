# -*- coding: utf-8 -*-
"""Generate_mixing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fLvHVr-RXe6X3aYCR7XIAgth-c54qP2_

StyleGan_pytorch_generator
"""

#!cd /content/drive/MyDrive/Stylegan_shang/Model2.py

from Model2 import StyledGenerator

#import os

#os.chdir('/content/drive/MyDrive/Stylegan_shang')   #修改当前工作目录

import argparse
import math

import torch
from torchvision import utils

device= torch.device('cuda:0')
#generator = StyledGenerator().to(device)

def sample(generator, step, mean_style, n_sample):
    image = generator(
        torch.randn(n_sample, 512).to(device),
        step=step,
        alpha=1,
        mean_style=mean_style,
        style_weight=0.7,
    )
    
    return image

def get_mean_style(generator, device):
    mean_style = None

    for i in range(10):
        style = generator.mean_style(torch.randn(1024, 512).to(device))

        if mean_style is None:
            mean_style = style

        else:
            mean_style += style

    mean_style /= 10
    return mean_style

def style_mixing(generator, step, mean_style, n_source, n_target, device):
    source_code = torch.randn(n_source, 512).to(device)
    target_code = torch.randn(n_target, 512).to(device)
    
    shape = 4 * 2 ** step
    alpha = 1

    images = [torch.ones(1, 3, shape, shape).to(device) * -1]

    source_image = generator(
        source_code, step=step, alpha=alpha, mean_style=mean_style, style_weight=0.7
    )
    target_image = generator(
        target_code, step=step, alpha=alpha, mean_style=mean_style, style_weight=0.7
    )

    images.append(source_image)

    for i in range(n_target):
        image = generator(
            [target_code[i].unsqueeze(0).repeat(n_source, 1), source_code],
            step=step,
            alpha=alpha,
            mean_style=mean_style,
            style_weight=0.7,
            mixing_range=(0, 1),
        )
        images.append(target_image[i].unsqueeze(0))
        images.append(image)

    images = torch.cat(images, 0)
    
    return images

'''
Note that:
train_step-2: Genarate size=8
train_step-3:Genarate size=16
train_step-4:Genarate size=32
train_step-5:Genarate size=64
and so on
'''
size=64
n_row=1
n_col=5
path='/content/drive/MyDrive/StyleGAN_rosin/checkpoint/train_step-5.model'
mixing=True
num_mixing=20



from train_stylegan import imshow

if __name__ == '__main__':

    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=1024, help='size of the image')
    parser.add_argument('--n_row', type=int, default=3, help='number of rows')
    parser.add_argument('--n_col', type=int, default=5, help='number of columns')
    parser.add_argument('path', type=str, help='path to checkpoint file')
    
    args = parser.parse_args()
    
    device = 'cuda'
    '''

    #512
    generator = StyledGenerator().to(device)
    generator.load_state_dict(torch.load(path)['g_running'])

    #generator.eval()
    generator.train()

    mean_style = get_mean_style(generator, device)

    step = int(math.log(size, 2)) - 2
    
    img = sample(generator, step, mean_style, n_row * n_col)
    utils.save_image(img, 'g_sample.png', nrow=n_col, normalize=True, range=(-1, 1))


    if mixing==True:
      for j in range(num_mixing):
        img = style_mixing(generator, step, mean_style, n_col, n_row, device)
        #imshow(img,j)
        utils.save_image(
            img, f'sample_mixing_{j}.png', nrow=n_col + 1, normalize=True, range=(-1, 1)
        )



      
    

      

      
      

    '''
    
    for j in range(20):
        img = style_mixing(generator, step, mean_style, args.n_col, args.n_row, device)
        utils.save_image(
            img, f'sample_mixing_{j}.png', nrow=args.n_col + 1, normalize=True, range=(-1, 1)
        )

    '''