from PyQt5 import QtGui, QtCore, QtWidgets
from trackerUI import Ui_TrackerUI
from easyEBB import EasyEBB
from managers import CaptureManager
from finder import WormFinder
import time, datetime
import numpy as np
import cv2
import logging
import sys
import threading
from _functools import partial
import utils
import copy
import serial, os
import re

LOGGING_LEVELS = {'critical': logging.CRITICAL,
             'error': logging.ERROR,
             'warning': logging.WARNING,
             'info': logging.INFO,
             'debug': logging.DEBUG}

logger = logging.getLogger('')
logger.setLevel(logging.INFO)

class Gui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        logger.warning('starting up')
        self.startRecTime = None
        ## Instantiate classes
        self.ui = Ui_TrackerUI()
        self.ui.setupUi(self)
        self._cap  = None
        #What to display on screeeeeeen
        source = [0, 1, 2, 3, 'led_move1.avi', 'wormtest.avi',
                  'screencast.avi',
                  'screencast 1.avi',
                  'shortNoBox.avi',
                  'longNoBox.avi',
                  'H299.avi',
                  'testRec.avi',
                  'longDemo.avi',
                  'cinqodemayo.avi']
        
        for s in source:
            self.ui.srcCombo.addItem(str(s))
        self.ui.srcCombo.setCurrentText('0')
        self.showImage = False ## If True, video gets displayed (need _cap)

        ## Stuff you can change in the UI
        self.idealRes = [1280, 960]

        ## Video stuff
        self._timer = QtCore.QTimer( self )
        self._timer.timeout.connect( self.play )
        self._timer.start(27)
        self.update()

        ## Tracking parameters
        self._lastCheck = time.time()
        self._sampleFreq = 0.1
        self.motorsOn = False
        self.runTracking = False
        self.ebb = None 
        self._wormFinder = None  
        cv2.namedWindow('gaussian')


        ## Register button actions
        self.ui.buttonRight.clicked.connect( partial( self.motors, 'right' ) )
        self.ui.buttonLeft.clicked.connect( partial( self.motors, 'left' ) )
        self.ui.buttonUp.clicked.connect( partial( self.motors, 'up' ) )
        self.ui.buttonDown.clicked.connect( partial( self.motors, 'down' ) )
        self.ui.buttonRefresh.clicked.connect( self.getNewRef )
        self.ui.buttonRun.clicked.connect( self.run )
        self.ui.buttonConnect.clicked.connect( self.connectMotors )
        self.ui.buttonReset.clicked.connect (self.resetAll )

        self.ui.buttonMotorized.clicked.connect( self.motorized )

        self.ui.buttonRec.clicked.connect( self.record )

        self.ui.srcCombo.activated['QString'].connect( self.setSource )

        self.ui.scalingSlider.valueChanged[int].connect( self.setMultFactor )
        self.ui.scaling.setText( 'Step scaling is %d' % self.ui.scalingSlider.value() ) 
        self.multFactor = self.ui.scalingSlider.value()
        self.ui.studyName.editingFinished.connect( self.setFileName )

        ## Change button colors for pretty
 
        self.ui.buttonMotorized.setText("Turn On")
        self.ui.buttonRec.setText("Start")
        self.ui.fps.setText("")
        self.ui.lcdNumber.display("")
        ## Read in file from calibration GUI
        self.readInCalibration()

        ## Disable buttons
        self.setAble( 'motors', False ) 
        self.setAble( 'motorized', False ) 
        self.setAble( 'source', False ) 
        self.setAble( 'buttons', False ) 
        self.setAble( 'recording', False )

        

    def setAble( self, group, ability ): 
        groups = { 'connectMotors' : [ self.ui.buttonConnect ],
                   'motors' : [ self.ui.scaling, 
                                self.ui.buttonUp, 
                                self.ui.buttonDown, 
                                self.ui.buttonLeft,
                                self.ui.buttonRight ], 
                   'motorized' : [ self.ui.buttonMotorized, 
                                   self.ui.motorsDesc ], 
                   'study' : [ self.ui.studyDesc, 
                               self.ui.studyName ], 
                   'source': [ self.ui.srcDesc, 
                               self.ui.srcCombo ], 
                   'buttons': [ self.ui.buttonRun, 
                                self.ui.buttonConnect, 
                                self.ui.buttonRefresh ], 
                   'recording' : [ self.ui.recordingDesc, 
                                   self.ui.buttonRec ],
                   'reset' : [ self.ui.scaling, 
                               self.ui.buttonUp, 
                               self.ui.buttonDown, 
                               self.ui.buttonLeft,
                               self.ui.buttonRight,
                               self.ui.buttonMotorized, 
                               self.ui.motorsDesc,
                               self.ui.studyDesc, 
                               self.ui.studyName,
                               self.ui.buttonRun, 
                               self.ui.buttonConnect, 
                               self.ui.buttonRefresh,
                               self.ui.recordingDesc, 
                               self.ui.buttonRec ] 
               }
        for c in groups[group]:
            c.setEnabled(ability)

    def setFileName ( self ) :
        self.shareFileName = '%s/%s-%s' % ('output', self.ui.studyName.text(), time.strftime( "%a_%d_%b_%Y-%H%M%S" ) )
        self.setLogging('debug')
        self.setAble( 'study', False ) 
        self.setAble( 'buttons', True)
        self.ui.buttonRefresh.setEnabled(False) 

    def getNewRef( self ):
        if self._wormFinder:
            self._wormFinder.resetRef()


    def record( self ):
        if self._cap.isWritingVideo:
            self._cap.stopWritingVideo()
            self.ui.buttonRec.setStyleSheet('QPushButton {color:green}')
            self.ui.buttonRec.setText("Start")
            self.startRecTime = None
        else:
            self.startRecTime = time.time()
            self.shareFileName = '%s/%s-%s' % ('output', 
                                               self.ui.studyName.text(), 
                                               time.strftime( "%a_%d_%b_%Y-%H%M%S" ) )
            logger.debug('New sharefilename')

            platform = sys.platform.lower()
            if platform in ['win32', 'win64']:
                fourcc = cv2.VideoWriter_fourcc(*'IYUV')
                logger.warning( 'fourcc is IYUV')
            else:
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                logger.warning( 'fourcc is MJPG')
            if not self._cap.isWritingVideo:
                self._cap.startWritingVideo('%s.avi' % self.shareFileName, 
                                            fourcc)    
            self.ui.buttonRec.setStyleSheet('QPushButton {color:red}')
            self.ui.buttonRec.setText("Stop")

    def motorized( self ):
        if self.motorsOn:
            self.motorsOn = False
            logger.info('motors off')
            self.ui.buttonMotorized.setStyleSheet('QPushButton {color:green}')
            self.ui.buttonMotorized.setText("Turn On")
            self.setAble('motors', True) 
        else:
            self.motorsOn = True
            self._wormFinder.launch = 0
            logger.info('motors on')
            self.ui.buttonMotorized.setStyleSheet('QPushButton {color:red}')
            self.ui.buttonMotorized.setText("Turn Off")
            self.setAble('motors', False) 
    def run ( self ):
        logger.info("Start worm finder")

        if self._wormFinder:
            self._wormFinder = None

        if not self._cap:
            self.setSource(self.ui.sourceCombo.currentText())

        self.centerPt = utils.Point(self.actualRes[0] / 2, self.actualRes[1] / 2)
        self.cropSize = 100
        
        self.finderArgs = {
            'gsize' :  45,
            'gsig' : 9,
            'window' : 3,
            'method' : 'lazyc',
            'MAXONEFRAME': 500,
            'REFPING' : 1000,
            'MAXREF': 1000,
            'cropSize': self.cropSize,
            'centerPt': self.centerPt,
            'servos': self.ebb,
            'actualRes': self.actualRes,
            'motorsOn': self.motorsOn
            }


        self._wormFinder = WormFinder( **self.finderArgs )     

        self.runTracking = True
        self.startTrackTime = time.time()
        self.showImage = True
        self.ui.buttonRun.setEnabled(False)
        self.ui.buttonRefresh.setEnabled(True) 
        if self.ebb:
            self.setAble('motorized', True )
        self.setAble('recording', True ) 
    
    def connectMotors( self ):
        logger.info("Connect Motors")
        if self._cap:
            try:
                logger.debug('width mm %d' % self.widthMM)
                self.ebb = EasyEBB(resolution = self.actualRes, sizeMM = self.widthMM)
                self.setAble('motors', True)
                self.setAble('connectMotors', False)
                self._cap.resetFPSestimate()
                if self._wormFinder:
                    self._wormFinder.servos = self.ebb
                    self.setAble('motorized', True) 
            except serial.SerialException as e:
                logger.exception(str(e))
                QtWidgets.QMessageBox.information( self, "Motors Issue",
                                                  "Unable to connect to motors. Please connect or reboot motors. If problem persists, reboot computer")

    def setSource ( self, value ):
        self.existingVid = False

        if type(value) != int:
            nums = re.compile(r'\d*')
            mat = re.match(nums,value).group(0)
            
            if re.match(nums, value).group(0) is not u'':
                src = int(value)
            else:
                src = str(value)
                self.existingVid = True
        else: #read in from calibration
            src = value
            self.ui.sourceCombo.setCurrentText(str(src))
            
        if self._cap:
            if self._cap._capture.isOpened(): #ugly access to VideoCapture object from managers
                self._cap._capture.release()

        
        self._cap = CaptureManager( cv2.VideoCapture(src) )
        self.showImage = True
        
        self.actualRes = self._cap.getResolution()
        
        if self.actualRes != self.calibrationRes and not self.existingVid:
            self._cap.setProp( 'height', self.calibrationRes[1] )
            self._cap.setProp( 'width', self.calibrationRes[0] )
        
        self.showImage = True

        self.actualRes = self._cap.getResolution()
        logger.warning("Actual resolution from cam is %s" % str( self.actualRes ) )
        self.setAble('source', False) 
        self.setAble('buttons', True)
        self.ui.buttonRefresh.setEnabled(False)

    def setLogging( self, value ):
        addFile = True
        formatter = logging.Formatter( '%(asctime)s\t%(levelname)s\t%(name)s\t\t%(message)s' )
        file = logging.FileHandler( '%s.log' % self.shareFileName )
        logger.warning('New file')
        file.setLevel( LOGGING_LEVELS['debug'] )
        file.setFormatter( formatter )
        
        console = logging.StreamHandler()
        console.setLevel( LOGGING_LEVELS['debug'] )
        console.setFormatter( formatter )
        
        for h in logger.handlers:
            if type(h) == logging.StreamHandler:
                logger.removeHandler( h ) 
            elif type(h) == logging.FileHandler: #if file has started, leave it be!!!
                addFile = False

        if addFile:
            logger.addHandler( file )

        logger.addHandler( console )
        self.newFileFLAG = False

    def setMultFactor ( self, value ):
        self.multFactor = value
        self.ui.scaling.setText( 'Step scaling is %d' % value)
   
   
    def readInCalibration( self ):
        c = os.path.dirname(os.getcwd())
        cc = os.path.dirname(c)
        f = open( ("%s/config.txt" % cc) , "r")
        line = f.readline()
        f.close()        
        logger.warning('line: %s' % str(line)  )
        w, h, widthMM, source = line.split('|')
        self.widthMM = float(widthMM)
        self.calibrationRes = [int(w), int(h)]
        if source is not None:
            self.setSource( source )



    def motors( self, direction):
        if self.ebb:
            xdir = 1
            ydir = 1
            t = 100

            dir ={ 'left': (t, xdir * self.multFactor * (-1), 0 ) ,
                  'right': ( t, xdir * self.multFactor * (1), 0 ),
                  'up': (t, 0, ydir * self.multFactor * (1) ),
                  'down': (t, 0, ydir * self.multFactor * (-1) )
                  }

            #print dir[direction]
            th = threading.Thread(target  = self.ebb.move , args = dir[direction] )
            try:
                th.start()

            except Exception as e:
                logger.exception( str(e) )
    
    def resetAll ( self ):
        if self.ebb:
            self.ebb.closeSerial()
        if self._wormFinder:
            self._wormFinder = None
            self.runTracking = False
            cv2.destroyWindow('gaussian')
            
        if self._cap.isWritingVideo:
            self.record()
            self.ui.buttonRec.setStyleSheet('QPushButton {}')
