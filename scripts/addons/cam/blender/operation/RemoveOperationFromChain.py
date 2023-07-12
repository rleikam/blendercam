from bpy.types import Operator
from bpy.props import IntProperty

class RemoveOperationFromChain(Operator):
    """Remove operation from chain"""
    bl_idname = "scene.cam_chain_operation_remove"
    bl_label = "Remove operation from chain"
    bl_options = {'REGISTER', 'UNDO'}

    chainIndex: IntProperty(name="The chain, where the operation is located.")
    operationIndex: IntProperty(name="The index of the chain that should be removed.")

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene
        chain = scene.cam_chains[self.chainIndex]
        chain.operations.remove(self.operationIndex)

        return {'FINISHED'}