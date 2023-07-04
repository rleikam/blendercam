# blender CAM gcodepath.py (c) 2012 Vilem Novak
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# here is the Gcode generaton

import bpy
import time
import mathutils
import math
from math import *
from mathutils import *
from bpy.props import *

import cam.strategy

import numpy

from cam.chunk import *

from cam.collision import *

from cam import simple
from cam.simple import *

from cam import bridges
from cam.bridges import *

from cam import utils
from cam import strategy

from cam import pattern
from cam.pattern import *

from cam import polygon_utils_cam
from cam.polygon_utils_cam import *

from cam import image_utils
from cam.image_utils import *
from cam.opencamlib.opencamlib import *
from cam.nc import iso

def pointonline(a, b, c, tolerence):
    b = b - a  # convert to vector by subtracting origin
    c = c - a
    dot_pr = b.dot(c)  # b dot c
    norms = numpy.linalg.norm(b) * numpy.linalg.norm(c)  # find norms
    angle = (numpy.rad2deg(numpy.arccos(dot_pr / norms)))  # find angle between the two vectors
    if angle > tolerence:
        return False
    else:
        return True


def exportGcodePath(filename, verticeList, operations):
    """exports gcode with the heeks nc adopted library."""
    print("EXPORT")
    progress('exporting gcode file')
    expiredTime = time.process_time()
    scene = bpy.context.scene
    camMachine = scene.cam_machine
    enable_dust = False
    enable_hold = False
    enable_mist = False
    # find out how many files will be done:

    split = False

    totops = 0
    findex = 0
    if camMachine.eval_splitting:  # detect whether splitting will happen
        for mesh in verticeList:
            totops += len(mesh.vertices)
        print(totops)
        if totops > camMachine.split_limit:
            split = True
            filesnum = ceil(totops / camMachine.split_limit)
            print('file will be separated into %i files' % filesnum)


    basefilename = bpy.data.filepath[:-len(bpy.path.basename(bpy.data.filepath))] + safeFileName(filename)

    extension = '.tap'
    match camMachine.post_processor:
        case "ISO":
            from .nc import iso as postprocessor
        case "MACH3":
            from .nc import mach3 as postprocessor
        case "EMC":
            extension = '.ngc'
            from .nc import emc2b as postprocessor
        case "FADAL":
            extension = '.tap'
            from .nc import fadal as postprocessor
        case "GRBL":
            extension = '.gcode'
            from .nc import grbl as postprocessor
        case "HM50":
            from .nc import hm50 as postprocessor
        case "HEIDENHAIN":
            extension = '.H'
            from .nc import heiden as postprocessor
        case "HEIDENHAIN530":
            extension = '.H'
            from .nc import heiden530 as postprocessor
        case "TNC151":
            from .nc import tnc151 as postprocessor
        case "SIEGKX1":
            from .nc import siegkx1 as postprocessor
        case "CENTROID":
            from .nc import centroid1 as postprocessor
        case "ANILAM":
            from .nc import anilam_crusader_m as postprocessor
        case "GRAVOS":
            extension = '.nc'
            from .nc import gravos as postprocessor
        case "WIN-PC":
            extension = '.din'
            from .nc import winpc as postprocessor
        case "SHOPBOT MTC":
            extension = '.sbp'
            from .nc import shopbot_mtc as postprocessor
        case "LYNX_OTTER_O":
            extension = '.nc'
            from .nc import lynx_otter_o as postprocessor

    match scene.unit_settings.system:
        case "METRIC":
            unitcorr = 1000.0
        case "IMPERIAL":
            unitcorr = 1 / 0.0254
        case _:
            unitcorr = 1

    rotcorr = 180.0 / pi

    use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

    def startNewFile():
        fileindex = ''
        if split:
            fileindex = '_' + str(findex)
        filename = basefilename + fileindex + extension
        c = postprocessor.Creator()

        # process user overrides for post processor settings

        if use_experimental and isinstance(c, iso.Creator):
            c.output_block_numbers = camMachine.output_block_numbers
            c.start_block_number = camMachine.start_block_number
            c.block_number_increment = camMachine.block_number_increment

        c.output_tool_definitions = camMachine.output_tool_definitions
        c.output_tool_change = camMachine.output_tool_change
        c.output_g43_on_tool_change_line = camMachine.output_g43_on_tool_change

        c.file_open(filename)

        # unit system correction
        ###############
        if scene.unit_settings.system == 'METRIC':
            c.metric()
        elif scene.unit_settings.system == 'IMPERIAL':
            c.imperial()

        # start program
        c.program_begin(0, filename)
        c.flush_nc()
        c.comment('G-code generated with BlenderCAM and NC library')
        # absolute coordinates
        c.absolute()

        # work-plane, by now always xy,
        c.set_plane(0)
        c.flush_nc()

        return c

    c = startNewFile()
    last_cutter = None  # [o.cutter_id,o.cutter_dameter,o.cutter_type,o.cutter_flutes]

    processedops = 0
    last = Vector((0, 0, 0))

    duration = 0.0
    for i, operation in enumerate(operations):

        if use_experimental and operation.output_header:
            lines = operation.gcode_header.split(';')
            for aline in lines:
                c.write(aline + '\n')

        free_movement_height = operation.free_movement_height  # o.max.z+
        if operation.useG64:
            c.set_path_control_mode(2, round(operation.G64 * 1000, 5), 0)

        mesh = verticeList[i]
        verts = mesh.vertices[:]
        if operation.machine_axes != '3':
            rots = mesh.shape_keys.key_blocks['rotations'].data

        # spindle rpm and direction
        ###############
        if operation.spindle_rotation_direction == 'CW':
            spdir_clockwise = True
        else:
            spdir_clockwise = False

        # write tool, not working yet probably
        # print (last_cutter)
        if camMachine.output_tool_change and last_cutter != [operation.cutter_id, operation.cutter_diameter, operation.cutter_type, operation.cutter_flutes]:
            if camMachine.output_tool_change:
                c.tool_change(operation.cutter_id)

        if camMachine.output_tool_definitions:
            c.comment('Tool: D = %s type %s flutes %s' % (
                strInUnits(operation.cutter_diameter, 4), operation.cutter_type, operation.cutter_flutes))

        c.flush_nc()

        last_cutter = [operation.cutter_id, operation.cutter_diameter, operation.cutter_type, operation.cutter_flutes]
        if operation.cutter_type not in ['LASER', 'PLASMA']:
            if operation.enable_hold:
                c.write('(Hold Down)\n')
                lines = operation.gcode_start_hold_cmd.split(';')
                for aline in lines:
                    c.write(aline + '\n')
                enable_hold = True
                stop_hold = operation.gcode_stop_hold_cmd
            if operation.enable_mist:
                c.write('(Mist)\n')
                lines = operation.gcode_start_mist_cmd.split(';')
                for aline in lines:
                    c.write(aline + '\n')
                enable_mist = True
                stop_mist = operation.gcode_stop_mist_cmd

            c.spindle(operation.spindle_rpm, spdir_clockwise)  # start spindle
            c.write_spindle()
            c.flush_nc()
            c.write('\n')

            if operation.enable_dust:
                c.write('(Dust collector)\n')
                lines = operation.gcode_start_dust_cmd.split(';')
                for aline in lines:
                    c.write(aline + '\n')
                enable_dust = True
                stop_dust = operation.gcode_stop_dust_cmd

        if camMachine.spindle_start_time > 0:
            c.dwell(camMachine.spindle_start_time)

        #        c.rapid(z=free_movement_height*1000)  #raise the spindle to safe height
        fmh = round(free_movement_height * unitcorr, 2)
        if operation.cutter_type not in ['LASER', 'PLASMA']:
            c.write('G00 Z' + str(fmh) + '\n')
        if operation.enable_A:
            if operation.rotation_A == 0:
                operation.rotation_A = 0.0001
            c.rapid(a=operation.rotation_A * 180 / math.pi)

        if operation.enable_B:
            if operation.rotation_B == 0:
                operation.rotation_B = 0.0001
            c.rapid(a=operation.rotation_B * 180 / math.pi)

        c.write('\n')
        c.flush_nc()

        # dhull c.feedrate(unitcorr*o.feedrate)

        # commands=[]
        camMachine = bpy.context.scene.cam_machine

        millfeedrate = min(operation.feedrate, camMachine.feedrate_max)

        millfeedrate = unitcorr * max(millfeedrate, camMachine.feedrate_min)
        plungefeedrate = millfeedrate * operation.plunge_feedrate / 100
        freefeedrate = camMachine.feedrate_max * unitcorr
        fadjust = False
        if operation.do_simulation_feedrate and mesh.shape_keys is not None \
                and mesh.shape_keys.key_blocks.find('feedrates') != -1:
            shapek = mesh.shape_keys.key_blocks['feedrates']
            fadjust = True

        if camMachine.use_position_definitions:  # dhull
            last = Vector((camMachine.starting_position.x, camMachine.starting_position.y, camMachine.starting_position.z))

        lastrot = Euler((0, 0, 0))
        f = 0.1123456  # nonsense value, so first feedrate always gets written
        fadjustval = 1  # if simulation load data is Not present

        downvector = Vector((0, 0, -1))
        plungelimit = (pi / 2 - operation.plunge_angle)

        scale_graph = 0.05  # warning this has to be same as in export in utils!!!!

        ii = 0
        offline = 0
        online = 0
        cut = True  # active cut variable for laser or plasma
        for vi, vert in enumerate(verts):
            # skip the first vertex if this is a chained operation
            # ie: outputting more than one operation
            # otherwise the machine gets sent back to 0,0 for each operation which is unecessary
            if i > 0 and vi == 0:
                continue
            v = vert.co
            # redundant point on line detection
            if operation.remove_redundant_points and operation.strategy != 'DRILL':
                nextv = v
                if ii == 0:
                    firstv = v  # only happens once
                elif ii == 1:
                    middlev = v
                else:
                    if pointonline(firstv, middlev, nextv, operation.simplify_tol / 1000):
                        middlev = nextv
                        online += 1
                        continue
                    else:  # create new start point with the last tested point
                        ii = 0
                        offline += 1
                        firstv = nextv
                ii += 1
            # end of redundant point on line detection
            if operation.machine_axes != '3':
                v = v.copy()  # we rotate it so we need to copy the vector
                r = Euler(rots[vi].co)
                # conversion to N-axis coordinates
                # this seems to work correctly for 4 axis.
                rcompensate = r.copy()
                rcompensate.x = -r.x
                rcompensate.y = -r.y
                rcompensate.z = -r.z
                v.rotate(rcompensate)

                if r.x == lastrot.x:
                    ra = None
                # print(r.x,lastrot.x)
                else:

                    ra = r.x * rotcorr
                # print(ra,'RA')
                # ra=r.x*rotcorr
                if r.y == lastrot.y:
                    rb = None
                else:
                    rb = r.y * rotcorr
            # rb=r.y*rotcorr
            # print (	ra,rb)

            if vi > 0 and v.x == last.x:
                vx = None
            else:
                vx = v.x * unitcorr
            if vi > 0 and v.y == last.y:
                vy = None
            else:
                vy = v.y * unitcorr
            if vi > 0 and v.z == last.z:
                vz = None
            else:
                vz = v.z * unitcorr

            if fadjust:
                fadjustval = shapek.data[vi].co.z / scale_graph

            # v=(v.x*unitcorr,v.y*unitcorr,v.z*unitcorr)
            vect = v - last
            l = vect.length
            if vi > 0 and l > 0 and downvector.angle(vect) < plungelimit:
                # print('plunge')
                # print(vect)
                if f != plungefeedrate or (fadjust and fadjustval != 1):
                    f = plungefeedrate * fadjustval
                    c.feedrate(f)

                if operation.machine_axes == '3':
                    if operation.cutter_type in ['LASER', 'PLASMA']:
                        if not cut:
                            if operation.cutter_type == 'LASER':
                                c.write("(*************dwell->laser on)\n")
                                c.write("G04 P" + str(round(operation.Laser_delay, 2)) + "\n")
                                c.write(operation.Laser_on + '\n')
                            elif operation.cutter_type == 'PLASMA':
                                c.write("(*************dwell->PLASMA on)\n")
                                plasma_delay = round(operation.Plasma_delay, 5)
                                if plasma_delay > 0:
                                    c.write("G04 P" + str(plasma_delay) + "\n")
                                c.write(operation.Plasma_on + '\n')
                                plasma_dwell = round(operation.Plasma_dwell, 5)
                                if plasma_dwell > 0:
                                    c.write("G04 P" + str(plasma_dwell) + "\n")
                            cut = True
                    else:
                        c.feed(x=vx, y=vy, z=vz)
                else:

                    # print('plungef',ra,rb)
                    c.feed(x=vx, y=vy, z=vz, a=ra, b=rb)

            elif v.z >= free_movement_height or vi == 0:  # v.z==last.z==free_movement_height or vi==0

                if f != freefeedrate:
                    f = freefeedrate
                    c.feedrate(f)

                #                if o.machine_axes == '3':
                #                    c.rapid(x=vx, y=vy, z=vz)

                if operation.machine_axes == '3':
                    if operation.cutter_type in ['LASER', 'PLASMA']:
                        if cut:
                            if operation.cutter_type == 'LASER':
                                c.write("(**************laser off)\n")
                                c.write(operation.Laser_off + '\n')
                            elif operation.cutter_type == 'PLASMA':
                                c.write("(**************Plasma off)\n")
                                c.write(operation.Plasma_off + '\n')

                            cut = False
                        c.rapid(x=vx, y=vy)
                    else:
                        c.rapid(x=vx, y=vy, z=vz)
                else:
                    # print('rapidf',ra,rb)
                    c.rapid(x=vx, y=vy, z=vz, a=ra, b=rb)
            # gcommand='{RAPID}'

            else:

                if f != millfeedrate or (fadjust and fadjustval != 1):
                    f = millfeedrate * fadjustval
                    c.feedrate(f)

                if operation.machine_axes == '3':
                    c.feed(x=vx, y=vy, z=vz)
                else:
                    # print('normalf',ra,rb)
                    c.feed(x=vx, y=vy, z=vz, a=ra, b=rb)

            duration += vect.length / f
            # print(duration)
            last = v
            if operation.machine_axes != '3':
                lastrot = r

            processedops += 1
            if split and processedops > camMachine.split_limit:
                c.rapid(x=last.x * unitcorr, y=last.y * unitcorr, z=free_movement_height * unitcorr)
                # @v=(ch.points[-1][0],ch.points[-1][1],free_movement_height)
                findex += 1
                c.file_close()
                c = startNewFile()
                c.flush_nc()
                c.comment('Tool change - D = %s type %s flutes %s' % (
                    strInUnits(operation.cutter_diameter, 4), operation.cutter_type, operation.cutter_flutes))
                c.tool_change(operation.cutter_id)
                c.spindle(operation.spindle_rpm, spdir_clockwise)
                c.write_spindle()
                c.flush_nc()

                if camMachine.spindle_start_time > 0:
                    c.dwell(camMachine.spindle_start_time)
                    c.flush_nc()

                c.feedrate(unitcorr * operation.feedrate)
                c.rapid(x=last.x * unitcorr, y=last.y * unitcorr, z=free_movement_height * unitcorr)
                c.rapid(x=last.x * unitcorr, y=last.y * unitcorr, z=last.z * unitcorr)
                processedops = 0

        if operation.remove_redundant_points and operation.strategy != "DRILL":
            print("online " + str(online) + " offline " + str(offline) + " " + str(
                round(online / (offline + online) * 100, 1)) + "% removal")
        c.feedrate(unitcorr * operation.feedrate)

        if use_experimental and operation.output_trailer:
            lines = operation.gcode_trailer.split(';')
            for aline in lines:
                c.write(aline + '\n')

    operation.info.duration = duration * unitcorr
    if enable_dust:
        c.write(stop_dust + '\n')
    if enable_hold:
        c.write(stop_hold + '\n')
    if enable_mist:
        c.write(stop_mist + '\n')

    c.program_end()
    c.file_close()
    print(time.process_time() - expiredTime)


