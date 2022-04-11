# -*- coding: utf-8 -*-
# @Author: moqin
# @Date:   2022-04-05 15:42:33
# @Last Modified by:   moqin
# @Last Modified time: 2022-04-09 10:15:57
import cv2
import os
import numpy as np
def white2transparent(img):
    height, width, channel = img.shape
    for h in range(height):
        for w in range(width):
            color = img[h, w]
            if (color == np.array([255, 255, 255, 255])).all():
                img[h, w] = [0, 0, 0, 0]
    return img


for dirs,path,files in os.walk("./fonts/xqy"):
	for f in files:
		filepath = ("/".join([dirs,f]))

		img = cv2.imread(filepath,-1)
		img1=cv2.resize(img,(547,513),interpolation=cv2.INTER_NEAREST)  #修改图片的尺寸
#参数1 原图片
#参数2 修改后的尺寸；300宽  400高；表示缩放后图像的大小。如果设置了这个参数，那么设置的（width，height）就代表将原图像缩放到指定的宽高；如果未设置这个参数(0,0)，那么原图像缩放之后的大小就要通过公式“dsize=（round（fx*原图像的宽），round（fy*原【的高））”来计算，fx和fy表示图像宽度方向和高度方向上的缩放比例
#fx：可选参数，表示图像宽度方向上的缩放比例，默认为0，表示自动按照“（double）dsize.width/原图像的宽度”来计算。
#fy：可选参数，表示图像高度方向上的缩放比例，默认为0，表示自动按照“（double）dsize.height/原图像的高度”来计算。
#interpolation  所用的插值方法
#INTER_NEAREST    最近邻插值;INTER_LINEAR 双线性插值（默认设置）;INTER_AREA 使用像素区域关系进行重采样;INTER_CUBIC 4x4像素邻域的双三次插值;INTER_LANCZOS4 8x8像素邻域的Lanczos插值
		cv2.imwrite(filepath,img1)


# cv2.waitKey(0)