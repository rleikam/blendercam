from scripts.addons.GPack import doGameUV


class GPackUVOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "object.gpack_uv"
	bl_label = "Gravity Pack UVs"

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects)>0

	def execute(self, context):
		doGameUV(context)
		return {'FINISHED'}