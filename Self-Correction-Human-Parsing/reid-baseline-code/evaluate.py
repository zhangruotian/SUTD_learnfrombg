import scipy.io
import torch
import numpy as np
import time
import os
os.environ['OMP_NUM_THREADS'] = '1'
import argparse
import logging
import os.path as osp

parser = argparse.ArgumentParser(description='Evaluate')
parser.add_argument('--name', default='two_stream_resnet_equal', type=str, help='save model path')
parser.add_argument('--cross', default='two_stream_resnet_equal.mat', type=str, help='corss testing')
parser.add_argument('--logs_dir', type=str, metavar='PATH', default='log/two_stream_resnet_equal.txt')
opt = parser.parse_args()
#which_epoch = opt.which_epoch
name = opt.name
cross = opt.cross
logs_dir=opt.logs_dir
#sxx updata

#######################################################################
# log
def logger_config(log_path,logging_name):
    '''
    配置log
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :return:
    '''
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger

#######################################################################
# Evaluate
def evaluate_xx(qf,ql,qc,gf,gl,gc):
    query = qf
    score = np.dot(gf,query)
    # predict index
    index = np.argsort(score)  #from small to large
    index = index[::-1]
    #index = index[0:2000]
    # good index
    query_index = np.argwhere(gl==ql)
    camera_index = np.argwhere(gc==qc)

    good_index = np.setdiff1d(query_index, camera_index, assume_unique=True)
    junk_index1 = np.argwhere(gl==-1)
    junk_index2 = np.intersect1d(query_index, camera_index)
 #sxx
    junk_index3 = camera_index
    junk_index_xx= np.append(junk_index1, junk_index3) #.flatten())
    CMC_tmp_xx = compute_mAP(index, good_index, junk_index_xx)
    return CMC_tmp_xx

def evaluate(qf,ql,qc,gf,gl,gc):
    query = qf
    score = np.dot(gf,query)
    # predict index
    index = np.argsort(score)  #from small to large
    index = index[::-1]
    #index = index[0:2000]
    # good index
    query_index = np.argwhere(gl==ql)
    camera_index = np.argwhere(gc==qc)

    good_index = np.setdiff1d(query_index, camera_index, assume_unique=True)
    junk_index1 = np.argwhere(gl==-1)
    junk_index2 = np.intersect1d(query_index, camera_index)
    junk_index = np.append(junk_index2, junk_index1) #.flatten())

    CMC_tmp = compute_mAP(index, good_index, junk_index)
    return CMC_tmp

def compute_mAP(index, good_index, junk_index):
    ap = 0
    cmc = torch.IntTensor(len(index)).zero_()
    if good_index.size==0:   # if empty
        cmc[0] = -1
        return ap,cmc

    # remove junk_index
    mask = np.in1d(index, junk_index, invert=True)
    index = index[mask]

    # find good_index index
    ngood = len(good_index)
    mask = np.in1d(index, good_index)
    rows_good = np.argwhere(mask==True)
    rows_good = rows_good.flatten()
    
    cmc[rows_good[0]:] = 1
    for i in range(ngood):
        d_recall = 1.0/ngood
        precision = (i+1)*1.0/(rows_good[i]+1)
        if rows_good[i]!=0:
            old_precision = i*1.0/rows_good[i]
        else:
            old_precision=1.0
        ap = ap + d_recall*(old_precision + precision)/2

    return ap, cmc

######################################################################
result = scipy.io.loadmat(os.path.join('model_test/',name,cross))
query_feature = result['query_f']
query_cam = result['query_cam'][0]
query_label = result['query_label'][0]
gallery_feature = result['gallery_f']
gallery_cam = result['gallery_cam'][0]
gallery_label = result['gallery_label'][0]

CMC = torch.IntTensor(len(gallery_label)).zero_()
ap = 0.0
#print(query_label)
for i in range(len(query_label)):
    ap_tmp, CMC_tmp = evaluate(query_feature[i],query_label[i],query_cam[i],gallery_feature,gallery_label,gallery_cam)
    if CMC_tmp[0]==-1:
        continue
    CMC = CMC + CMC_tmp
    ap += ap_tmp
 #   print(i, CMC_tmp[0])

#############################add#################################
CMC_xx = torch.IntTensor(len(gallery_label)).zero_()
ap_xx = 0.0
for i in range(len(query_label)):
    ap_tmp_xx, CMC_tmp_xx = evaluate_xx(query_feature[i],query_label[i],query_cam[i],gallery_feature,gallery_label,gallery_cam)
    if CMC_tmp_xx[0]==-1:
        continue
    CMC_xx = CMC_xx + CMC_tmp_xx
    ap_xx += ap_tmp_xx
#    print(i, CMC_tmp_xx[0])

CMC = CMC.float()
CMC = CMC/len(query_label) #average CMC

CMC_xx = CMC_xx.float()
CMC_xx = CMC_xx/len(query_label) #average CMC
#
print(name,cross)
#print('original_top1:%f top5:%f top10:%f mAP:%f'%(CMC[0],CMC[4],CMC[9],ap/len(query_label)))
#
#print('modified_top1:%f top5:%f top10:%f mAP:%f'%(CMC_xx[0],CMC_xx[4],CMC_xx[9],ap_xx/len(query_label)))
#
logger = logger_config(log_path=logs_dir, logging_name='evaluate_log')
logger.info('train on %s'%(name))
logger.info('test on %s'%(cross))
logger.info('top1:%f top5:%f top10:%f mAP:%f'%(CMC[0],CMC[4],CMC[9],ap/len(query_label)))