import os
import cv2
import argparse
from tqdm import tqdm
parser = argparse.ArgumentParser(description="Get the foreground of the original images")
parser.add_argument('--image_folder_path', type=str, default='./test',help='Path to image')
parser.add_argument('--masks_folder_path', type=str, default='./test_out',help='Path to mask')
parser.add_argument('--fore_folder_path', type=str, default='./test_fore',help='Path to the foreground of image')

args = parser.parse_args()
image_list=os.listdir(args.image_folder_path)

if not os.path.exists(args.fore_folder_path):
    os.makedirs(args.fore_folder_path)
for i in tqdm(image_list):
    ori_data=cv2.imread(os.path.join(args.image_folder_path,i))
    mask_data=cv2.imread(os.path.join(args.masks_folder_path,i))
    fore_data=ori_data*mask_data
    cv2.imwrite(os.path.join(args.fore_folder_path,i),fore_data)