from .Cutter import *
from math import tan, radians, sin, cos, acos, asin

class BallconeCutter(Cutter):
    def __init__(self, angle : float, ballDiameter : float, diameter : float):

        self._slope = tan(radians(angle / 2))

        self._ballRadius = ballDiameter/2

        self._depthBallTangentToBallCenter = self._ballRadius * sin(radians(angle/2))
        self._radiusBallTangent = self._ballRadius * cos(radians(angle/2))
        self._depthConeTipToBallTangent = self._radiusBallTangent/self._slope
        self._depthConeTipToBallCenter = self._depthConeTipToBallTangent + self._depthBallTangentToBallCenter
        self._depthConeTipToBallTip = self._depthConeTipToBallCenter - self._ballRadius
        self._depthBallTipToBallTangent = self._depthConeTipToBallCenter - self._depthConeTipToBallTip - self._depthBallTangentToBallCenter

        self._maximumToolDepth = (diameter/2)/self._slope - self._depthConeTipToBallTip

    def calculateMillDepthFor(self, diameter: float) -> float:
        calculatedDepth = 0.0
        millRadius = diameter/2
        if millRadius < self._radiusBallTangent:
            calculatedRadians = acos(millRadius/self._ballRadius)
            calculatedDepth = self._ballRadius - self._ballRadius*sin(calculatedRadians)
        else:
            calculatedDepth = (millRadius/self._slope) - self._depthConeTipToBallTip
        
        return calculatedDepth
    
    def calculateMillDiameterFor(self, depth: float) -> float:
        if depth < self._depthBallTipToBallTangent:
            depthInverse = self._ballRadius - depth
            calculatedRadians = asin(depthInverse/self._ballRadius)
            calculatedDepth = 2*self._ballRadius*cos(calculatedRadians)
        else:
            calculatedDepth = 2*((depth+self._depthConeTipToBallTip)*self._slope)

        return calculatedDepth

    def getMaximumToolLength(self) -> float:
        return self._maximumToolDepth