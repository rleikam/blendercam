from .Cutter import Cutter
from math import tan, radians

class ConeCutter(Cutter):
    def __init__(self, angle, diameter):
        self._slope = tan(radians(angle / 2))
        self._maximumToolDepth = (diameter/2)/self._slope

    def calculateMillDepthFor(self, diameter: float) -> float:
        return (diameter/2)/self._slope
    
    def calculateMillDiameterFor(self, depth: float) -> float:
        return (depth*self._slope)*2

    def getMaximumToolLength(self) -> float:
        return self._maximumToolDepth