def getPath(context, operation):  # should do all path calculations.
    expiredTime = time.process_time()

    if shapely.speedups.available:
        shapely.speedups.enable()

    # these tags are for caching of some of the results. Not working well still
    # - although it can save a lot of time during calculation...

    chd = getChangeData(operation)

    if operation.changedata != chd:  # or 1:
        operation.update_offsetimage_tag = True
        operation.update_zbufferimage_tag = True
        operation.changedata = chd

    operation.update_silhouete_tag = True
    operation.update_ambient_tag = True
    operation.update_bullet_collision_tag = True

    utils.getOperationSources(operation)

    operation.info.warnings = ''
    checkMemoryLimit(operation)

    print(operation.machine_axes)

    if operation.machine_axes == '3':
        getPath3axis(context, operation)

    elif (operation.machine_axes == '5' and operation.strategy5axis == 'INDEXED') or (
            operation.machine_axes == '4' and operation.strategy4axis == 'INDEXED'):
        # 5 axis operations are now only 3 axis operations that get rotated...
        operation.orientation = prepareIndexed(operation)  # TODO RENAME THIS

        getPath3axis(context, operation)  # TODO RENAME THIS

        cleanupIndexed(operation)  # TODO RENAME THIS
    # transform5axisIndexed
    elif operation.machine_axes == '4':
        getPath4axis(context, operation)

    # export gcode if automatic.
    if operation.auto_export:
        if bpy.data.objects.get("cam_path_{}".format(operation.name)) is None:
            return
        p = bpy.data.objects["cam_path_{}".format(operation.name)]
        exportGcodePath(operation.filename, [p.data], [operation])

    operation.changed = False
    t1 = time.process_time() - expiredTime
    progress('total time', t1)


