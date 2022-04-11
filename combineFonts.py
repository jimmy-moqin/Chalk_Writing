# -*- coding: utf-8 -*-
# @Author: moqin
# @Date:   2022-04-05 16:35:25
# @Last Modified by:   moqin
# @Last Modified time: 2022-04-05 18:01:08
import cv2
import os
import numpy as np
import random

filePaths = []

for dirs,path,files in os.walk("../fonts/gkn"):
	for f in files:
		filepath = ("/".join([dirs,f]))
		filePaths.append(filepath)


sublist = np.array(random.sample(filePaths,24))
IMGmap = sublist.reshape(4,6)

image = np.zeros((513*4,547*6, 4), np.uint8)
H=0
for r in range(4):
	W = 0;
	for a in range(6):
		img = cv2.imread(IMGmap[r][a],cv2.IMREAD_UNCHANGED)
		h,w,c = img.shape
		image[H:H+h,W:W+w] = img
		W += w
	H += 513
cv2.imwrite(str(i)+".png",image)	

		


