import bpy

from ...constants import *
from ...utils import *

class InfoProperties(bpy.types.PropertyGroup):
    
    warnings: bpy.props.StringProperty(
        name='warnings',
        description='warnings',
        default='',
        update=update_operation
    )

    chipload: bpy.props.FloatProperty(
        name="chipload", description="Calculated chipload",
        default=0.0, unit='LENGTH',
        precision=CHIPLOAD_PRECISION
    )

    duration: bpy.props.FloatProperty(
        name="Estimated time", default=0.01, min=0.0000,
        max=MAX_OPERATION_TIME,
        precision=PRECISION, unit="TIME"
    )