#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 20:25:44 2019

@author: wangzhongju
"""

import cv2
import numpy as np
import os
import os.path as osp
import glob
import matplotlib.pyplot as plt

#感知哈希算法
def pHash(image): 
    image = cv2.resize(image,(32,32), interpolation=cv2.INTER_CUBIC) 
    image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) 
#     cv2.imshow('image', image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
    # 将灰度图转为浮点型，再进行dct变换 
    dct = cv2.dct(np.float32(image))
#     print(dct)
    # 取左上角的8*8，这些代表图片的最低频率 
    # 这个操作等价于c++中利用opencv实现的掩码操作 
    # 在python中进行掩码操作，可以直接这样取出图像矩阵的某一部分 
    dct_roi = dct[0:8,0:8]  
    avreage = np.mean(dct_roi) 
    hash = [] 
    for i in range(dct_roi.shape[0]): 
        for j in range(dct_roi.shape[1]): 
            if dct_roi[i,j] > avreage: 
                hash.append(1) 
            else: 
                hash.append(0) 
    return hash

#均值哈希算法
def aHash(image):
    #缩放为8*8
    image=cv2.resize(image,(8,8),interpolation=cv2.INTER_CUBIC)
    #转换为灰度图
    image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    avreage = np.mean(image) 
    hash = [] 
    for i in range(image.shape[0]): 
        for j in range(image.shape[1]): 
            if image[i,j] > avreage: 
                hash.append(1) 
            else: 
                hash.append(0) 
    return hash

#差值感知算法
def dHash(image):
    #缩放9*8
    image=cv2.resize(image,(9,8),interpolation=cv2.INTER_CUBIC)
    #转换灰度图
    image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
#     print(image.shape)
    hash=[]
    #每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(8):
        for j in range(8):
            if image[i,j]>image[i,j+1]:
                hash.append(1)
            else:
                hash.append(0)
    return hash

#计算汉明距离
def Hamming_distance(hash1,hash2): 
    num = 0
    for index in range(len(hash1)): 
        if hash1[index] != hash2[index]: 
            num += 1
    return num
if __name__ == "__main__":
    #image_file1 = '../image/img_all/004.jpg'
    #image_file2 = '../image/img_all/005.jpg'
    realpath = osp.abspath('..')
    imgpath = osp.join(realpath, 'image', 'img_fore')
    imgs = glob.glob(imgpath+"/*")
    Hash_dist_list = []
    similarity_list = []
    for i in range(len(imgs)-1):
        image_file1 = imgs[i]
        image_file2 = imgs[i+1]
        img1 = cv2.imread(image_file1)
        img2 = cv2.imread(image_file2)
        hash1 = aHash(img1)
        hash2 = aHash(img2)
        dist = Hamming_distance(hash1, hash2)
        #将距离转化为相似度
        similarity = 1 - dist * 1.0 / 64
        Hash_dist_list.append(dist)
        similarity_list.append(similarity)
        print(dist)
        print(similarity)
    print(len(Hash_dist_list))
    fig = plt.figure(figsize=(20,10),dpi=50)
    x = range(1,len(Hash_dist_list)+1)
    plt.title('similarity between two pictures',fontsize=20,fontweight='black',
               fontstyle='italic')
    plt.xlabel("image number",fontsize=16,fontweight='black',
               fontstyle='italic')
    plt.ylabel("similarity",fontsize=16,fontweight='black',
               fontstyle='italic')
#    plt.tight_layout(pad=1.0,w_pad=0.5,h_pad=1.0)
    plt.tight_layout()
    plt.plot(x,similarity_list,label="similarity")
    plt.plot(x,[0.9 for i in range(len(similarity_list))],color='red',label="Line of threshold value")
    plt.legend(loc='lower right', fontsize=16)
    plt.savefig("./similarity")
#    plt.xticks(x,x[::1])
    plt.show()
    
        #Shows images with a similarity greater than 0.9
#        if similarity > 0.90:
#            img1 = cv2.imread(image_file1)
#            img2 = cv2.imread(image_file2)
#            cv2.imshow("{}".format(osp.basename(image_file1)), img1)
#            cv2.imshow("{}".format(osp.basename(image_file2)), img2)
#            cv2.waitKey(0)
#            cv2.destroyAllWindows()
            
            
            
            
            
            
            
            
            
            
