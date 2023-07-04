from scripts.addons.GPack import doGameObs


class GPackCurvesOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "object.gpack"
	bl_label = "Gravity Pack Curves"

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects)>0

	def execute(self, context):
		doGameObs(context)
		return {'FINISHED'}