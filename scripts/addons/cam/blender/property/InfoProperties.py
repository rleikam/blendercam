from bpy.types import PropertyGroup
from bpy.props import StringProperty, FloatProperty

from ...constants import *
from ...utils import *

class InfoProperties(PropertyGroup):
    
    warnings: StringProperty(
        name='warnings',
        description='warnings',
        default='',
        update=update_operation
    )

    chipload: FloatProperty(
        name="chipload", description="Calculated chipload",
        default=0.0, unit='LENGTH',
        precision=CHIPLOAD_PRECISION
    )

    duration: FloatProperty(
        name="Estimated time", default=0.01, min=0.0000,
        max=MAX_OPERATION_TIME,
        precision=PRECISION, unit="TIME"
    )