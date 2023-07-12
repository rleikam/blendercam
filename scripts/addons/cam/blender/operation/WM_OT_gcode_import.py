from cam import gcodeimportparser
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

class WM_OT_gcode_import(Operator, ImportHelper):
    """Import Gcode, travel lines don't get drawn"""
    bl_idname = "wm.gcode_import"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Gcode"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        print(self.filepath)
        return gcodeimportparser.import_gcode(context, self.filepath)