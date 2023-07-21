from .Cutter import *
from math import pow, sqrt

class BallnoseCutter(Cutter):
    def __init__(self, diameter):
        self.ballRadius = diameter/2
        self.squaredBallRadius = pow(self.ballRadius, 2)


    def calculateMillDepthFor(self, diameter: float) -> float:
        millRadius = diameter/2
        if millRadius >= self.ballRadius:
            return self.ballRadius
        
        if millRadius <= 0:
            return 0

        # Calculate mill depth with the pythagorean theorem
        squaredMillRadius = pow(millRadius, 2)
        invertedMillDepth = sqrt(self.squaredBallRadius - squaredMillRadius)
        millDepth = self.ballRadius - invertedMillDepth

        return millDepth
    
    def calculateMillDiameterFor(self, depth: float) -> float:
        if depth >= self.ballRadius:
            return self.ballRadius
        
        if depth <= 0:
            return 0
        
        # Calculate mill diameter with the pythagorean theorem
        invertedMillDepth = self.ballRadius - depth
        squaredInvertedMillDepth = pow(invertedMillDepth, 2)
        millRadius = sqrt(self.squaredBallRadius - squaredInvertedMillDepth)

        return millRadius*2

    def getMaximumToolLength(self) -> float:
        return self.ballRadius
