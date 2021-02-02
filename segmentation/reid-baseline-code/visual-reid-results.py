# -*- coding: utf-8 -*-

from __future__ import print_function, division

import argparse
import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np
import autograd.numpy as np
from torchvision import datasets, models, transforms
import os
import scipy.io
from model import ft_net, ft_net_dense

from reid.utils.distance import compute_dist
from reid.evaluators import pairwise_distance
from reid.utils import to_numpy
from reid.utils.visualization import get_rank_list
from reid.utils.visualization import save_rank_list_to_im
from os.path import join as ospj
from reid.utils.utils import str2bool
######################################################################
# Options
# --------
parser = argparse.ArgumentParser(description='Training')
parser.add_argument('--gpu_ids',default='2', type=str,help='gpu_ids: e.g. 0  0,1,2  0,2')
parser.add_argument('--which_epoch',default='last', type=str, help='0,1,2,3...or last')
parser.add_argument('--test_dir',default='./market/pytorch',type=str, help='./test_data')
parser.add_argument('--ptest_dir',default='./market/pytorch',type=str, help='./ptest_data')
parser.add_argument('--name', default='ft_ResNet50', type=str, help='save model path')
parser.add_argument('--batchsize', default=32, type=int, help='batchsize')
parser.add_argument('--use_dense', action='store_true', help='use densenet121' )
parser.add_argument('--cross', default='pytorch_result.mat', type=str, help='corss testing')


parser.add_argument('--num_queries', type=int, default=16)
parser.add_argument('--rank_list_size', type=int, default=10)
parser.add_argument('--exp_dir', type=str, default='')
#  flip if consider to remove same_cam, 1 means removing
parser.add_argument('--same_cam', type=int, default=1)
parser.add_argument('--visual', action='store_true',
                    help="visualization only")
parser.add_argument('--extractf', action='store_true',
                    help="extractf only")


opt = parser.parse_args()

str_ids = opt.gpu_ids.split(',')
#which_epoch = opt.which_epoch
name = opt.name
cross = opt.cross
test_dir = opt.test_dir
ptest_dir = opt.ptest_dir
gpu_ids = []
for str_id in str_ids:
    id = int(str_id)
    if id >=0:
        gpu_ids.append(id)

# set gpu ids
if len(gpu_ids)>0:
    torch.cuda.set_device(gpu_ids[0])

######################################################################
# Load Data
# ---------
#
# We will use torchvision and torch.utils.data packages for loading the
# data.
#
data_transforms = transforms.Compose([
        transforms.Resize((256,128), interpolation=3),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
############### Ten Crop
        #transforms.TenCrop(224),
        #transforms.Lambda(lambda crops: torch.stack(
         #   [transforms.ToTensor()(crop)
          #      for crop in crops]
           # )),
        #transforms.Lambda(lambda crops: torch.stack(
         #   [transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])(crop)
          #       for crop in crops]
          # ))
])


data_dir = ptest_dir
image_datasets = {x: datasets.ImageFolder( os.path.join(data_dir,x) ,data_transforms) for x in ['gallery','query']}
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=opt.batchsize,
                                             shuffle=False, num_workers=0) for x in ['gallery','query']}

class_names = image_datasets['query'].classes
use_gpu = torch.cuda.is_available()

######################################################################
# Load model
#---------------------------
def load_network(network):
    save_path = os.path.join('model_test/',name,'net_%s.pth'%opt.which_epoch)
    network.load_state_dict(torch.load(save_path))
    return network


######################################################################
# Extract feature
# ----------------------
#
# Extract feature from  a trained model.
#
def fliplr(img):
    '''flip horizontal'''
    inv_idx = torch.arange(img.size(3)-1,-1,-1).long()  # N x C x H x W
    img_flip = img.index_select(3,inv_idx)
    return img_flip

def extract_feature(model,dataloaders):
    features = torch.FloatTensor()
    count = 0
    for data in dataloaders:
        img, label = data
        n, c, h, w = img.size()
        count += n
        print(count)
        if opt.use_dense:
            ff = torch.FloatTensor(n,1024).zero_()
        else:
            ff = torch.FloatTensor(n, 2048 * 7).zero_()
        for i in range(2):
            if(i==1):
                img = fliplr(img)
            input_img = Variable(img.cuda())
            outputs = model(input_img)
            f = outputs.data.cpu()
            #print(f.size())
            ff = ff+f
        # norm feature
        fnorm = torch.norm(ff, p=2, dim=1, keepdim=True)
        ff = ff.div(fnorm.expand_as(ff))
        features = torch.cat((features,ff), 0)
    return features

