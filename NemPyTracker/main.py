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

logger = logging.getLogger('')

class Gui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        logger.warning('starting up')
        

        
        ## Instantiate classes
        self.ui = Ui_TrackerUI()
        self.ui.setupUi(self)
        self._cap  = None


        ## Give options to comboBoxes
        for k,v in LOGGING_LEVELS.items():
            self.ui.loggingCombo.addItem(k,v)

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

        
#        self.shareFileName = '%s' % (time.strftime("%a_%d_%b_%Y-%H %M %S") )

        ## Register button actions
        self.ui.buttonRight.clicked.connect( partial( self.motors, 'right' ) )
        self.ui.buttonLeft.clicked.connect( partial( self.motors, 'left' ) )
        self.ui.buttonUp.clicked.connect( partial( self.motors, 'up' ) )
        self.ui.buttonDown.clicked.connect( partial( self.motors, 'down' ) )
        self.ui.buttonRefresh.clicked.connect( self.getNewRef )
        self.ui.buttonRun.clicked.connect( self.run )
        self.ui.buttonConnect.clicked.connect( self.connectMotors )
        self.ui.buttonReset.clicked.connect (self.resetAll )

        self.ui.buttonMotorsOn.clicked.connect( self.motorsToOn )
        self.ui.buttonMotorsOff.clicked.connect( self.motorsToOff )

        self.ui.buttonStartRecording.clicked.connect( self.recordingToStart )
        self.ui.buttonStopRecording.clicked.connect( self.recordingToStop )

        self.ui.scalingSlider.valueChanged[int].connect( self.setMultFactor )
        self.ui.scaling.setText( 'Step scaling is %d' % self.ui.scalingSlider.value() ) 
        self.multFactor = self.ui.scalingSlider.value()
        
        #self.ui.loggingCombo.activated['QString'].connect( self.setLogging )
        self.ui.sourceCombo.activated['QString'].connect( self.setSource )
        self.ui.methodCombo.activated['QString'].connect( self.setMethod )
        self.ui.coloringCombo.activated['QString'].connect( self.setColoring )

#        self.ui.boundaryEdit.textChanged.connect( self.setDecisionOffset )
        self.ui.boundaryEdit.editingFinished.connect( self.setDecisionOffset )
        self.ui.studyName.editingFinished.connect( self.setFileName )

        self.newFileFLAG = True

        self.readInCalibration()
        #self.setAble('motors', False)
        # self.setFileName()
        self.setAble('debug', False)
        self.setAble('buttons', False)
        self.setAble('motors', False)
        self.setAble('motorized', False)
        self.setAble('recording', False)


    def setFileName ( self ) :
        self.shareFileName = '%s-%s' % ( self.ui.studyName.text(), time.strftime( "%a_%d_%b_%Y-%H %M %S" ) )
        if self.ui.loggingCombo.currentText is not '':
            self.setLogging( self.ui.loggingCombo.currentText())
        self.setAble( self.ui.buttonRun, True)
        self.setAble( self.ui.buttonConnect, True)
        self.setAble( 'study', False ) 

    def getNewRef( self ):
        if self._wormFinder:
            self._wormFinder.resetRef()

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
        self.shareFileName = '%s-%s' % ( self.ui.studyName.text(), time.strftime( "%a_%d_%b_%Y-%H %M %S" ) )
        platform = sys.platform.lower()
        if platform in ['win32', 'win64']:

            fourcc = cv2.VideoWriter_fourcc(*'IYUV')
            logger.warning( 'fourcc is IYUV')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            logger.warning( 'fourcc is MJPG')
        if not self._cap.isWritingVideo:
            self._cap.startWritingVideo('%s.avi' % self.shareFileName, fourcc)
        #self.ui.fps.setText( str( self._cap._fpsEstimate ) )
        self.setAble(self.ui.buttonStartRecording, False)
        self.setAble(self.ui.buttonStopRecording, True)

    def recordingToStop( self ):
        if self._cap.isWritingVideo:
            self._cap.stopWritingVideo()
            #        self.ui.buttonStartRecording
        self.setAble(self.ui.buttonStartRecording, True)
        self.setAble(self.ui.buttonStopRecording, False)


    def motorsToOn( self ):
        self.motorsOn = True
        self._wormFinder.launch = 0
        logger.info('motors on')
        self.setAble('motors', False)
        self.setAble('recording', True)
        self.setAble(self.ui.buttonStopRecording, False)
        self.setAble(self.ui.buttonMotorsOff, True)
        self.setAble(self.ui.buttonMotorsOn, False)
        self.setAble(self.ui.boundaryEdit, False)
        self.setAble(self.ui.boundaryDesc, False)

    def motorsToOff( self ):
        self.motorsOn = False
        logger.info('motors off')
        self.setAble(self.ui.buttonMotorsOff, False )
        self.setAble(self.ui.buttonMotorsOn, True )
        self.setAble('motors', True)
