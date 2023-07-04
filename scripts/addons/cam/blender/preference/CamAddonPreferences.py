from bpy.types import AddonPreferences
from bpy.props import BoolProperty

class CamAddonPreferences(AddonPreferences):
    bl_idname = "cam"

    experimental: BoolProperty(
        name="Show experimental features",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Use experimental features when you want to help development of Blender CAM:")

        layout.prop(self, "experimental")