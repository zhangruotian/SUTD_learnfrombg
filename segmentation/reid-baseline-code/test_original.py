# -*- coding: utf-8 -*-


from __future__ import print_function, division

import os
os.environ['OMP_NUM_THREADS'] = '1'
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
from torch.autograd import Variable
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import time
import scipy.io
from model import ft_net, two_stream_resnet
import two_stream_dataset
######################################################################
# Options
# --------
parser = argparse.ArgumentParser(description='Training')
parser.add_argument('--gpu_ids',default='1', type=str,help='gpu_ids: e.g. 0  0,1,2  0,2')
parser.add_argument('--which_epoch',default='49', type=str, help='0,1,2,3...or last')
parser.add_argument('--test_dir',default='../fg_person/pytorch',type=str, help='./test_data')
parser.add_argument('--name', default='fg_person_baseline', type=str, help='save model path')
parser.add_argument('--cross', default='fg_person_baseline.mat', type=str, help='corss testing')
parser.add_argument('--batchsize', default=32, type=int, help='batchsize')
parser.add_argument('--use_two_stream_resnet', action='store_true', help='use our two stream resnet' )
parser.add_argument('--training_set_classes', default=318,type=int, help='the number of classes of training set' )
opt = parser.parse_args()

str_ids = opt.gpu_ids.split(',')
#which_epoch = opt.which_epoch
name = opt.name
cross = opt.cross
test_dir = opt.test_dir

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

if opt.use_two_stream_resnet:
    transform_train_list = [
        transforms.Resize((384,192), interpolation=3),
        # transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]
    transform_bg_list=[
        transforms.Resize((24,12),interpolation=3),
        transforms.ToTensor()
    ]
    data_transforms = {
        'train': transforms.Compose( transform_train_list ),
        'bg': transforms.Compose(transform_bg_list),
    }
else:
    data_transforms = transforms.Compose([
        transforms.Resize((256, 128), interpolation=3),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

data_dir = test_dir
if opt.use_two_stream_resnet:
    image_datasets = {x: two_stream_dataset.TwoStreamDataset(os.path.join(data_dir,x) ,data_transforms['train'],data_transforms['bg']) for x in ['gallery','query']}

else:
    image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms) for x in ['gallery', 'query']}
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
        ff = torch.FloatTensor(n,2048).zero_()
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

def extract_feature_two_stream(model,dataloaders):
    features = torch.FloatTensor()
    count = 0
    for data in dataloaders:
        (img1,img2),label = data
        n, c, h, w = img1.size()
        count += n
        print(count)
        ff = torch.FloatTensor(n, 4096).zero_()
        for i in range(2):
            if(i==1):
                img1 = fliplr(img1)
                img2 = fliplr(img2)
            input_img1 = Variable(img1.cuda())
            input_img2 = Variable(img2.cuda())
            outputs = model(input_img1,input_img2)
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
    for path, *_ in img_path:
        filename = path.split('/')[-1]
        label = filename[0:4]
        camera = filename.split('c')[1]
        if label[0:2]=='-1':
            labels.append(-1)
        else:
            labels.append(int(label))
        camera_id.append(int(camera[0]))
    return camera_id, labels

gallery_path = image_datasets['gallery'].imgs
query_path = image_datasets['query'].imgs

gallery_cam,gallery_label = get_id(gallery_path)
query_cam,query_label = get_id(query_path)

######################################################################
# Load Collected data Trained model
nnn=opt.training_set_classes
# duke-market 702
print('-------test-----------')

if opt.use_two_stream_resnet:
    model_structure = two_stream_resnet(nnn,True)
else:
    model_structure = ft_net(nnn)
model = load_network(model_structure)

#model.model.avgpool = nn.AdaptiveMaxPool2d((7,1))

# Remove the final fc layer and classifier layer
if not opt.use_two_stream_resnet:
    model.classifier.fc = nn.Sequential()
    model.classifier = nn.Sequential()


# Change to test mode
model = model.eval()
if use_gpu:
    model = model.cuda()

# Extract feature
if opt.use_two_stream_resnet:
    gallery_feature = extract_feature_two_stream(model,dataloaders['gallery'])
    query_feature = extract_feature_two_stream(model,dataloaders['query'])
else:
    gallery_feature = extract_feature(model, dataloaders['gallery'])
    query_feature = extract_feature(model, dataloaders['query'])


# Save to Matlab for check
result = {'gallery_f':gallery_feature.numpy(),'gallery_label':gallery_label,'gallery_cam':gallery_cam,'query_f':query_feature.numpy(),'query_label':query_label,'query_cam':query_cam}
scipy.io.savemat(os.path.join('model_test/',name,cross),result)

