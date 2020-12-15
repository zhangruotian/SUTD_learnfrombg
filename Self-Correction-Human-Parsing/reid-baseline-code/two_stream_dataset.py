from torch.utils.data import Dataset
import os
import cv2
from PIL import Image
'''
two-stream dataloader

author: ruotian
'''
def get_example(dir):
    samples = []
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            if name.find('bg') != -1:
                file_name, file_type = os.path.splitext(name)
                original_name = file_name[0:-3] + file_type
                label = name[0:4]
                full_bg_name=os.path.join(root,name)
                full_original_name=os.path.join(root,original_name)
                samples.append((full_original_name, full_bg_name, label))
    return samples


class TwoStreamDataset(Dataset):
    def __init__(self,dir,transforms=None):
        self.dir=dir
        self.transforms=transforms
        self.examples=get_example(self.dir)
        classes, class_to_idx = self._find_classes(self.dir)
        self.classes = classes
        self.class_to_idx = class_to_idx

    def _find_classes(self, dir):
        classes = [d.name for d in os.scandir(dir) if d.is_dir()]
        classes.sort()
        class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        return classes, class_to_idx

    def __getitem__(self, index):
        original_name, name, label=self.examples[index]
        original_data=Image.open(original_name)
        bg_data=Image.open(name)
        if self.transforms:
            original_data=self.transforms(original_data)
            bg_data=self.transforms(bg_data)
        return (original_data,bg_data),self.class_to_idx[label]


    def __len__(self):
        return len(self.examples)

if __name__ == '__main__':
    data=TwoStreamDataset('../example3/pytorch/train')
    print(len(data))
    print(data[5])