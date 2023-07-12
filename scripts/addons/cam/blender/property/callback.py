from cam import utils
import bpy

def updateBridges(operation, context):
    print('update bridges ')
    operation.changed = True

def updateRotation(operation, context):
    if operation.enable_B or operation.enable_A:
        print(operation, operation.rotation_A)
        ob = bpy.data.objects[operation.object_name]
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        if operation.A_along_x:  # A parallel with X
            if operation.enable_A:
                bpy.context.active_object.rotation_euler.x = operation.rotation_A
            if operation.enable_B:
                bpy.context.active_object.rotation_euler.y = operation.rotation_B
        else:  # A parallel with Y
            if operation.enable_A:
                bpy.context.active_object.rotation_euler.y = operation.rotation_A
            if operation.enable_B:
                bpy.context.active_object.rotation_euler.x = operation.rotation_B

def updateOpencamlib(operation, context):
    print('update opencamlib ')
    operation.changed = True
    if operation.optimisation.use_opencamlib and (
            operation.strategy == 'POCKET' or operation.strategy == 'MEDIAL_AXIS'):
        operation.optimisation.use_exact = False
        operation.optimisation.use_opencamlib = False
        print('Current operation cannot use opencamlib')

def updateRest(self, context):
    print('update rest ')
    self.changed = True

def updateExact(operation, context):
    print('update exact ')
    operation.changed = True
    operation.update_zbufferimage_tag = True
    operation.update_offsetimage_tag = True
    if operation.optimisation.use_exact:
        if operation.strategy == 'POCKET' or operation.strategy == 'MEDIAL_AXIS' or operation.inverse:
            operation.optimisation.use_opencamlib = False
            print('Current operation cannot use exact mode')
    else:
        operation.optimisation.use_opencamlib = False

def updateCutout(o, context):
    pass

def updateStrategy(operation, context):
    """"""
    operation.changed = True
    print('update strategy')
    if operation.machine_axes == '5' or (
            operation.machine_axes == '4' and operation.strategy4axis == 'INDEXED'):  # INDEXED 4 AXIS DOESN'T EXIST NOW...
        utils.addOrientationObject(operation)
    else:
        utils.removeOrientationObject(operation)
    updateExact(operation, context)

def updateZbufferImage(self, context):
    """changes tags so offset and zbuffer images get updated on calculation time."""
    self.changed = True
    self.update_zbufferimage_tag = True
    self.update_offsetimage_tag = True
    utils.getOperationSources(self)

def updateChipload(self, context):
    """this is very simple computation of chip size, could be very much improved"""
    print('update chipload ')
    operation = self
    # Old chipload
    operation.info.chipload = (operation.feedrate / (operation.spindle_rpm * operation.cutter_flutes))
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
    print(operation.info.chipload)

def updateOffsetImage(self, context):
    """refresh offset image tag for rerendering"""
    updateChipload(self, context)
    print('update offset')
    self.changed = True
    self.update_offsetimage_tag = True

def operationValid(self, context):
    operation = self
    operation.changed = True
    operation.valid = True
    invalidmsg = "Operation has no valid data input\n"
    operation.info.warnings = ""
    operation = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    if operation.geometry_source == 'OBJECT':
        if operation.object_name not in bpy.data.objects:
            operation.valid = False
            operation.info.warnings = invalidmsg

    if operation.geometry_source == 'COLLECTION':
        if operation.collection_name not in bpy.data.collections:
            operation.valid = False
            operation.info.warnings = invalidmsg
        elif len(bpy.data.collections[operation.collection_name].objects) == 0:
            operation.valid = False
            operation.info.warnings = invalidmsg

    if operation.geometry_source == 'IMAGE':
        if operation.source_image_name not in bpy.data.images:
            operation.valid = False
            operation.info.warnings = invalidmsg

        operation.optimisation.use_exact = False
    operation.update_offsetimage_tag = True
    operation.update_zbufferimage_tag = True
    print('validity ')

was_hidden_dict = {}

def updateOperation(self, context):
    scene = context.scene
    activeOperation = scene.cam_operations[scene.cam_active_operation]

    if activeOperation.hide_all_others:
        for _ao in scene.cam_operations:
            if _ao.path_object_name in bpy.data.objects:
                other_obj = bpy.data.objects[_ao.path_object_name]
                current_obj = bpy.data.objects[activeOperation.path_object_name]
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
        ob = bpy.data.objects[activeOperation.path_object_name]
        ob.select_set(state=True, view_layer=None)
        # Show object if, it's was hidden
        if ob.hide:
            ob.hide = False
            was_hidden_dict[activeOperation.path_object_name] = True
        bpy.context.scene.objects.active = ob
    except Exception as e:
        print(e)

def createUniqueOperationName(name: str):
    newOperationName = name
    nameCounter = 1
    operationNames = [operation.name for operation in bpy.context.scene.cam_operations]
    operationsWithSameName = [newOperationName == operationName for operationName in operationNames]

    while any(operationsWithSameName):
        newOperationName = f"{name}.{nameCounter}"
        nameCounter += 1
        operationNames = [operation.name for operation in bpy.context.scene.cam_operations]
        operationsWithSameName = [newOperationName == operationName for operationName in operationNames]

    return newOperationName

def getOperationDuplicates():
    duplicatedOperations = {}
    for index, operation in enumerate(bpy.context.scene.cam_operations):
        if operation.name not in duplicatedOperations:
            duplicatedOperations[operation.name] = [index]
        else:
            duplicatedOperations[operation.name].append(index)

    return duplicatedOperations

def updateOperationName(self, context):
    duplicatedNames = getOperationDuplicates()

    if len(duplicatedNames[self.name]) > 1:
        newOperationName = createUniqueOperationName(self.name)

        self.name = newOperationName
        self.changed = True

def updateOperationValid(self, context):
    operationValid(self, context)
    updateOperation(self, context)

def updateMaterial(self, context):
    print('update material')
    utils.addMaterialAreaObject()

def updateMachine(self, context):
    print('update machine ')
    utils.addMachineAreaObject()

def resolveDuplicatedNameOperations():
    duplicatedOperations = getOperationDuplicates()

    for operationName, operationIndices in duplicatedOperations.items():
        duplicateCount = len(operationIndices)
        if duplicateCount > 1:

            for index in operationIndices[1:]:
                newOperationName = createUniqueOperationName(operationName)
                bpy.context.scene.cam_operations[index].name = newOperationName

def resetOperationComputationsState():
    scene = bpy.context.scene
    for operation in scene.cam_operations:
        if operation.computing:
            operation.computing = False

@bpy.app.handlers.persistent
def check_operations_on_load(context):
    resolveDuplicatedNameOperations()
    resetOperationComputationsState()

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