#        self.setAble('recording', True)
        



    def run ( self ):
        logger.info("Start running tracking")
        # setup logggin????
        #self.setLogging(self.ui.loggingCombo.currentText())
        if self._wormFinder:
            self._wormFinder = None

        if not self._cap:
            self.setSource(self.ui.sourceCombo.currentText())
            
        #self.actualRes = self._cap.getResolution()
        self.centerPt = utils.Point(self.actualRes[0] / 2, self.actualRes[1] / 2)
        self.cropSize = 100
#        self.decisionOffset = 55
        
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
 #           'decisionOffset': self.decisionOffset,
            'servos': self.ebb,
            'actualRes': self.actualRes,
            'motorsOn': self.motorsOn
            }

        self.ui.boundaryEdit.setText( str(self.cropSize) )
        self._wormFinder = WormFinder( **self.finderArgs )     

        self.runTracking = True
        self.showImage = True
        self.setAble( self.ui.buttonRefresh, True) 
        self.setAble( self.ui.buttonRun, False )
        self.setAble ( self.ui.coloringCombo, True ) 
        self.setAble( self.ui.coloringDesc, True ) 
        self.setAble( self.ui.boundaryEdit, True ) 
        self.setAble( self.ui.boundaryDesc, True ) 
        if self.ebb:
            self.setAble('motorized', True)
            self.setAble(self.ui.buttonMotorsOff, False)
        self.setAble('recording', True)

    def connectMotors( self ):
        logger.info("Connect Motors")
        if self._cap:
            #self.actualRes = self._cap.getResolution()
            try:
                logger.debug('width mm %d' % self.widthMM)
                self.ebb = EasyEBB(resolution = self.actualRes, sizeMM = self.widthMM)
                self.setAble('motors', True)
                self.setAble(self.ui.buttonConnect, False)
                if self._wormFinder:
                    self._wormFinder.servos = self.ebb
                    self.setAble('motorized', True)
                    self.setAble(self.ui.buttonMotorsOff, False)
            except serial.SerialException as e:
                logger.exception(str(e))
                QtWidgets.QMessageBox.information( self, "Motors Issue",
                                                  "Unable to connect to motors. Please connect or reboot motors. If problem persists, reboot computer")

        else: #possibly not necessary now with greyed out options
            self.setSource( self.ui.sourceCombo.currentText() )
            logger.debug('Source set to current combo box value')
            try:
                logger.debug('width mm: %d' % self.widthMM )
                self.ebb = EasyEBB(resolution = self.actualRes, sizeMM = self.widthMM)
                self.setAble('motors', True)
            except serial.SerialException as e:
                logger.exception(str(e))
                QtWidgets.QMessageBox.information( self, "Motors Issue",
                                                  "Unable to connect to motors. Please connect or reboot motors. If problem persists, reboot computer")



    def setMethod (self, value ):
        self.method = str(value)
        if self._wormFinder:
            self._wormFinder.setMethod( self.method )

    def setSource ( self, value ):
        #self.setLogging(self.ui.loggingCombo.currentText())
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
        self.setAble(self.ui.buttonConnect, True)
        self.setAble(self.ui.buttonRun, True)
        

    def setLogging( self, value ):
        addFile = True
        formatter = logging.Formatter( '%(asctime)s\t%(levelname)s\t%(name)s\t\t%(message)s' )
        #self.setFileName() 
        file = logging.FileHandler( '%s.log' % self.shareFileName )
        logger.warning('New file')
        file.setLevel( LOGGING_LEVELS['debug'] )
        file.setFormatter( formatter )
        
        #logger.setLevel(LOGGING_LEVELS[str(value)] )
        console = logging.StreamHandler()
        console.setLevel( LOGGING_LEVELS[str(value)] )
        console.setFormatter( formatter )
        
        for h in logger.handlers:
            if type(h) == logging.StreamHandler:
                logger.removeHandler( h ) 
            elif type(h) == logging.FileHandler: #if file has started, leave it be!!!
            #    if self.newFileFLAG:
                addFile = False
            #        h.close()
            #    else:
            #       addFile = False
                    
        if addFile:
            logger.addHandler( file )

        logger.addHandler( console )
        self.newFileFLAG = False

    def setMultFactor ( self, value ):
        self.multFactor = value
        self.ui.scaling.setText( 'Step scaling is %d' % value)
   
    def setAble( self, group, ability ):
        groups = {'debug' : [ self.ui.loggingCombo, 
                             self.ui.loggingDesc,
                             self.ui.methodCombo,
                             self.ui.methodDesc,
                             self.ui.boundaryDesc,
                             self.ui.boundaryEdit, 
                             self.ui.coloringCombo,
                             self.ui.coloringDesc],
                  'source' : [ self.ui.sourceCombo,
                              self.ui.sourceDesc],
                  'motors' : [self.ui.buttonLeft, 
                               self.ui.buttonRight,
                               self.ui.buttonUp, 
                               self.ui.buttonDown, 
                               self.ui.scalingSlider, 
                               self.ui.scaling],

                  'motorized': [ self.ui.buttonMotorsOff, 
                                self.ui.buttonMotorsOn,
                                self.ui.motorsDesc ],

                  'recording': [self.ui.buttonStartRecording, 
                                self.ui.buttonStopRecording, 
                                self.ui.recordingDesc ],

                  'study':[self.ui.studyDesc, 
                           self.ui.studyName],
                  'buttons': [self.ui.buttonConnect, self.ui.buttonRefresh, self.ui.buttonRun]
                  }
       
        if group in groups.iterkeys():
            for g in groups[group]:
                g.setEnabled(ability)

        else:
            group.setEnabled(ability)


    def readInCalibration( self ):
        c = os.path.dirname(os.getcwd())
        cc = os.path.dirname(c)
        f = open( ("%s\\config.txt" % cc) , "r")
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
                #partial(self.ebb.move, dir[direction])
                th.start()
                #th.join()
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
            self._cap.stopWritingVideo()
        if self._cap._capture.isOpened():
            self._cap._capture.release()
        self.showImage = False
        self.runTracking = False
        self.motorsOn = False
        self.ui.videoFrame.setText("Select source if video not displayed here on boot up")
        self.ui.fps.setText("")
        logger.info("Reset button pressed") 
