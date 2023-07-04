# Operations panel
# This panel displays the list of operations created by the user
# Functionnalities are:
# - list Operations
# - create/delete/duplicate/reorder operations
# - display preset operations
#
# For each operation, generate the corresponding gcode and export the gcode file

import bpy
from ...utils import *

from bpy.types import PropertyGroup

from ...constants import*

class CAMMaterialProperties(PropertyGroup):

    estimate_from_model: bpy.props.BoolProperty(
        name="Estimate cut area from model",
        description="Estimate cut area based on model geometry",
        default=True,
        update=update_material
    )

    radius_around_model: bpy.props.FloatProperty(
        name='Radius around model',
        description="Increase cut area around the model on X and Y by this amount",
        default=0.0, unit='LENGTH', precision=PRECISION,
        update=update_material
    )

    center_x: bpy.props.BoolProperty(
        name="Center on X axis",
        description="Position model centered on X",
        default=False, update=update_material
    )

    center_y: bpy.props.BoolProperty(
        name="Center on Y axis",
        description="Position model centered on Y",
        default=False, update=update_material
    )

    z_position: bpy.props.EnumProperty(
        name="Z placement", items=(
            ('ABOVE', 'Above', 'Place object vertically above the XY plane'),
            ('BELOW', 'Below', 'Place object vertically below the XY plane'),
            ('CENTERED', 'Centered', 'Place object vertically centered on the XY plane')),
        description="Position below Zero", default='BELOW',
        update=update_material
    )

    # material_origin
    origin: bpy.props.FloatVectorProperty(
        name='Material origin', default=(0, 0, 0), unit='LENGTH',
        precision=PRECISION, subtype="XYZ",
        update=update_material
    )

    # material_size
    size: bpy.props.FloatVectorProperty(
        name='Material size', default=(0.200, 0.200, 0.100), min=0, unit='LENGTH',
        precision=PRECISION, subtype="XYZ",
        update=update_material
    )