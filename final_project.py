import os
import sys
import numpy as np 
from PyQt5 import QtCore, QtGui, QtWidgets
import main_intro
from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from time import sleep
import time,board,busio
import adafruit_mlx90640_new



class MatplotlibWindow(QtWidgets.QMainWindow, main_intro.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MatplotlibWindow, self).__init__(parent)
        self.setupUi(self)

        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
        self.mlx = adafruit_mlx90640_new.MLX90640(i2c) # begin MLX90640 with I2C comm
        refresh_rate='1'
        exec(f"self.mlx.refresh_rate = adafruit_mlx90640_new.RefreshRate.REFRESH_{str(refresh_rate)}_HZ") # set refresh rate
        
        self.fig=Figure()
        self.ax=self.fig.add_subplot(111,frame_on=False)
        self.canvas=FigureCanvas(self.fig)
        l=QVBoxLayout(self.matplotlib_widget)
        l.addWidget(self.canvas)
        self.mlx_shape = (24,32)
        self.line1=self.ax.imshow(np.zeros(self.mlx_shape),vmin=0,vmax=60)
        self.cbar = self.fig.colorbar(self.line1) # setup colorbar for temps
        self.cbar.set_label('Temperature [$^{\circ}$C]',fontsize=14) # colorbar label


        self.fig2=Figure()
        self.ax2=self.fig2.add_subplot(111,frame_on=False)
        self.canvas2=FigureCanvas(self.fig2)
        l2=QVBoxLayout(self.matplotlib_widget_2)
        l2.addWidget(self.canvas2)
        self.mlx_shape = (24,32)
        self.line2=self.ax2.imshow(np.zeros(self.mlx_shape),vmin=0,vmax=60)
        self.cbar2 = self.fig2.colorbar(self.line2) # setup colorbar for temps
        self.cbar2.set_label('Temperature [$^{\circ}$C]',fontsize=14) # colorbar label

        self.calibrationcalibration_button_clicked=1
        self.calibrationcalibration_button.clicked.connect(self.readycalibration)
        self.importcalibration_button.clicked.connect(self.readycalibration2)
        self.frame = np.zeros((24*32,))
        self.frame2 = np.zeros((24*32,))
        self.gainofset=[]


        self.testtest_button.clicked.connect(self.readytest)
        self.tabWidget.currentChanged.connect(lambda:self.reset())
        self.matplotlib_widget.hide()
        self.matplotlib_widget_2.hide()


    def update_plot(self,frame):
        try:
            self.mlx.getFrame(frame) 
            print(frame[0])
        except:
            print('cant')
        data_array = (np.reshape(frame,self.mlx_shape)) # reshape to 24x32
        self.line1.set_data(np.fliplr(data_array)) # flip left to right
        self.fig.canvas.draw()
        self.line1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array)) # set bounds
        self.cbar.update_normal(self.line1) # update colorbar range

    def update_plot2(self,frame):
        try:
            self.mlx.getFrame(frame) 
            print(frame[0])
        except:
            print('cant')
        data_array2 = (np.reshape(frame,self.mlx_shape)) # reshape to 24x32
        self.line2.set_data(np.fliplr(data_array2)) # flip left to right
        self.fig2.canvas.draw()
        self.line2.set_clim(vmin=np.min(data_array2),vmax=np.max(data_array2)) # set bounds
        self.cbar2.update_normal(self.line2) # update colorbar range


    def readycalibration(self):
        self.calibrationcalibration_button_clicked+=1
        if(self.calibrationcalibration_button_clicked==2):
            self.realT1=float(self.blackbodytemperator_spin.value())
            self.calibration(self.calibrationcalibration_button_clicked)
            self.blackbodytemperator_spin.setProperty("value", 35)
            self.blackbodytemperator_label.setText("second Black Body Temperature")
            self.blackbodytemperator_spin.show()
            self.blackbodytemperator_label.show()
        elif(self.calibrationcalibration_button_clicked==3):
            self.realT2=float(self.blackbodytemperator_spin.value())
            self.blackbodytemperator_spin.setProperty("value", 35)
            self.blackbodytemperator_label.setText("first Black Body Temperature")
            self.calibration(self.calibrationcalibration_button_clicked)

    def readycalibration2(self):
        self.calibrationcalibration_button_clicked=2
        self.meanimage=np.zeros((24*32,))
        self.blackbodytemperator_spin.setProperty("value", 35)
        self.blackbodytemperator_label.setText("second Black Body Temperature")
        self.blackbodytemperator_spin.show()
        self.blackbodytemperator_label.show()
        self.importcalibration_button.hide()
        with open('import.csv','r') as f:
            self.realT1=float(f.readline())
            for k in range(24):
                x=f.readline()
                for i in range(32):
                    self.meanimage[k*32+i]=float(x.split(',')[i])
        print(self.meanimage)
        self.gainofset.append(self.meanimage)


    def fin2(self):
        sleep(1)
        self.line2.set_clim(vmin=np.min(self.data_array2),vmax=np.max(self.data_array2)) # set bounds
        self.line2.set_data(np.fliplr(self.data_array2)) # flip left to right
        self.fig2.canvas.draw()
        self.cbar2.update_normal(self.line2) # update colorbar range


    def fin(self):
        self.gain=np.zeros((24*32,))
        self.offset=np.zeros((24*32,))
        print(np.shape(self.gain))
        print(np.shape(self.gainofset))
        print(np.shape(self.offset))
        for j in range(24*32):
            self.gain[j]=(self.gainofset[1][j]-self.gainofset[0][j])/(self.realT2-self.realT1)
            self.offset[j]=(self.realT1-((self.gainofset[1][j]-self.gainofset[0][j])/(self.realT2-self.realT1)*self.gainofset[0][j]))
        
        with open("file.csv",'w') as f:
            data1 = (np.reshape(self.gainofset[0],self.mlx_shape))
            f.write("pic1\n")
            for i in range(np.shape(data1)[0]):
                for j in range(np.shape(data1)[1]):
                    f.write(str(data1[i][j]))
                    f.write(",")
                f.write("\n")
            f.write("\n")
            f.write("\n")
            f.write("pic2\n")
            data1 = (np.reshape(self.gainofset[1],self.mlx_shape)) 
            for i in range(np.shape(data1)[0]):
                for j in range(np.shape(data1)[1]):
                    f.write(str(data1[i][j]))
                    f.write(",")
                f.write("\n")
            f.write("\n")
            f.write("\n")
            data1 = (np.reshape(self.gain,self.mlx_shape)) 
            f.write("gain\n")
            for i in range(np.shape(data1)[0]):
                for j in range(np.shape(data1)[1]):
                    f.write(str(data1[i][j]))
                    f.write(",")
                f.write("\n")
            f.write("\n")
            f.write("\n")
            data1 = (np.reshape(self.offset,self.mlx_shape)) 
            f.write("offset\n")
            for i in range(np.shape(data1)[0]):
                for j in range(np.shape(data1)[1]):
                    f.write(str(data1[i][j]))
                    f.write(",")
                f.write("\n")
            f.write("\n")
            f.write("\n")

    def readytest(self):
        with open("file.csv" , 'r') as f:
            inn=f.read()
        offsetstr=inn.split('offset')[1]
        self.offset=np.zeros((24,32))
        for i in range(24):
            for j in range(32):
                self.offset[i][j]=float(offsetstr.split('\n')[i+1].split(',')[j])
        gainstr=inn.split('gain')[1]
        self.gain=np.zeros((24,32))
        for i in range(24):
            for j in range(32):
                self.gain[i][j]=float(gainstr.split('\n')[i+1].split(',')[j])
        self.test()

    def test(self):
        self.framestest_spin.hide()
        self.framestest_label.hide()
        self.testtest_button.hide()

        self.meanimage2=np.zeros((24*32,))
        self.images2=[]
        self.mlx.getFrame(self.frame2) # read MLX temperatures into frame var
        print(self.frame2[0])
        self.images2.append(self.frame2)
        data_array2 = (np.reshape(self.frame2,self.mlx_shape)) # reshape to 24x32
        self.line2.set_data(np.fliplr(data_array2)) # flip left to right
        self.fig2.canvas.draw()
        self.line2.set_clim(vmin=np.min(data_array2),vmax=np.max(data_array2)) # set bounds
        self.cbar2.update_normal(self.line2) # update colorbar range
        self.matplotlib_widget_2.show()
        self.thread2=PlotThread2(self)
        self.thread2.update_trriger2.connect(self.update_plot2)
        self.thread2.start()

                

    def calibration(self,n):
        self.meanimage=np.zeros((24*32,))
        self.images=[]
        self.mlx.getFrame(self.frame) # read MLX temperatures into frame var
        print(self.frame[0])
        self.images.append(self.frame)
        data_array = (np.reshape(self.frame,self.mlx_shape)) # reshape to 24x32
        self.line1.set_data(np.fliplr(data_array)) # flip left to right
        self.fig.canvas.draw()
        self.line1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array)) # set bounds
        self.cbar.update_normal(self.line1) # update colorbar range
        self.matplotlib_widget.show()
        self.framescalibration_spin.hide()
        self.blackbodytemperator_spin.hide()
        self.framescalibration_label.hide()
        self.blackbodytemperator_label.hide()
        self.thread=PlotThread(self,n)
        self.thread.update_trriger.connect(self.update_plot)
        self.thread.start()

    
    def reset(self):
        self.gainofset=[]
        self.framescalibration_spin.show()
        self.blackbodytemperator_spin.show()
        self.importcalibration_button.show()
        self.framescalibration_label.show()
        self.blackbodytemperator_label.show()
        self.calibrationcalibration_button.show()
        self.framestest_spin.show()
        self.framestest_label.show()
        self.testtest_button.show()
        self.matplotlib_widget.hide()
        self.matplotlib_widget_2.hide()