def get_id(img_path):
    camera_id = []
    labels = []
    filenames = []
    for path, v in img_path:
        filename = path.split('/')[-1]
        label = filename[0:4]
        camera = filename.split('c')[1]
        if label[0:2]=='-1':
            labels.append(-1)
        else:
            labels.append(int(label))
        camera_id.append(int(camera[0]))
        filenames.append(filename)
    return camera_id, labels, filenames

gallery_path = image_datasets['gallery'].imgs
query_path = image_datasets['query'].imgs

gallery_cam,gallery_label, gallery_fnames = get_id(gallery_path)
query_cam,query_label, query_fnames = get_id(query_path)

######################################################################
# Load Collected data Trained model
if opt.extractf:
    if name[0:1] == 'm':
        nnn = 751
    elif name == 'duke':
        nnn = 702
    else:
        nnn = 410
    # duke-market 702
    print('-------test-----------')
    if opt.use_dense:
        model_structure = ft_net_dense(nnn)
    else:
        model_structure = ft_net(nnn)
    model = load_network(model_structure)
    model.model.avgpool = nn.AdaptiveMaxPool2d((7, 1))

    # Remove the final fc layer and classifier layer
    model.model.fc = nn.Sequential()
    model.classifier = nn.Sequential()

    # Change to test mode
    model = model.eval()
    if use_gpu:
        model = model.cuda()

    # Extract feature
    gallery_feature = extract_feature(model,dataloaders['gallery'])
    query_feature = extract_feature(model,dataloaders['query'])

    # Save to Matlab for check
    result = {'gallery_f':gallery_feature.numpy(),'gallery_label':gallery_label,'gallery_cam':gallery_cam,'query_f':query_feature.numpy(),'query_label':query_label,'query_cam':query_cam}
    scipy.io.savemat(os.path.join('model_test/',name,cross),result)
else:
    result = scipy.io.loadmat(os.path.join('model_test/',name,cross))
    query_feature = result['query_f']
    gallery_feature = result['gallery_f']


if opt.visual:
    print("Visual:")
    query_ids = np.asarray(query_label)
    gallery_ids = np.asarray(gallery_label)
    query_cams = np.asarray(query_cam)
    gallery_cams = np.asarray(gallery_cam)
    query_fnames = np.asarray(query_fnames)
    gallery_fnames = np.asarray(gallery_fnames)
    # Fix some query images, so that the visualization for different models can
    # be compared.
    q_g_dist = compute_dist(query_feature, gallery_feature, type='euclidean')

    q_g_dist = to_numpy(q_g_dist)

    if opt.num_queries < len(query_ids):
        # Sort in the order of image names
        inds = np.argsort(query_fnames)
        query_ids, query_cams, query_fnames = \
            query_ids[inds], query_cams[inds], query_fnames[inds]
        prng = np.random.RandomState(1)
        # selected query indices
        sel_q_inds = prng.permutation(range(len(query_cams)))[:opt.num_queries]
        query_ids = query_ids[sel_q_inds]
        query_cams = query_cams[sel_q_inds]
        query_fnames = query_fnames[sel_q_inds]
        q_g_dist = q_g_dist[sel_q_inds]

    q_im_paths = [ospj(opt.test_dir, 'query/', n) for n in query_fnames]
    save_paths = [ospj(opt.exp_dir, name, n) for n in query_fnames]
    g_im_paths = [ospj(opt.test_dir, 'gallery/', n) for n in gallery_fnames]
    sss = 0

    for dist_vec, q_id, q_cam, q_im_path, save_path in zip(
            q_g_dist, query_ids, query_cams, q_im_paths, save_paths):
        rank_list, same_id = get_rank_list(
            dist_vec, q_id, q_cam, gallery_ids, gallery_cams, opt.rank_list_size)
        if same_id[0]:
            sss = sss + 1
        print("Visual:",sss)
        save_rank_list_to_im(rank_list, same_id, q_im_path, g_im_paths, save_path)