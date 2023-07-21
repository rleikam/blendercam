# blender CAM utils.py (c) 2012 Vilem Novak
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

# here is the main functionality of Blender CAM. The functions here are called with operators defined in ops.py.

import bpy
import mathutils
import math
from bpy.props import *
from cam import utils
import numpy as np

from cam import simple
from cam import image_utils
from .tool.ToolManager import ToolManager

def createSimulationObject(name, operations, image):
    simulationObjectName = utils.getCAMSimulationObjectNameConventionFrom(name)

    operation = operations[0]

    if simulationObjectName in bpy.data.objects:
        object = bpy.data.objects[simulationObjectName]
    else:
        bpy.ops.mesh.primitive_plane_add(align='WORLD', enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
        object = bpy.context.active_object
        object.name = simulationObjectName

        bpy.ops.object.modifier_add(type='SUBSURF')
        subdivisionSurfaceModifier = object.modifiers[-1]
        subdivisionSurfaceModifier.subdivision_type = 'SIMPLE'
        subdivisionSurfaceModifier.levels = 6
        subdivisionSurfaceModifier.render_levels = 6
        bpy.ops.object.modifier_add(type='SUBSURF')
        subdivisionSurfaceModifier = object.modifiers[-1]
        subdivisionSurfaceModifier.subdivision_type = 'SIMPLE'
        subdivisionSurfaceModifier.levels = 4
        subdivisionSurfaceModifier.render_levels = 3
        bpy.ops.object.modifier_add(type='DISPLACE')

    collection = utils.getCAMSimulationCollection()

    utils.reassignObjectsToCollection([object], collection)

    object.location = ((operation.max.x + operation.min.x) / 2, (operation.max.y + operation.min.y) / 2, operation.min.z)
    object.scale.x = (operation.max.x - operation.min.x) / 2
    object.scale.y = (operation.max.y - operation.min.y) / 2
    print(operation.max.x, operation.min.x)
    print(operation.max.y, operation.min.y)
    print('bounds')
    disp = object.modifiers[-1]
    disp.direction = 'Z'
    disp.texture_coords = 'LOCAL'
    disp.mid_level = 0

    if simulationObjectName in bpy.data.textures:
        t = bpy.data.textures[simulationObjectName]

        t.type = 'IMAGE'
        disp.texture = t

        t.image = image
    else:
        bpy.ops.texture.new()
        for t in bpy.data.textures:
            if t.name == 'Texture':
                t.type = 'IMAGE'
                t.name = simulationObjectName
                t = t.type_recast()
                t.type = 'IMAGE'
                t.image = image
                disp.texture = t
    object.hide_render = True
    bpy.ops.object.shade_smooth()


def doSimulation(name, operations):
    """perform simulation of operations. Currently only for 3 axis"""
    for operation in operations:
        utils.getOperationSources(operation)

    # this is here because some background computed operations still didn't have bounds data
    limits = utils.getBoundsMultiple(operations)
    image = generateSimulationImage(operations, limits)

    cp = simple.getSimulationPath()+name
    print('cp=', cp)
    imageName = cp + '_sim.exr'

    image_utils.numpysave(image, imageName)
    image = bpy.data.images.load(imageName)
    createSimulationObject(name, operations, image)

def generateSimulationImage(operations, limits):
    minx, miny, minz, maxx, maxy, maxz = limits
    # print(minx,miny,minz,maxx,maxy,maxz)
    sx = maxx - minx
    sy = maxy - miny

    operation = operations[0]  # getting sim detail and others from first op.
    simulation_detail = operation.optimisation.simulation_detail
    borderwidth = operation.borderwidth
    resx = math.ceil(sx / simulation_detail) + 2 * borderwidth
    resy = math.ceil(sy / simulation_detail) + 2 * borderwidth

    # create array in which simulation happens, similar to an image to be painted in.
    si = np.array(0.1, dtype=float)
    si.resize(resx, resy)
    si.fill(maxz)

    for operation in operations:
        camPathName = utils.getCAMPathObjectNameConventionFrom(operation.name)
        object = bpy.data.objects[camPathName]
        mesh = object.data
        verts = mesh.vertices

        if operation.do_simulation_feedrate:
            kname = 'feedrates'
            mesh.use_customdata_edge_crease = True

            if mesh.shape_keys is None or mesh.shape_keys.key_blocks.find(kname) == -1:
                object.shape_key_add()
                if len(mesh.shape_keys.key_blocks) == 1:
                    object.shape_key_add()
                shapek = mesh.shape_keys.key_blocks[-1]
                shapek.name = kname
            else:
                shapek = mesh.shape_keys.key_blocks[kname]
            shapek.data[0].co = (0.0, 0, 0)
        # print(len(shapek.data))
        # print(len(verts_rotations))

        # print(r)

        totalvolume = 0.0

        cutterArray = getCutterArray(operation, simulation_detail)
        cutterArray = -cutterArray
        lasts = verts[1].co
        perc = -1
        vtotal = len(verts)
        dropped = 0

        xs = 0
        ys = 0

        for i, vert in enumerate(verts):
            if perc != int(100 * i / vtotal):
                perc = int(100 * i / vtotal)
                simple.progress('simulation', perc)
            # progress('simulation ',int(100*i/l))

            if i > 0:
                volume = 0
                volume_partial = 0
                s = vert.co
                v = s - lasts

                l = v.length
                if (lasts.z < maxz or s.z < maxz) and not (
                        v.x == 0 and v.y == 0 and v.z > 0):  # only simulate inside material, and exclude lift-ups
                    if (
                            v.x == 0 and v.y == 0 and v.z < 0):
                        # if the cutter goes straight down, we don't have to interpolate.
                        pass

                    elif v.length > simulation_detail:  # and not :

                        v.length = simulation_detail
                        lastxs = xs
                        lastys = ys
                        while v.length < l:
                            xs = int((lasts.x + v.x - minx) / simulation_detail + borderwidth + simulation_detail / 2)
                            # -middle
                            ys = int((lasts.y + v.y - miny) / simulation_detail + borderwidth + simulation_detail / 2)
                            # -middle
                            z = lasts.z + v.z
                            # print(z)
                            if lastxs != xs or lastys != ys:
                                volume_partial = simCutterSpot(xs, ys, z, cutterArray, si, operation.do_simulation_feedrate)
                                if operation.do_simulation_feedrate:
                                    totalvolume += volume
                                    volume += volume_partial
                                lastxs = xs
                                lastys = ys
                            else:
                                dropped += 1
                            v.length += simulation_detail

                    xs = int((s.x - minx) / simulation_detail + borderwidth + simulation_detail / 2)  # -middle
                    ys = int((s.y - miny) / simulation_detail + borderwidth + simulation_detail / 2)  # -middle
                    volume_partial = simCutterSpot(xs, ys, s.z, cutterArray, si, operation.do_simulation_feedrate)
                if operation.do_simulation_feedrate:  # compute volumes and write data into shapekey.
                    volume += volume_partial
                    totalvolume += volume
                    if l > 0:
                        load = volume / l
                    else:
                        load = 0

                    # this will show the shapekey as debugging graph and will use same data to estimate parts
                    # with heavy load
                    if l != 0:
                        shapek.data[i].co.y = (load) * 0.000002
                    else:
                        shapek.data[i].co.y = shapek.data[i - 1].co.y
                    shapek.data[i].co.x = shapek.data[i - 1].co.x + l * 0.04
                    shapek.data[i].co.z = 0
                lasts = s

        # print('dropped '+str(dropped))
        if operation.do_simulation_feedrate:  # smoothing ,but only backward!
            xcoef = shapek.data[len(shapek.data) - 1].co.x / len(shapek.data)
            for a in range(0, 10):
                # print(shapek.data[-1].co)
                nvals = []
                val1 = 0  #
                val2 = 0
                w1 = 0  #
                w2 = 0

                for i, d in enumerate(shapek.data):
                    val = d.co.y

                    if i > 1:
                        d1 = shapek.data[i - 1].co
                        val1 = d1.y
                        if d1.x - d.co.x != 0:
                            w1 = 1 / (abs(d1.x - d.co.x) / xcoef)

                    if i < len(shapek.data) - 1:
                        d2 = shapek.data[i + 1].co
                        val2 = d2.y
                        if d2.x - d.co.x != 0:
                            w2 = 1 / (abs(d2.x - d.co.x) / xcoef)

                    # print(val,val1,val2,w1,w2)

                    val = (val + val1 * w1 + val2 * w2) / (1.0 + w1 + w2)
                    nvals.append(val)
                for i, d in enumerate(shapek.data):
                    d.co.y = nvals[i]

            # apply mapping - convert the values to actual feedrates.
            total_load = 0
            max_load = 0
            for i, d in enumerate(shapek.data):
                total_load += d.co.y
                max_load = max(max_load, d.co.y)
            normal_load = total_load / len(shapek.data)

            thres = 0.5

            scale_graph = 0.05  # warning this has to be same as in export in utils!!!!

            totverts = len(shapek.data)
            for i, d in enumerate(shapek.data):
                if d.co.y > normal_load:
                    d.co.z = scale_graph * max(0.3, normal_load / d.co.y)
                else:
                    d.co.z = scale_graph * 1
                if i < totverts - 1:
                    mesh.edges[i].crease = d.co.y / (normal_load * 4)

    si = si[borderwidth:-borderwidth, borderwidth:-borderwidth]
    si += -minz

    return si


def getCutterArray(operation, pixelSize):
    cutterType = operation.cutter_type

    millRadius = operation.cutter_diameter / 2 + operation.skin
    resolution = math.ceil((millRadius * 2) / pixelSize)
    midLengthOffset = resolution / 2.0
    cutterArray = np.array((0), dtype=float)
    cutterArray.resize(resolution, resolution)
    cutterArray.fill(-10)

    resolutionArray = (
        (
            x,
            y,
            mathutils.Vector
            (
                (
                    (x + 0.5 - midLengthOffset) * pixelSize,
                    (y + 0.5 - midLengthOffset) * pixelSize
                )
            )
        )
        for x in range(0, resolution)
        for y in range(0, resolution)
    )

    vector = mathutils.Vector((0, 0, 0))
    match cutterType:
        case 'END':
            for x, y, vector in resolutionArray:
                if vector.length <= millRadius:
                    cutterArray.itemset((x, y), 0)

        case 'BALL' | 'BALLNOSE':

            tool = ToolManager.constructToolFromOperation(operation)
            for x, y, vector in resolutionArray:
                if vector.length <= millRadius:
                    z = -tool.calculateMillDepthFor(vector.length*2)
                    cutterArray.itemset((x, y), z)

        case 'VCARVE':
            tool = ToolManager.constructToolFromOperation(operation)

            for x, y, vector in resolutionArray:
                if vector.length <= millRadius:
                    z = -tool.calculateMillDepthFor(vector.length*2)
                    cutterArray.itemset((x, y), z)

        case 'CYLCONE':
            angle = operation.cutter_tip_angle
            cyl_r = operation.cylcone_diameter/2
            slope = math.tan(math.pi * (90 - angle / 2) / 180)

            for x, y, vector in resolutionArray:
                if vector.length <= millRadius:
                    z = (-(vector.length - cyl_r) * slope)
                    if vector.length <= cyl_r:
                        z = 0
                    cutterArray.itemset((x, y), z)

        case 'BALLCONE':
            tool = ToolManager.constructToolFromOperation(operation)
            
            for x, y, vector in resolutionArray:
                if vector.length <= millRadius:
                    z = -tool.calculateMillDepthFor(vector.length*2)
                    cutterArray.itemset((x, y), z)
            
        case 'CUSTOM':
            cutterObject = bpy.data.objects[operation.cutter_object_name]
            scale = ((cutterObject.dimensions.x / cutterObject.scale.x) / 2) / millRadius  #

            vstart = mathutils.Vector((0, 0, -10))
            vend = mathutils.Vector((0, 0, 10))
            print('sampling custom cutter')
            maxz = -1
            for x in range(0, resolution):
                vstart.x = (x + 0.5 - midLengthOffset) * pixelSize * scale
                vend.x = vstart.x

                for y in range(0, resolution):
                    vstart.y = (y + 0.5 - midLengthOffset) * pixelSize * scale
                    vend.y = vstart.y
                    vector = vend - vstart
                    c = cutterObject.ray_cast(vstart, vector, distance=1.70141e+38)
                    if c[3] != -1:
                        z = -c[1][2] / scale
                        # print(c)
                        if z > -9:
                            # print(z)
                            if z > maxz:
                                maxz = z
                            cutterArray.itemset((x, y), z)
            cutterArray -= maxz

    return cutterArray


def simCutterSpot(xs, ys, z, cutterArray, si, getvolume=False):
    """simulates a cutter cutting into stock, taking away the volume,
    and optionally returning the volume that has been milled. This is now used for feedrate tweaking."""
    m = int(cutterArray.shape[0] / 2)
    size = cutterArray.shape[0]
    if xs > m and xs < si.shape[0] - m and ys > m and ys < si.shape[1] - m:  # whole cutter in image there
        if getvolume:
            volarray = si[xs - m:xs - m + size, ys - m:ys - m + size].copy()
        si[xs - m:xs - m + size, ys - m:ys - m + size] = np.minimum(si[xs - m:xs - m + size, ys - m:ys - m + size],
                                                                    cutterArray + z)
        if getvolume:
            volarray = si[xs - m:xs - m + size, ys - m:ys - m + size] - volarray
            vsum = abs(volarray.sum())
            # print(vsum)
            return vsum

    elif xs > -m and xs < si.shape[0] + m and ys > -m and ys < si.shape[1] + m:
        # part of cutter in image, for extra large cutters

        startx = max(0, xs - m)
        starty = max(0, ys - m)
        endx = min(si.shape[0], xs - m + size)
        endy = min(si.shape[0], ys - m + size)
        castartx = max(0, m - xs)
        castarty = max(0, m - ys)
        caendx = min(size, si.shape[0] - xs + m)
        caendy = min(size, si.shape[1] - ys + m)

        if getvolume:
            volarray = si[startx:endx, starty:endy].copy()
        si[startx:endx, starty:endy] = np.minimum(si[startx:endx, starty:endy],
                                                  cutterArray[castartx:caendx, castarty:caendy] + z)
        if getvolume:
            volarray = si[startx:endx, starty:endy] - volarray
            vsum = abs(volarray.sum())
            # print(vsum)
            return vsum
    return 0
