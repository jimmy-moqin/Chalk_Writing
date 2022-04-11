# -*- coding: utf-8 -*-
# @Author: moqin
# @Date:   2022-04-09 13:19:05
# @Last Modified by:   moqin
# @Last Modified time: 2022-04-09 14:38:19
import cv2
import numpy as np
img = cv2.imread("./combine/01.png",-1)
mask = cv2.imread("./masks/dots.png",-1)
print(mask)
alpha = np.where(img[:,:,3]==0)
mask[alpha] = [0,0,0,0]
newimg = img + mask 
# img = 255 * np.ones(480*640*4,dtype=np.uint8).reshape((480,640,4))

# vis2 = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

cv2.imshow("text",newimg)
cv2.waitKey(0)
cv2.destroyAllWindows()