#        self.setFileName()
#        self.newFileFLAG = True
        ## GUI buttons enable
        self.setAble('source', True)
#        self.setAble('study', True)
        self.setAble('debug', False)
        self.setAble('buttons', False)
        self.setAble('motors', False)
        self.setAble('motorized', False)
        self.setAble('recording', False)
        self.readInCalibration()
        self.setAble('study', False)
        self.setAble('source', True)
#        self.ui.setupUi(self)

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
            if not self.runTracking:
                if self.showImage:
                    self.ui.videoFrame.setPixmap(self._cap.convertFrame(self.currentFrame))
            else:
                ## Tracking procedure
                if time.time() - self._lastCheck >= self._sampleFreq:
                    if self.ui.methodCombo.currentText() in ['lazyc', 'lazyd', 'lazy']:

                        gaussian = self._wormFinder.processFrame( self.currentFrame )
                        if gaussian is not None:
                            cv2.imshow( 'gaussian', gaussian )
                        #self.overlayImage = copy.deepcopy(self.currentFrame)
                        
                        if self.motorsOn:
                            self._wormFinder.decideMove()
                        self._lastCheck = time.time()
                        self._wormFinder.drawDebugCropped( self.currentFrame)

                        self.ui.videoFrame.setPixmap(self._cap.convertFrame(self.currentFrame))
            #if self._cap.isWritingVideo:
            self.ui.fps.setText( str( self._cap._fpsEstimate ) )
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
    #filter = ValEventFilter()
    #app.installEventFilter(filter)
    g = Gui()
    g.show()
    sys.exit( app.exec_() )

if __name__ == '__main__':
    main()