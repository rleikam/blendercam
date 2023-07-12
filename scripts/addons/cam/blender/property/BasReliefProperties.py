from ...basrelief import PRECISION

from bpy.types import PropertyGroup
from bpy.props import StringProperty, FloatProperty, IntProperty, EnumProperty, BoolProperty

class BasReliefProperties(PropertyGroup):
    source_image_name: StringProperty(
        name='Image source',
        description='image source'
    )

    bit_diameter: FloatProperty(
        name="Diameter of ball end in mm",
        description="Diameter of bit which will be used for carving",
        min=0.01,
        max=50.0,
        default=3.175,
        precision=PRECISION
    
	)
    pass_per_radius: IntProperty(
        name="Passes per radius",
        description="Amount of passes per radius\n(more passes, more mesh precision)",
        default=2,
        min=1,
        max=10
    )

    widthmm: IntProperty(
        name="Desired width in mm",
        default=200,
        min=5,
        max=4000
    )
    
    heightmm: IntProperty(
        name="Desired height in mm",
        default=150,
        min=5,
        max=4000
    )
    
    thicknessmm: IntProperty(
        name="Thickness in mm",
        default=15,
        min=5,
        max=100
    )

    justifyx: EnumProperty(
        name="X",
        items=[
            ('1', 'Left', '', 0),
            ('-0.5', 'Centered', '', 1),
            ('-1', 'Right', '', 2)
        ],
        default='-1')
    
    justifyy: EnumProperty(
        name="Y",
        items=[
            ('1', 'Bottom', '', 0),
            ('-0.5', 'Centered', '', 2),
            ('-1', 'Top', '', 1)
        ],
        default='-1'
    )
    
    justifyz: EnumProperty(
        name="Z",
        items=[
            ('-1', 'Below 0', '', 0),
            ('-0.5', 'Centered', '', 2),
            ('1', 'Above 0', '', 1)
        ],
        default='-1')

    silhouette_threshold: FloatProperty(
        name="Silhouette threshold",
        description="Silhouette threshold",
        min=0.000001,
        max=1.0,
        default=0.003,
        precision=PRECISION
    
	)
    recover_silhouettes: BoolProperty(
        name="Recover silhouettes",
        description="",
        default=True
    )
    
    silhouette_scale: FloatProperty(
        name="Silhouette scale",
        description="Silhouette scale",
        min=0.000001,
        max=5.0,
        default=0.3,
        precision=PRECISION
    )
    
    silhouette_exponent: IntProperty(
        name="Silhouette square exponent",
        description="If lower, true depht distances between objects will be more visibe in the relief",
        default=3,
        min=0,
        max=5
    )
    
    attenuation: FloatProperty(
        name="Gradient attenuation",
        description="Gradient attenuation",
        min=0.000001,
        max=100.0,
        default=1.0,
        precision=PRECISION
    )
    
    min_gridsize: IntProperty(
        name="Minimum grid size",
        default=16,
        min=2,
        max=512
    )
    
    smooth_iterations: IntProperty(
        name="Smooth iterations",
        default=1,
        min=1,
        max=64
    )
    
    vcycle_iterations: IntProperty(
        name="V-cycle iterations",
        description="set up higher for plananr constraint",
        default=2,
        min=1,
        max=128
    )
    
    linbcg_iterations: IntProperty(
        name="Linbcg iterations",
        description="set lower for flatter relief, and when using planar constraint",
        default=5,
        min=1,
        max=64
    )
    
    use_planar: BoolProperty(
        name="Use planar constraint",
        description="",
        default=False
    )
    
    gradient_scaling_mask_use: BoolProperty(
        name="Scale gradients with mask",
        description="",
        default=False
    )
    
    decimate_ratio: FloatProperty(
        name="Decimate Ratio",
        description="Simplify the mesh using the Decimate modifier.  The lower the value the more simplyfied",
        min=0.01,
        max=1.0, 
        default=0.1,
        precision=PRECISION
    )

    gradient_scaling_mask_name: StringProperty(
        name='Scaling mask name',
        description='mask name'
    )
    
    scale_down_before_use: BoolProperty(
        name="Scale down image before processing",
        description="",
        default=False
    )
    
    scale_down_before: FloatProperty(
        name="Image scale",
        description="Image scale",
        min=0.025,
        max=1.0,
        default=.5,
        precision=PRECISION
    )
    
    detail_enhancement_use: BoolProperty(
        name="Enhance details ",
        description="enhance details by frequency analysis",
        default=False
    )

    detail_enhancement_amount: FloatProperty(
        name="amount",
        description="Image scale",
        min=0.025,
        max=1.0,
        default=.5,
        precision=PRECISION
    )

    advanced: BoolProperty(
        name="Advanced options",
        description="show advanced options",
        default=True
    )
