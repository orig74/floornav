# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 11:13:00 2015

@author: ori
"""

import grabber
import numpy as np

sim=True
    
if sim:
    dim=(3,3)
    grab=grabber.NetGrabber
    use_local_find_chess_board=True
    cameramtx=\
        np.array([
            [   2         ,     0.        ,     0 ],
            [   0.        ,     2         ,     0 ],
            [   0.        ,     0.        ,     1.        ]])

    
else:
    dim=(7,6)
    grab=grabber.WebGrabber
    use_local_find_chess_board=False
    
    camera='tablet'
    
    if camera=='tablet':
       fx=fy=2.0*630/480.0 #maybe we need to multiply by 2 since the image normalized to [-1,1]
       cameramtx=np.array(\
                [[   fx,  0 ,  0],
                [  0  ,  fy ,  0],
                [  0,   0  , 1.]])

