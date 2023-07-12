from bpy.types import RenderEngine

class BlenderCAMEngine(RenderEngine):
    bl_idname = 'BLENDERCAM_RENDER'
    bl_label = "Cam"