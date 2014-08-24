import sys
import numpy as np
#import pandas as pd
import utils
import time
#from imgProc import imgProc
#from managers import WindowManager

import cv2
import logging
import threading


logger = logging.getLogger(__name__)

class WormFinder ( object ):
    
    '''
    arguments given:
    - method
    - gsize (size of gaussian filter)
    - gsig (sigma for gaussian filter)
    - window (number of locations to avg)
    '''
    def __init__( self, **kwargs ) :
        
        for k in kwargs.keys():
            if k in ['method', 'gsize', 'gsig', 'window', 
                     'MAXONEFRAME', 'REFPING', 'MAXREF', 
                     'centerPt', 'decisionOffset', 'cropSize', 'actualRes',
                     'motorsOn', 'servos']:
                self.__setattr__(k, kwargs[k])

        #self.trackerConnected = True
        self.captureSize = utils.Rect(self.actualRes[0], self.actualRes[1], self.centerPt)
        self.cropRegion = utils.Rect(self.cropSize,self.cropSize,self.centerPt) 
        
        self.decisionBoundary = utils.Rect(self.actualRes[0] - self.cropSize - 100, 
                                           self.actualRes[1] - self.cropSize - 100, 
                                           self.centerPt)

        ### Timing ###
        self.lastRefTime = time.time()        
        self.pauseFrame = 0 #cropping wise
        self.nPauseFrames = 20 #cropping wise
        
        self.breakDuration = 5 # motor wise
        self.breakStart = time.time()

        ### Worm Finding
        ## points
        self.wormLocation = utils.Point(-1 , -1 ) 
        self.wormLocationPrevious = utils.Point( -1, -1)
        self.frameCenter = utils.Point(self.captureSize.ncols / 2, self.captureSize.nrows / 2)

        ## images 
        self.refImg = None
        self.subImg = None
        self.croppedImg = None

        ### Cropping ###
        self.cmin = 0
        self.cmax = self.captureSize.ncols
        self.rmin = 0
        self.rmax = self.captureSize.nrows


        ## Cosmetic ##
        self.coloring = 'gray-1'

    def setColoring( self, value ):
        self.coloring = value

    def setDecisionOffset( self, value ):
        self.cropSize = value
        self.cropRegion = utils.Rect(self.cropSize,self.cropSize,self.centerPt) 
        self.decisionBoundary = utils.Rect(self.actualRes[0] - self.cropSize - 100,
                                           self.actualRes[1] - self.cropSize - 100,
                                           self.centerPt)

    @property
    def hasReference ( self ):
        return self.refImg is not None

    @property
    def isColor ( self ):
        return self.color
    def setMethod ( self, newMethod ):
        self.method = newMethod

    def resetRef( self ):
        self.pauseFrame = 0
        self.refImg = None

                ### Cropping ###
        self.cmin = 0
        self.cmax = self.captureSize.ncols
        self.rmin = 0
        self.rmax = self.captureSize.nrows
