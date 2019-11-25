#! /usr/bin/env/ python
# coding=utf-8
#===================================================
#  Copyright (c) 2019 * Ltd. All rights reserved.
#  Editor          : VScode
#  Autor           : config.py
#  Created date    : 2019-11-15
#  Description
#===================================================



import os
import os.path as osp
import sys
import time


arg = sys.argv[1]
imgpath = arg.split("/")[-1]
print(imgpath)
# realpath = os.chdir(osp.join(os.getcwd(), "data"))
path1 = osp.join(os.getcwd(), "data")
path2 = osp.join(os.getcwd(), "res")

#TIME
# time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
time = time.strftime('%Y.%m.%d',time.localtime(time.time()))
print(time)

#Contain
tar_list = os.listdir(osp.join(path1, "tar"))
# print(tar_list)
data_time = []
for a in tar_list:
    b = a.split("-")
    name = b[0]+"."+b[1]+"."+b[2]
    if name not in data_time:
        data_time.append(name)
if data_time == []:
    min_time = "No tar"
    max_time = "No tar"
else:
    min_time = min(data_time)
    max_time = max(data_time)

#Low brightness
data_bright = len(os.listdir(osp.join(path1, "img_bright", imgpath)))
#High occlusion
data_occlusion = len(os.listdir(osp.join(path1, "img_canny", imgpath)))
#High similarity
data_similarity = len(os.listdir(osp.join(path1, "img_simi", imgpath)))
#Bbox compare
data_compare = len(os.listdir(osp.join(path2, imgpath, "other")))
#Available
data_av = len(os.listdir(osp.join(path2, imgpath, "imgorg")))
#Total number of iamges
data_all = data_bright + data_occlusion + data_similarity + data_compare + data_av
with open(osp.join(path1, "result", imgpath, "{}_res.txt".format(imgpath)), "w") as fp:
        fp.writelines("TIME                                  : {}\n".format(time))
        fp.writelines("Contain                               : {0} ~ {1}\n".format(min_time, max_time))
        fp.writelines("\n")
        fp.writelines("Total number of images                : {}\n".format(data_all))
        fp.writelines("Low brightness filter                 : {}\n".format(data_bright))
        fp.writelines("High occlusion filter                 : {}\n".format(data_occlusion))
        fp.writelines("High similarity filter                : {}\n".format(data_similarity))
        fp.writelines("Bbox compare between v3 and v2 filter : {}\n".format(data_compare))
        fp.writelines("Available images for train            : {}".format(data_av))
    
