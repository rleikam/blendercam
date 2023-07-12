import bpy, math
from ..property.CAMInfoProperties import CAMInfoProperties
from ..property.CAMMaterialProperties import CAMMaterialProperties
from ..property.CAMOptimizationProperties import CAMOptimizationProperties
from ..property.OperationListExpansions import OperationListExpansions

from bpy.props import BoolProperty, FloatProperty, StringProperty, IntProperty, EnumProperty, PointerProperty, FloatVectorProperty

from ...constants import *

import numpy
from shapely import geometry as sgeometry

import math

from .callback import operationValid, updateBridges, updateChipload, \
    updateCutout, updateOffsetImage, updateOperationValid, \
    updateRest, updateStrategy, updateZbufferImage, \
    getStrategyList, updateOperationName

class CamOperation(bpy.types.PropertyGroup):
    material: PointerProperty(type=CAMMaterialProperties)
    info: PointerProperty(type=CAMInfoProperties)
    optimisation: PointerProperty(type=CAMOptimizationProperties)
    expansion: PointerProperty(type=OperationListExpansions)

    name: StringProperty(name="Operation Name", default="Operation", update=updateOperationName)
    filename: StringProperty(name="File name", default="Operation", subtype="FILE_PATH", update=updateRest)
    auto_export: BoolProperty(name="Auto export",
                                        description="export files immediately after path calculation", default=True)
    remove_redundant_points: BoolProperty(
        name="Symplify Gcode",
        description="Remove redundant points sharing the same angle"
                    " as the start vector",
        default=False)
    simplify_tol: IntProperty(name="Tolerance", description='lower number means more precise', default=50,
                                        min=1, max=1000)
    hide_all_others: BoolProperty(
        name="Hide all others",
        description="Hide all other tool pathes except toolpath"
                    " assotiated with selected CAM operation",
        default=False)
    parent_path_to_object: BoolProperty(
        name="Parent path to object",
        description="Parent generated CAM path to source object",
        default=False)
    object_name: StringProperty(name='Object', description='object handled by this operation',
                                          update=updateOperationValid)
    collection_name: StringProperty(name='Collection',
                                              description='Object collection handled by this operation',
                                              update=updateOperationValid)
    curve_object: StringProperty(name='Curve source',
                                           description='curve which will be sampled along the 3d object',
                                           update=operationValid)
    curve_object1: StringProperty(name='Curve target',
                                            description='curve which will serve as attractor for the cutter when the cutter follows the curve',
                                            update=operationValid)
    source_image_name: StringProperty(name='image_source', description='image source', update=operationValid)
    geometry_source: EnumProperty(name='Source of data',
                                  items=(
                                      ('OBJECT', 'object', 'a'), ('COLLECTION', 'Collection of objects', 'a'),
                                      ('IMAGE', 'Image', 'a')),
                                  description='Geometry source',
                                  default='OBJECT', update=updateOperationValid)
    cutter_typeb: EnumProperty(name='Cutter',
                              items=(
                                  ('END', 'End', 'end - flat cutter'),
                                  ('BALLNOSE', 'Ballnose', 'ballnose cutter'),
                                  ('BULLNOSE', 'Bullnose', 'bullnose cutter ***placeholder **'),
                                  ('VCARVE', 'V-carve', 'v carve cutter'),
                                  ('BALLCONE', 'Ballcone', 'Ball with a Cone for Parallel - X'),
                                  ('CYLCONE', 'Cylinder cone', 'Cylinder end with a Cone for Parallel - X'),
                                  ('LASER', 'Laser', 'Laser cutter'),
                                  ('PLASMA', 'Plasma', 'Plasma cutter'),
                                  ('CUSTOM', 'Custom-EXPERIMENTAL', 'modelled cutter - not well tested yet.')),
                              description='Type of cutter used',
                              default='END', update=updateZbufferImage)

    cutter_type: EnumProperty(
        name='Cutter',
        items=(
            ('END', 'End', 'end - flat cutter'),
            ('BALLNOSE', 'Ballnose', 'ballnose cutter'),
            ('BULLNOSE', 'Bullnose', 'bullnose cutter ***placeholder **'),
            ('VCARVE', 'V-carve', 'v carve cutter'),
            ('BALLCONE', 'Ballcone', 'Ball with a Cone for Parallel - X'),
            ('CYLCONE', 'Cylinder cone', 'Cylinder end with a Cone for Parallel - X'),
            ('LASER', 'Laser', 'Laser cutter'),
            ('PLASMA', 'Plasma', 'Plasma cutter'),
            ('CUSTOM', 'Custom-EXPERIMENTAL', 'modelled cutter - not well tested yet.')
        ),
        description='Type of cutter used',
        default='END',
        update=updateZbufferImage)
    
    cutter_object_name: StringProperty(name='Cutter object',
                                                 description='object used as custom cutter for this operation',
                                                 update=updateZbufferImage)

    machine_axes: EnumProperty(name='Number of axes',
                               items=(
                                   ('3', '3 axis', 'a'),
                                   ('4', '#4 axis - EXPERIMENTAL', 'a'),
                                   ('5', '#5 axis - EXPERIMENTAL', 'a')),
                               description='How many axes will be used for the operation',
                               default='3', update=updateStrategy)
    strategy: EnumProperty(name='Strategy',
                           items=getStrategyList,
                           description='Strategy',
                           update=updateStrategy)

    strategy4axis: EnumProperty(name='4 axis Strategy',
                                items=(
                                    ('PARALLELR', 'Parallel around 1st rotary axis',
                                     'Parallel lines around first rotary axis'),
                                    ('PARALLEL', 'Parallel along 1st rotary axis',
                                     'Parallel lines along first rotary axis'),
                                    ('HELIX', 'Helix around 1st rotary axis', 'Helix around rotary axis'),
                                    ('INDEXED', 'Indexed 3-axis',
                                     'all 3 axis strategies, just applied to the 4th axis'),
                                    ('CROSS', 'Cross', 'Cross paths')),
                                description='#Strategy',
                                default='PARALLEL',
                                update=updateStrategy)
    strategy5axis: EnumProperty(name='Strategy',
                                items=(
                                    ('INDEXED', 'Indexed 3-axis', 'all 3 axis strategies, just rotated by 4+5th axes'),
                                ),
                                description='5 axis Strategy',
                                default='INDEXED',
                                update=updateStrategy)

    rotary_axis_1: EnumProperty(name='Rotary axis',
                                items=(
                                    ('X', 'X', ''),
                                    ('Y', 'Y', ''),
                                    ('Z', 'Z', ''),
                                ),
                                description='Around which axis rotates the first rotary axis',
                                default='X',
                                update=updateStrategy)
    rotary_axis_2: EnumProperty(name='Rotary axis 2',
                                items=(
                                    ('X', 'X', ''),
                                    ('Y', 'Y', ''),
                                    ('Z', 'Z', ''),
                                ),
                                description='Around which axis rotates the second rotary axis',
                                default='Z',
                                update=updateStrategy)

    skin: FloatProperty(name="Skin", description="Material to leave when roughing ", min=0.0, max=1.0, default=0.0,
                        precision=PRECISION, unit="LENGTH", update=updateOffsetImage)
    inverse: BoolProperty(name="Inverse milling", description="Male to female model conversion",
                                    default=False, update=updateOffsetImage)
    array: BoolProperty(name="Use array",
                                  description="Create a repetitive array for producing the same thing manytimes",
                                  default=False, update=updateRest)
    array_x_count: IntProperty(name="X count", description="X count", default=1, min=1, max=32000,
                                         update=updateRest)
    array_y_count: IntProperty(name="Y count", description="Y count", default=1, min=1, max=32000,
                                         update=updateRest)
    array_x_distance: FloatProperty(name="X distance", description="distance between operation origins", min=0.00001,
                                    max=1.0, default=0.01, precision=PRECISION, unit="LENGTH", update=updateRest)
    array_y_distance: FloatProperty(name="Y distance", description="distance between operation origins", min=0.00001,
                                    max=1.0, default=0.01, precision=PRECISION, unit="LENGTH", update=updateRest)

    # pocket options
    pocket_option: EnumProperty(name='Start Position', items=(
        ('INSIDE', 'Inside', 'a'), ('OUTSIDE', 'Outside', 'a')),
                                description='Pocket starting position', default='INSIDE', update=updateRest)
    pocketToCurve: BoolProperty(name="Pocket to curve",
                                          description="generates a curve instead of a path",
                                          default=False, update=updateRest)

    ignoreRadiusCompensation: BoolProperty(
        name="Inline cutting",
        description="Cut additional on the silhouette",
        default=False,
        update=updateRest)

    # Cutout
    cut_type: EnumProperty(name='Cut',
                           items=(('OUTSIDE', 'Outside', 'a'), ('INSIDE', 'Inside', 'a'), ('ONLINE', 'On line', 'a')),
                           description='Type of cutter used', default='OUTSIDE', update=updateRest)
    outlines_count: IntProperty(name="Outlines count`EXPERIMENTAL", description="Outlines count", default=1,
                                          min=1, max=32, update=updateCutout)
    straight: BoolProperty(name="Overshoot Style",
                                     description="Use overshoot cutout instead of conventional rounded",
                                     default=False, update=updateRest)
    # cutter
    cutter_id: IntProperty(name="Tool number", description="For machines which support tool change based on tool id",
                           min=0, max=10000, default=1, update=updateRest)
    cutter_diameter: FloatProperty(name="Cutter diameter", description="Cutter diameter = 2x cutter radius",
                                   min=0.000001, max=10, default=0.003, precision=PRECISION, unit="LENGTH",
                                   update=updateOffsetImage)
    cylcone_diameter: FloatProperty(name="Bottom Diameter", description="Bottom diameter",
                                    min=0.000001, max=10, default=0.003, precision=PRECISION, unit="LENGTH",
                                    update=updateOffsetImage)
    cutter_length: FloatProperty(name="#Cutter length", description="#not supported#Cutter length", min=0.0, max=100.0,
                                 default=25.0, precision=PRECISION, unit="LENGTH", update=updateOffsetImage)
    cutter_flutes: IntProperty(name="Cutter flutes", description="Cutter flutes", min=1, max=20, default=2,
                               update=updateChipload)
    cutter_tip_angle: FloatProperty(name="Cutter v-carve angle", description="Cutter v-carve angle", min=0.0,
                                    max=180.0, default=60.0, precision=PRECISION, update=updateOffsetImage)
    ball_radius: FloatProperty(name="Ball radius", description="Radius of", min=0.0,
                               max=0.035, default=0.001, unit="LENGTH", precision=PRECISION, update=updateOffsetImage)
    # ball_cone_flute: FloatProperty(name="BallCone Flute Length", description="length of flute", min=0.0,
    #                                 max=0.1, default=0.017, unit="LENGTH", precision=cam.constants.PRECISION, update=updateOffsetImage)
    bull_corner_radius: FloatProperty(name="Bull Corner Radius", description="Radius tool bit corner", min=0.0,
                                      max=0.035, default=0.005, unit="LENGTH", precision=PRECISION,
                                      update=updateOffsetImage)

    cutter_description: StringProperty(name="Tool Description", default="", update=updateOffsetImage)

    Laser_on: StringProperty(name="Laser ON string", default="M68 E0 Q100")
    Laser_off: StringProperty(name="Laser OFF string", default="M68 E0 Q0")
    Laser_cmd: StringProperty(name="Laser command", default="M68 E0 Q")
    Laser_delay: FloatProperty(name="Laser ON Delay",
                                         description="time after fast move to turn on laser and let machine stabilize",
                                         default=0.2)
    Plasma_on: StringProperty(name="Plasma ON string", default="M03")
    Plasma_off: StringProperty(name="Plasma OFF string", default="M05")
    Plasma_delay: FloatProperty(name="Plasma ON Delay",
                                          description="time after fast move to turn on Plasma and let machine stabilize",
                                          default=0.1)
    Plasma_dwell: FloatProperty(name="Plasma dwell time", description="Time to dwell and warm up the torch",
                                          default=0.0)

    # steps
    dist_between_paths: FloatProperty(name="Distance between toolpaths", default=0.001, min=0.00001, max=32,
                                                precision=PRECISION, unit="LENGTH", update=updateRest)
    dist_along_paths: FloatProperty(name="Distance along toolpaths", default=0.0002, min=0.00001, max=32,
                                              precision=PRECISION, unit="LENGTH", update=updateRest)
    parallel_angle: FloatProperty(name="Angle of paths", default=0, min=-360, max=360, precision=0,
                                            subtype="ANGLE", unit="ROTATION", update=updateRest)
    old_rotation_A: FloatProperty(name="A axis angle",
                                            description="old value of Rotate A axis\nto specified angle", default=0,
                                            min=-360, max=360, precision=0, subtype="ANGLE", unit="ROTATION",
                                            update=updateRest)

    old_rotation_B: FloatProperty(name="A axis angle",
                                            description="old value of Rotate A axis\nto specified angle", default=0,
                                            min=-360, max=360, precision=0, subtype="ANGLE", unit="ROTATION",
                                            update=updateRest)

    rotation_A: FloatProperty(name="A axis angle", description="Rotate A axis\nto specified angle", default=0,
                                        min=-360, max=360, precision=0,
                                        subtype="ANGLE", unit="ROTATION", update=updateRest)
    enable_A: BoolProperty(name="Enable A axis", description="Rotate A axis", default=False,
                                     update=updateRest)
    A_along_x: BoolProperty(name="A Along X ", description="A Parallel to X", default=True, update=updateRest)

    rotation_B: FloatProperty(name="B axis angle", description="Rotate B axis\nto specified angle", default=0,
                                        min=-360, max=360, precision=0,
                                        subtype="ANGLE", unit="ROTATION", update=updateRest)
    enable_B: BoolProperty(name="Enable B axis", description="Rotate B axis", default=False,
                                     update=updateRest)

    # carve only
    carve_depth: FloatProperty(name="Carve depth", default=0.001, min=-.100, max=32, precision=PRECISION,
                                         unit="LENGTH", update=updateRest)

    # drill only
    drill_type: EnumProperty(name='Holes on', items=(
        ('MIDDLE_SYMETRIC', 'Middle of symetric curves', 'a'), ('MIDDLE_ALL', 'Middle of all curve parts', 'a'),
        ('ALL_POINTS', 'All points in curve', 'a')), description='Strategy to detect holes to drill',
                             default='MIDDLE_SYMETRIC', update=updateRest)
    # waterline only
    slice_detail: FloatProperty(name="Distance betwen slices", default=0.001, min=0.00001, max=32,
                                          precision=PRECISION, unit="LENGTH", update=updateRest)
    waterline_fill: BoolProperty(name="Fill areas between slices",
                                           description="Fill areas between slices in waterline mode", default=True,
                                           update=updateRest)
    waterline_project: BoolProperty(name="Project paths - not recomended",
                                              description="Project paths in areas between slices", default=True,
                                              update=updateRest)

    # movement and ramps
    use_layers: BoolProperty(name="Use Layers", description="Use layers for roughing", default=True,
                                       update=updateRest)
    stepdown: FloatProperty(name="", description="Layer height", default=0.01, min=0.00001, max=32, precision=PRECISION,
                                      unit="LENGTH", update=updateRest)
    first_down: BoolProperty(name="First down",
                                       description="First go down on a contour, then go to the next one",
                                       default=False, update=updateRest)
    ramp: BoolProperty(name="Ramp in - EXPERIMENTAL",
                                 description="Ramps down the whole contour, so the cutline looks like helix",
                                 default=False, update=updateRest)
    ramp_out: BoolProperty(name="Ramp out - EXPERIMENTAL",
                                     description="Ramp out to not leave mark on surface", default=False,
                                     update=updateRest)
    ramp_in_angle: FloatProperty(name="Ramp in angle", default=math.pi / 6, min=0, max=math.pi * 0.4999,
                                           precision=1, subtype="ANGLE", unit="ROTATION", update=updateRest)
    ramp_out_angle: FloatProperty(name="Ramp out angle", default=math.pi / 6, min=0, max=math.pi * 0.4999,
                                            precision=1, subtype="ANGLE", unit="ROTATION", update=updateRest)
    helix_enter: BoolProperty(name="Helix enter - EXPERIMENTAL", description="Enter material in helix",
                                        default=False, update=updateRest)
    lead_in: FloatProperty(name="Lead in radius",
                                     description="Lead out radius for torch or laser to turn off",
                                     min=0.00, max=1, default=0.0, precision=PRECISION, unit="LENGTH")
    lead_out: FloatProperty(name="Lead out radius",
                                      description="Lead out radius for torch or laser to turn off",
                                      min=0.00, max=1, default=0.0, precision=PRECISION, unit="LENGTH")
    profile_start: IntProperty(name="Start point", description="Start point offset", min=0, default=0,
                                         update=updateRest)

    # helix_angle: FloatProperty(name="Helix ramp angle", default=3*math.pi/180, min=0.00001, max=math.pi*0.4999,precision=1, subtype="ANGLE" , unit="ROTATION" , update = updateRest)
    helix_diameter: FloatProperty(name='Helix diameter % of cutter D', default=90, min=10, max=100,
                                            precision=1, subtype='PERCENTAGE', update=updateRest)
    retract_tangential: BoolProperty(name="Retract tangential - EXPERIMENTAL",
                                               description="Retract from material in circular motion", default=False,
                                               update=updateRest)
    retract_radius: FloatProperty(name='Retract arc radius', default=0.001, min=0.000001, max=100,
                                            precision=PRECISION, unit="LENGTH", update=updateRest)
    retract_height: FloatProperty(name='Retract arc height', default=0.001, min=0.00000, max=100,
                                            precision=PRECISION, unit="LENGTH", update=updateRest)

    minz_from_ob: BoolProperty(name="Depth from object", description="Operation ending depth from object",
                                         default=True, update=updateRest)
    minz_from_material: BoolProperty(name="Depth from material",
                                               description="Operation ending depth from material",
                                               default=False, update=updateRest)
    minz: FloatProperty(name="Operation depth end", default=-0.01, min=-3, max=3, precision=PRECISION,
                                  unit="LENGTH",
                                  update=updateRest)  # this is input minz. True minimum z can be something else, depending on material e.t.c.
    start_type: EnumProperty(name='Start type',
                                       items=(
                                           ('ZLEVEL', 'Z level', 'Starts on a given Z level'),
                                           ('OPERATIONRESULT', 'Rest milling',
                                            'For rest milling, operations have to be put in chain for this to work well.'),
                                       ),
                                       description='Starting depth',
                                       default='ZLEVEL',
                                       update=updateStrategy)

    maxz: FloatProperty(name="Operation depth start", description='operation starting depth', default=0,
                                  min=-3, max=10, precision=PRECISION, unit="LENGTH",
                                  update=updateRest)  # EXPERIMENTAL

    #######################################################
    # Image related
    ####################################################

    source_image_scale_z: FloatProperty(name="Image source depth scale", default=0.01, min=-1, max=1,
                                                  precision=PRECISION, unit="LENGTH", update=updateZbufferImage)
    source_image_size_x: FloatProperty(name="Image source x size", default=0.1, min=-10, max=10,
                                                 precision=PRECISION, unit="LENGTH", update=updateZbufferImage)
    source_image_offset: FloatVectorProperty(name='Image offset', default=(0, 0, 0), unit='LENGTH',
                                                       precision=PRECISION, subtype="XYZ", update=updateZbufferImage)
    source_image_crop: BoolProperty(name="Crop source image",
                                              description="Crop source image - the position of the sub-rectangle is relative to the whole image, so it can be used for e.g. finishing just a part of an image",
                                              default=False, update=updateZbufferImage)
    source_image_crop_start_x: FloatProperty(name='crop start x', default=0, min=0, max=100,
                                                       precision=PRECISION, subtype='PERCENTAGE',
                                                       update=updateZbufferImage)
    source_image_crop_start_y: FloatProperty(name='crop start y', default=0, min=0, max=100,
                                                       precision=PRECISION, subtype='PERCENTAGE',
                                                       update=updateZbufferImage)
    source_image_crop_end_x: FloatProperty(name='crop end x', default=100, min=0, max=100,
                                                     precision=PRECISION, subtype='PERCENTAGE',
                                                     update=updateZbufferImage)
    source_image_crop_end_y: FloatProperty(name='crop end y', default=100, min=0, max=100,
                                                     precision=PRECISION, subtype='PERCENTAGE',
                                                     update=updateZbufferImage)

    #########################################################
    # Toolpath and area related
    #####################################################

    protect_vertical: BoolProperty(name="Protect vertical",
                                             description="The path goes only vertically next to steep areas",
                                             default=True)
    protect_vertical_limit: FloatProperty(name="Verticality limit",
                                                    description="What angle is allready considered vertical",
                                                    default=math.pi / 45, min=0, max=math.pi * 0.5, precision=0,
                                                    subtype="ANGLE", unit="ROTATION", update=updateRest)

    ambient_behaviour: EnumProperty(name='Ambient', items=(('ALL', 'All', 'a'), ('AROUND', 'Around', 'a')),
                                    description='handling ambient surfaces', default='ALL', update=updateZbufferImage)

    ambient_radius: FloatProperty(name="Ambient radius",
                                  description="Radius around the part which will be milled if ambient is set to Around",
                                  min=0.0, max=100.0, default=0.01, precision=PRECISION, unit="LENGTH",
                                  update=updateRest)
    # ambient_cutter = EnumProperty(name='Borders',items=(('EXTRAFORCUTTER', 'Extra for cutter', "Extra space for cutter is cut around the segment"),('ONBORDER', "Cutter on edge", "Cutter goes exactly on edge of ambient with it's middle") ,('INSIDE', "Inside segment", 'Cutter stays within segment')	 ),description='handling of ambient and cutter size',default='INSIDE')
    use_limit_curve: BoolProperty(name="Use limit curve", description="A curve limits the operation area",
                                            default=False, update=updateRest)
    ambient_cutter_restrict: BoolProperty(name="Cutter stays in ambient limits",
                                                    description="Cutter doesn't get out from ambient limits otherwise goes on the border exactly",
                                                    default=True,
                                                    update=updateRest)  # restricts cutter inside ambient only
    limit_curve: StringProperty(name='Limit curve',
                                          description='curve used to limit the area of the operation',
                                          update=updateRest)

    # feeds
    feedrate: FloatProperty(name="Feedrate", description="Feedrate", min=0.00005, max=50.0, default=1.0,
                            precision=PRECISION, unit="LENGTH", update=updateChipload)
    plunge_feedrate: FloatProperty(name="Plunge speed ", description="% of feedrate", min=0.1, max=100.0, default=50.0,
                                   precision=1, subtype='PERCENTAGE', update=updateRest)
    plunge_angle: FloatProperty(name="Plunge angle",
                                          description="What angle is allready considered to plunge",
                                          default=math.pi / 6, min=0, max=math.pi * 0.5, precision=0, subtype="ANGLE",
                                          unit="ROTATION", update=updateRest)
    spindle_rpm: FloatProperty(name="Spindle rpm", description="Spindle speed ", min=0, max=60000, default=12000,
                               update=updateChipload)
    # movement parallel_step_back
    movement_type: EnumProperty(name='Movement type', items=(
        ('CONVENTIONAL', 'Conventional / Up milling', 'cutter rotates against the direction of the feed'),
        ('CLIMB', 'Climb / Down milling', 'cutter rotates with the direction of the feed'),
        ('MEANDER', 'Meander / Zig Zag', 'cutting is done both with and against the rotation of the spindle')),
                                description='movement type', default='CLIMB', update=updateRest)
    spindle_rotation_direction: EnumProperty(name='Spindle rotation',
                                             items=(('CW', 'Clock wise', 'a'), ('CCW', 'Counter clock wise', 'a')),
                                             description='Spindle rotation direction', default='CW', update=updateRest)
    free_movement_height: FloatProperty(name="Free movement height", default=0.01, min=0.0000, max=32,
                                                  precision=PRECISION, unit="LENGTH", update=updateRest)
    useG64: BoolProperty(name="G64 trajectory",
                                   description='Use only if your machie supports G64 code.  LinuxCNC and Mach3 do',
                                   default=False, update=updateRest)
    G64: FloatProperty(name="Path Control Mode with Optional Tolerance", default=0.0001, min=0.0000,
                                 max=0.005,
                                 precision=PRECISION, unit="LENGTH", update=updateRest)
    movement_insideout: EnumProperty(name='Direction',
                                     items=(('INSIDEOUT', 'Inside out', 'a'), ('OUTSIDEIN', 'Outside in', 'a')),
                                     description='approach to the piece', default='INSIDEOUT', update=updateRest)
    parallel_step_back: BoolProperty(name="Parallel step back",
                                               description='For roughing and finishing in one pass: mills material in climb mode, then steps back and goes between 2 last chunks back',
                                               default=False, update=updateRest)
    stay_low: BoolProperty(name="Stay low if possible", default=True, update=updateRest)
    merge_dist: FloatProperty(name="Merge distance - EXPERIMENTAL", default=0.0, min=0.0000, max=0.1,
                                        precision=PRECISION, unit="LENGTH", update=updateRest)
    # optimization and performance

    do_simulation_feedrate: BoolProperty(name="Adjust feedrates with simulation EXPERIMENTAL",
                                                   description="Adjust feedrates with simulation", default=False,
                                                   update=updateRest)

    dont_merge: BoolProperty(name="Dont merge outlines when cutting",
                                       description="this is usefull when you want to cut around everything",
                                       default=False, update=updateRest)

    pencil_threshold: FloatProperty(name="Pencil threshold", default=0.00002, min=0.00000001, max=1,
                                              precision=PRECISION, unit="LENGTH", update=updateRest)
    crazy_threshold1: FloatProperty(name="min engagement", default=0.02, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    crazy_threshold5: FloatProperty(name="optimal engagement", default=0.3, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    crazy_threshold2: FloatProperty(name="max engagement", default=0.5, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    crazy_threshold3: FloatProperty(name="max angle", default=2, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    crazy_threshold4: FloatProperty(name="test angle step", default=0.05, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    # Add pocket operation to medial axis
    add_pocket_for_medial: BoolProperty(name="Add pocket operation",
                                                  description="clean unremoved material after medial axis",
                                                  default=True,
                                                  update=updateRest)

    add_mesh_for_medial: BoolProperty(name="Add Medial mesh",
                                                description="Medial operation returns mesh for editing and further processing",
                                                default=False,
                                                update=updateRest)
    ####
    medial_axis_threshold: FloatProperty(
        name="Long vector threshold",
        default=0.001,
        min=0.00000001,
        max=100,
        precision=PRECISION,
        unit="LENGTH",
        update=updateRest)
    
    medial_axis_subdivision: FloatProperty(
        name="Fine subdivision",
        default=0.0002,
        min=0.00000001,
        max=100,
        precision=PRECISION,
        unit="LENGTH",
        update=updateRest)
    
    overwriteCurveResolution: BoolProperty(
        name="Overwrite Curve Resolution",
        description="Temporarily overwrites the curve resolution (computed points in U direction of curves) of the objects in the operation with the given value",
        default=False,
        update=updateRest)
    
    temporaryCurveResolutionIsLowerThreshold: BoolProperty(
        name="Apply only to curves under the resolution",
        description="Overwrite only for resolutions under the given value, so that curves with lower resolution are set to the given value and curves with higher resolution are unaffected",
        default=False,
        update=updateRest)
    
    temporaryCurveResolution: IntProperty(
        name="Temporary Curve U-Resolution",
        description="The temporary curve resolution that should be set",
        default=12,
        min=1,
        max=128,
        update=updateRest)

    # bridges
    use_bridges: BoolProperty(name="Use bridges", description="Use bridges in cutout", default=False,
                                        update=updateBridges)
    bridges_width: FloatProperty(name='Width of bridges', default=0.002, unit='LENGTH', precision=PRECISION,
                                           update=updateBridges)
    bridges_height: FloatProperty(name='Height of bridges',
                                            description="Height from the bottom of the cutting operation",
                                            default=0.0005, unit='LENGTH', precision=PRECISION, update=updateBridges)
    bridges_collection_name: StringProperty(name='Bridges Collection',
                                                      description='Collection of curves used as bridges',
                                                      update=operationValid)
    use_bridge_modifiers: BoolProperty(name="Use bridge modifiers",
                                       description="Include bridge curve modifiers using render level when calculating operation, does not effect original bridge data",
                                       default=True, update=updateBridges)

    # commented this - auto bridges will be generated, but not as a setting of the operation
    # bridges_placement = EnumProperty(name='Bridge placement',
    #     items=(
    #         ('AUTO','Automatic', 'Automatic bridges with a set distance'),
    #         ('MANUAL','Manual', 'Manual placement of bridges'),
    #         ),
    #     description='Bridge placement',
    #     default='AUTO',
    #     update = updateStrategy)
    #
    # bridges_per_curve = IntProperty(name="minimum bridges per curve", description="", default=4, min=1, max=512, update = updateBridges)
    # bridges_max_distance = FloatProperty(name = 'Maximum distance between bridges', default=0.08, unit='LENGTH', precision=cam.constants.PRECISION, update = updateBridges)

    use_modifiers: BoolProperty(name="use mesh modifiers",
                                description="include mesh modifiers using render level when calculating operation, does not effect original mesh",
                                default=True, update=operationValid)
    # optimisation panel

    # material settings






##############################################################################
    # MATERIAL SETTINGS

    min: FloatVectorProperty(
        name='Operation minimum', default=(0, 0, 0), unit='LENGTH', precision=PRECISION,
                                       subtype="XYZ")
    max: FloatVectorProperty(name='Operation maximum', default=(0, 0, 0), unit='LENGTH', precision=PRECISION,
                                       subtype="XYZ")


    # g-code options for operation
    output_header: BoolProperty(name="output g-code header",
                                description="output user defined g-code command header at start of operation",
                                default=False)

    gcode_header: StringProperty(name="g-code header",
                                 description="g-code commands at start of operation. Use ; for line breaks",
                                 default="G53 G0")

    enable_dust: BoolProperty(name="Dust collector",
                                description="output user defined g-code command header at start of operation",
                                default=False)

    gcode_start_dust_cmd: StringProperty(name="Start dust collector",
                                 description="commands to start dust collection. Use ; for line breaks",
                                 default="M100")

    gcode_stop_dust_cmd: StringProperty(name="Stop dust collector",
                                 description="command to stop dust collection. Use ; for line breaks",
                                 default="M101")

    enable_hold: BoolProperty(name="Hold down",
                              description="output hold down command at start of operation",
                              default=False)

    gcode_start_hold_cmd: StringProperty(name="g-code header",
                                         description="g-code commands at start of operation. Use ; for line breaks",
                                         default="M102")

    gcode_stop_hold_cmd: StringProperty(name="g-code header",
                                        description="g-code commands at end operation. Use ; for line breaks",
                                        default="M103")

    enable_mist: BoolProperty(name="Mist",
                              description="Mist command at start of operation",
                              default=False)

    gcode_start_mist_cmd: StringProperty(name="g-code header",
                                         description="g-code commands at start of operation. Use ; for line breaks",
                                         default="M104")

    gcode_stop_mist_cmd: StringProperty(name="g-code header",
                                        description="g-code commands at end operation. Use ; for line breaks",
                                        default="M105")

    output_trailer: BoolProperty(name="output g-code trailer",
                                 description="output user defined g-code command trailer at end of operation",
                                 default=False)

    gcode_trailer: StringProperty(name="g-code trailer",
                                  description="g-code commands at end of operation. Use ; for line breaks",
                                  default="M02")

    # internal properties
    ###########################################

    # testing = IntProperty(name="developer testing ", description="This is just for script authors for help in coding, keep 0", default=0, min=0, max=512)
    offset_image = numpy.array([], dtype=float)
    zbuffer_image = numpy.array([], dtype=float)

    silhouete = sgeometry.Polygon()
    ambient = sgeometry.Polygon()
    operation_limit = sgeometry.Polygon()
    borderwidth = 50
    object = None
    path_object_name: StringProperty(name='Path object', description='actual cnc path')

    # update and tags and related

    changed: BoolProperty(name="True if any of the operation settings has changed",
                                    description="mark for update", default=False)
    update_zbufferimage_tag: BoolProperty(name="mark zbuffer image for update",
                                                    description="mark for update", default=True)
    update_offsetimage_tag: BoolProperty(name="mark offset image for update", description="mark for update",
                                                   default=True)
    update_silhouete_tag: BoolProperty(name="mark silhouete image for update", description="mark for update",
                                                 default=True)
    update_ambient_tag: BoolProperty(name="mark ambient polygon for update", description="mark for update",
                                               default=True)
    update_bullet_collision_tag: BoolProperty(name="mark bullet collisionworld for update",
                                                        description="mark for update", default=True)

    valid: BoolProperty(name="Valid", description="True if operation is ok for calculation", default=True);
    changedata: StringProperty(name='changedata', description='change data for checking if stuff changed.')

    # process related data

    computing: BoolProperty(name="Computing right now", description="", default=False)
    pid: IntProperty(name="process id", description="Background process id", default=-1)
    outtext: StringProperty(name='outtext', description='outtext', default='')