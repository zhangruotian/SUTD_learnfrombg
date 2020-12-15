import os
# for root,dirs,files in os.walk('../example3/pytorch/train'):
#     print(root)
#     print(dirs)
#     print(files)
#     import os
samples=[]
for root, dirs, files in os.walk('../example3/pytorch/train/0116', topdown=False):
    for name in files:
        if name.find('bg')!=-1:
            file_name,file_type=os.path.splitext(name)
            original_name=file_name[0:-3]+file_type
            label=int(name[0:4])
            samples.append((original_name,name,label))
print(samples)
print(len(samples))
    # for name in dirs:
    #     print(os.path.join(root, name))