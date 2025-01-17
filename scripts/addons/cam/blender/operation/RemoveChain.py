from bpy.types import Operator
from bpy.props import IntProperty

class RemoveChain(Operator):
    """Remove  CAM chain"""
    bl_idname = "scene.cam_chain_remove"
    bl_label = "Remove CAM chain"
    bl_options = {'REGISTER', 'UNDO'}

    chainToRemove: IntProperty(name="The index of the chain that should be removed.")

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        context.scene.cam_chains.remove(self.chainToRemove)
        
        if context.scene.cam_active_chain > 0:
            context.scene.cam_active_chain -= 1

        return {'FINISHED'}