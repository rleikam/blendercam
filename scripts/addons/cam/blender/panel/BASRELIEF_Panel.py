from bpy.types import Panel
import bpy

class BASRELIEF_Panel(Panel):
	"""Bas relief panel"""
	bl_label = "Bas relief"
	bl_idname = "WORLD_PT_BASRELIEF"

	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

	#def draw_header(self, context):
	#   self.layout.menu("CAM_CUTTER_MT_presets", text="CAM Cutter")
	@classmethod
	def poll(cls, context):
		renderer = context.scene.render
		return renderer.engine in cls.COMPAT_ENGINES

	def draw(self, context):
		layout = self.layout
		#print(dir(layout))
		scene = bpy.context.scene

		settings = scene.basreliefsettings

		#if br:
			#cutter preset
		layout.operator("scene.calculate_bas_relief", text="Calculate relief")
		layout.prop(settings,'advanced')
		layout.prop_search(settings,'source_image_name', bpy.data, "images")
#		layout.prop(br,'output_image_name')
		layout.label(text="Project parameters")
		layout.prop(settings,'bit_diameter')
		layout.prop(settings,'pass_per_radius')
		layout.prop(settings,'widthmm')
		layout.prop(settings,'heightmm')
		layout.prop(settings,'thicknessmm')

		layout.label(text="Justification")
		layout.prop(settings,'justifyx')
		layout.prop(settings,'justifyy')
		layout.prop(settings,'justifyz')

		layout.label(text="Silhouette")
		layout.prop(settings,'silhouette_threshold')
		layout.prop(settings,'recover_silhouettes')
		if settings.recover_silhouettes:
			layout.prop(settings,'silhouette_scale')
			if settings.advanced:
				layout.prop(settings,'silhouette_exponent')
		#layout.template_curve_mapping(br,'curva')
		if settings.advanced:
			#layout.prop(br,'attenuation')
			layout.prop(settings,'min_gridsize')
			layout.prop(settings,'smooth_iterations')
		layout.prop(settings,'vcycle_iterations')
		layout.prop(settings,'linbcg_iterations')
		layout.prop(settings,'use_planar')
		layout.prop(settings,'decimate_ratio')


		layout.prop(settings,'gradient_scaling_mask_use')
		if settings.advanced:
			if settings.gradient_scaling_mask_use:
				layout.prop_search(settings,'gradient_scaling_mask_name', bpy.data, "images")
			layout.prop(settings,'detail_enhancement_use')
			if settings.detail_enhancement_use:
				#layout.prop(br,'detail_enhancement_freq')
				layout.prop(settings,'detail_enhancement_amount')