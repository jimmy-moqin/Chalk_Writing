import cv2
import numpy as np

# class ChalkPic(object):
    
#     def chalkPicRead(self,img):
#         if isinstance(img,str):
#             self.img = cv2.imdecode(np.fromfile(img,dtype=np.uint8),-1)

#         elif isinstance(img,np.ndarray):
#             self.img = img
#         else:
#             raise AttributeError("error!")
#         return self.img
    
#     def preview(self,img): 
#         shape = img.shape
#         self.resizeImg = cv2.resize(self.img,(0,0),fx=640/shape[1],fy=480/shape[0])
#         return self.resizeImg

def add_alpha_channel(img):
    """ 为jpg图像添加alpha通道 """
 
    b_channel, g_channel, r_channel = cv2.split(img) # 剥离jpg图像通道
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255 # 创建Alpha通道
 
    img_new = cv2.merge((b_channel, g_channel, r_channel, alpha_channel)) # 融合通道
    return img_new

# def merge_img(jpg_img, png_img, y1, y2, x1, x2):
#     """ 将png透明图像与jpg图像叠加 
#         y1,y2,x1,x2为叠加位置坐标值
#     """
    
#     # 判断jpg图像是否已经为4通道
#     if jpg_img.shape[2] == 3:
#         jpg_img = add_alpha_channel(jpg_img)
    
#     '''
#     当叠加图像时，可能因为叠加位置设置不当，导致png图像的边界超过背景jpg图像，而程序报错
#     这里设定一系列叠加位置的限制，可以满足png图像超出jpg图像范围时，依然可以正常叠加
#     '''
#     yy1 = 0
#     yy2 = png_img.shape[0]
#     xx1 = 0
#     xx2 = png_img.shape[1]
 
#     if x1 < 0:
#         xx1 = -x1
#         x1 = 0
#     if y1 < 0:
#         yy1 = - y1
#         y1 = 0
#     if x2 > jpg_img.shape[1]:
#         xx2 = png_img.shape[1] - (x2 - jpg_img.shape[1])
#         x2 = jpg_img.shape[1]
#     if y2 > jpg_img.shape[0]:
#         yy2 = png_img.shape[0] - (y2 - jpg_img.shape[0])
#         y2 = jpg_img.shape[0]
 
#     # 获取要覆盖图像的alpha值，将像素值除以255，使值保持在0-1之间
#     alpha_png = png_img[yy1:yy2,xx1:xx2,3] / 255.0
#     alpha_jpg = 1 - alpha_png
    
#     # 开始叠加
#     for c in range(0,3):
#         jpg_img[y1:y2, x1:x2, c] = ((alpha_jpg*jpg_img[y1:y2,x1:x2,c]) + (alpha_png*png_img[yy1:yy2,xx1:xx2,c]))
 
#     return jpg_img
     
        
        

layers = [(cv2.imread("./bg/IMG_20220405_105056.jpg",cv2.IMREAD_UNCHANGED),(0,0)),(cv2.imread("./blackboard/bb01.png",cv2.IMREAD_UNCHANGED),(0,0))]
layers.reverse()
layersCopy = layers.copy()
# print(layersCopy)

def rmerge(layers):
    
    layersCopy = layers.copy()
    layersCopy.reverse()

    layersNum = len(layersCopy)
    while layersNum>1:
        imgbelow = layersCopy[-2][0]
        imgabove = layersCopy[-1][0]

        if imgabove.shape[2] == 3 :
            imgabove = add_alpha_channel(imgabove)
        elif imgbelow.shape[2] == 3:
            imgbelow = add_alpha_channel(imgbelow)
        elif (imgabove.shape[2] == 3) and (imgbelow.shape[2] == 3):
            imgabove = add_alpha_channel(imgabove)
            imgbelow = add_alpha_channel(imgbelow)
        
        x1 = layersCopy[-2][1][0]
        y1 = layersCopy[-2][1][1]
        x2 = x1 + imgabove.shape[1]
        y2 = y1 + imgabove.shape[0]
        '''
        当叠加图像时，可能因为叠加位置设置不当，导致png图像的边界超过背景jpg图像，而程序报错
        这里设定一系列叠加位置的限制，可以满足png图像超出jpg图像范围时，依然可以正常叠加
        '''
        yy1 = 0
        yy2 = imgabove.shape[0]
        xx1 = 0
        xx2 = imgabove.shape[1]
     
        if x1 < 0:
            xx1 = -x1
            x1 = 0
        if y1 < 0:
            yy1 = - y1
            y1 = 0
        if x2 > imgbelow.shape[1]:
            xx2 = imgabove.shape[1] - (x2 - imgbelow.shape[1])
            x2 = imgbelow.shape[1]
        if y2 > imgbelow.shape[0]:
            yy2 = imgabove.shape[0] - (y2 - imgbelow.shape[0])
            y2 = imgbelow.shape[0]
     
        # 获取要覆盖图像的alpha值，将像素值除以255，使值保持在0-1之间
        alpha_imgabove = imgabove[yy1:yy2,xx1:xx2,3] / 255.0
        alpha_imgbelow = 1 - alpha_imgabove
        
        # 开始叠加
        for c in range(0,3):
            imgbelow[y1:y2, x1:x2, c] = ((alpha_imgbelow*imgbelow[y1:y2,x1:x2,c]) + (alpha_imgabove*imgabove[yy1:yy2,xx1:xx2,c]))
        
        layersCopy.pop()
        layersCopy[-1] = [imgbelow,[0,0]]
        layersNum = len(layersCopy)
    cv2.imshow("0",imgbelow)
    cv2.waitKey (0)  
    cv2.destroyAllWindows() 
