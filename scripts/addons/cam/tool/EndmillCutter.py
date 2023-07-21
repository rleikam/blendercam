from .Cutter import Cutter

class EndmillCutter(Cutter):
    def __init__(self, diameter):
        self.diameter = diameter

    def calculateMillDepthFor(self, diameter: float) -> float:
        return 0
    
    def calculateMillDiameterFor(self, depth: float) -> float:
        return self.diameter

    def getMaximumToolLength(self) -> float:
        return self.diameter
