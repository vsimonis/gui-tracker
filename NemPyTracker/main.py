from PyQt5 import QtGui, QtCore, QtWidgets
from NemPyTracker import Ui_TrackerUI
#f#rom Capture import Capture
from easyEBB import EasyEBB
from managers import CaptureManager
from finder import WormFinder
import time
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

logger = logging.getLogger(__name__)

class Gui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        logger.warning('starting up')
        

        
        ## Instantiate classes
        self.ui = Ui_TrackerUI()
        self.ui.setupUi(self)
        self._cap  = None
        self.readInCalibration()

        ## Give options to comboBoxes
        for k,v in LOGGING_LEVELS.items():
            self.ui.loggingCombo.addItem(k,v)

        #What to display on screeeeeeen
        source = [0, 1, 2, 3, 'led_move1.avi', 
                  'screencast.avi',
                  'screencast 1.avi',
                  'shortNoBox.avi',
                  'longNoBox.avi',
                  'H299.avi',
                  'testRec.avi',
                  'longDemo.avi']
        
        for s in source:
            self.ui.sourceCombo.addItem(str(s))
        self.ui.sourceCombo.setCurrentText('0')

        method = ['lazy','lazyc','lazyd']

        for m in method:
            self.ui.methodCombo.addItem(str(m))
        self.ui.methodCombo.setCurrentText( 'lazyc' )
        
        for c in utils.colors.iterkeys():
            self.ui.coloringCombo.addItem( str(c) )
        self.ui.coloringCombo.setCurrentText( 'gray-1')

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

        #self.shareFileName = '%s-%s' % (self.ui.studyName.text(), time.strftime("%a_%d_%b_%Y-%H %M %S") )

        ## Register button actions
        self.ui.buttonRight.clicked.connect( partial( self.motors, 'right' ) )
        self.ui.buttonLeft.clicked.connect( partial( self.motors, 'left' ) )
        self.ui.buttonUp.clicked.connect( partial( self.motors, 'up' ) )
        self.ui.buttonDown.clicked.connect( partial( self.motors, 'down' ) )

        self.ui.buttonRun.clicked.connect( self.run )
        self.ui.buttonConnect.clicked.connect( self.connectMotors )

        self.ui.buttonMotorsOn.clicked.connect( self.motorsToOn )
        self.ui.buttonMotorsOff.clicked.connect( self.motorsToOff )

        self.ui.buttonStartRecording.clicked.connect( self.recordingToStart )
        self.ui.buttonStopRecording.clicked.connect( self.recordingToStop )

        self.ui.scalingSlider.valueChanged[int].connect( self.setMultFactor )
        self.ui.scaling.setText( 'Step scaling is %d' % self.ui.scalingSlider.value() ) 
        self.multFactor = self.ui.scalingSlider.value()
        
        self.ui.loggingCombo.activated['QString'].connect( self.setLogging )
        self.ui.sourceCombo.activated['QString'].connect( self.setSource )
        self.ui.methodCombo.activated['QString'].connect( self.setMethod )
        self.ui.coloringCombo.activated['QString'].connect( self.setColoring )