def merge(layers):
    
    if len(layersCopy) >=2:
        imgbelow = layersCopy[-1][0]
        imgabove = layersCopy[-2][0]
        if imgabove.shape[2] == 3 :
            imgabove = add_alpha_channel(imgabove)
        elif imgbelow.shape[2] == 3:
            imgbelow = add_alpha_channel(imgbelow)
        elif (imgabove.shape[2] == 3) and (imgbelow.shape[2] == 3):
            imgabove = add_alpha_channel(imgabove)
            imgbelow = add_alpha_channel(imgbelow)
        
        x1 = layersCopy[-2][1][0]
        y1 = layersCopy[-2][1][1]
        x2 = x1 + imgabove.shape[1]
        y2 = y1 + imgabove.shape[0]
        '''
        当叠加图像时，可能因为叠加位置设置不当，导致png图像的边界超过背景jpg图像，而程序报错
        这里设定一系列叠加位置的限制，可以满足png图像超出jpg图像范围时，依然可以正常叠加
        '''
        yy1 = 0
        yy2 = imgabove.shape[0]
        xx1 = 0
        xx2 = imgabove.shape[1]
     
        if x1 < 0:
            xx1 = -x1
            x1 = 0
        if y1 < 0:
            yy1 = - y1
            y1 = 0
        if x2 > imgbelow.shape[1]:
            xx2 = imgabove.shape[1] - (x2 - imgbelow.shape[1])
            x2 = imgbelow.shape[1]
        if y2 > imgbelow.shape[0]:
            yy2 = imgabove.shape[0] - (y2 - imgbelow.shape[0])
            y2 = imgbelow.shape[0]
     
        # 获取要覆盖图像的alpha值，将像素值除以255，使值保持在0-1之间
        alpha_imgabove = imgabove[yy1:yy2,xx1:xx2,3] / 255.0
        alpha_imgbelow = 1 - alpha_imgabove
        
        # 开始叠加
        for c in range(0,3):
            imgbelow[y1:y2, x1:x2, c] = ((alpha_imgbelow*imgbelow[y1:y2,x1:x2,c]) + (alpha_imgabove*imgabove[yy1:yy2,xx1:xx2,c]))
        
        layersCopy.pop()
        layersCopy[-1] = (imgbelow,(0,0))
        
        merge(layers)
    else:
        imgbelow = layersCopy[0][0]
        cv2.imshow("0",imgbelow)
        cv2.waitKey (0)  
        cv2.destroyAllWindows() 
        
rmerge(layersCopy)



# pic2 = "./shadows/002.png"
# pic = "./combine/01.png"
# P=ChalkPic(pic2)

# img1 = ChalkPic(pic)
# img2 = ChalkPic(pic2)
# resizeImg1 = img1.preview()
# resizeImg2 = img2.preview()
# x1 = 0
# y1 = 0
# x2 = x1 + resizeImg1.shape[1]
# y2 = y1 + resizeImg2.shape[0]
# cres_img = P.merge_img(resizeImg1,resizeImg2, y1, y2, x1, x2)
# cv2.imshow("0",cres_img)
# cv2.waitKey (0)  
# cv2.destroyAllWindows() 