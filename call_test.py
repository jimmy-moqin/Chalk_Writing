from operator import invert
import cv2
import numpy as np
fonts = "./fonts/gkn/gkn_074.png"
def invercePic(self,img) 
    blankPic = np.zeros(img.shape,dtype = np.uint8)
    b,g,r,a = cv2.split(img)
    b = np.zeros(b.shape,dtype = np.uint8)
    g = np.zeros(g.shape,dtype = np.uint8)
    r = np.zeros(r.shape,dtype = np.uint8)
    alaphPic = cv2.merge((b,g,r,a))
    alaph_mask = np.where(img[:,:,3]!=0)
    blankPic[alaph_mask] = [255,255,255,0]
    resPic = blankPic+alaphPic
    resPic.reshape(img.shape)
