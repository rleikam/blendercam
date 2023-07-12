from ..operation.CalculateChainPaths import CalculateChainPaths
from ..operation.ExportChainPaths import ExportChainPaths
from ..operation.SimulateChain import SimulateChain
from ..operation.RemoveChain import RemoveChain
from ..operation.MoveOperationInChain import MoveOperationInChain
from ..operation.RemoveOperationFromChain import RemoveOperationFromChain

from bpy.types import UIList

class Chains(UIList):
    bl_idname = "CAM_UL_chains"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        column = layout.column(align=True)

        chainRow = column.row(align=True)
        nameIconID = context.scene.previewCollection["name"].icon_id
        chainRow.prop(item, "name", text="", icon_value=nameIconID, emboss=False)
        chainRow.prop(item, "filename", icon="FILE", text="", emboss=False)

        if not item.computing:
            if item.valid:
                chainRow = layout.row(align=True)
                millIconId = context.scene.previewCollection["millPath"].icon_id
                calculateChainPathButton = chainRow.operator(CalculateChainPaths.bl_idname, text="", icon_value=millIconId, emboss=False)
                calculateChainPathButton.operationIndex = index

                millPathSimulationId = context.scene.previewCollection["millSimulation"].icon_id
                exportPathId = context.scene.previewCollection["exportGCode"].icon_id
                chainRow.operator(SimulateChain.bl_idname, text="", icon_value=millPathSimulationId, emboss=False)
                chainRow.operator(ExportChainPaths.bl_idname, text="", icon_value=exportPathId, emboss=False)
            else:
                chainRow.label(text="chain invalid, can't compute")

        chainRow.operator(RemoveChain.bl_idname, icon='REMOVE', text="", emboss=False).chainToRemove = index

        # Draw operations
        for operationIndex, operation in enumerate(item.operations):
            operationName = operation.name
            operationRow = column.split(factor=0.02)
            operationRow.label(text="   ")
            operationRow = operationRow.row(align=True)

            for operation in context.scene.cam_operations:
                if operation.name == operationName:
                    operationRow.label(text=operation.name)

                    upOperator = operationRow.operator(MoveOperationInChain.bl_idname, icon='TRIA_UP', text="", emboss=False)
                    upOperator.direction = "UP"
                    upOperator.chainIndex = index
                    upOperator.operationIndex = operationIndex

                    downOperator = operationRow.operator(MoveOperationInChain.bl_idname, icon='TRIA_DOWN', text="", emboss=False)
                    downOperator.direction = "DOWN"
                    downOperator.chainIndex = index
                    downOperator.operationIndex = operationIndex

                    camChainOperationRemoveOperator = operationRow.operator(RemoveOperationFromChain.bl_idname, icon='REMOVE', text="", emboss=False)
                    camChainOperationRemoveOperator.chainIndex = index
                    camChainOperationRemoveOperator.operationIndex = operationIndex