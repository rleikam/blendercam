from bpy.types import Operator
from bpy.props import IntProperty

class AddOperationToChain(Operator):
    """Add operation to chain"""
    bl_idname = "scene.cam_chain_operation_add"
    bl_label = "Add operation to chain"
    bl_options = {'REGISTER', 'UNDO'}

    operationIndex: IntProperty(name="OperationIndex")

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene
        chain = scene.cam_chains[scene.cam_active_chain]

        chainOperation = chain.operations.add()
        chainOperation.name = scene.cam_operations[self.operationIndex].name
        return {'FINISHED'}