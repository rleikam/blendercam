from cam import utils
import bpy

def updateBridges(o, context):
    print('update bridges ')
    o.changed = True

def updateRotation(o, context):
    if o.enable_B or o.enable_A:
        print(o, o.rotation_A)
        ob = bpy.data.objects[o.object_name]
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        if o.A_along_x:  # A parallel with X
            if o.enable_A:
                bpy.context.active_object.rotation_euler.x = o.rotation_A
            if o.enable_B:
                bpy.context.active_object.rotation_euler.y = o.rotation_B
        else:  # A parallel with Y
            if o.enable_A:
                bpy.context.active_object.rotation_euler.y = o.rotation_A
            if o.enable_B:
                bpy.context.active_object.rotation_euler.x = o.rotation_B

def updateOpencamlib(o, context):
    print('update opencamlib ')
    o.changed = True
    if o.optimisation.use_opencamlib and (
            o.strategy == 'POCKET' or o.strategy == 'MEDIAL_AXIS'):
        o.optimisation.use_exact = False
        o.optimisation.use_opencamlib = False
        print('Current operation cannot use opencamlib')

def updateRest(self, context):
    print('update rest ')
    self.changed = True

def updateExact(o, context):
    print('update exact ')
    o.changed = True
    o.update_zbufferimage_tag = True
    o.update_offsetimage_tag = True
    if o.optimisation.use_exact:
        if o.strategy == 'POCKET' or o.strategy == 'MEDIAL_AXIS' or o.inverse:
            o.optimisation.use_opencamlib = False
            print('Current operation cannot use exact mode')
    else:
        o.optimisation.use_opencamlib = False

def updateCutout(o, context):
    pass

def updateStrategy(o, context):
    """"""
    o.changed = True
    print('update strategy')
    if o.machine_axes == '5' or (
            o.machine_axes == '4' and o.strategy4axis == 'INDEXED'):  # INDEXED 4 AXIS DOESN'T EXIST NOW...
        utils.addOrientationObject(o)
    else:
        utils.removeOrientationObject(o)
    updateExact(o, context)

def updateZbufferImage(self, context):
    """changes tags so offset and zbuffer images get updated on calculation time."""
    # print('updatezbuf')
    # print(self,context)
    self.changed = True
    self.update_zbufferimage_tag = True
    self.update_offsetimage_tag = True
    utils.getOperationSources(self)

def updateChipload(self, context):
    """this is very simple computation of chip size, could be very much improved"""
    print('update chipload ')
    o = self
    # Old chipload
    o.info.chipload = (o.feedrate / (o.spindle_rpm * o.cutter_flutes))
    # New chipload with chip thining compensation.
    # I have tried to combine these 2 formulas to compinsate for the phenomenon of chip thinning when cutting at less
    # than 50% cutter engagement with cylindrical end mills. formula 1 Nominal Chipload is
    # " feedrate mm/minute = spindle rpm x chipload x cutter diameter mm x cutter_flutes "
    # formula 2 (.5*(cutter diameter mm devided by dist_between_paths)) divided by square root of
    # ((cutter diameter mm devided by dist_between_paths)-1) x Nominal Chipload
    # Nominal Chipload = what you find in end mill data sheats recomended chip load at %50 cutter engagment.
    # I am sure there is a better way to do this. I dont get consistent result and
    # I am not sure if there is something wrong with the units going into the formula, my math or my lack of
    # underestanding of python or programming in genereal. Hopefuly some one can have a look at this and with any luck
    # we will be one tiny step on the way to a slightly better chipload calculating function.

    # self.chipload = ((0.5*(o.cutter_diameter/o.dist_between_paths))/(math.sqrt((o.feedrate*1000)/(o.spindle_rpm*o.cutter_diameter*o.cutter_flutes)*(o.cutter_diameter/o.dist_between_paths)-1)))
    print(o.info.chipload)

def updateOffsetImage(self, context):
    """refresh offset image tag for rerendering"""
    updateChipload(self, context)
    print('update offset')
    self.changed = True
    self.update_offsetimage_tag = True

