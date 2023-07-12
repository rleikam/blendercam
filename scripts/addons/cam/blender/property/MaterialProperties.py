from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatProperty, EnumProperty, FloatVectorProperty

from ...utils import *

from ...constants import *

class MaterialProperties(PropertyGroup):

    estimate_from_model: BoolProperty(
        name="Estimate cut area from model",
        description="Estimate cut area based on model geometry",
        default=True,
        update=update_material
    )

    radius_around_model: FloatProperty(
        name='Radius around model',
        description="Increase cut area around the model on X and Y by this amount",
        default=0.0,
        unit='LENGTH',
        precision=PRECISION,
        update=update_material
    )

    center_x: BoolProperty(
        name="Center on X axis",
        description="Position model centered on X",
        default=False,
        update=update_material
    )

    center_y: BoolProperty(
        name="Center on Y axis",
        description="Position model centered on Y",
        default=False,
        update=update_material
    )

    z_position: EnumProperty(
        name="Z placement",
        items=(
            ('ABOVE', 'Above', 'Place object vertically above the XY plane'),
            ('BELOW', 'Below', 'Place object vertically below the XY plane'),
            ('CENTERED', 'Centered', 'Place object vertically centered on the XY plane')),
        description="Position below Zero",
        default='BELOW',
        update=update_material
    )

    # material_origin
    origin: FloatVectorProperty(
        name='Material origin',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=PRECISION,
        subtype="XYZ",
        update=update_material
    )

    # material_size
    size: FloatVectorProperty(
        name='Material size',
        default=(0.200, 0.200, 0.100),
        min=0,
        unit='LENGTH',
        precision=PRECISION,
        subtype="XYZ",
        update=update_material
    )