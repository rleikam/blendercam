from ...basrelief import problemAreas
from bpy.types import Operator

class ProblemAreas(Operator):
	"""find Bas relief Problem areas"""
	bl_idname = "scene.problemareas_bas_relief"
	bl_label = "problem areas Bas relief"
	bl_options = {'REGISTER', 'UNDO'}

	processes=[]

	def execute(self, context):
		scene = context.scene
		settings = scene.basreliefsettings
		problemAreas(settings)
		return {'FINISHED'}