def operationValid(self, context):
    o = self
    o.changed = True
    o.valid = True
    invalidmsg = "Operation has no valid data input\n"
    o.info.warnings = ""
    o = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    if o.geometry_source == 'OBJECT':
        if o.object_name not in bpy.data.objects:
            o.valid = False
            o.info.warnings = invalidmsg
    if o.geometry_source == 'COLLECTION':
        if o.collection_name not in bpy.data.collections:
            o.valid = False
            o.info.warnings = invalidmsg
        elif len(bpy.data.collections[o.collection_name].objects) == 0:
            o.valid = False
            o.info.warnings = invalidmsg

    if o.geometry_source == 'IMAGE':
        if o.source_image_name not in bpy.data.images:
            o.valid = False
            o.info.warnings = invalidmsg

        o.optimisation.use_exact = False
    o.update_offsetimage_tag = True
    o.update_zbufferimage_tag = True
    print('validity ')

was_hidden_dict = {}

def updateOperation(self, context):
    scene = context.scene
    ao = scene.cam_operations[scene.cam_active_operation]

    if ao.hide_all_others:
        for _ao in scene.cam_operations:
            if _ao.path_object_name in bpy.data.objects:
                other_obj = bpy.data.objects[_ao.path_object_name]
                current_obj = bpy.data.objects[ao.path_object_name]
                if other_obj != current_obj:
                    other_obj.hide = True
                    other_obj.select = False
    else:
        for path_obj_name in was_hidden_dict:
            print(was_hidden_dict)
            if was_hidden_dict[path_obj_name]:
                # Find object and make it hidde, then reset 'hidden' flag
                obj = bpy.data.objects[path_obj_name]
                obj.hide = True
                obj.select = False
                was_hidden_dict[path_obj_name] = False

    # try highlighting the object in the 3d view and make it active
    bpy.ops.object.select_all(action='DESELECT')
    # highlight the cutting path if it exists
    try:
        ob = bpy.data.objects[ao.path_object_name]
        ob.select_set(state=True, view_layer=None)
        # Show object if, it's was hidden
        if ob.hide:
            ob.hide = False
            was_hidden_dict[ao.path_object_name] = True
        bpy.context.scene.objects.active = ob
    except Exception as e:
        print(e)

def updateOperationValid(self, context):
    operationValid(self, context)
    updateOperation(self, context)

def updateMaterial(self, context):
    print('update material')
    utils.addMaterialAreaObject()

def updateMachine(self, context):
    print('update machine ')
    utils.addMachineAreaObject()

@bpy.app.handlers.persistent
def check_operations_on_load(context):
    """checks any broken computations on load and reset them."""
    scene = bpy.context.scene
    for operation in scene.cam_operations:

        foundOperationExpansions = (expansion for expansion in scene.cam_operation_expansions if expansion.operationName == operation.name)
        foundOperationExpansion = next(foundOperationExpansions, None)

        if foundOperationExpansion == None:
            newOperationExpansion = scene.cam_operation_expansions.add()
            newOperationExpansion.operationName = operation.name

        if operation.computing:
            operation.computing = False

# Update functions start here
def getStrategyList(scene, context):

    items = [
        ('CUTOUT', 'Profile(Cutout)', 'Cut the silhouete with offset'),
        ('POCKET', 'Pocket', 'Pocket operation'),
        ('DRILL', 'Drill', 'Drill operation'),
        ('PARALLEL', 'Parallel', 'Parallel lines on any angle'),
        ('CROSS', 'Cross', 'Cross paths'),
        ('BLOCK', 'Block', 'Block path'),
        ('SPIRAL', 'Spiral', 'Spiral path'),
        ('CIRCLES', 'Circles', 'Circles path'),
        ('OUTLINEFILL', 'Outline Fill',
         'Detect outline and fill it with paths as pocket. Then sample these paths on the 3d surface'),
        ('CARVE', 'Project curve to surface', 'Engrave the curve path to surface'),
        ('WATERLINE', 'Waterline - Roughing -below zero', 'Waterline paths - constant z below zero'),
        ('CURVE', 'Curve to Path', 'Curve object gets converted directly to path'),
        ('MEDIAL_AXIS', 'Medial axis',
         'Medial axis, must be used with V or ball cutter, for engraving various width shapes with a single stroke ')
    ]
    return items