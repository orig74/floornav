# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 08:31:22 2015

@author: root
"""

import cv2,zmq,cPickle
import numpy as np
import config
from numpy import cos,sin
def create_chess_board(dim=(4,4),slot_size=80):
    img=np.zeros((slot_size*dim[0],slot_size*dim[1]),dtype='float32')
    for i in range(dim[1]):
        for j in range(dim[0]):
            if (i%2==0 and j%2==0) or (i%2==1 and j%2==1):
                img[i*slot_size:(i+1)*slot_size,j*slot_size:(j+1)*slot_size]=1
    return img
#code from http://jepsonsblog.blogspot.co.il/2012/11/rotation-in-3d-using-opencvs.html
def rotate_img(img,alpha,beta,gamma,dx,dy,dz,f):
    alpha = (alpha - 0.)*np.pi/180.
    beta = (beta - 0.)*np.pi/180.
    gamma = (gamma - 0.)*np.pi/180.
    h,w=img.shape
    RX=np.mat([              
              1,          0,           0, 0,

              0, cos(alpha), -sin(alpha), 0,

              0, sin(alpha),  cos(alpha), 0,

              0,          0,           0, 1
    ]).reshape((4,4))
    
    RY=np.mat([
              cos(beta), 0, -sin(beta), 0,

              0, 1,          0, 0,

              sin(beta), 0,  cos(beta), 0,

              0, 0,          0, 1        
    ]).reshape((4,4))
    RZ=np.mat([
              cos(gamma), -sin(gamma), 0, 0,

              sin(gamma),  cos(gamma), 0, 0,

              0,          0,           1, 0,

              0,          0,           0, 1    
    ]).reshape((4,4))
    R = RX * RY * RZ
    T=np.mat([
             1, 0, 0, -dx,

             0, 1, 0, -dy,

             0, 0, 1, -dz,

             0, 0, 0, 1    
    ]).reshape((4,4))

    ############################
    
    
    tv=np.mat([
        [-1,-1,0,1],
        [-1,1,0,1],
        [1,1,0,1],
        [1,-1,0,1]]).T  
      
    A3=np.mat([
            f, 0 , -0,

            0, f ,  0,

            0, 0,   1
    ]).reshape((3,3))  


    pr=A3*(R*T*tv)[:3,:]
    #normalizing
    pr=pr/pr[2,:].A1
    tr,res=cv2.findHomography(tv[:2,:].T.A.astype('float32'),pr[:2,:].T.A.astype('float32'))
    
    Scale=np.mat([  1.0/h*2, 0, 0, #scale only by h  not w!!
    
                            0, 1.0/h*2, 0,#scale only by h !!
    
                            0, 0,    1]).reshape((3,3))    
    
    Center=np.mat([1.0, 0, -w/2.0,

              0, 1.0, -h/2.0,

              0, 0,    1]).reshape((3,3))
    #np.set_printoptions(precision=4)
    #return cv2.warpPerspective(img,trans[:3,:3],img.shape[::-1],borderValue=0.5)
    return R[:3,:3],cv2.warpPerspective(img,Center.I*Scale.I*np.mat(tr)*Scale*Center,img.shape[::-1],borderValue=0.1)
    #return cv2.warpPerspective(img,np.eye(3),img.shape[::-1],borderValue=0.5)

    
if __name__=='__main__':

    port = "5557"
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)

    pubsocket = context.socket(zmq.PUB)
    pubsocket.bind("tcp://*:%s" % config.sim_posport)



    chess_img=create_chess_board()
    h,w=480,640
    cw,ch=chess_img.shape
    img=np.ones((h,w),dtype=chess_img.dtype)*0.1
    #img[w/2-cw/2:w/2+cw/2,h/2-ch/2:h/2+ch/2]=chess_img
    img[h/2-ch/2:h/2+ch/2,w/2-cw/2:w/2+cw/2]=chess_img

    pitch=0
    roll=0
    yaw=0
    xx,yy, zz =0,0,-1.4
    ff=2
    while 1:
        R,cam_img=rotate_img(img,pitch,roll,yaw, xx,yy, zz,ff)
        rvec,J=cv2.Rodrigues(R)
        #import pdb;pdb.set_trace()
        if len(zmq.select([],[pubsocket],[],0)[1])>0:
                #print '---,sending'
            rvec=rvec.flatten()
            tosend=(xx,yy,zz,rvec[0],rvec[1],rvec[2])
          #  print tosend
            pubsocket.send("%d %s"%((config.topic_simposdata,cPickle.dumps(tosend))))

        #cam_img=img
        cv2.circle(cam_img,(img.shape[1]/2,img.shape[0]/2),3,(0.3,0,0))
        #import pdb;pdb.set_trace()
        cv2.imshow('tets',cam_img)
        if len(zmq.select([],[socket],[],0)[1])>0:
            socket.send(cam_img)
        k=cv2.waitKey(0)
        if k==27:
            break
        if k==ord('q'): pitch+=1
        if k==ord('a'): pitch-=1
        if k==ord('w'): roll+=1
        if k==ord('s'): roll-=1
        if k==ord('e'): yaw+=1
        if k==ord('d'): yaw-=1
        if k==ord('r'): xx+=.1
        if k==ord('f'): xx-=.1
        if k==ord('t'): yy+=.1
        if k==ord('g'): yy-=.1
        if k==ord('y'): zz+=0.1
        if k==ord('h'): zz-=0.1
        #print '>>>',pitch,roll,yaw, xx,yy, zz
            
        