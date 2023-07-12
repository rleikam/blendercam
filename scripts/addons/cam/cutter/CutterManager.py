from .CutterType import *
from .ConeCutter import *
from .BallconeCutter import *
from .BallnoseCutter import *
from typing import Iterator

class CutterManager:
    """
    Helper class for generating the calculation objects based on supported mill types
    """
    @staticmethod
    def constructToolFromOperation(operation) -> Cutter:
        """Constructs a matching mill from the given operation"""

        match(operation.cutter_type):
            case CutterType.CONE.value:
                return ConeCutter(operation.cutter_tip_angle, operation.cutter_diameter)
            case CutterType.BALLNOSE.value:
                return BallnoseCutter(operation.cutter_diameter)
            case CutterType.BALLCONE.value:
                return BallconeCutter(operation.cutter_tip_angle, operation.ball_radius*2, operation.cutter_diameter)

    @staticmethod
    def isToolSupported(toolTypeName : str) -> str:
        """Checks if the given tool type is supported"""
        return toolTypeName in [enum.value for enum in CutterType]
    
    @staticmethod
    def getSupportedTools() -> Iterator[str]:
        """Gets the list of supported tools"""
        return [enum.value for enum in CutterType]