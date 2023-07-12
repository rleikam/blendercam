from ...constants import *
from ...utils import *
from bpy.props import BoolProperty, FloatProperty, IntProperty
from bpy.types import PropertyGroup

class OptimizationProperties(PropertyGroup):

    optimize: BoolProperty(
        name="Reduce path points",
        description="Reduce path points", 
        default=True,
        update=update_operation
    )

    optimize_threshold: FloatProperty(
        name="Reduction threshold in μm",
        default=.2,
        min=0.000000001,
        max=1000,
        precision=20,
        update=update_operation
    )

    use_exact: BoolProperty(
        name="Use exact mode",
        description="Exact mode allows greater precision, but is slower with complex meshes",
        default=True, update=update_exact_mode
    )

    imgres_limit: IntProperty(
        name="Maximum resolution in megapixels",
        default=16,
        min=1,
        max=512,
        description="Limits total memory usage and prevents crashes. Increase it if you know what are doing",
        update=update_zbuffer_image
    )

    pixsize: FloatProperty(
        name="sampling raster detail",
        default=0.0001,
        min=0.00001,
        max=0.1,
        precision=PRECISION,
        unit="LENGTH",
        update=update_zbuffer_image
    )

    use_opencamlib: BoolProperty(
        name="Use OpenCAMLib",
        description="Use OpenCAMLib to sample paths or get waterline shape",
        default=False,
        update=update_opencamlib
    )

    exact_subdivide_edges: BoolProperty(
        name="Auto subdivide long edges",
        description="This can avoid some collision issues when importing CAD models",
        default=False,
        update=update_exact_mode
    )

    circle_detail: IntProperty(
        name="Detail of circles used for curve offsets",
        default=64,
        min=12,
        max=512,
        update=update_operation
    )

    simulation_detail: FloatProperty(
        name="Simulation sampling raster detail",
        default=0.0002,
        min=0.00001,
        max=0.01,
        precision=PRECISION,
        unit="LENGTH",
        update=update_operation
    )