#            self._cap.stopWritingVideo()

        if self._cap._capture.isOpened():
            self._cap._capture.release()

        self.showImage = False
        self.runTracking = False
        if self.motorsOn:
            self.motorized()
            self.motorsOn = False
            self.ui.buttonMotorized.setStyleSheet('QPushButton {}')
        self.ui.videoFrame.setText("Select source if video not displayed here on boot up")
        self.ui.fps.setText("")
        logger.info("Reset button pressed") 

        self.setAble('source', True)
        self.setAble('reset', False) 

    def closeEvent ( self, event):
        logger.debug("closing")
        if self.ebb:
            self.ebb.closeSerial()
        if self._cap.isWritingVideo:
            self._cap.stopWritingVideo()
        
        for h in logger.handlers:
            if type(h) == logging.FileHandler:
                h.close()
        
        try:
            cv2.destroyWindow('gaussian')
        except Exception as e:
            pass
            
    def isColor( self, imgIn ):
        
            try:
                ncolor = np.shape(imgIn)[2]
                boolt = int(ncolor) > 2
                return boolt
            except IndexError:
                if self.existingVid:
                    logger.warning('Video has ended')
                    self.existingVid = False
                    self.resetAll()
                else:
                    logger.warning('Issue with video input')
                    self.resetAll()
   
    def play( self ):
        
        if self.showImage:
            ## Get image from camera
            self._cap.enterFrame()
            self.currentFrame = self._cap.getFrame()
        
            self.color = self.isColor(self.currentFrame)

            t1 = time.time()

            if self.color:
                try:
                    self.currentFrame = cv2.cvtColor(self.currentFrame, cv2.COLOR_BGR2GRAY)
                except TypeError:
                    logger.exception("No Frame")
                finally:
                    self._cap.exitFrame()
            
            self._cap.exitFrame()
            
            if not self.runTracking: #no finder
                if self.showImage: #yes capture
                    self.ui.videoFrame.setPixmap(self._cap.convertFrame(self.currentFrame))
                    self.ui.videoFrame.setScaledContents(True)
            else: # yes finder
                ## Stop if too dark!!!
                if time.time() - self.startTrackTime < 5:
                    self.firstAvgPixIntensity = np.mean(self.currentFrame)
                    logger.debug('first avg int: %d' % self.firstAvgPixIntensity)
               ## Tracking procedure
                if time.time() - self._lastCheck >= self._sampleFreq:
                    gaussian = self._wormFinder.processFrame( self.currentFrame )
                    if gaussian is not None:
                        cv2.imshow( 'gaussian', gaussian )
                        
                    if self.motorsOn: #yes motorized
                        ## Stop motors if too dark
                        self.currentAvgPixIntensity = np.mean(self.currentFrame)
                        logger.debug('current avg int: %d' % self.currentAvgPixIntensity)
                        if self.currentAvgPixIntensity < self.firstAvgPixIntensity - 50:
                            logger.warning('Darkening of picture: motors turned off')
                            if self.motorsOn:
                                self.motorized()
                            if self._cap.isWritingVideo:
                                self.record()
                        else:
                          self._wormFinder.decideMove()
                    self._lastCheck = time.time()
                    self._wormFinder.drawDebugCropped( self.currentFrame)
                    
                    self.ui.videoFrame.setPixmap(self._cap.convertFrame(self.currentFrame))
                    self.ui.videoFrame.setScaledContents(True)

            if self._cap._fpsEstimate:
               self.ui.fps.setText( 'FPS: %0.2f' % ( self._cap._fpsEstimate ))

            if self.startRecTime:
                elapsedSec = time.time() - self.startRecTime
                elapsed = time.strftime("%H.%M.%S", time.gmtime(elapsedSec) ) 
                self.ui.lcdNumber.setNumDigits(8)
                self.ui.lcdNumber.display( elapsed )
            else:
                self.ui.lcdNumber.display("") 
        return
        
    '''
    def keyPressEvent( self, e ):
        #logger.debug('\tPressed\t%d' % e.key() )
        
        options = {
                   QtCore.Qt.Key_Escape : self.close(),
                   QtCore.Qt.Key_Left : self.motors( 'left' ),
                   QtCore.Qt.Key_Right : self.motors( 'right' ),
                   QtCore.Qt.Key_Up : self.motors( 'up' ),
                   QtCore.Qt.Key_Down : self.motors( 'down' ) 
               }
        #logging.debug( str(options[e.key()]) )
        options[e.key()]
        
        '''


def main():
    app = QtWidgets.QApplication( sys.argv )
    g = Gui()
    g.show()
    sys.exit( app.exec_() )

if __name__ == '__main__':
    main()
