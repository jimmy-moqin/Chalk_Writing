# -*- coding: utf-8 -*-
# @Author: moqin
# @Date:   2022-04-06 15:53:06
# @Last Modified by:   moqin
# @Last Modified time: 2022-04-06 19:52:07


from PyQt5.QtWidgets import *
from ui_ChalkWriting import Ui_MainWindow
from PyQt5.QtCore import pyqtSignal,Qt,QPointF
from PyQt5.QtGui import QImage, QPixmap

import sys,os
import cv2
import numpy as np
import random

# np.set_printoptions(threshold=np.inf)

class MainWindow(QMainWindow,Ui_MainWindow):
    #定义信号
	comboSignal = pyqtSignal() # 下拉选择信号
	slideSignal = pyqtSignal(int) # 滑动信号
	pushSignal = pyqtSignal(bool) # 按钮点击信号

	
	
	def __init__(self,parent=None):
		super(MainWindow, self).__init__(parent)
		self.setupUi(self)
		self.initUI()
		
	def initUI(self):
		
		self.previewBits = 480*640*4
		self.previewShape = (480,640,4) 
		self.fontsOffset = (195,281)

		# 指定素材储存位置
		bgPath = "./bg/"
		bgFormatFilter = ["jpg"]

		blackboardPath = "./blackboard/"
		blackboardFormatFilter = ["png"]

		dustsPath = "./dusts/"
		dustsFormatFilter = ["png"]

		fontsPath = "./fonts/"
		fontsFormatFilter = ["png"]

		shadowsPath = "./shadows/"
		shadowsFormatFilter = ["png"]
		
		# 遍历路径获取文件列表
		self.bgList = self.scanFolder(bgPath,bgFormatFilter)
		self.blackboardList = self.scanFolder(blackboardPath,blackboardFormatFilter)
		self.dustsList = self.scanFolder(dustsPath,dustsFormatFilter)
		self.fontsList = self.scanFolder(fontsPath,fontsFormatFilter)
		self.shadowsList = self.scanFolder(shadowsPath,fontsFormatFilter)

		#加载列表到ComboBox
		self.bgComboBox.addItems(self.bgList)
		self.bbComboBox.addItems(self.blackboardList)
		self.fontsComboBox.addItems(self.fontsList)
		self.shadowComboBox.addItems(self.shadowsList)
		self.dustsComboBox.addItems(self.dustsList)

		# 隐藏警告文字
		self.bgChsWarnLabel.hide()
		self.bbChsWarnLabel.hide()
		self.fontsChsWarnLabel.hide()
		# 设置标识
		self.isSetBg = 0
		self.isSetBb = 0
		self.isSetFonts = 0
		self.isSetMask = 0
		self.maskNum = 0

		# 设置效果器Silder的位置以及对应标签的值
		## 颗粒感
		self.particlesSlider.setValue(0)
		self.particlesNumLabel.setText(str(self.particlesSlider.value()))
		## 角度
		self.angleSlider.setValue(0)
		self.angleNumLabel.setText(str(self.angleSlider.value()))
		## 水平偏移量
		self.hOffsetSlider.setValue(0)
		self.hOffsetNumLabel.setText(str(self.hOffsetSlider.value()))
		self.hOffsetSliderValue = self.hOffsetSlider.value() # 读取初始偏移量
		## 垂直偏移量
		self.vOffsetSlider.setValue(0)
		self.vOffsetNumLabel.setText(str(self.vOffsetSlider.value()))
		self.vOffsetSliderValue = self.vOffsetSlider.value() # 读取初始偏移量
		## 不透明度
		self.opacitySlider.setValue(30)
		self.opacityNumLabel.setText(str(self.opacitySlider.value()))
		## 投影大小
		self.projectionSizeSlider.setValue(0)
		self.projectionSizeNumLabel.setText(str(self.projectionSizeSlider.value()))
		## 模糊程度
		self.fuzzyDegreeSlider.setValue(0)
		self.fuzzyDegreeNumLabel.setText(str(self.fuzzyDegreeSlider.value()))
		## 投影距离
		self.projectionDistanceSlider.setValue(0)
		self.projectionDistanceNumLabel.setText(str(self.projectionDistanceSlider.value()))
		## 投影角度
		self.projectionAngleSlider.setValue(0)
		self.projectionAngleNumLabel.setText(str(self.projectionAngleSlider.value()))

		# GraphicView 相关设置
		self.picViewScene = QGraphicsScene()  # 创建场景管理器
		self.picView.setScene(self.picViewScene) # 在视口中置入场景
		self.picView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # 关闭滚动条
		self.picView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		# 置灰不可用项
		self.flushUI()
		## 是否启用批处理
		self.label_25.setEnabled(0)
		self.runNumLineText.setEnabled(0)
		self.runNumLineText.setText("----")

		# 信号连接槽函数
		##基本素材控件信号
		self.bgComboBox.activated[str].connect(self.chooseBg)
		self.bbComboBox.activated[str].connect(self.chooseBlackboard)
		self.fontsComboBox.activated[str].connect(self.choosefonts)
		
		## 黑板偏移量控件信号
		self.angleSlider.valueChanged[int].connect(self.changeAngle)
		self.hOffsetSlider.valueChanged[int].connect(self.changeXOffset)
		self.vOffsetSlider.valueChanged[int].connect(self.changeYOffset)
		self.resizeSlider.valueChanged[int].connect(self.changeSize)

		##效果控制信号
		self.particlesSlider.valueChanged[int].connect(self.changeparticles)


	def flushUI(self):
		'''用于更新UI控件可用状态'''
		self.bgChsWarnLabel.show()
		self.bbComboBox.setEnabled(0)
		self.bbChsLabel.setEnabled(0)
		self.fontsChsLabel.setEnabled(0)
		self.fontsComboBox.setEnabled(0)
		self.OffsetGroupBox.setEnabled(0)
		self.EffectGroupBox.setEnabled(0)
		self.ShadowGroupBox.setEnabled(0)

		if self.isSetBg == 1:
			self.bgChsWarnLabel.hide()
			self.bbComboBox.setEnabled(1)
			self.bbChsLabel.setEnabled(1)
			if self.isSetBb == 1:
				self.bbChsWarnLabel.hide()
				self.fontsComboBox.setEnabled(1)
				self.fontsChsLabel.setEnabled(1)
				# 重新连接黑板偏移量控件信号
				self.angleSlider.valueChanged[int].connect(self.changeAngle)
				self.hOffsetSlider.valueChanged[int].connect(self.changeXOffset)
				self.vOffsetSlider.valueChanged[int].connect(self.changeYOffset)
				self.resizeSlider.valueChanged[int].connect(self.changeSize)
				if self.isSetFonts == 1:
					self.EffectGroupBox.setEnabled(1)
					self.ShadowGroupBox.setEnabled(1)
					self.OffsetGroupBox.setEnabled(1)
				else:
					self.EffectGroupBox.setEnabled(0)
					self.ShadowGroupBox.setEnabled(0)
					self.OffsetGroupBox.setEnabled(0)
					# 断开黑板偏移量控件信号
			else:
				self.bbChsWarnLabel.show()
				self.fontsComboBox.setEnabled(0)
				self.fontsChsLabel.setEnabled(0)
		else:
			self.bgChsWarnLabel.show()
			self.bbComboBox.setEnabled(0)
			self.bbChsLabel.setEnabled(0)


	def formatFilter(self, x, Formats):
		'''筛选符合格式要求的文件'''
		for end in Formats:
			if x.endswith(end):
				return x
			else:
				pass

	def scanFolder(self,path,Formats):
		'''扫描指定文件夹，并筛选出符合要求的文件路径'''
		resList = []
		for dirs, paths, files in os.walk(path):
			if len(paths) != 0:
				for p in paths:
					absPath = "".join([dirs,p])
					resList.append(absPath)
					return resList
			else:
				for f in files:
					absPath = "".join([dirs,f])
					resList.append(absPath)
		if all([os.path.isfile(i) for i in resList]):
			resList = filter(lambda x: self.formatFilter(x,Formats), resList)

		return list(resList)

	def chooseBg(self,bgPath):
		if not self.isSetBg: # 第一次
			if bgPath == "无":
				self.flushUI()
			else:
				self.bgPic = cv2.imread(bgPath,cv2.IMREAD_UNCHANGED)
				
				h,w,c = self.bgPic.shape
				self.wShapeRatio = self.previewShape[1]/w # 由背景确定预览缩放比例
				self.hShapeRatio = self.previewShape[0]/h # 由背景确定预览缩放比例
				
				self.previewBgPic = self.preview(self.bgPic)
				
				self.bgPicItem = QGraphicsPixmapItem()
				self.bgPicPix = self.transToPixmap(self.previewBgPic)
				self.bgPicItem.setPixmap(self.bgPicPix)
				self.bgPicItem.setFlags(QGraphicsItem.ItemIsSelectable)
				# 将图片加入Sence场景管理器
				self.bgPicItem.setZValue(0)
				self.picViewScene.addItem(self.bgPicItem)
				self.isSetBg = 1
				self.flushUI()
		else: # 非第一次
			if bgPath == "无":
				self.picViewScene.removeItem(self.bgPicItem)
				self.isSetBg = 0
				self.flushUI()
			else:
				# 先删除之前的背景
				self.picViewScene.removeItem(self.bgPicItem)
				
				self.bgPic = cv2.imread(bgPath,cv2.IMREAD_UNCHANGED)
				h,w,c = self.bgPic.shape
				self.wShapeRatio = self.previewShape[1]/w # 由背景确定预览缩放比例
				self.hShapeRatio = self.previewShape[0]/h # 由背景确定预览缩放比例
				
				self.previewBgPic = self.preview(self.bgPic)
				
				self.bgPicItem = QGraphicsPixmapItem()
				self.bgPicPix = self.transToPixmap(self.previewBgPic)
				self.bgPicItem.setPixmap(self.bgPicPix)
				self.bgPicItem.setFlags(QGraphicsItem.ItemIsSelectable)
				# 将图片加入Sence场景管理器
				self.bgPicItem.setZValue(0)
				self.picViewScene.addItem(self.bgPicItem)
				self.isSetBg = 1
				self.flushUI()
				
	
	def chooseBlackboard(self,bbPath):
		if not self.isSetBb: # 第一次
			if bbPath == "无":
				self.flushUI()
			else:
				self.bbPic = cv2.imread(bbPath,cv2.IMREAD_UNCHANGED)
				self.previewBbPic = self.preview(self.bbPic)
				self.previewBbPicShape = self.previewBbPic.shape
				self.bbPicItem = QGraphicsPixmapItem()
				self.bbPicPix = self.transToPixmap(self.previewBbPic)
				self.bbPicItem.setPixmap(self.bbPicPix)
				# 将图片加入Sence场景管理器
				self.bbPicItem.setZValue(1)
				self.picViewScene.addItem(self.bbPicItem)
				
				# 获取黑板初始坐标
				self.bbPicItemPos = [
					self.bbPicItem.boundingRect().x(),
					self.bbPicItem.boundingRect().y()
					]
				self.isSetBb = 1
				self.flushUI()
		else: # 非第一次
			if bbPath == "无": # 黑板置空
				self.picViewScene.removeItem(self.bbPicItem)
				# 如果有字体图层，则一并删除
				if self.isSetFonts: 
					self.picViewScene.removeItem(self.fontsPicItem)
				else:
					pass
				# 重置黑板偏移量滑块,要先断开信号连接
				self.angleSlider.valueChanged[int].disconnect(self.changeAngle)
				self.hOffsetSlider.valueChanged[int].disconnect(self.changeXOffset)
				self.vOffsetSlider.valueChanged[int].disconnect(self.changeYOffset)
				self.resizeSlider.valueChanged[int].disconnect(self.changeSize)
				
				self.angleSlider.setValue(0)
				self.resizeSlider.setValue(0)
				self.hOffsetSlider.setValue(0)
				self.vOffsetSlider.setValue(0)

				self.isSetBb = 0
				self.flushUI()
			else: # 黑板替换
				# 先删除之前的背景
				self.picViewScene.removeItem(self.bbPicItem)
				if self.isSetFonts: # 如果有字体图层，则一并删除
					self.picViewScene.removeItem(self.fontsPicItem)
				else:
					pass
				self.bbPic = cv2.imread(bbPath,cv2.IMREAD_UNCHANGED)
				self.previewBbPic = self.preview(self.bbPic)
				self.previewBbPicShape = self.previewBbPic.shape
				self.bbPicItem = QGraphicsPixmapItem()
				self.bbPicPix = self.transToPixmap(self.previewBbPic)
				self.bbPicItem.setPixmap(self.bbPicPix)
				# 将图片加入Sence场景管理器
				self.bbPicItem.setZValue(1)
				self.picViewScene.addItem(self.bbPicItem)
				
				# 获取黑板初始坐标
				self.bbPicItemPos = [
					self.bbPicItem.boundingRect().x(),
					self.bbPicItem.boundingRect().y()
					]

				self.isSetBb = 1
				self.flushUI()

	
	def choosefonts(self,fontsPath):
		if not self.isSetFonts:
			if fontsPath == "无":
				self.flushUI()
			else:
				fontsPicPathList = []
				for dirs, paths, files in os.walk(fontsPath):
					for f in files:
						fontsPicPathList.append("/".join([dirs,f]))
				self.fontsPic = self.combineFonts(fontsPicPathList)
				self.previewFontsPic = self.preview(self.fontsPic)
				self.previewFontsPicShape = self.previewFontsPic.shape
				self.fontsPicItem = QGraphicsPixmapItem()
				self.fontsPicPix = self.transToPixmap(self.previewFontsPic)
				self.fontsPicItem.setPixmap(self.fontsPicPix)
				# 将图片加入Sence场景管理器
				self.fontsPicItem.setZValue(2)
				self.picViewScene.addItem(self.fontsPicItem)
				
				self.fontsPos = self.fontsPicItem.mapToScene(
					QPointF(self.bbPicItemPos[0] + self.wShapeRatio*self.fontsOffset[1],
					self.bbPicItemPos[1] + self.hShapeRatio*self.fontsOffset[0]
					)
				)
				self.fontsPicItem.setPos(self.fontsPos) 
				# 如果进行了缩放
				size = self.resizeSlider.value()
				if size != 0:
					self.fontsPicItem.setScale((100+size)/100)
				else:
					pass
				# 如果进行了旋转
				angle = self.angleSlider.value()
				if angle != 0:
					self.fontsPicItem.setTransformOriginPoint(self.fontsCenterPos)
					self.fontsPicItem.setRotation(angle)
				else:
					pass

				self.isSetFonts = 1
				self.flushUI()
		else:
			if fontsPath == "无":
				self.picViewScene.removeItem(self.fontsPicItem)
				self.isSetFonts = 0
				self.flushUI()
			else:
				self.picViewScene.removeItem(self.fontsPicItem)
				
				fontsPicPathList = []
				for dirs, paths, files in os.walk(fontsPath):
					for f in files:
						fontsPicPathList.append("/".join([dirs,f]))
				self.fontsPic = self.combineFonts(fontsPicPathList)
				self.previewFontsPic = self.preview(self.fontsPic)
				self.previewFontsPicShape = self.previewFontsPic.shape
				self.fontsPicItem = QGraphicsPixmapItem()
				self.fontsPicPix = self.transToPixmap(self.previewFontsPic)
				self.fontsPicItem.setPixmap(self.fontsPicPix)
				# 将图片加入Sence场景管理器
				self.fontsPicItem.setZValue(2)
				self.picViewScene.addItem(self.fontsPicItem)
				self.fontsPos = self.fontsPicItem.mapToScene(
					QPointF(
						self.bbPicItemPos[0]+ self.wShapeRatio*self.fontsOffset[1],
						self.bbPicItemPos[1] + self.hShapeRatio*self.fontsOffset[0]
					)
				)
				self.fontsPicItem.setPos(self.fontsPos)
				# 如果进行了缩放
				size = self.resizeSlider.value()
				if size != 0:
					self.fontsPicItem.setScale((100+size)/100)
				else:
					pass
				# 如果进行了旋转
				angle = self.angleSlider.value()
				if angle != 0:
					self.fontsPicItem.setTransformOriginPoint(self.fontsCenterPos)
					self.fontsPicItem.setRotation(angle)
				else:
					pass

				self.isSetFonts = 1
				self.flushUI()


	def changeparticles(self,particles):
		if self.isSetMask == 0:
			if particles == 0:
				mask = np.zeros((3282*2052*4),dtype=np.uint8).reshape(2052,3282,4)
				self.maskPicPix = self.transToPixmap(mask)
				self.maskPicItem = QGraphicsPixmapItem()
				self.maskPicItem.setPixmap(self.maskPicPix)
				self.picViewScene.addItem(self.maskPicItem)

				self.fontsPos = self.fontsPicItem.mapToScene(
					QPointF(self.bbPicItemPos[0] + self.wShapeRatio*self.fontsOffset[1],
					self.bbPicItemPos[1] + self.hShapeRatio*self.fontsOffset[0]
					)
				)
				self.maskPicItem.setPos(self.fontsPos) 
				# 如果进行了缩放
				size = self.resizeSlider.value()
				if size != 0:
					self.maskPicItem.setScale((100+size)/100)
				else:
					pass
				# 如果进行了旋转
				angle = self.angleSlider.value()
				if angle != 0:
					self.maskPicItem.setTransformOriginPoint(self.fontsCenterPos)
					self.maskPicItem.setRotation(angle)
				else:
					pass

				self.maskPicItem.setZValue(3)
				self.isSetMask = 0
			else:
				maskFileName = "./masks/{:0>2}.png".format(str(particles//10))
				self.particlesNumLabel.setText(str(particles)+"%")
				mask = cv2.imread(maskFileName,cv2.IMREAD_UNCHANGED)
				alpha = np.where(self.previewFontsPic[:,:,3]==0)
				print(alpha)
				mask[alpha] = [0,0,0,0]
				self.maskPicPix = self.transToPixmap(mask)
				self.maskPicItem = QGraphicsPixmapItem()
				self.maskPicItem.setPixmap(self.maskPicPix)
				self.picViewScene.addItem(self.maskPicItem)
				
				self.fontsPos = self.fontsPicItem.mapToScene(
					QPointF(self.bbPicItemPos[0],
					self.bbPicItemPos[1]
					)
				)
				self.maskPicItem.setPos(self.fontsPos) 
				# 如果进行了缩放
				size = self.resizeSlider.value()
				if size != 0:
					self.maskPicItem.setScale((100+size)/100)
				else:
					pass
				# 如果进行了旋转
				angle = self.angleSlider.value()
				if angle != 0:
					self.maskPicItem.setTransformOriginPoint(self.fontsCenterPos)
					self.maskPicItem.setRotation(angle)
				else:
					pass

				self.maskPicItem.setZValue(3)
				self.isSetMask = 1	
		else:
			self.picViewScene.removeItem(self.maskPicItem)

			if particles == 0:
				mask = np.zeros((3282*2052*4),dtype=np.uint8).reshape(2052,3282,4)
				self.maskPicPix = self.transToPixmap(mask)
				self.maskPicItem = QGraphicsPixmapItem()
				self.maskPicItem.setPixmap(self.maskPicPix)
				self.picViewScene.addItem(self.maskPicItem)

				self.fontsPos = self.fontsPicItem.mapToScene(
					QPointF(self.bbPicItemPos[0] ,
					self.bbPicItemPos[1]
					)
				)
				self.maskPicItem.setPos(self.fontsPos) 
				# 如果进行了缩放
				size = self.resizeSlider.value()
				if size != 0:
					self.maskPicItem.setScale((100+size)/100)
				else:
					pass
				# 如果进行了旋转
				angle = self.angleSlider.value()
				if angle != 0:
					self.maskPicItem.setTransformOriginPoint(self.fontsCenterPos)
					self.maskPicItem.setRotation(angle)
				else:
					pass

				self.maskPicItem.setZValue(3)
				self.isSetMask = 0
			else:
				maskFileName = "./masks/{:0>2}.png".format(str(particles//10))
				self.particlesNumLabel.setText(str(particles)+"%")
				mask = cv2.imread(maskFileName,cv2.IMREAD_UNCHANGED)
				alpha = np.where(self.fontsPic[:,:,3]==0)
				mask[alpha] = [0,0,0,0]
				self.maskPicPix = self.transToPixmap(mask)
				self.maskPicItem = QGraphicsPixmapItem()
				self.maskPicItem.setPixmap(self.maskPicPix)
				self.picViewScene.addItem(self.maskPicItem)
				
				self.fontsPos = self.fontsPicItem.mapToScene(
					QPointF(self.bbPicItemPos[0] ,
					self.bbPicItemPos[1]
					)
				)
				self.maskPicItem.setPos(self.fontsPos) 
				# 如果进行了缩放
				size = self.resizeSlider.value()
				if size != 0:
					self.maskPicItem.setScale((100+size)/100)
				else:
					pass
				# 如果进行了旋转
				angle = self.angleSlider.value()
				if angle != 0:
					self.maskPicItem.setTransformOriginPoint(self.fontsCenterPos)
					self.maskPicItem.setRotation(angle)
				else:
					pass

				self.maskPicItem.setZValue(3)
				self.isSetMask = 1		


	def changeAngle(self,angle):
		self.angleNumLabel.setText(str(angle)+"°")
		# 获取黑板图元的几何中心
		self.bbCenterPos = self.bbPicItem.boundingRect().center()
		# 获取文字图元的几何中心
		self.fontsCenterPos = self.fontsPicItem.boundingRect().center()
		# 设置旋转中心
		self.bbPicItem.setTransformOriginPoint(self.bbCenterPos)
		self.fontsPicItem.setTransformOriginPoint(self.fontsCenterPos)
		self.bbPicItem.setRotation(angle)
		self.fontsPicItem.setRotation(angle)

	def changeXOffset(self,x_offset):
		self.hOffsetNumLabel.setText(str(x_offset)+"%")
		x_offset_new = x_offset - self.hOffsetSliderValue
		self.hOffsetSliderValue = x_offset
		ratio = 1 + (self.resizeSlider.value()/100)
		self.bbPicItem.moveBy(self.previewBbPicShape[1]*x_offset_new*ratio/100,0)
		self.bbPicItemPos[0] += self.previewBbPicShape[1]*x_offset_new*ratio/100
		self.fontsPicItem.moveBy(self.previewBbPicShape[1]*x_offset_new*ratio/100,0)
	
	def changeYOffset(self,y_offset):
		self.vOffsetNumLabel.setText(str(y_offset)+"%")
		y_offset_new =   y_offset - self.vOffsetSliderValue
		self.vOffsetSliderValue = y_offset
		ratio = 1 + (self.resizeSlider.value()/100)
		self.bbPicItem.moveBy(0,self.previewBbPicShape[0]*y_offset_new*ratio/100)
		self.bbPicItemPos[1] += self.previewBbPicShape[0]*y_offset_new*ratio/100
		self.fontsPicItem.moveBy(0,self.previewBbPicShape[0]*y_offset_new*ratio/100)
	
	def changeSize(self,size):
		self.resizeNumLabel.setText(str(size)+"%")
		self.bbPicItem.setScale((100+size)/100)
		self.fontsPicItem.setScale((100+size)/100)
				
	
	def combineFonts(self,fontsPicPathList):
		sublist = np.array(random.sample(fontsPicPathList,24))
		IMGmap = sublist.reshape(4,6)
		# 读取第一张字体的图片，意在获取其单字的尺寸
		fontPicOnePath = IMGmap[0][0]
		imgOne = cv2.imread(fontPicOnePath,cv2.IMREAD_UNCHANGED)
		fontShape = imgOne.shape
		
		# 建立空白图像容器
		combineImage = np.zeros((fontShape[0]*4,fontShape[1]*6, 4), np.uint8)
		H=0
		for r in range(4):
			W = 0;
			for a in range(6):
				img = cv2.imread(IMGmap[r][a],cv2.IMREAD_UNCHANGED)
				combineImage[H:H+fontShape[0],W:W+fontShape[1]] = img
				W += fontShape[1]
			H += fontShape[0]

		inverseImage = self.PNGinverse(combineImage)

		return inverseImage	
	
	def PNGinverse(self,img): 
		# 建立空白图片容器
		blankPic = np.zeros(img.shape,dtype = np.uint8)
		# 拆分原图的通道，保留alpha通道信息，其余通道置零
		b,g,r,a = cv2.split(img)
		b = np.zeros(b.shape,dtype = np.uint8)
		g = np.zeros(g.shape,dtype = np.uint8)
		r = np.zeros(r.shape,dtype = np.uint8)
		alphaPic = cv2.merge((b,g,r,a))
		# 提取原图中非透明区域的坐标
		alpha_mask = np.where(img[:,:,3]!=0)
		# 将原图非透明区域变为白色，alpha通道置零
		blankPic[alpha_mask] = [255,255,255,0]
		# 将反色后的图片加上之前的alpha通道信息
		resPic = blankPic+alphaPic
		# 将图片尺寸改回原图样式
		resPic.reshape(img.shape)
		
		return resPic


	def preview(self,img):

		imgShow = cv2.resize(img,(0,0),fx=self.previewShape[1]/3648,fy=self.previewShape[0]/2736)
		return imgShow

	def add_alpha_channel(self,img):
		""" 为jpg图像添加alpha通道 """
		if img.shape[2] == 3:
			b_channel, g_channel, r_channel = cv2.split(img) # 剥离jpg图像通道
			alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255 # 创建Alpha通道
		
			img_new = cv2.merge((b_channel, g_channel, r_channel, alpha_channel)) # 融合通道
			return img_new
		else:
			return img
	
	def rmerge(self,layers):

		layersCopy = layers.copy()
		layersCopy.reverse()
		layersNum = len(layersCopy)
		while layersNum>1:
			imgbelow = layersCopy[-1][0]
			imgabove = layersCopy[-2][0]

			if imgabove.shape[2] == 3 :
				imgabove = self.add_alpha_channel(imgabove)
			elif imgbelow.shape[2] == 3:
				imgbelow = self.add_alpha_channel(imgbelow)
			elif (imgabove.shape[2] == 3) and (imgbelow.shape[2] == 3):
				imgabove = self.add_alpha_channel(imgabove)
				imgbelow = self.add_alpha_channel(imgbelow)
			
			x1 = layersCopy[-2][1][0]
			y1 = layersCopy[-2][1][1]
			x2 = x1 + imgabove.shape[1]
			y2 = y1 + imgabove.shape[0]

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
			for c in range(0,4):
				imgbelow[y1:y2, x1:x2, c] = ((alpha_imgbelow*imgbelow[y1:y2,x1:x2,c]) + (alpha_imgabove*imgabove[yy1:yy2,xx1:xx2,c]))
			
			layersCopy.pop()
			layersCopy[-1] = [imgbelow,[0,0]]
			layersNum = len(layersCopy)
		
		return layersCopy[0][0]

	def merge(self,layersCopy):
		'''对layersCopy内的图层进行递归融合'''
		if len(layersCopy) >1:
			imgbelow = layersCopy[-1][0]
			imgabove = layersCopy[-2][0]
			if imgabove.shape[2] == 3 :
				imgabove = add_alpha_channel(imgabove)
			elif imgbelow.shape[2] == 3:
				imgbelow = add_alpha_channel(imgbelow)
			elif (imgabove.shape[2] == 3) and (imgbelow.shape[2] == 3):
				imgabove = add_alpha_channel(imgabove)
				imgbelow = add_alpha_channel(imgbelow)
			# 融合起始角标
			x1 = layersCopy[-2][1][0]
			y1 = layersCopy[-2][1][1]
			x2 = x1 + imgabove.shape[1]
			y2 = y1 + imgabove.shape[0]

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
			
			self.merge(layersCopy) # 递归调用
		
		else:
			imgbelow = layersCopy[0][0]
			del layersCopy
			return imgbelow
		
		return imgbelow #self.merge(layersCopy) # 递归函数返回的问题
	
	def transToPixmap(self,img):

		h,w,c = img.shape
		if c == 3:
			qimage = QImage(img.data, w, h, 3*w, QImage.Format_RGB888).rgbSwapped()
		elif c == 4:
			qimage = QImage(img.data, w, h, 4*w, QImage.Format_ARGB32)
		pix = QPixmap.fromImage(qimage)
		
		return pix
		
			

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())