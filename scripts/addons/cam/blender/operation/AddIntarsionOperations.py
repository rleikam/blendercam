from bpy.types import Operator
from ..property.IntarsionProperties import *
from ..property.ChainProperties import *
from ..property.OperationProperties import *
from ..property.OperationReferenceProperties import *

class AddIntarsionOperations(Operator):
    bl_idname = "scene.cam_intarsion_operations"
    bl_label = "Create intarsion operations"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def createPocketChain(self, context):
        intarsionProperties: IntarsionProperties = context.scene.intarsion
        operations = context.scene.cam_operations
        chains = context.scene.cam_chains

        """
        ----- POCKET CHAIN -----
        """
        pocketChain: ChainProperties = chains.add()
        pocketChainName = f"Pocket_{intarsionProperties.operationObjectName}"
        pocketChain.name = pocketChainName
        pocketChain.filename = pocketChainName

        """
        ----- POCKET CLEARING -----
        """
        pocketClearingOperation: OperationProperties = operations.add()
        pocketClearingOperationName = f"PocketClearing_{intarsionProperties.operationObjectName}"
        pocketClearingOperation.name = pocketClearingOperationName
        pocketClearingOperation.filename = pocketClearingOperationName

        pocketClearingOperation.strategy = "POCKET"
        pocketClearingOperation.cutter_type = "END"
        pocketClearingOperation.cutter_id = 1
        pocketClearingOperation.cutter_diameter = intarsionProperties.clearingCutterDiameter
        pocketClearingOperation.dist_between_paths = intarsionProperties.clearingCutterDistanceBetweenToolPaths

        pocketClearingOperation.use_layers = False
        pocketClearingOperation.minz_from_ob = False
        pocketClearingOperation.minz = -intarsionProperties.pocketDepth

        pocketClearingOperationInChain: OperationReferenceProperties = pocketChain.operations.add()
        pocketClearingOperationInChain.name = pocketClearingOperation.name

        """
        ----- POCKET CORNER CLEARING -----
        """
        pocketCornerClearingOperation: OperationProperties = operations.add()
        pocketCornerClearingOperationName = f"PocketCornerClearing_{intarsionProperties.operationObjectName}"
        pocketCornerClearingOperation.name = pocketCornerClearingOperationName
        pocketCornerClearingOperation.filename = pocketCornerClearingOperationName

        pocketCornerClearingOperation.strategy = "POCKET"
        pocketCornerClearingOperation.ignoreRadiusCompensation = True
        pocketCornerClearingOperation.cutter_type = "END"
        pocketCornerClearingOperation.cutter_id = 2
        pocketCornerClearingOperation.cutter_diameter = intarsionProperties.ballRadius*2
        pocketCornerClearingOperation.dist_between_paths = intarsionProperties.carvingCutterDistanceBetweenToolpaths

        pocketCornerClearingOperation.use_layers = False
        pocketCornerClearingOperation.minz_from_ob = False
        pocketCornerClearingOperation.minz = -intarsionProperties.pocketDepth

        pocketCornerClearingOperationInChain: OperationReferenceProperties = pocketChain.operations.add()
        pocketCornerClearingOperationInChain.name = pocketCornerClearingOperation.name

        """
        ----- POCKET CARVING -----
        """
        pocketCarvingOperation: OperationProperties = operations.add()
        pocketCarvingOperationName = f"PocketCarving_{intarsionProperties.operationObjectName}"
        pocketCarvingOperation.name = pocketCarvingOperationName
        pocketCarvingOperation.filename = pocketCarvingOperationName
        pocketCarvingOperation.object_name = intarsionProperties.operationObjectName

        pocketCarvingOperation.strategy = "MEDIAL_AXIS"
        pocketCarvingOperation.cutter_type = intarsionProperties.carvingCutterType
        pocketCarvingOperation.cutter_id = 2
        pocketCarvingOperation.cutter_diameter = intarsionProperties.carvingCutterDiameter
        pocketCarvingOperation.ball_radius = intarsionProperties.ballRadius
        pocketCarvingOperation.cutter_tip_angle = intarsionProperties.angle

        pocketCarvingOperation.use_layers = False
        pocketCarvingOperation.minz_from_ob = False
        pocketCarvingOperation.minz = -intarsionProperties.pocketDepth

        pocketCarvingOperationInChain: OperationReferenceProperties = pocketChain.operations.add()
        pocketCarvingOperationInChain.name = pocketCarvingOperation.name

    def createInlayChain(self, context):
        intarsionProperties: IntarsionProperties = context.scene.intarsion
        operations = context.scene.cam_operations
        chains = context.scene.cam_chains

        """
        ----- INLAY CHAIN -----
        """
        inlayChain: ChainProperties = chains.add()
        inlayChainName = f"Inlay_{intarsionProperties.operationObjectName}"
        inlayChain.name = inlayChainName
        inlayChain.filename = inlayChainName

        """
        ----- INLAY CLEARING -----
        """
        inlayClearingOperation: OperationProperties = operations.add()
        inlayClearingOperationName = f"InlayClearing_{intarsionProperties.operationObjectName}"
        inlayClearingOperation.name = inlayClearingOperationName
        inlayClearingOperation.filename = inlayClearingOperationName

        inlayClearingOperation.strategy = "POCKET"
        inlayClearingOperation.cutter_type = "END"
        inlayClearingOperation.cutter_id = 1
        inlayClearingOperation.cutter_diameter = intarsionProperties.clearingCutterDiameter
        inlayClearingOperation.dist_between_paths = intarsionProperties.clearingCutterDistanceBetweenToolPaths

        inlayClearingOperation.use_layers = False
        inlayClearingOperation.minz_from_ob = False
        inlayClearingOperation.minz = -intarsionProperties.pocketDepth

        inlayClearingOperationInChain: OperationReferenceProperties = inlayChain.operations.add()
        inlayClearingOperationInChain.name = inlayClearingOperation.name

        """
        ----- INLAY CORNER CLEARING -----
        """
        inlayCornerClearingOperation: OperationProperties = operations.add()
        inlayCornerClearingOperationName = f"InlayCornerClearing_{intarsionProperties.operationObjectName}"
        inlayCornerClearingOperation.name = inlayCornerClearingOperationName
        inlayCornerClearingOperation.filename = inlayCornerClearingOperationName

        inlayCornerClearingOperation.strategy = "POCKET"
        inlayCornerClearingOperation.ignoreRadiusCompensation = True
        inlayCornerClearingOperation.cutter_type = "END"
        inlayCornerClearingOperation.cutter_id = 2
        inlayCornerClearingOperation.cutter_diameter = intarsionProperties.ballRadius*2
        inlayCornerClearingOperation.dist_between_paths = intarsionProperties.carvingCutterDistanceBetweenToolpaths

        inlayCornerClearingOperation.use_layers = False
        inlayCornerClearingOperation.minz_from_ob = False
        inlayCornerClearingOperation.minz = -intarsionProperties.pocketDepth

        inlayCornerClearingOperationInChain: OperationReferenceProperties = inlayChain.operations.add()
        inlayCornerClearingOperationInChain.name = inlayCornerClearingOperation.name

        """
        ----- INLAY CARVING -----
        """
        inlayCarvingOperation: OperationProperties = operations.add()
        inlayCarvingOperationName = f"InlayCarving_{intarsionProperties.operationObjectName}"
        inlayCarvingOperation.name = inlayCarvingOperationName
        inlayCarvingOperation.filename = inlayCarvingOperationName

        inlayCarvingOperation.strategy = "CUTOUT"
        inlayCarvingOperation.cut_type = "ONLINE"
        inlayCarvingOperation.cutter_type = intarsionProperties.carvingCutterType
        inlayCarvingOperation.cutter_id = 2
        inlayCarvingOperation.cutter_diameter = intarsionProperties.ballRadius*2
        inlayCarvingOperation.dist_between_paths = intarsionProperties.carvingCutterDistanceBetweenToolpaths

        inlayCarvingOperation.use_layers = False
        inlayCarvingOperation.minz_from_ob = False
        inlayCarvingOperation.minz = -intarsionProperties.pocketDepth

        inlayCarvingOperationInChain: OperationReferenceProperties = inlayChain.operations.add()
        inlayCarvingOperationInChain.name = inlayCarvingOperation.name

        """
        ----- INLAY CUTOUT -----
        """
        inlayCutoutOperation: OperationProperties = operations.add()
        inlayCutoutOperationName = f"InlayCutout_{intarsionProperties.operationObjectName}"
        inlayCutoutOperation.name = inlayCutoutOperationName
        inlayCutoutOperation.filename = inlayCutoutOperationName

        inlayCarvingOperation.strategy = "CUTOUT"
        inlayCarvingOperation.cut_type = "OUTSIDE"
        inlayCarvingOperation.cutter_type = "END"
        inlayCarvingOperation.cutter_id = 3
        inlayCarvingOperation.cutter_diameter = intarsionProperties.cutoutCutterDiameter

        inlayCarvingOperation.use_layers = False
        inlayCarvingOperation.minz_from_ob = False
        inlayCarvingOperation.minz = -intarsionProperties.inlayMaterialDepth

        inlayCutoutOperationInChain: OperationReferenceProperties = inlayChain.operations.add()
        inlayCutoutOperationInChain.name = inlayCutoutOperation.name

    def createFinishChain(self, context):
        intarsionProperties: IntarsionProperties = context.scene.intarsion
        operations = context.scene.cam_operations
        chains = context.scene.cam_chains

        """
        ----- FINISH CHAIN -----
        """
        finishChain: ChainProperties = chains.add()
        finishChainName = f"Finish_{intarsionProperties.operationObjectName}"
        finishChain.name = finishChainName
        finishChain.filename = finishChainName

        """
        ----- FINISH CLEARING -----
        """
        finishClearingOperation: OperationProperties = operations.add()
        finishClearingOperationName = f"FinishClearing_{intarsionProperties.operationObjectName}"
        finishClearingOperation.name = finishClearingOperationName
        finishClearingOperation.filename = finishClearingOperationName

        finishClearingOperation.strategy = "POCKET"
        finishClearingOperation.cutter_type = "END"
        finishClearingOperation.cutter_id = 1
        finishClearingOperation.cutter_diameter = intarsionProperties.finishCutterDiameter
        finishClearingOperation.dist_between_paths = intarsionProperties.finishCutterDistanceBetweenToolPaths

        finishClearingOperation.use_layers = False
        finishClearingOperation.minz_from_ob = False
        finishClearingOperation.minz = -0.000001

        finishClearingOperationInChain: OperationReferenceProperties = finishChain.operations.add()
        finishClearingOperationInChain.name = finishClearingOperation.name

    def execute(self, context):
        
        self.createPocketChain(context)
        self.createInlayChain(context)
        self.createFinishChain(context)
        
        return {'FINISHED'}