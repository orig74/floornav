# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 07:38:16 2015

@author: root
"""
import cv2
import numpy as np
from scipy import ndimage

def myfindChessboardCorners(im,dim):
    gr=30
    patern=np.zeros((gr,gr),dtype='uint8')
    patern[:gr/2,:gr/2]=255
    patern[gr/2:,gr/2:]=255
    m1=cv2.matchTemplate(im,patern,cv2.TM_CCORR_NORMED)
    patern=np.ones((gr,gr),dtype='uint8')*255
    patern[:gr/2,:gr/2]=0
    patern[gr/2:,gr/2:]=0
    m2=cv2.matchTemplate(im,patern,cv2.TM_CCORR_NORMED)
    #m=np.bitwise_or(m1>0.9,m2>0.9)
    #import pdb;pdb.set_trace()
    tresh=0.95
    labels=ndimage.label(np.bitwise_or(m1>tresh,m2>tresh))
    if labels[1]!=dim[0]*dim[1]:
        return False,[]
    objs=ndimage.find_objects(labels[0])
    corners=[]
    for xx,yy in objs:
        xpos=(xx.start+xx.stop)/2.0#+gr/2-0.5
        ypos=(yy.start+yy.stop)/2.0#+gr/2-0.5
        se=5
        #import pdb;pdb.set_trace()
        minVal, maxVal, minLoc, maxLoc=cv2.minMaxLoc(m2[xpos-se:xpos+se,ypos-se:ypos+se])
        if maxVal<tresh:
            minVal, maxVal, minLoc, maxLoc=cv2.minMaxLoc(m1[xpos-se:xpos+se,ypos-se:ypos+se])
        xpos+=-se+maxLoc[0]+gr/2-0.5
        ypos+=-se+maxLoc[1]+gr/2-0.5
        
        #xpos=xx.start+gr/2
        #ypos=yy.start+gr/2
        corners.append((ypos,xpos) )
    return True,np.array(corners)

