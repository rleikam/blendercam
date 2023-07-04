from scripts.addons.print_3d import PrintSettings, draw_callback_px, threadComPrint3d, threadread_print3d, tweakCuraPreferences


import os
import subprocess
import threading


class Print3d(bpy.types.Operator):
	"""send object to 3d printer"""
	bl_idname = "object.print3d"
	bl_label = "Print object in 3d"
	bl_options = {'REGISTER', 'UNDO'}
	#processes=[]


	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	@staticmethod
	def handle_add(self, context):
		if not(hasattr(PrintSettings,'handle')) or PrintSettings.handle == None:
			PrintSettings.handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
		#bpy.app.handlers.scene_update_pre.append(timer_update_print3d)
		#ScreencastKeysStatus._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
		#ScreencastKeysStatus._timer = context.window_manager.event_timer_add(0.075, context.window)

	@staticmethod
	def handle_remove(context):
		if ScreencastKeysStatus._handle is not None:
			#context.window_manager.event_timer_remove(ScreencastKeysStatus._timer)
			bpy.types.SpaceView3D.draw_handler_remove(PrintSettings._handle, 'WINDOW')
		PrintSettings._handle = None
		#PrintSettings._timer = None

	def execute(self, context):
		Print3d.handle_add(self,context)


		s=bpy.context.scene
		settings=s.print3d_settings
		ob=bpy.context.active_object


		"""
		#this was first try - using the slicer directly.
		if settings.slicer=='CURA':
			fpath=bpy.data.filepath+'_'+ob.name+'.stl'
			gcodepath=bpy.data.filepath+'_'+ob.name+'.gcode'
			enginepath=settings.filepath_engine
			#Export stl, with a scale correcting blenders and Cura size interpretation in stl:
			bpy.ops.export_mesh.stl(check_existing=False, filepath=fpath, filter_glob="*.stl", ascii=False, use_mesh_modifiers=True, axis_forward='Y', axis_up='Z', global_scale=1000)
			#this is Cura help line:
			#CuraEngine [-h] [-v] [-m 3x3matrix] [-s <settingkey>=<value>] -o <output.gcode> <model.stl>
			#we build the command line here:
			commands=[enginepath]
			#add the properties, here add whatever you want exported from cura props, so far it doesn't work. Going with .ini files will be probably better in future:
			unit=1000000#conversion between blender mm unit(0.001 of basic unit) and slicer unit (0.001 mm)
			for name in settings.propnames:
				#print(s)
				commands.append('-s')
				commands.append(name+'='+str(eval('settings.'+name)))
				#commands.extend([key,str(propsdict[key])])
			commands.extend(['-o', gcodepath,fpath])
			print(commands)
			#run cura in background:
			proc = subprocess.Popen(commands,bufsize=1, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
			s=''
			for command in commands:
				s+=(command)+' '
			print(s)
			print('gcode file exported:')
			print(gcodepath)
		"""
		#second try - use cura command line options, with .ini files.
		if settings.slicer=='CURA':

			opath=bpy.data.filepath[:-6]
			fpath=opath+'_'+ob.name+'.stl'
			gcodepath=opath+'_'+ob.name+'.gcode'
			enginepath=settings.dirpath_engine
			inipath=settings.preset
			tweakCuraPreferences(enginepath,settings.printer)
			#return {'FINISHED'}
			#Export stl, with a scale correcting blenders and Cura size interpretation in stl:
			bpy.ops.export_mesh.stl(check_existing=False, filepath=fpath, filter_glob="*.stl", ascii=False, use_mesh_modifiers=True, axis_forward='Y', axis_up='Z', global_scale=1000)

			#this is Cura help line:
			#CuraEngine [-h] [-v] [-m 3x3matrix] [-s <settingkey>=<value>] -o <output.gcode> <model.stl>

			#we build the command line here:
			#commands=[enginepath+'python\python.exe,']#,'-m', 'Cura.cura', '%*']
			os.chdir(settings.dirpath_engine)
			#print('\n\n\n')

			#print(os.listdir())
			commands=['python\\python.exe','-m', 'Cura.cura','-i',inipath, '-s', fpath]
			#commands=[enginepath+'cura.bat', '-s', fpath]

			#commands.extend()#'-o', gcodepath,

			#print(commands)
			#print('\n\n\n')

			s=''
			for command in commands:
				s+=(command)+' '
			#print(s)


			#run cura in background:
			#proc = subprocess.call(commands,bufsize=1, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
			#print(proc)
			proc= subprocess.Popen(commands,bufsize=1, stdout=subprocess.PIPE,stdin=subprocess.PIPE)#,env={"PATH": enginepath})
			#print(proc)
			tcom=threadComPrint3d(ob,proc)
			readthread=threading.Thread(target=threadread_print3d, args = ([tcom]), daemon=True)
			readthread.start()
			#self.__class__.print3d_processes=[]
			if not hasattr(bpy.ops.object.print3d.__class__,'print3d_processes'):
				bpy.ops.object.print3d.__class__.print3d_processes=[]
			bpy.ops.object.print3d.__class__.print3d_processes.append([readthread,tcom])

			#print('gcode file exported:')
			#print(gcodepath)

		return {'FINISHED'}