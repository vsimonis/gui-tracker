import cv2
import numpy
import time
import logging
from PyQt5 import QtGui, QtCore, Qt

logc = logging.getLogger(__name__)
logw = logging.getLogger('window')

class CaptureManager( object ):
    

    def __init__( self, capture ):
        self._capture = capture

        
        self._enteredFrame = False
        self._frame = None

        self._imageFilename = None
        self._videoFilename = None

        self._videoEncoding = None
        self._videoWriter = None
        self.gotFrame = True
        self._startTime = None
        self._framesElapsed = long(0)
        self._fpsEstimate = None
     
    @property
    def frame( self ): 
        if self._enteredFrame and self._frame is None:
            self.gotFrame, self._frame = self._capture.retrieve()
           
        return self._frame

    @property
    def isWritingImage( self ):
        return self._imageFilename is not None

    @property
    def isWritingVideo( self ):
        return self._videoFilename is not None
    
    def gray2qimage(self, gray):
        """Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
        colormap.  The first dimension represents the vertical image axis.
        
        ATTENTION: This QImage carries an attribute `ndimage` with a
        reference to the underlying numpy array that holds the data. On
        Windows, the conversion into a QPixmap does not copy the data, so
        that you have to take care that the QImage does not get garbage
        collected (otherwise PyQt will throw away the wrapper, effectively
        freeing the underlying memory - boom!).
        """
        if len(gray.shape) != 2:
            raise ValueError("gray2QImage can only convert 2D arrays")
      
        gray = numpy.require(gray, numpy.uint8, 'C')

        h, w = gray.shape

        result = QtGui.QImage(gray.data, w, h, QtGui.QImage.Format_Indexed8)
        result.ndarray = gray
        for i in range(256):
            result.setColor(i, QtGui.QColor(i, i, i).rgb())
        return result

    def convertFrame(self,imgIn):
        """                                                    
        converts frame to format suitable for QtGui            
        """
        try:
            img = self.gray2qimage( imgIn )
            img = QtGui.QPixmap.fromImage(img)

            return img
        except:
            return None

   

    def enterFrame( self ):
        #Capture the next frame, if any
        #Check that previous frame is exited
        assert not self._enteredFrame, \
            'previous enterFrame() has no matching exitFrame()'
        
        if self._capture is not None:
            self._enteredFrame = self._capture.grab()
        

    def exitFrame( self ):
        #Write to files
        #Release the frame

        #Check whether grabbed frame is retrievable
        # The getter may retrieve and cache the frame

        if self.frame is None: ####IS THIS OK? _FRAME INST
            self._enteredFrame = False
            return

        #Update FPS estimate and related
        if self._framesElapsed == 0:
            self._startTime = time.time()
        else: 
            timeElapsed = time.time() - self._startTime
            self._fpsEstimate = self._framesElapsed / timeElapsed
            logc.info('fps estimate: %d' % self._fpsEstimate )
        self._framesElapsed += 1

        #Write to video 
        self._writeVideoFrame()
            
        #Release
        self._frame = None
        self._enteredFrame = False

    def writeImage( self, filename ):
        self._imageFilename = filename


    def startWritingVideo( self, filename, encoding ):
        self._videoFilename = filename
        self._videoEncoding = encoding
        logc.warning( 'Start Writing Video: %s' % filename )

    def stopWritingVideo ( self ):
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
        logc.warning( 'Stop Writing Video' )
        

    def _writeVideoFrame( self ):
        if not self.isWritingVideo:
            return
        
        if self._videoWriter is None:
            fps = self._capture.get( cv2.CAP_PROP_FPS ) 
            logc.warning("fps: %d" % fps)
            if fps <= 0.0:
                if self._framesElapsed < 20: 
                    # wait for more frames to get good estimate
                    return
                else: 
                    logc.warning('fps estimate used: %d' % self._fpsEstimate )
                    fps = self._fpsEstimate            

            size = ( int (self._capture.get( cv2.CAP_PROP_FRAME_WIDTH )), 
                     int( self._capture.get( cv2.CAP_PROP_FRAME_HEIGHT) ))
            logc.warning('size used: %d x %d' % (size[0], size[1]) )

            self._videoWriter = cv2.VideoWriter( self._videoFilename, 
                                                 self._videoEncoding, fps, size, False )
        self._videoWriter.write(self._frame)
 
    def setCaptureSpace( self, fourccCode ):
        
        try: 
            self.setProp('fourcc', fourccCode)
        except Exception as e:
            logc.exception(e)

    def getResolution( self ):
        h = self.getProp( 'height')
        w = self.getProp( 'width')
        return [w, h]
   
    def getProp( self, prop ):
        props = {
                 'mode': cv2.CAP_PROP_MODE,
                 'brightness': cv2.CAP_PROP_BRIGHTNESS,
                 'contrast': cv2.CAP_PROP_CONTRAST,
                 'saturation': cv2.CAP_PROP_SATURATION,
                 'hue':cv2.CAP_PROP_HUE,
                 'gain': cv2.CAP_PROP_GAIN,
                 'exposure': cv2.CAP_PROP_EXPOSURE,
                 'height': cv2.CAP_PROP_FRAME_HEIGHT,
                 'width': cv2.CAP_PROP_FRAME_WIDTH
                 }

        newval = self._capture.get(props[prop])
        if newval == 0:
            logc.warn('- get prop %s\tnot available' % prop)
        else:
            logc.warn('- get prop: %s\t%s' % (prop, newval) )
        return newval

    def setProp( self, prop, value):
        props = {
                 'mode': cv2.CAP_PROP_MODE,
                 'brightness': cv2.CAP_PROP_BRIGHTNESS,
                 'contrast': cv2.CAP_PROP_CONTRAST,
                 'saturation': cv2.CAP_PROP_SATURATION,
                 'hue':cv2.CAP_PROP_HUE,
                 'gain': cv2.CAP_PROP_GAIN,
                 'exposure': cv2.CAP_PROP_EXPOSURE,
                 'height': cv2.CAP_PROP_FRAME_HEIGHT,
                 'width': cv2.CAP_PROP_FRAME_WIDTH,
                 'fourcc': cv2.CAP_PROP_FOURCC
                 }
    
        self._capture.set(props[prop], float(value))
        logc.warn('- set prop: %s\t%s' % ( prop, str(value) ))
        self._capture.get(props[prop])
    
      
    def debugProps( self ):
        for prop, name in [(cv2.CAP_PROP_MODE, "Mode"),
                           (cv2.CAP_PROP_BRIGHTNESS, "Brightness"),
                           (cv2.CAP_PROP_CONTRAST, "Contrast"),
                           (cv2.CAP_PROP_SATURATION, "Saturation"),
                           (cv2.CAP_PROP_HUE, "Hue"),
                           (cv2.CAP_PROP_GAIN, "Gain"),
                           (cv2.CAP_PROP_EXPOSURE, "Exposure")]:
            value = self._capture.get(prop)
            if value == 0:
                logc.warn(" - %s not available" % name)
            else:
                logc.warn(" - %s = %r" % (name, value))

 

