from ..operation.PathsChain import PathsChain
from ..operation.PathExportChain import PathExportChain
from ..operation.CAMSimulateChain import CAMSimulateChain
from ..operation.CamChainRemove import CamChainRemove
from ..operation.CamChainOperationMove import CamChainOperationMove
from ..operation.CamChainOperationRemove import CamChainOperationRemove

from bpy.types import UIList

class CAMULChains(UIList):
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
                chainRow.operator(PathsChain.bl_idname, text="", icon_value=millIconId, emboss=False).operationIndex = index

                millPathSimulationId = context.scene.previewCollection["millSimulation"].icon_id
                exportPathId = context.scene.previewCollection["exportGCode"].icon_id
                chainRow.operator(CAMSimulateChain.bl_idname, text="", icon_value=millPathSimulationId, emboss=False)
                chainRow.operator(PathExportChain.bl_idname, text="", icon_value=exportPathId, emboss=False)
            else:
                chainRow.label(text="chain invalid, can't compute")

        chainRow.operator(CamChainRemove.bl_idname, icon='REMOVE', text="", emboss=False).chainToRemove = index

        # Draw operations
        for operationIndex, operation in enumerate(item.operations):
            operationName = operation.name
            operationRow = column.split(factor=0.02)
            operationRow.label(text="   ")
            operationRow = operationRow.row(align=True)

            for operation in context.scene.cam_operations:
                if operation.name == operationName:
                    operationRow.label(text=operation.name)

                    upOperator = operationRow.operator(CamChainOperationMove.bl_idname, icon='TRIA_UP', text="", emboss=False)
                    upOperator.direction = "UP"
                    upOperator.chainIndex = index
                    upOperator.operationIndex = operationIndex

                    downOperator = operationRow.operator(CamChainOperationMove.bl_idname, icon='TRIA_DOWN', text="", emboss=False)
                    downOperator.direction = "DOWN"
                    downOperator.chainIndex = index
                    downOperator.operationIndex = operationIndex

                    camChainOperationRemoveOperator = operationRow.operator(CamChainOperationRemove.bl_idname, icon='REMOVE', text="", emboss=False)
                    camChainOperationRemoveOperator.chainIndex = index
                    camChainOperationRemoveOperator.operationIndex = operationIndex