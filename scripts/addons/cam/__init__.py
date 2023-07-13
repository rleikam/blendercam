# blender CAM __init__.py (c) 2012 Vilem Novak
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

import bpy
import os
import subprocess
import sys
import bpy.utils.previews
from pathlib import PurePath

from .blender.menu import *
from .blender.list import *
from .blender.property import *
from .blender.operation import *
from .blender.preference import *
from .blender.panel import *
from .blender.render_engine import *
from .curvecamtools import *
from .curvecamequation import *
from .curvecamcreate import *
from .ops import *

try:
    import shapely
except ImportError:
    # pip install required python stuff
    subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "shapely","Equation","opencamlib"])

from bpy.props import CollectionProperty, IntProperty, PointerProperty, StringProperty
from mathutils import *

bl_info = {
    "name": "CAM - gcode generation tools",
    "author": "Vilem Novak",
    "version": (0, 9, 3),
    "blender": (2, 80, 0),
    "location": "Properties > render",
    "description": "Generate machining paths for CNC",
    "warning": "there is no warranty for the produced gcode by now",
    "wiki_url": "https://github.com/vilemduha/blendercam/wiki",
    "tracker_url": "",
    "category": "Scene"}

classes = [
    AddonPreference,
    OperationListExpansionsProperties,
    Operations,
    Chains,
    OperationReferenceProperties,
    ChainProperties,
    MachineProperties,
    ImportProperties,
    ExpandOperation,
    ChainsPanel,
    OperationsPanel,
    MaterialProperties,
    PositionOperationObject,
    OptimizationProperties,
    IntarsionProperties,
    InfoProperties,
    InfoPanel,
    IntarsionPanel,
    MachinePanel,
    PackPanel,
    SlicePanel,
    CurveToolsPanel,
    CurveCreatorPanel,
    CustomPanel,
    ImportGCode,
    CalculatePathsInBackground,
    StopPathCalculationsInBackground,
    CalculateOperationPath,
    CalculateChainPaths,
    ExportChainPaths,
    CalculatePathsForAllOperations,
    ExportOperationPath,
    SimulateOperation,
    SimulateChain,
    AddChain,
    RemoveChain,
    AddOperationToChain,
    RemoveOperationFromChain,
    MoveOperationInChain,
	BasReliefProperties,
	BasReliefPanel,
	CalculateBasRelief,
	ProblemAreas,

    AddOperation,
    CopyOperation,
    RemoveOperation,
    MoveOperation,
    AddBridges,
    AddOrientation,
    PackObjects,
    SliceObjects,
    CamCurveBoolean,
    CamCurveConvexHull,
    CamOffsetSilhouete,
    CamObjectSilhouete,
    CamCurveIntarsion,
    CurveToolPathSilhouette,
    CamCurveOvercuts,
    CamCurveOvercutsB,
    CamCurveRemoveDoubles,
    CamMeshGetPockets,

    CamSineCurve,
    CamLissajousCurve,
    CamHypotrochoidCurve,
    CamCustomCurve,

    CamCurveHatch,
    CamCurvePlate,
    CamCurveDrawer,
    CamCurveGear,
    CamCurveFlatCone,
    CamCurveMortise,
    CamCurveInterlock,
    CamCurvePuzzle,

    ToolPresetsMenu,
    OperationPresetsMenu,
    MachinePresetsMenu,
    AddToolPreset,
    AddOperationPreset,
    AddMachinePreset,
    BlenderCAMEngine,
    PackObjectProperties,
    SliceObjectProperties,
    OperationProperties,
]

def loadIcons():
    previewCollection = bpy.utils.previews.new()
    iconDirectory = os.path.join(os.path.dirname(__file__), "icons")

    # load a preview thumbnail of a file and store in the previews collection
    for fileName in os.listdir(iconDirectory):
        path = PurePath(fileName)
        suffixLength = len(path.suffix)
        nameLength = len(fileName)
        nameWithoutSuffix = path.name[: nameLength - suffixLength] 
        previewCollection.load(nameWithoutSuffix, os.path.join(iconDirectory, fileName), 'IMAGE')

    bpy.types.Scene.previewCollection =  previewCollection

def register():
    loadIcons()

    for panels in classes:
        bpy.utils.register_class(panels)

    scene = bpy.types.Scene

    scene.cam_operation_expansions = CollectionProperty(type=OperationListExpansionsProperties)
    scene.cam_chains = CollectionProperty(type=ChainProperties)
    scene.cam_active_chain = IntProperty(name="CAM Active Chain", description="The selected chain")

    scene.cam_operations = CollectionProperty(type=OperationProperties)

    scene.cam_active_operation = IntProperty(name="CAM Active Operation",
                                                description="The selected operation",
                                                update=updateOperation)
    scene.cam_machine = PointerProperty(type=MachineProperties)

    scene.cam_import_gcode = PointerProperty(type=ImportProperties)

    scene.cam_text = StringProperty()
    bpy.app.handlers.frame_change_pre.append(ops.timer_update)
    bpy.app.handlers.load_post.append(check_operations_on_load)

    scene.basreliefsettings = PointerProperty(type=BasReliefProperties)
    scene.cam_pack = PointerProperty(type=PackObjectProperties)

    scene.cam_slice = PointerProperty(type=SliceObjectProperties)

    scene.intarsion = PointerProperty(type=IntarsionProperties)

def unregister():
    for panels in classes:
        bpy.utils.unregister_class(panels)
    scene = bpy.types.Scene

    # cam chains are defined hardly now.
    del scene.cam_chains
    del scene.cam_active_chain
    del scene.cam_operations
    del scene.cam_active_operation
    del scene.cam_machine
    del scene.cam_import_gcode
    del scene.cam_text
    del scene.cam_pack
    del scene.cam_slice
    del scene.basreliefsettings