#        self.launch = 0

    """ 
    FIND WORMS
    """
    def lazy (self ):
        self.findWorm(self.wormLocation)
    
    def lazyDemo (self):
        self.findWorm(self.frameCenter)

    def findWorm ( self, cropPoint ):
        t = time.time()
        if self.hasReference:
            # Subtract images 
            self.subImg = cv2.subtract(self.refImg, self._img)
            # If timing is right, crop!
            if self.croppedSearchSpace():
                self.calculateCrop(cropPoint) # crop with cropPoint as center
                # perform crop
                self.subImg = self.subImg[self.rmin : self.rmax, self.cmin : self.cmax]
            # Gaussian Blur
            self.subImg  = cv2.GaussianBlur( self.subImg, 
                                           (self.gsize, self.gsize) , self.gsig )
            # Worm Location
            maxImg = self.subImg == np.max( self.subImg )
            r, c = np.nonzero ( maxImg )
            self.wormLocation.update( c[0] + self.cmin, r[0] + self.rmin)
            self.wormLocationPrevious.update( self.wormLocation.col, self.wormLocation.row )
            self.pauseFrame += 1
            self.justMoved = False #necessary?
            
        else:
            return
        
    def lazyNoCrop(self):
        self.findWormNoCropping( 'nada')

    def findWormNoCropping ( self, cropPoint ):
        t = time.time()
    
        if self.hasReference:
            # Subtract images 
            self.subImg = cv2.subtract(self.refImg, self._img)
            # Gaussian Blur
            self.subImg  = cv2.GaussianBlur( self.subImg, 
                                           (self.gsize, self.gsize) , self.gsig )
            # Worm Location
            r, c = np.nonzero ( self.subImg == np.max( self.subImg ) )
            self.wormLocation.update( c[0] + self.cmin, r[0] + self.rmin)
            self.wormLocationPrevious.update( self.wormLocation.col, self.wormLocation.row )
            self.pauseFrame += 1
            self.justMoved = False #necessary?
        else:
            return

    def croppedSearchSpace ( self ):
        return ( self.method in ['lazyc', 'lazyd'] ) and ( self.pauseFrame > self.nPauseFrames )

    def calculateCrop ( self, p ):
        self.cropRegion.update(p)
        if self.cropRegion.left > 0:
            self.cmin = self.cropRegion.left
        else:
            self.cmin = 0
        if self.cropRegion.right < self.captureSize.right:
            self.cmax = self.cropRegion.right
        else:
            self.cmax = self.captureSize.right
        if self.cropRegion.top > 0:
            self.rmin = self.cropRegion.top
        else:
            self.rmin = 0
        if self.cropRegion.bottom < self.captureSize.bottom:
            self.rmax = self.cropRegion.bottom
        else:
            self.rmax = self.captureSize.bottom

    """
    DISPATCH
    lazyd -> keep decision boundary restricted to center of the image
    lazy  -> use full image
    
    """

    def processFrame ( self, img ):

        options = {
            'lazy' : self.lazyNoCrop,
            'lazyc': self.lazy, 
            'lazyd': self.lazyDemo
            }
        t = time.time()
        

        if self.method in ['lazy','lazyc','lazyd']:
            if not self.hasReference:
               self.refImg = img
               self.lastRefTime = time.time()
            else:
               self._img = img
      
               try:
                   options[self.method]()
               except KeyError:
                   self.lazyc() #default

        return self.subImg ## gets displayed in the window
    

    def decideMove ( self ):
        t = time.time()

        if not self.hasReference:
            return
        if not self.breakOver():
            return
  
        if self.method in ['lazy','lazyc','lazyd']:
            if time.time() - self.lastRefTime >= self.REFPING:
                self.resetRef()
                logger.warning('New reference based on PING')

            ### Possible move: make sure
            if self.wormOutsideBoundary('point'):
                ## Check previous location of worm
                if not self.wormRidiculousLocation():
                    #logger.warning('MOVE!!!')
                    self.justMoved = True
                    self.resetRef()
                    self.breakStart = time.time()
                    th = threading.Thread(target = self.servos.centerWorm, 
                                         args = (100, self.wormLocation.col, self.wormLocation.row) )
                    try:
                        th.start()
#                        self.servos.centerWorm(100, self.wormLocation.col, self.wormLocation.row)
                    except:
                        logger.warning('move command not sent')
                else:
                    logger.warning('Impossible location: too far from previous')
        logger.debug('processing: %0.6f' % (time.time() - t))
        return

                                                 
    def breakOver( self ):
        currentTime = time.time()
        if currentTime - self.breakStart > self.breakDuration:
            return True
        else:
            return False

    def wormRidiculousLocation( self ):
        farRow = abs ( self.wormLocationPrevious.row - self.wormLocation.row ) > self.MAXONEFRAME
        farCol = abs ( self.wormLocationPrevious.col - self.wormLocation.col ) > self.MAXONEFRAME
        return farRow or farCol
    
    def wormOutsideBoundary ( self, method ):
        if method == 'point':
            
            rowTop = self.wormLocation.row < self.decisionBoundary.top
            rowBottom = self.wormLocation.row > self.decisionBoundary.bottom
            colLeft = self.wormLocation.col < self.decisionBoundary.left
            colRight =  self.wormLocation.col > self.decisionBoundary.right
        
       # elif method == 'rect': 
       #     rowLeft = self.cropRegion.left < self.decisionBoundary.left
       #     rowRight = self.cropRegion.right > self.decisionBoundary.right
       #     colTop = self.cropRegion.bottom < self.decisionBoundary.top
       #     colBottom = self.cropRegion.top > self.decisionBoundary.bottom
        
        return (rowTop or rowBottom) or (colLeft or colRight)


    """
    DEBUGGING
    """

    '''
    Debugging Points
    '''
    def drawDebugCropped( self, img ):
       self.wormLocation.draw( img, 'white-1')

       self.decisionBoundary.draw( img, 'black-1')
       if self.croppedSearchSpace():
           self.cropRegion.draw(img, 'black-1' )
