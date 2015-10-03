# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 14:21:08 2015

@author: root
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 12:45:13 2015

@author: root
"""

import cv2
#from scipy import ndimage
import numpy as np
import time,zmq
import cPickle
import config

from utils import myfindChessboardCorners
currect=False

dim=config.dim
cap=config.grab()


if  currect:
    ret, mtx, dist, rvecs, tvecs=cPickle.load(open('calib2.pkl','rb'))
    img=cap.get()
    h,  w = img.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
    import pdb;pdb.set_trace()

#images = glob.glob('*.jpg')

def get_object_points():
    objp = np.zeros((dim[0]*dim[1],3), np.float32)
    objp[:,:2] = np.mgrid[0:dim[0],0:dim[1]].T.reshape(-1,2)
    return objp


port = config.posport
context = zmq.Context()
socket = context.socket(zmq.PUB)
#socket.connect("tcp://localhost:%s" % port)
socket.bind("tcp://*:%s" % port)

rvec, tvec = None,None


def print_corners(cor):
    for c in cor:
        print '%d,%d '%tuple(c),
    print
    
while 1:
    img=cap.get()
    if currect:
        img=cv2.undistort(img, mtx, dist, None, newcameramtx)
    #import pdb;pdb.set_trace()
    gray = cv2.cvtColor(img.astype('uint8'),cv2.COLOR_BGR2GRAY)
    #myfindChessboardCorners(gray)
    tic=time.time()
    if config.use_local_find_chess_board:
        ret, corners = myfindChessboardCorners(gray, dim)
    else:
        ret, corners = cv2.findChessboardCorners(gray, dim, None,cv2.CALIB_CB_SYMMETRIC_GRID)
    toc=time.time()
    if ret:
    
        #sort corners
        #mport pdb;pdb.set_trace()
        aaa=corners.reshape(-1,2).tolist()
        tr=max(abs(aaa[0][0]-aaa[1][0]),abs(aaa[0][1]-aaa[1][1]))*0.7
        def comp(a,b):
            #tr=max(abs(a[0]-b[0]),abs(a[1]-b[1]))/2
            if abs(a[1]-b[1])>tr:
                return 1 if  a[1]>b[1] else -1
            return 1 if a[0]>b[0] else -1
        
        #aaa.sort(key=lambda x:x[0]+10000*x[1])
        aaa.sort(cmp=comp )
        #print_corners(aaa)
        corners=np.array(aaa,dtype=np.float32).reshape((dim[0]*dim[1],1,2))
    
    
        cv2.drawChessboardCorners(img, dim, corners,ret)
        obj_points_norm=get_object_points()-(dim[0]//2,dim[1]//2,0)
        h,w=gray.shape
        Scale=np.mat([  1.0/h*2, 0, 0, #scale only by h  not w!!

                        0, 1.0/h*2, 0,#scale only by h !!

                        0, 0,    1]).reshape((3,3))
        ToCenter=np.mat([   1, 0, -w/2, 

                          0, 1, -h/2,

                          0, 0,    1]).reshape((3,3))
        center_corners=(Scale*ToCenter*np.mat( map(lambda x:x+[1],aaa)).T).T
        corners_for_solve=center_corners[:,:2].A.reshape((-1,1,2))
        newcameramtx=config.cameramtx
            
        retval, rvec, tvec = cv2.solvePnP(obj_points_norm, 
                                          corners_for_solve, newcameramtx, np.zeros((5,1)))
        #import pdb;pdb.set_trace()
        if retval:
            nav_data=(tvec[0,0],tvec[1,0],tvec[2,0],rvec[0,0],rvec[1,0],rvec[2,0])
            #print ('%.2f '*6)%(nav_data)
            R,J=cv2.Rodrigues((rvec[0,0],rvec[1,0],rvec[2,0]))
            #import pdb;pdb.set_trace()
            T=(-np.mat(R).I*np.mat([[tvec[0,0],tvec[1,0],tvec[2,0]]]).T).A1.tolist()
            #print '---',T,R
            if len(zmq.select([],[socket],[],0)[1])>0:
                #print '---,sending'
                tosend=(T[0],T[1],T[2],rvec[0,0],rvec[1,0],rvec[2,0])
                socket.send("%d %s"%((config.topic_posdata,cPickle.dumps(tosend))))
    cv2.imshow('img',img)
    k=cv2.waitKey(30)
    if k==27:
        break 
    elif k==65513  or k==ord('b'):
        import pdb;pdb.set_trace()
    else:
        if k!=-1:
            print 'key is',k
    #else:
    #print '---',toc-tic
print 'Done..'
cv2.destroyAllWindows()

