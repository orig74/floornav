# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 13:00:19 2015

@author: root
"""
import urllib3,cv2,time,zmq
import numpy as np
context = zmq.Context()

class WebGrabber():
    def __init__(self,addr='10.0.0.2:8088/',fl='/shot.jpg'):
        self.conn=urllib3.connection_from_url(addr)
        self.file=fl
    def get(self):
        img_file=self.conn.urlopen('GET',self.file)
        open('/tmp/test.jpg','wb').write(img_file.data)
        aa=cv2.imread('/tmp/test.jpg')
        return aa
        

class NetGrabber():
    def __init__(self,imsize=(480,640)):
        port = "5557"
        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://localhost:%s" % port)
        self.imsize=imsize

    def get(self):
        ret=self.socket.recv()
        #import pdb;pdb.set_trace()
        gray=(np.frombuffer(ret,dtype='float32')*255).reshape(self.imsize).astype('uint8')
        return cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
        #return ret

class cv2Grabber():
    def __init__(self):
        self.cap=cv2.VideoCapture(0)
    
    def get(self):
        while 1:
            ret,img=self.cap.read()
            if ret:
                return img
            time.sleep(0.1)
        
if __name__ == '__main__':
    cap=WebGrabber()
    #cap=NetGrabber()
    #cap=cv2Grabber()
    while 1:
        img=cap.get()
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        cv2.imshow('img',gray)
        k=cv2.waitKey(10)
        if k==27:
            break
