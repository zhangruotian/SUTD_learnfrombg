import os
import cv2
import argparse
from tqdm import tqdm
parser = argparse.ArgumentParser(description="Get the background of the original images")
parser.add_argument('--image_folder_path', type=str, default='example3/query',help='Path to image')
parser.add_argument('--masks_folder_path', type=str, default='example3/query_bg',help='Path to mask')
parser.add_argument('--bg_folder_path', type=str, default='example3/query_background',help='Path to the foreground of image')

args = parser.parse_args()
image_list=os.listdir(args.image_folder_path)

if not os.path.exists(args.bg_folder_path):
    os.makedirs(args.bg_folder_path)
for i in tqdm(image_list):
    ori_data=cv2.imread(os.path.join(args.image_folder_path,i))
    mask_data=cv2.imread(os.path.join(args.masks_folder_path,i))
    fore_data=ori_data*mask_data
    cv2.imwrite(os.path.join(args.bg_folder_path,i),fore_data)