#        self.ui.boundaryEdit.textChanged.connect( self.setDecisionOffset )
        self.ui.boundaryEdit.editingFinished.connect( self.setDecisionOffset )

        self.setAble('motors', False)

    def setDecisionOffset( self ):
        if self._wormFinder:
            do = self.ui.boundaryEdit.text()
            try:
                d = int(do)
                self._wormFinder.setDecisionOffset( d )
            except Exception as e:
                logger.exception( str(e) )
                    

    def setColoring( self, value ):
        if self._wormFinder:
            self._wormFinder.setColoring( value )

    def recordingToStart( self ):
        if not self._cap.isWritingVideo:
            self._cap.startWritingVideo('%s.avi' % self.shareFileName,
                    cv2.VideoWriter_fourcc(*'MJPG'))
        self.ui.fps.setText( str( self._cap._fpsEstimate ) )
    
    def recordingToStop( self ):
        if self._cap.isWritingVideo:
            self._cap.stopWritingVideo()


    def motorsToOn( self ):
        self.motorsOn = True
        self._wormFinder.launch = 0
                

    def motorsToOff( self ):
        self.motorsOn = False


    def run ( self ):
        #self.setLogging(self.ui.loggingCombo.currentText())

        if not self._cap:
            self.setSource(self.ui.sourceCombo.currentText())
            
        self.actualRes = self._cap.getResolution()
        self.centerPt = utils.Point(self.actualRes[0] / 2, self.actualRes[1] / 2)
        self.cropSize = 100
        self.decisionOffset = 55
        
        self.finderArgs = {
            'gsize' :  45,
            'gsig' : 9,
            'window' : 3,
            'method' : self.ui.methodCombo.currentText(),
            'MAXONEFRAME': 500,
            'REFPING' : 1000,
            'MAXREF': 1000,
            'cropSize': self.cropSize,
            'centerPt': self.centerPt,
            'decisionOffset': self.decisionOffset,
            'servos': self.ebb,
            'actualRes': self.actualRes,
            'motorsOn': self.motorsOn
            }

        self.ui.boundaryEdit.setText( str(self.decisionOffset) )
        self._wormFinder = WormFinder( **self.finderArgs )     

        self.runTracking = True
        self.showImage = True


    def connectMotors( self ):
        if self._cap:
            try:
                logger.debug(self.widthMM)
                self.ebb = EasyEBB(resolution = self.actualRes, sizeMM = self.widthMM)
            except serial.SerialException as e:
                logger.exception(str(e))
        else:
            self.setSource( self.ui.sourceCombo.currentText() )
            try:
                logger.debug(self.widthMM )
                self.ebb = EasyEBB(resolution = self.actualRes, sizeMM = self.widthMM)
            except serial.SerialException as e:
                logger.exception(str(e))
            logger.warning('Source set to current combo box value')

    def setMethod (self, value ):
        self.method = str(value)
        if self._wormFinder:
            self._wormFinder.setMethod( self.method )

    def setSource ( self, value ):
        nums = re.compile(r'\d*')
        mat = re.match(nums,value).group(0)
        existingVid = False

        if re.match(nums, value).group(0) is not u'':
            src = int(value)
        else:
            src = str(value)
            existingVid = True
        self._cap = CaptureManager( cv2.VideoCapture(src) )

        self.showImage = True
        
        self.actualRes = self._cap.getResolution()
        if self.actualRes != self.calibrationRes and not existingVid:
            self._cap.setProp( 'height', self.calibrationRes[1] )
            self._cap.setProp( 'width', self.calibrationRes[0] )
        self.showImage = True
            

    def setLogging( self, value ):
        addFile = True

        formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(name)s\t\t%(message)s')
        self.shareFileName = '%s-%s' % (self.ui.studyName.text(), time.strftime("%a_%d_%b_%Y-%H %M %S") )
        
        file = logging.FileHandler( '%s.log' % self.shareFileName )
        file.setLevel(LOGGING_LEVELS['warning'])
        file.setFormatter(formatter)
        
        #logger.setLevel(LOGGING_LEVELS[str(value)] )
        console = logging.StreamHandler()
        console.setLevel(LOGGING_LEVELS[str(value)])
        console.setFormatter(formatter)
        
        for h in logger.handlers:
            if type(h) == logging.StreamHandler:
                logger.removeHandler(h)
            elif type(h) == logging.FileHandler: #if file has started, leave it be!!!
                addFile = False

        
        if addFile:
            logger.addHandler(file)
        
        logger.addHandler(console)

    def setMultFactor ( self, value ):
        self.multFactor = value
        self.ui.scaling.setText( 'Motor step scaling is %d' % value)
   
    def setAble( self, group, ability ):
        groups = { 'motors' : [self.ui.buttonLeft, 
                               self.ui.buttonRight,
                               self.ui.buttonUp, 
                               self.ui.buttonDown, 
                               self.ui.scalingSlider, 
                               self.ui.scaling],
                  'study':[self.ui.studyDesc, 
                           self.ui.studyName],
                  }
        
        for g in groups[group]:
            g.setEnabled(ability)

    def readInCalibration( self ):
        c = os.path.dirname(os.getcwd())
        cc = os.path.dirname(c)
        f = open( ("%s\\config.txt" % cc) , "r")
        line = f.readline()
        f.close()        
        logger.warning('line: %s' % str(line) )
        w, h, widthMM = line.split('|')
        self.widthMM = float(widthMM)
        self.calibrationRes = [int(w), int(h)]
            



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
                #partial(self.ebb.move, dir[direction])
                th.start()
                #th.join()
            except Exception as e:
                logger.exception( str(e) )


        

    def closeEvent ( self, event):
        logger.debug("closing")
        if self.ebb:
            self.ebb.closeSerial()
        if self._cap.isWritingVideo:
            self._cap.stopWritingVideo()
        
        for h in logger.handlers:
            if type(h) == logging.FileHandler:
                h.close()

        

       
            
    def isColor( self, imgIn ):
        ncolor = np.shape(imgIn)[2]
        boolt = int(ncolor) > 2
        return boolt
   
    def play( self ):
        
        if self.showImage:
            ## Get image from camera
            self._cap.enterFrame()
            self.currentFrame = self._cap.frame
        
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
            
           
            if self.runTracking:
                ## Tracking procedure
                if time.time() - self._lastCheck >= self._sampleFreq:
                    if self.ui.methodCombo.currentText() in ['lazyc', 'lazyd', 'lazy']:

                        gaussian = self._wormFinder.processFrame( self.currentFrame )
                        if gaussian is not None:
                            cv2.imshow( 'gaussian', gaussian )
                        self.overlayImage = copy.deepcopy(self.currentFrame)
                        
                        if self.motorsOn:
                            self._wormFinder.decideMove()
                        self._lastCheck = time.time()
                        self._wormFinder.drawDebugCropped( self.overlayImage)

                        self.ui.videoFrame.setPixmap(self._cap.convertFrame(self.overlayImage))
            #if self._cap.isWritingVideo:
            self.ui.fps.setText( str( self._cap._fpsEstimate ) )
        return
        
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
        
        





def main():
    app = QtWidgets.QApplication( sys.argv )
    #filter = ValEventFilter()
    #app.installEventFilter(filter)
    g = Gui()
    g.show()
    sys.exit( app.exec_() )

if __name__ == '__main__':
    main()