class PlotThread(QtCore.QThread):
    update_trriger=QtCore.pyqtSignal(np.ndarray)
    def __init__(self,window,n):
        self.window=window
        self.n=n
        QtCore.QThread.__init__(self,parent=window)


    def run(self):
        sleep(1)
        num_of_image=self.window.framescalibration_spin.value()
        for n in range(num_of_image-1):
            try:
                self.window.mlx.getFrame(self.window.frame) # read MLX temperatures into frame var
                self.update_trriger.emit(self.window.frame)
                self.window.images.append(self.window.frame)
                sleep(1)
            except:
                print('cant')
        sleep(1)
        for j in range(24*32):
            for i in range(len(self.window.images)):
                self.window.meanimage[j]+=self.window.images[i][j]
            self.window.meanimage[j]/=num_of_image

        with open('import.csv','w') as f:
            if(self.window.calibrationcalibration_button_clicked==2):
                f.write(str(self.window.realT1)+'\n')
            if(self.window.calibrationcalibration_button_clicked==3):
                f.write(str(self.window.realT2)+'\n')
            for i in range(24*32):
                f.write(str(self.window.meanimage[i])+',')
                if i%32==31:
                    f.write("\n")

        self.window.gainofset.append(self.window.meanimage)
        data_array = (np.reshape(self.window.meanimage,self.window.mlx_shape)) # reshape to 24x32
        self.window.line1.set_data(np.fliplr(data_array)) # flip left to right
        self.window.fig.canvas.draw()
        self.window.line1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array)) # set bounds
        self.window.cbar.update_normal(self.window.line1) # update colorbar range
        with open('valuescalibration.txt','w') as f:
            for i in range(len(self.window.images)):
                f.write(':'+str(self.window.images[i])+'\n')
            f.write(str(self.window.meanimage)+'\n')
        print(self.n)
        if(self.n==3):
            # try:

            print(self.window.gainofset[1])
            sleep(1)
            self.window.fin()
            # except:
            #     print("cccc")
            #     pass


