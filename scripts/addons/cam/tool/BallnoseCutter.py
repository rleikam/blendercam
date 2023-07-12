from .Cutter import *

class BallnoseCutter(Cutter):
    def __init(self, diameter):
        self.maximumToolDepth = diameter/2

    def calculateMillDepthFor(self, diameter: float) -> float:
        pass
    
    def calculateMillDiameterFor(self, depth: float) -> float:
        pass

    def getMaximumToolLength(self) -> float:
        pass
