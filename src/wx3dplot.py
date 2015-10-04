import os
import pprint
import random
import sys
import wx,zmq,cPickle
import cv2

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
import cv2
import config

class GraphFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'black L -> estimated camera, magenta L -> sim camera'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        
        self.data = []
        self.sim_data = []
        self.paused = False
        
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()
        
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        self.redraw_timer.Start(10)
        
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect ("tcp://localhost:%s" % config.posport)
        self.socket.connect ("tcp://localhost:%s" % config.sim_posport)
        self.socket.setsockopt(zmq.SUBSCRIBE, str(config.topic_posdata))
        self.socket.setsockopt(zmq.SUBSCRIBE, str(config.topic_simposdata))

        #self.socket.bind("tcp://*:%s" % port)
        self.PrevT=np.array([0,0,0])
        self.cumT=np.array([0,0,0])

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
                
        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)
        self.dpi = 100
        self.fig_xyz = Figure((6.0, 3.0), dpi=self.dpi)
        self.canvas_xyz = FigCanvas(self.panel, -1, self.fig_xyz)
        self.init_plot()
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.canvas_xyz, 1, flag=wx.LEFT | wx.TOP | wx.GROW)                
        self.panel.SetSizer(self.hbox)
        self.hbox.Fit(self)
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.axes_xyz = Axes3D(self.fig_xyz)
        #self.plot_data_xyz = self.axes_xyz.plot3D(
        #    [0],[0],[0], 
        #    linewidth=1,
        #    color=(1, 1, 0),
        #    )[0]


    def drawL(self,data,p1_color,p2_color,line_color=(0,0,0)):
        adata=np.array(data)
        base_pos=adata[:3]
        R,J=cv2.Rodrigues(data[3:])
        poses=R+base_pos
        self.axes_xyz.scatter(
                    poses[0,0],poses[0,1],poses[0,2], 
                    color=p1_color,
                    )
        self.axes_xyz.scatter(
                    poses[1,0],poses[1,1],poses[1,2], 
                    color=p2_color,
                    )

        xs,ys,zs=zip(poses[0,:],base_pos,poses[1,:])                 
                    
        self.axes_xyz.plot3D(
                    xs,ys,zs, 
                    linewidth=1,
                    color=line_color)

    def draw_plot(self):
        self.axes_xyz.cla()

        if len(self.data)>0:
            adata=np.array(self.data)      
            self.drawL(adata[-1],p1_color=(1,0,0),p2_color=(0,1,0))
        if len(self.sim_data)>0:
            adata=np.array(self.sim_data)   
            self.drawL(adata[-1],p1_color=(1,0,0),p2_color=(0,1,0),line_color=(0,1,1))
                  
          
        self.axes_xyz.set_xbound(lower=-5, upper=5)
        self.axes_xyz.set_ybound(lower=-5, upper=5)
        self.axes_xyz.set_zbound(lower=-5, upper=5)#
        
        self.canvas_xyz.draw()
    
    
    def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        if len(zmq.select([self.socket],[],[],0)[0])>0:
            #print 'got'
            topic,msg = self.socket.recv().split(' ',1)
            data=cPickle.loads(msg)
            if int(topic)==config.topic_simposdata:
                self.sim_data.append(data)
                #print '-*-','sim'
            if int(topic)==config.topic_posdata:
                self.data.append(data)
                #print '-*-','notsim'
            #import pdb;pdb.set_trace()
            #tx,ty,tz,r0,r1,r2=data
            data_history_len=10
            if len(self.data)>data_history_len:
                self.data=self.data[-data_history_len:]
            if len(self.data)>data_history_len:
                self.sim_data=self.sim_data[-data_history_len:]
            self.draw_plot()
            
    
    def on_exit(self, event):
        self.Destroy()
    
if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()

