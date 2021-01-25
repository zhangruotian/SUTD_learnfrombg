import os
from tqdm import tqdm
def rename(path):
    '''
    modify the file names excluding directories

    '''
    FileList = os.listdir(path)
    for files in tqdm(FileList):
        oldDirPath = os.path.join(path, files)
        if os.path.isdir(oldDirPath):
            rename(oldDirPath)
            continue
        fileName = os.path.splitext(files)[0]
        fileType = os.path.splitext(files)[1]
        newDirPath = os.path.join(path, fileName+'_bg' + fileType)
        os.rename(oldDirPath, newDirPath)

if __name__ == '__main__':
    rename('../market_bg_mask/pytorch')