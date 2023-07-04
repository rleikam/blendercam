from bpy.types import Operator
import bpy

class CamChainOperationAdd(Operator):
    """Add operation to chain"""
    bl_idname = "scene.cam_chain_operation_add"
    bl_label = "Add operation to chain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = bpy.context.scene
        chain = scene.cam_chains[scene.cam_active_chain]
        scene = bpy.context.scene
        chain.operations.add()
        chain.active_operation += 1
        chain.operations[-1].name = scene.cam_operations[scene.cam_active_operation].name
        return {'FINISHED'}