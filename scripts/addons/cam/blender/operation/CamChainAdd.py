from bpy.types import Operator
import bpy

class CamChainAdd(Operator):
    """Add new CAM chain"""
    bl_idname = "scene.cam_chain_add"
    bl_label = "Add new CAM chain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # main(context)
        scene = bpy.context.scene
        scene.cam_chains.add()
        chain = scene.cam_chains[-1]
        scene.cam_active_chain = len(scene.cam_chains) - 1
        chain.name = f"Chain_{scene.cam_active_chain + 1}"
        chain.filename = chain.name
        chain.index = scene.cam_active_chain

        return {'FINISHED'}