def getChangeData(operation):
    """this is a function to check if object props have changed,
    to see if image updates are needed in the image based method"""
    changedata = ''
    objects = []
    if operation.geometry_source == 'OBJECT':
        objects = [bpy.data.objects[operation.object_name]]
    elif operation.geometry_source == 'COLLECTION':
        objects = bpy.data.collections[operation.collection_name].objects
    for ob in objects:
        changedata += str(ob.location)
        changedata += str(ob.rotation_euler)
        changedata += str(ob.dimensions)

    return changedata


def checkMemoryLimit(o):
    # utils.getBounds(o)
    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y
    resx = sx / o.optimisation.pixsize
    resy = sy / o.optimisation.pixsize
    res = resx * resy
    limit = o.optimisation.imgres_limit * 1000000
    # print('co se to deje')
    if res > limit:
        ratio = (res / limit)
        o.optimisation.pixsize = o.optimisation.pixsize * math.sqrt(ratio)
        o.info.warnings += f"Memory limit: sampling resolution reduced to {o.optimisation.pixsize}\n"
        print('changing sampling resolution to %f' % o.optimisation.pixsize)

def getPath3axis(context, operation):
    scene = bpy.context.scene
    operation = operation
    utils.getBounds(operation)

    match operation.strategy:
        case "CUTOUT":
            strategy.cutout(operation)
        case "CURVE":
            strategy.curve(operation)
        case "PROJECTED_CURVE":
            strategy.projectCurve(scene, operation)
        case "POCKET":
            strategy.pocket(operation)
        case "PARALLEL", "CROSS", "BLOCK", "SPIRAL", "CIRCLES", "OUTLINEFILL", "CARVE", "PENCIL", "CRAZY":
            strategy.compound(operation)
        case "WATERLINE" if operation.optimisation.use_opencamlib:
            strategy.waterlineOCL(operation)
        case "WATERLINE" if not operation.optimisation.use_opencamlib:
            strategy.waterline(operation)
        case "DRILL":
            strategy.drill(operation)
        case "MEDIAL_AXIS":
            strategy.medialAxis(operation)


def getPath4axis(context, operation):
    operation = operation
    utils.getBounds(operation)
    if operation.strategy4axis in ['PARALLELR', 'PARALLEL', 'HELIX', 'CROSS']:
        path_samples = getPathPattern4axis(operation)

        depth = path_samples[0].depth
        chunks = []

        layers = strategy.getLayers(operation, 0, depth)

        chunks.extend(utils.sampleChunksNAxis(operation, path_samples, layers))
        strategy.chunksToMesh(chunks, operation)
