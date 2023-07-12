from .Tool import Tool

class Cutter(Tool):
    def __init__(self):
        pass

    def calculateMillDepthFor(self, diameter: float) -> float:
        """Calculates the mill depth for the given diameter based on the tip of the mill"""
        pass

    def calculateMillDiameterFor(self, depth: float) -> float:
        """Calculates the mill diameter for the given depth based on the tip of the mill"""
        pass
    
    def getMaximumToolLength(self) -> float:
        """Get the maximum tool depth"""
        pass