import os
import argparse

parser = argparse.ArgumentParser(description='rename')
parser.add_argument('--dir', default='/home/ruotian/SUTD_learnfrombg/fg_person_bg_mask/pytorch', type=str, help='directory')
opt = parser.parse_args()
dir=opt.dir
def rename(path):
    '''
    modify the file names excluding directories

    '''
    FileList = os.listdir(path)
    for files in FileList:
        oldDirPath = os.path.join(path, files)
        if os.path.isdir(oldDirPath):
            rename(oldDirPath)
            continue
        fileName = os.path.splitext(files)[0]
        fileType = os.path.splitext(files)[1]
        newDirPath = os.path.join(path, fileName+'_bg' + fileType)
        os.rename(oldDirPath, newDirPath)

if __name__ == '__main__':
    rename(dir)
    print('The files have been renamed')