# /usr/bin/python python3
# -*-  coding: utf-8 -*-
"""
Created on Wed May  8 15:17:43 2019

@author: wangzhongju
"""

import os
import os.path as osp
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageStat
import math
import shutil
import glob
import cv2
import sys




def brightness(path):
    im = Image.open(path)
    stat = ImageStat.Stat(im)
    r,g,b = stat.mean
    return math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068 *(b**2))

def brightness_avg(path, b_list, realpath):
    filename = os.path.basename(path)
    os.chdir(path)
    savepath = osp.join(realpath, "img_bright", filename)
    bankpath = osp.join(realpath, "img_bank", filename)
    if not osp.exists(savepath):
        # shutil.rmtree(savepath)
        os.makedirs(savepath)
    if not osp.exists(bankpath):os.makedirs(bankpath)
    for name_list_image in os.listdir():
        if name_list_image.endswith(".jpg"):
            image_url = os.getcwd()+'/'+name_list_image
            if osp.getsize(image_url):
                b = brightness(image_url)
                b_list.append(b)
                # print("image: ", image_url, "   brightness: ", b)
                name = osp.basename(image_url).split(".")[0] + "_%s"%int(b) + ".jpg"
                # shutil.copy(image_url, osp.join(savepath, name))
                if b < 48:
                    shutil.move(image_url, osp.join(savepath, name))
            elif not osp.getsize(image_url):
                os.remove(image_url)

def plot_brightness(b_list, filename):
    if not os.path.exists("./result/{}".format(filename)):
        os.makedirs("./result/{}".format(filename))
    Efiebright_valld = np.array(b_list)
    plt.hist(Efiebright_valld, range=(0, 250), bins=10, density=1, facecolor='blue', alpha=0.5)
    plt.savefig("./result/{0}/{1}_bright.png".format(filename, filename))
    plt.close("all")    

def start_bright(path, realpath):
    b_list = []
    filename = os.path.basename(path)
    brightness_avg(path, b_list, realpath)
    os.chdir(realpath)
    plot_brightness(b_list, filename)

def cal_canny(imgpath, realpath):
    filename = os.path.basename(imgpath)
    os.chdir(os.path.dirname(os.getcwd()))
    savepath = osp.join(realpath, "img_canny", filename)
    savepath_gau = osp.join(realpath, "img_Gau", filename)
    if not osp.exists(savepath):
        # shutil.rmtree(savepath)
        os.makedirs(savepath)
    if not osp.exists(savepath_gau):
        # shutil.rmtree(savepath_gau)
        os.makedirs(savepath_gau)
    files = glob.glob(imgpath+"/*.jpg")
    files.sort()
    total_num = len(files)
    count     = 0
    print("Total images {}".format(total_num))
    for file in files:
        # print(file)
        img = cv2.imread(file, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgG = cv2.GaussianBlur(gray, (5,5), 0)
        dst = cv2.Canny(imgG, 50, 50)
        n = 0
        for a in dst:
            for b in a:
                if b == 255: n += 1
        basename = osp.basename(file)
        name = osp.basename(file).split(".")[0] + "_%d"%n + ".jpg"
        cv2.imwrite(osp.join(savepath_gau, name), dst)
        if n < 2500:
            print("   canny bad")
            shutil.move(file, osp.join(savepath, name))
        count += 1
        if count % 100 == 0:
            print("Remaining {} images!".format(total_num - count))

def main():
    imgpath = sys.argv[1]
    realpath = osp.join(os.getcwd(), "data")
    # imgpath = osp.join(realpath, "imgorg")
    print("now calculate bright!")
    start_bright(imgpath, realpath)
    print("calculate end, next filter low quality images, this step will take some times!")
    cal_canny(imgpath, realpath)


if __name__ == "__main__":
    main()
