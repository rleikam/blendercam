from cam import gcodepath, utils
from ...exception import CamException
from bpy.types import Operator
from bpy.props import IntProperty
import bpy

class CalculatePath(Operator):
    """calculate CAM paths"""
    bl_idname = "object.calculate_cam_path"
    bl_label = "Calculate CAM paths"
    bl_options = {'REGISTER', 'UNDO'}

    operationIndex: IntProperty(name="Operation", description="Specify the operation to calculate")

    def execute(self, context):
        scene = bpy.context.scene
        operation = scene.cam_operations[self.operationIndex]
        if operation.geometry_source == 'OBJECT':
            ob = bpy.data.objects[operation.object_name]
            ob.hide_set(False)

        if operation.geometry_source == 'COLLECTION':
            objectCollection = bpy.data.collections[operation.collection_name]
            for ob in objectCollection.objects:
                ob.hide_set(False)

        if operation.strategy == "CARVE":
            curveObject = bpy.data.objects[operation.curve_object]
            curveObject.hide_set(False)

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        camPath = utils.getCAMPathObjectNameConventionFrom(operation.name)
        pathObject = bpy.data.objects.get(camPath)
        if pathObject:
            pathObject.select_set(state=True)
            bpy.ops.object.delete()

        if not operation.valid:
            self.report({'ERROR_INVALID_INPUT'}, "Operation can't be performed, see warnings for info")
            print("Operation can't be performed, see warnings for info")
            return {'CANCELLED'}

        if operation.computing:
            return {'FINISHED'}

        operation.operator = self

        if operation.use_layers:
            operation.parallel_step_back = False

        try:
            gcodepath.getPath(context, operation)
        except CamException as e:
            self.report({'ERROR'},str(e))
            return {'CANCELLED'}
        
        coll = bpy.data.collections.get('RigidBodyWorld')
        if coll:
            bpy.data.collections.remove(coll)

        return {'FINISHED'}