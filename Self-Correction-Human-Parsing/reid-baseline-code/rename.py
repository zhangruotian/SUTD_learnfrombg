import os
def rename(path):

    '修改文件夹下所有文件名字，不修改文件夹名字'
    FileList = os.listdir(path)
    '遍历所有文件'
    for files in FileList:
        '原来的文件路径'
        oldDirPath = os.path.join(path, files)
        '如果是文件夹则递归调用'
        if os.path.isdir(oldDirPath):
            rename(oldDirPath)
            continue
        '文件名'
        fileName = os.path.splitext(files)[0]
        '文件扩展名'
        fileType = os.path.splitext(files)[1]
        '新的文件路径'
        newDirPath = os.path.join(path, fileName+'_bg' + fileType)
        '重命名'
        os.rename(oldDirPath, newDirPath)

if __name__ == '__main__':
    rename('../example3/pytorch_background')