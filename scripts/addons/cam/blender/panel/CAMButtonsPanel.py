import bpy

# Panel definitions
class CAMButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    always_show_panel = True

    @classmethod
    def poll(cls, context):
        renderer = bpy.context.scene.render
        if renderer.engine in cls.COMPAT_ENGINES:
            if cls.always_show_panel:
                return True
        return False

    def __init__(self):
        self.use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

