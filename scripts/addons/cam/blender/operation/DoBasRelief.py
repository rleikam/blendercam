from ...basrelief import relief, renderScene
from bpy.types import Operator
import bpy

class DoBasRelief(Operator):
	"""calculate Bas relief"""
	bl_idname = "scene.calculate_bas_relief"
	bl_label = "calculate Bas relief"
	bl_options = {'REGISTER', 'UNDO'}

	processes=[]

	def execute(self, context):
		scene = bpy.context.scene
		settings = scene.basreliefsettings

		renderScene(settings.widthmm, settings.heightmm, settings.bit_diameter, settings.pass_per_radius)

		relief(settings)
		return {'FINISHED'}