class PlotThread2(QtCore.QThread):
    update_trriger2=QtCore.pyqtSignal(np.ndarray)
    def __init__(self,window):
        self.window=window
        QtCore.QThread.__init__(self,parent=window)


    def run(self):
        sleep(1)
        num_of_image=self.window.framestest_spin.value()
        for n in range(num_of_image-1):
            try:
                self.window.mlx.getFrame(self.window.frame2) # read MLX temperatures into frame var
                self.update_trriger2.emit(self.window.frame2)
                self.window.images2.append(self.window.frame2)
                sleep(1)
            except:
                print('cant')
        sleep(1)
        for j in range(24*32):
            for i in range(len(self.window.images2)):
                self.window.meanimage2[j]+=self.window.images2[i][j]
            self.window.meanimage2[j]/=num_of_image

        self.window.data_array2 = (np.reshape(self.window.meanimage2,self.window.mlx_shape)) # reshape to 24x32
        sleep(1)
        for i in range(24):
            for j in range(32):
                self.window.data_array2[i][j]=self.window.gain[i][j]*self.window.data_array2[i][j]+self.window.offset[i][j]
                if i==23 and j==31:
                    self.window.fin2()
                    
                    with open("mean.csv",'w') as f:
                        f.write(str(self.window.meanimage2))
                    print(self.window.meanimage2)
                    print(sum(self.window.meanimage2)/(24*32))



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = MatplotlibWindow()
    form.show()
    app.exec_()