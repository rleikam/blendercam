
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
import time
import mathutils
import math
from math import *
from mathutils import *
from bpy.props import *
from bpy_extras import object_utils

import sys
import numpy
import pickle

from cam.chunk import *
from cam.collision import *
from cam.simple import *
from cam.pattern import *
from cam.polygon_utils_cam import *
from cam.image_utils import *
from cam.exception import *

from cam.opencamlib.opencamlib import oclSample, oclSamplePoints, oclResampleChunks, oclGetWaterline

from shapely.geometry import polygon as spolygon
from shapely.geometry import MultiPolygon
from shapely import ops as sops
from shapely import geometry as sgeometry

# from shapely.geometry import * not possible until Polygon libs gets out finally..
SHAPELY = True


# The following functions are temporary
# until all content in __init__.py is cleaned up

def update_material(self, context):
    addMaterialAreaObject()

def update_operation(self, context):
    from .blender.property.callback import updateRest
    active_op = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    updateRest(active_op, bpy.context)

def update_exact_mode(self, context):
    from .blender.property.callback import updateExact
    active_op = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    updateExact(active_op, bpy.context)

def update_opencamlib(self, context):
    from .blender.property.callback import updateOpencamlib
    active_op = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    updateOpencamlib(active_op, bpy.context)

def update_zbuffer_image(self, context):
    from .blender.property.callback import updateZbufferImage
    active_op = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    updateZbufferImage(active_op, bpy.context)






# Import OpencamLib
# Return available OpenCamLib version on success, None otherwise
def opencamlib_version():
    try:
        import ocl
    except ImportError:
        try:
            import opencamlib as ocl
        except ImportError as e:
            return
    return(ocl.version())

def positionObject(operation):
    ob = bpy.data.objects[operation.object_name]
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

    minx, miny, minz, maxx, maxy, maxz = getBoundsWorldspace([ob], operation.use_modifiers)
    totx = maxx - minx
    toty = maxy - miny
    totz = maxz - minz
    if operation.material.center_x:
        ob.location.x -= minx + totx / 2
    else:
        ob.location.x -= minx

    if operation.material.center_y:
        ob.location.y -= miny + toty / 2
    else:
        ob.location.y -= miny

    if operation.material.z_position == 'BELOW':
        ob.location.z -= maxz
    elif operation.material.z_position == 'ABOVE':
        ob.location.z -= minz
    elif operation.material.z_position == 'CENTERED':
        ob.location.z -= minz + totz / 2

    if ob.type != 'CURVE':
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    # addMaterialAreaObject()


def getBoundsWorldspace(obs, use_modifiers=False):
    # progress('getting bounds of object(s)')
    t = time.time()

    maxx = maxy = maxz = -10000000
    minx = miny = minz = 10000000
    for ob in obs:
        # bb=ob.bound_box
        mw = ob.matrix_world
        if ob.type == 'MESH':
            if use_modifiers:
                depsgraph = bpy.context.evaluated_depsgraph_get()
                mesh_owner = ob.evaluated_get(depsgraph)
                mesh = mesh_owner.to_mesh()
            else:
                mesh = ob.data

            for c in mesh.vertices:
                coord = c.co
                worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                minx = min(minx, worldCoord.x)
                miny = min(miny, worldCoord.y)
                minz = min(minz, worldCoord.z)
                maxx = max(maxx, worldCoord.x)
                maxy = max(maxy, worldCoord.y)
                maxz = max(maxz, worldCoord.z)

            if use_modifiers:
                mesh_owner.to_mesh_clear()

        elif ob.type == "FONT":
            activate(ob)
            bpy.ops.object.duplicate()
            co = bpy.context.active_object
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            bpy.ops.object.convert(target='MESH', keep_original=False)
            mesh = co.data
            for c in mesh.vertices:
                coord = c.co
                worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                minx = min(minx, worldCoord.x)
                miny = min(miny, worldCoord.y)
                minz = min(minz, worldCoord.z)
                maxx = max(maxx, worldCoord.x)
                maxy = max(maxy, worldCoord.y)
                maxz = max(maxz, worldCoord.z)
            bpy.ops.object.delete()
            bpy.ops.outliner.orphans_purge()
        else:
            if not hasattr(ob.data,"splines"):
                raise CamException("Can't do CAM operation on the selected object type")
            # for coord in bb:
            for c in ob.data.splines:
                for p in c.bezier_points:
                    coord = p.co
                    # this can work badly with some imported curves, don't know why...
                    # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
                    worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                    minx = min(minx, worldCoord.x)
                    miny = min(miny, worldCoord.y)
                    minz = min(minz, worldCoord.z)
                    maxx = max(maxx, worldCoord.x)
                    maxy = max(maxy, worldCoord.y)
                    maxz = max(maxz, worldCoord.z)
                for p in c.points:
                    coord = p.co
                    # this can work badly with some imported curves, don't know why...
                    # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
                    worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                    minx = min(minx, worldCoord.x)
                    miny = min(miny, worldCoord.y)
                    minz = min(minz, worldCoord.z)
                    maxx = max(maxx, worldCoord.x)
                    maxy = max(maxy, worldCoord.y)
                    maxz = max(maxz, worldCoord.z)
    # progress(time.time()-t)
    return minx, miny, minz, maxx, maxy, maxz


def getSplineBounds(ob, curve):
    # progress('getting bounds of object(s)')
    maxx = maxy = maxz = -10000000
    minx = miny = minz = 10000000
    mw = ob.matrix_world

    for p in curve.bezier_points:
        coord = p.co
        # this can work badly with some imported curves, don't know why...
        # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
        worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
        minx = min(minx, worldCoord.x)
        miny = min(miny, worldCoord.y)
        minz = min(minz, worldCoord.z)
        maxx = max(maxx, worldCoord.x)
        maxy = max(maxy, worldCoord.y)
        maxz = max(maxz, worldCoord.z)
    for p in curve.points:
        coord = p.co
        # this can work badly with some imported curves, don't know why...
        # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
        worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
        minx = min(minx, worldCoord.x)
        miny = min(miny, worldCoord.y)
        minz = min(minz, worldCoord.z)
        maxx = max(maxx, worldCoord.x)
        maxy = max(maxy, worldCoord.y)
        maxz = max(maxz, worldCoord.z)
    # progress(time.time()-t)
    return minx, miny, minz, maxx, maxy, maxz


def getOperationSources(operation):
    if operation.geometry_source == 'OBJECT':
        object = bpy.data.objects[operation.object_name]
        operation.objects = [object]
        object.select_set(True)
        bpy.context.view_layer.objects.active = object

        if operation.enable_B or operation.enable_A:
            if operation.old_rotation_A != operation.rotation_A or operation.old_rotation_B != operation.rotation_B:
                operation.old_rotation_A = operation.rotation_A
                operation.old_rotation_B = operation.rotation_B
                object = bpy.data.objects[operation.object_name]
                object.select_set(True)
                bpy.context.view_layer.objects.active = object
                if operation.A_along_x:  # A parallel with X
                    if operation.enable_A:
                        bpy.context.active_object.rotation_euler.x = operation.rotation_A
                    if operation.enable_B:
                        bpy.context.active_object.rotation_euler.y = operation.rotation_B
                else:  # A parallel with Y
                    if operation.enable_A:
                        bpy.context.active_object.rotation_euler.y = operation.rotation_A
                    if operation.enable_B:
                        bpy.context.active_object.rotation_euler.x = operation.rotation_B

    elif operation.geometry_source == 'COLLECTION':
        collection = bpy.data.collections[operation.collection_name]
        operation.objects = collection.objects

    elif operation.geometry_source == 'IMAGE':
        operation.optimisation.use_exact = False

    if operation.geometry_source == 'OBJECT' or operation.geometry_source == 'COLLECTION':
        operation.onlycurves = True
        for object in operation.objects:
            if object.type == 'MESH':
                operation.onlycurves = False
    else:
        operation.onlycurves = False


def getBounds(operation):
    # print('kolikrat sem rpijde')
    if operation.geometry_source == 'OBJECT' or operation.geometry_source == 'COLLECTION' or operation.geometry_source == 'CURVE':
        print("valid geometry")
        minx, miny, minz, maxx, maxy, maxz = getBoundsWorldspace(operation.objects, operation.use_modifiers)

        if operation.minz_from_ob:
            if minz == 10000000:
                minz = 0
            print("minz from object:" + str(minz))
            operation.min.z = minz
            operation.minz = operation.min.z
        else:
            operation.min.z = operation.minz  # max(bb[0][2]+l.z,o.minz)#
            print("not minz from object")

        if operation.material.estimate_from_model:
            print("Estimate material from model")

            operation.min.x = minx - operation.material.radius_around_model
            operation.min.y = miny - operation.material.radius_around_model
            operation.max.z = max(operation.maxz, maxz)

            operation.max.x = maxx + operation.material.radius_around_model
            operation.max.y = maxy + operation.material.radius_around_model
        else:
            print("not material from model")
            operation.min.x = operation.material.origin.x
            operation.min.y = operation.material.origin.y
            operation.min.z = operation.material.origin.z - operation.material.size.z
            operation.max.x = operation.min.x + operation.material.size.x
            operation.max.y = operation.min.y + operation.material.size.y
            operation.max.z = operation.material.origin.z

    else:
        i = bpy.data.images[operation.source_image_name]
        if operation.source_image_crop:
            sx = int(i.size[0] * operation.source_image_crop_start_x / 100)
            ex = int(i.size[0] * operation.source_image_crop_end_x / 100)
            sy = int(i.size[1] * operation.source_image_crop_start_y / 100)
            ey = int(i.size[1] * operation.source_image_crop_end_y / 100)
        else:
            sx = 0
            ex = i.size[0]
            sy = 0
            ey = i.size[1]

        operation.optimisation.pixsize = operation.source_image_size_x / i.size[0]

        operation.min.x = operation.source_image_offset.x + sx * operation.optimisation.pixsize
        operation.max.x = operation.source_image_offset.x + ex * operation.optimisation.pixsize
        operation.min.y = operation.source_image_offset.y + sy * operation.optimisation.pixsize
        operation.max.y = operation.source_image_offset.y + ey * operation.optimisation.pixsize
        operation.min.z = operation.source_image_offset.z + operation.minz
        operation.max.z = operation.source_image_offset.z
    scene = bpy.context.scene
    machine = scene.cam_machine
    if operation.max.x - operation.min.x > machine.working_area.x or operation.max.y - operation.min.y > machine.working_area.y \
            or operation.max.z - operation.min.z > machine.working_area.z:
        operation.info.warnings += 'Operation exceeds your machine limits\n'


def getBoundsMultiple(operations):
    """gets bounds of multiple operations, mainly for purpose of simulations or rest milling. highly suboptimal."""
    maxx = maxy = maxz = -10000000
    minx = miny = minz = 10000000
    for operation in operations:
        getBounds(operation)
        maxx = max(maxx, operation.max.x)
        maxy = max(maxy, operation.max.y)
        maxz = max(maxz, operation.max.z)
        minx = min(minx, operation.min.x)
        miny = min(miny, operation.min.y)
        minz = min(minz, operation.min.z)

    return minx, miny, minz, maxx, maxy, maxz


def samplePathLow(o, ch1, ch2, dosample):
    v1 = Vector(ch1.points[-1])
    v2 = Vector(ch2.points[0])

    v = v2 - v1
    d = v.length
    v.normalize()

    vref = Vector((0, 0, 0))
    bpath = camPathChunk([])
    i = 0
    while vref.length < d:
        i += 1
        vref = v * o.dist_along_paths * i
        if vref.length < d:
            p = v1 + vref
            bpath.points.append([p.x, p.y, p.z])
    # print('between path')
    # print(len(bpath))
    pixsize = o.optimisation.pixsize
    if dosample:
        if not (o.optimisation.use_opencamlib and o.optimisation.use_exact):
            if o.optimisation.use_exact:
                if o.update_bullet_collision_tag:
                    prepareBulletCollision(o)
                    o.update_bullet_collision_tag = False

                cutterdepth = o.cutter_shape.dimensions.z / 2
                for p in bpath.points:
                    z = getSampleBullet(o.cutter_shape, p[0], p[1], cutterdepth, 1, o.minz)
                    if z > p[2]:
                        p[2] = z
            else:
                for p in bpath.points:
                    xs = (p[0] - o.min.x) / pixsize + o.borderwidth + pixsize / 2  # -m
                    ys = (p[1] - o.min.y) / pixsize + o.borderwidth + pixsize / 2  # -m
                    z = getSampleImage((xs, ys), o.offset_image, o.minz) + o.skin
                    if z > p[2]:
                        p[2] = z
    return bpath

def sampleChunks(operation, pathSamples, layers):
    minx, miny, minz, maxx, maxy, maxz = operation.min.x, operation.min.y, operation.min.z, operation.max.x, operation.max.y, operation.max.z
    getAmbient(operation)

    if operation.optimisation.use_exact:  # prepare collision world
        if operation.optimisation.use_opencamlib:
            oclSample(operation, pathSamples)
            cutterdepth = 0
        else:
            if operation.update_bullet_collision_tag:
                prepareBulletCollision(operation)

                operation.update_bullet_collision_tag = False

            cutter = operation.cutter_shape
            cutterdepth = cutter.dimensions.z / 2
    else:
        if operation.strategy != 'WATERLINE':  # or prepare offset image, but not in some strategies.
            prepareArea(operation)

        pixsize = operation.optimisation.pixsize

        coordoffset = operation.borderwidth + pixsize / 2  # -m

        res = ceil(operation.cutter_diameter / operation.optimisation.pixsize)
        m = res / 2

    totalLength = 0
    for chunk in pathSamples:
        totalLength += len(chunk.points)

    layerchunks = []
    minz = operation.minz - 0.000001  # correction for image method problems
    layerActiveChunks = []
    lastrunchunks = []

    for layer in layers:
        layerchunks.append([])
        layerActiveChunks.append(camPathChunk([]))
        lastrunchunks.append([])

    if operation.inverse:
        object = bpy.data.objects[operation.object_name]

    n = 0
    last_percent = -1

    samplingtime = timinginit()
    sortingtime = timinginit()
    totaltime = timinginit()
    timingstart(totaltime)

    for patternchunk in pathSamples:
        thisrunchunks = []
        for layer in layers:
            thisrunchunks.append([])
        lastlayer = None
        currentlayer = None
        lastsample = None

        for s in patternchunk.points:
            if operation.strategy != 'WATERLINE' and int(100 * n / totalLength) != last_percent:
                last_percent = int(100 * n / totalLength)
                progress('sampling paths ', last_percent)
            n += 1
            x = s[0]
            y = s[1]
            if not operation.ambient.contains(sgeometry.Point(x, y)):
                newsample = (x, y, 1)
            else:
                if operation.optimisation.use_opencamlib and operation.optimisation.use_exact:
                    z = s[2]
                    if minz > z:
                        z = minz
                    newsample = (x, y, z)
                # ampling
                elif operation.optimisation.use_exact and not operation.optimisation.use_opencamlib:

                    if lastsample is not None:  # this is an optimalization,
                        # search only for near depths to the last sample. Saves about 30% of sampling time.
                        z = getSampleBullet(cutter, x, y, cutterdepth, 1,
                                            lastsample[2] - operation.dist_along_paths)  # first try to the last sample
                        if z < minz - 1:
                            z = getSampleBullet(cutter, x, y, cutterdepth, lastsample[2] - operation.dist_along_paths, minz)
                    else:
                        z = getSampleBullet(cutter, x, y, cutterdepth, 1, minz)

                # print(z)
                else:
                    timingstart(samplingtime)
                    xs = (x - minx) / pixsize + coordoffset
                    ys = (y - miny) / pixsize + coordoffset
                    timingadd(samplingtime)
                    z = getSampleImage((xs, ys), operation.offset_image, minz) + operation.skin

                ################################
                # handling samples
                ############################################

                if minz > z:
                    z = minz
                newsample = (x, y, z)

            for index, layer in enumerate(layers):
                terminatechunk = False

                chunk = layerActiveChunks[index]

                if layer[1] <= newsample[2] <= layer[0]:
                    lastlayer = None  # rather the last sample here ? has to be set to None,
                    # since sometimes lastsample vs lastlayer didn't fit and did ugly ugly stuff....
                    if lastsample is not None:
                        for i2, l2 in enumerate(layers):
                            if l2[1] <= lastsample[2] <= l2[0]:
                                lastlayer = i2

                    currentlayer = index
                    if lastlayer is not None and lastlayer != currentlayer:  # and lastsample[2]!=newsample[2]:
                        # #sampling for sorted paths in layers- to go to the border of the sampled layer at least...
                        # there was a bug here, but should be fixed.
                        if currentlayer < lastlayer:
                            growing = True
                            layerRange = range(currentlayer, lastlayer)

                        else:
                            layerRange = range(lastlayer, currentlayer)
                            growing = False

                        li = 0
                        for ls in layerRange:
                            splitz = layers[ls][1]

                            v1 = lastsample
                            v2 = newsample
                            if operation.protect_vertical:
                                v1, v2 = isVerticalLimit(v1, v2, operation.protect_vertical_limit)
                            v1 = Vector(v1)
                            v2 = Vector(v2)

                            ratio = (splitz - v1.z) / (v2.z - v1.z)
  
                            betweensample = v1 + (v2 - v1) * ratio

                            if growing:
                                if li > 0:
                                    layerActiveChunks[ls].points.insert(-1, betweensample.to_tuple())
                                else:
                                    layerActiveChunks[ls].points.append(betweensample.to_tuple())
                                layerActiveChunks[ls + 1].points.append(betweensample.to_tuple())
                            else:
                                layerActiveChunks[ls].points.insert(-1, betweensample.to_tuple())
                                layerActiveChunks[ls + 1].points.insert(0, betweensample.to_tuple())

                            li += 1

                    chunk.points.append(newsample)
                elif layer[1] > newsample[2]:
                    chunk.points.append((newsample[0], newsample[1], layer[1]))
                elif layer[0] < newsample[2]:
                    terminatechunk = True

                if terminatechunk:
                    if len(chunk.points) > 0:
                        layerchunks[index].append(chunk)
                        thisrunchunks[index].append(chunk)
                        layerActiveChunks[index] = camPathChunk([])
            lastsample = newsample

        for index, layer in enumerate(layers):
            chunk = layerActiveChunks[index]
            if len(chunk.points) > 0:
                layerchunks[index].append(chunk)
                thisrunchunks[index].append(chunk)
                layerActiveChunks[index] = camPathChunk([])

            if operation.strategy == 'PARALLEL' or operation.strategy == 'CROSS' or operation.strategy == 'OUTLINEFILL':
                timingstart(sortingtime)
                parentChildDist(thisrunchunks[index], lastrunchunks[index], operation)
                timingadd(sortingtime)

        lastrunchunks = thisrunchunks

    progress('checking relations between paths')
    timingstart(sortingtime)

    if operation.strategy == 'PARALLEL' or operation.strategy == 'CROSS' or operation.strategy == 'OUTLINEFILL':
        if len(layers) > 1:  # sorting help so that upper layers go first always
            for index in range(0, len(layers) - 1):
                parents = []
                children = []
                # only pick chunks that should have connectivity assigned - 'last' and 'first' ones of the layer.
                for chunk in layerchunks[index + 1]:
                    if not chunk.children:
                        parents.append(chunk)

                for ch1 in layerchunks[index]:
                    if not ch1.parents:
                        children.append(ch1)

                parentChild(parents, children, operation)  # parent only last and first chunk, before it did this for all.
    timingadd(sortingtime)
    chunks = []

    for index, layer in enumerate(layers):
        if operation.ramp:
            for chunk in layerchunks[index]:
                chunk.zstart = layers[index][0]
                chunk.zend = layers[index][1]
        chunks.extend(layerchunks[index])
    
    timingadd(totaltime)
    print(samplingtime)
    print(sortingtime)
    print(totaltime)
    return chunks


def sampleChunksNAxis(operation, pathSamples, layers):
    #
    minx, miny, minz, maxx, maxy, maxz = operation.min.x, operation.min.y, operation.min.z, operation.max.x, operation.max.y, operation.max.z

    # prepare collision world
    if operation.update_bullet_collision_tag:
        prepareBulletCollision(operation)
        # print('getting ambient')
        getAmbient(operation)
        operation.update_bullet_collision_tag = False
    # print (o.ambient)
    cutter = operation.cutter_shape
    cutterdepth = cutter.dimensions.z / 2

    t = time.time()
    print('sampling paths')

    totlen = 0  # total length of all chunks, to estimate sampling time.
    for chs in pathSamples:
        totlen += len(chs.startpoints)
    layerchunks = []
    minz = operation.minz
    layeractivechunks = []
    lastrunchunks = []

    for layer in layers:
        layerchunks.append([])
        layeractivechunks.append(camPathChunk([]))
        lastrunchunks.append([])
    n = 0

    lastz = minz
    for patternchunk in pathSamples:
        # print (patternchunk.endpoints)
        thisrunchunks = []
        for layer in layers:
            thisrunchunks.append([])
        lastlayer = None
        currentlayer = None
        lastsample = None
        # threads_count=4
        lastrotation = (0, 0, 0)
        # for t in range(0,threads):
        # print(len(patternchunk.startpoints),len( patternchunk.endpoints))
        spl = len(patternchunk.startpoints)
        for si in range(0, spl):  # ,startp in enumerate(patternchunk.startpoints):
            # #TODO: seems we are writing into the source chunk ,
            #  and that is why we need to write endpoints everywhere too?

            if n / 200.0 == int(n / 200.0):
                progress('sampling paths ', int(100 * n / totlen))
            n += 1
            sampled = False
            # print(si)

            # get the vector to sample
            startp = Vector(patternchunk.startpoints[si])
            endp = Vector(patternchunk.endpoints[si])
            rotation = patternchunk.rotations[si]
            sweepvect = endp - startp
            sweepvect.normalize()
            # sampling
            if rotation != lastrotation:

                cutter.rotation_euler = rotation
                # cutter.rotation_euler.x=-cutter.rotation_euler.x
                # print(rotation)

                if operation.cutter_type == 'VCARVE':  # Bullet cone is always pointing Up Z in the object
                    cutter.rotation_euler.x += pi
                cutter.update_tag()
                bpy.context.scene.frame_set(1)  # this has to be :( it resets the rigidbody world.
                # No other way to update it probably now :(
                bpy.context.scene.frame_set(2)  # actually 2 frame jumps are needed.
                bpy.context.scene.frame_set(0)

            newsample = getSampleBulletNAxis(cutter, startp, endp, rotation, cutterdepth)

            # print('totok',startp,endp,rotation,newsample)
            ################################
            # handling samples
            ############################################
            if newsample is not None:  # this is weird, but will leave it this way now.. just prototyping here.
                sampled = True
            else:  # TODO: why was this here?
                newsample = startp
                sampled = True
            # print(newsample)

            # elif o.ambient_behaviour=='ALL' and not o.inverse:#handle ambient here
            # newsample=(x,y,minz)
            if sampled:
                for index, layer in enumerate(layers):
                    terminatechunk = False
                    ch = layeractivechunks[index]

                    # print(i,l)
                    # print(l[1],l[0])
                    v = startp - newsample
                    distance = -v.length

                    if layer[1] <= distance <= layer[0]:
                        lastlayer = currentlayer
                        currentlayer = index

                        if lastsample is not None and lastlayer is not None and currentlayer is not None \
                                and lastlayer != currentlayer:  # sampling for sorted paths in layers-
                            # to go to the border of the sampled layer at least...
                            # there was a bug here, but should be fixed.
                            if currentlayer < lastlayer:
                                growing = True
                                r = range(currentlayer, lastlayer)
                                spliti = 1
                            else:
                                r = range(lastlayer, currentlayer)
                                growing = False
                                spliti = 0
                            # print(r)
                            li = 0

                            for ls in r:
                                splitdistance = layers[ls][1]

                                ratio = (splitdistance - lastdistance) / (distance - lastdistance)
                                # print(ratio)
                                betweensample = lastsample + (newsample - lastsample) * ratio
                                # this probably doesn't work at all!!!! check this algoritm>
                                betweenrotation = tuple_add(lastrotation,
                                                            tuple_mul(tuple_sub(rotation, lastrotation), ratio))
                                # startpoint = retract point, it has to be always available...
                                betweenstartpoint = laststartpoint + (startp - laststartpoint) * ratio
                                # here, we need to have also possible endpoints always..
                                betweenendpoint = lastendpoint + (endp - lastendpoint) * ratio
                                if growing:
                                    if li > 0:
                                        layeractivechunks[ls].points.insert(-1, betweensample)
                                        layeractivechunks[ls].rotations.insert(-1, betweenrotation)
                                        layeractivechunks[ls].startpoints.insert(-1, betweenstartpoint)
                                        layeractivechunks[ls].endpoints.insert(-1, betweenendpoint)
                                    else:
                                        layeractivechunks[ls].points.append(betweensample)
                                        layeractivechunks[ls].rotations.append(betweenrotation)
                                        layeractivechunks[ls].startpoints.append(betweenstartpoint)
                                        layeractivechunks[ls].endpoints.append(betweenendpoint)
                                    layeractivechunks[ls + 1].points.append(betweensample)
                                    layeractivechunks[ls + 1].rotations.append(betweenrotation)
                                    layeractivechunks[ls + 1].startpoints.append(betweenstartpoint)
                                    layeractivechunks[ls + 1].endpoints.append(betweenendpoint)
                                else:

                                    layeractivechunks[ls].points.insert(-1, betweensample)
                                    layeractivechunks[ls].rotations.insert(-1, betweenrotation)
                                    layeractivechunks[ls].startpoints.insert(-1, betweenstartpoint)
                                    layeractivechunks[ls].endpoints.insert(-1, betweenendpoint)

                                    layeractivechunks[ls + 1].points.append(betweensample)
                                    layeractivechunks[ls + 1].rotations.append(betweenrotation)
                                    layeractivechunks[ls + 1].startpoints.append(betweenstartpoint)
                                    layeractivechunks[ls + 1].endpoints.append(betweenendpoint)

                                # layeractivechunks[ls+1].points.insert(0,betweensample)
                                li += 1
                        # this chunk is terminated, and allready in layerchunks /

                        # ch.points.append(betweensample)#
                        ch.points.append(newsample)
                        ch.rotations.append(rotation)
                        ch.startpoints.append(startp)
                        ch.endpoints.append(endp)
                        lastdistance = distance

                    elif layer[1] > distance:
                        v = sweepvect * layer[1]
                        p = startp - v
                        ch.points.append(p)
                        ch.rotations.append(rotation)
                        ch.startpoints.append(startp)
                        ch.endpoints.append(endp)
                    elif layer[0] < distance:  # retract to original track
                        ch.points.append(startp)
                        ch.rotations.append(rotation)
                        ch.startpoints.append(startp)
                        ch.endpoints.append(endp)

            lastsample = newsample
            lastrotation = rotation
            laststartpoint = startp
            lastendpoint = endp

        for index, layer in enumerate(layers):
            ch = layeractivechunks[index]
            if len(ch.points) > 0:
                layerchunks[index].append(ch)
                thisrunchunks[index].append(ch)
                layeractivechunks[index] = camPathChunk([])

            if operation.strategy == 'PARALLEL' or operation.strategy == 'CROSS' or operation.strategy == 'OUTLINEFILL':
                parentChildDist(thisrunchunks[index], lastrunchunks[index], operation)

        lastrunchunks = thisrunchunks

    progress('checking relations between paths')

    chunks = []
    for index, layer in enumerate(layers):
        chunks.extend(layerchunks[index])

    return chunks

def extendChunks5axis(chunks, operation):
    scene = bpy.context.scene
    machine = scene.cam_machine

    if machine.use_position_definitions:
        cutterstart = Vector((machine.starting_position.x, machine.starting_position.y,
                              max(operation.max.z, machine.starting_position.z)))
    else:
        free_height = operation.free_height
        cutterstart = Vector((0, 0, max(operation.max.z, free_height))) 

    cutterend = Vector((0, 0, operation.min.z))

    print('rot', operation.rotationaxes)
    a, b = operation.rotationaxes
    for chunk in chunks:
        for v in chunk.points:
            cutterstart.x = v[0]
            cutterstart.y = v[1]
            cutterend.x = v[0]
            cutterend.y = v[1]
            chunk.startpoints.append(cutterstart.to_tuple())
            chunk.endpoints.append(cutterend.to_tuple())
            chunk.rotations.append((a, b, 0))

def curveToShapely(cob, use_modifiers=False):
    chunks = curveToChunks(cob, use_modifiers)
    polys = chunksToShapely(chunks)
    return polys

def silhoueteOffset(context, offset, style=1, mitrelimit=1.0):
    bpy.context.scene.cursor.location = (0, 0, 0)
    object = context
    if object.type == 'CURVE' or object.type == 'FONT':
        silhouette = curveToShapely(object)
    else:
        silhouette = getObjectSilhouete('OBJECTS', [object])

    multiPolygon = shapely.ops.unary_union(silhouette)
    multiPolygon = multiPolygon.buffer(offset, cap_style=1, join_style=style, resolution=16, mitre_limit=mitrelimit)
    return shapelyToCurve(f"{object.name} _offset_  {round(offset, 5)}", multiPolygon, object.location.z)

def polygonBoolean(context, boolean_type):
    bpy.context.scene.cursor.location = (0, 0, 0)
    ob = bpy.context.active_object
    obs = []
    for ob1 in bpy.context.selected_objects:
        if ob1 != ob:
            obs.append(ob1)
    plist = curveToShapely(ob)
    p1 = MultiPolygon(plist)
    polys = []
    for o in obs:
        plist = curveToShapely(o)
        p2 = MultiPolygon(plist)
        polys.append(p2)
    # print(polys)
    if boolean_type == 'UNION':
        for p2 in polys:
            p1 = p1.union(p2)
    elif boolean_type == 'DIFFERENCE':
        for p2 in polys:
            p1 = p1.difference(p2)
    elif boolean_type == 'INTERSECT':
        for p2 in polys:
            p1 = p1.intersection(p2)

    shapelyToCurve('boolean', p1, ob.location.z)
    # bpy.ops.object.convert(target='CURVE')
    # bpy.context.scene.cursor_location=ob.location
    # bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    return {'FINISHED'}

def polygonConvexHull(context):
    coords = []

    bpy.ops.object.duplicate()
    bpy.ops.object.join()
    bpy.context.object.data.dimensions = '3D'  #  force curve to be a 3D curve
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.active_object.name = "_tmp"

    bpy.ops.object.convert(target='MESH')
    obj = bpy.context.view_layer.objects.active

    for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
        c = (v.co.x, v.co.y)
        coords.append(c)

    simple.select_multiple('_tmp')  # delete temporary mesh
    simple.select_multiple('ConvexHull')  # delete old hull

    points = sgeometry.MultiPoint(coords)  # convert coordinates to shapely MultiPoint datastructure

    hull = points.convex_hull
    shapelyToCurve('ConvexHull', hull, 0.0)

    return {'FINISHED'}


def Helix(r, np, zstart, pend, rev):
    c = []
    pi = math.pi
    v = mathutils.Vector((r, 0, zstart))
    e = mathutils.Euler((0, 0, 2.0 * pi / np))
    zstep = (zstart - pend[2]) / (np * rev)
    for a in range(0, int(np * rev)):
        c.append((v.x + pend[0], v.y + pend[1], zstart - (a * zstep)))
        v.rotate(e)
    c.append((v.x + pend[0], v.y + pend[1], pend[2]))

    return c


def comparezlevel(x):
    return x[5]


def overlaps(bb1, bb2):  # true if bb1 is child of bb2
    ch1 = bb1
    ch2 = bb2
    if (ch2[1] > ch1[1] > ch1[0] > ch2[0] and ch2[3] > ch1[3] > ch1[2] > ch2[2]):
        return True


def connectChunksLow(chunks, operation):
    """ connects chunks that are close to each other without lifting, sampling them 'low' """
    if not operation.stay_low or (operation.strategy == 'CARVE' and operation.carve_depth > 0):
        return chunks

    connectedchunks = []
    chunks_to_resample = []  # for OpenCAMLib sampling
    mergeDistance = 3 * operation.dist_between_paths
    if operation.strategy == 'PENCIL':  # this is bigger for pencil path since it goes on the surface to clean up the rests,
        # and can go to close points on the surface without fear of going deep into material.
        mergeDistance = 10 * operation.dist_between_paths

    if operation.strategy == 'MEDIAL_AXIS':
        mergeDistance = 1 * operation.medial_axis_subdivision

    if operation.parallel_step_back:
        mergeDistance *= 2

    if operation.merge_dist > 0:
        mergeDistance = operation.merge_dist
    # mergedist=10
    lastChunk = None
    i = len(chunks)
    pos = (0, 0, 0)

    for chunk in chunks:
        if len(chunk.points) > 0:
            if lastChunk is not None and (chunk.distStart(pos, operation) < mergeDistance):
                # CARVE should lift allways, when it goes below surface...
                # print(mergedist,ch.dist(pos,o))
                if operation.strategy == 'PARALLEL' or operation.strategy == 'CROSS' or operation.strategy == 'PENCIL':
                    # for these paths sorting happens after sampling, thats why they need resample the connection
                    between = samplePathLow(operation, lastChunk, chunk, True)
                else:
                    # print('addbetwee')
                    between = samplePathLow(operation, lastChunk, chunk,
                                            False)  # other paths either dont use sampling or are sorted before it.
                if operation.optimisation.use_opencamlib and operation.optimisation.use_exact and (
                        operation.strategy == 'PARALLEL' or operation.strategy == 'CROSS' or operation.strategy == 'PENCIL'):
                    chunks_to_resample.append(
                        (connectedchunks[-1], len(connectedchunks[-1].points), len(between.points)))

                connectedchunks[-1].points.extend(between.points)
                connectedchunks[-1].points.extend(chunk.points)
            else:
                connectedchunks.append(chunk)
            lastChunk = chunk
            pos = lastChunk.points[-1]

    if operation.optimisation.use_opencamlib and operation.optimisation.use_exact and operation.strategy != 'CUTOUT' and operation.strategy != 'POCKET':
        oclResampleChunks(operation, chunks_to_resample)

    return connectedchunks


def getClosest(operation, position, chunks):
    # ch=-1
    mind = 2000
    d = 100000000000
    ch = None
    for chtest in chunks:
        cango = True
        for child in chtest.children:  # here was chtest.getNext==chtest, was doing recursion error and slowing down.
            if not child.sorted:
                cango = False
                break
        if cango:
            d = chtest.dist(position, operation)
            if d < mind:
                ch = chtest
                mind = d
    return ch


def sortChunks(chunks, operation):
    if operation.strategy != 'WATERLINE':
        progress('sorting paths')
    sys.setrecursionlimit(100000)  
    sortedChunks = []

    lastChunk = None
    position = (0, 0, 0)

    while len(chunks) > 0:
        chunk = None
        if len(sortedChunks) == 0 or len(
                lastChunk.parents) == 0:  # first chunk or when there are no parents -> parents come after children here...
            chunk = getClosest(operation, position, chunks)
        elif len(lastChunk.parents) > 0:  # looks in parents for next candidate, recursively
            for parent in lastChunk.parents:
                chunk = parent.getNextClosest(operation, position)
                if chunk is not None:
                    break
            if chunk is None:
                chunk = getClosest(operation, position, chunks)

        if chunk is not None:  # found next chunk, append it to list
            # only adaptdist the chunk if it has not been sorted before
            if not chunk.sorted:
                chunk.adaptdist(position, operation)
                chunk.sorted = True
            # print(len(ch.parents),'children')
            chunks.remove(chunk)
            sortedChunks.append(chunk)
            lastChunk = chunk
            position = lastChunk.points[-1]
        # print(i, len(chunks))
        # experimental fix for infinite loop problem
        # else:
        # THIS PROBLEM WASN'T HERE AT ALL. but keeping it here, it might fix the problems somwhere else:)
        # can't find chunks close enough and still some chunks left
        # to be sorted. For now just move the remaining chunks over to
        # the sorted list.
        # This fixes an infinite loop condition that occurs sometimes.
        # This is a bandaid fix: need to find the root cause of this problem
        # suspect it has to do with the sorted flag?
        # print("no chunks found closest. Chunks not sorted: ", len(chunks))
        # sortedchunks.extend(chunks)
        # chunks[:] = []
    if operation.strategy == 'POCKET' and operation.pocket_option == 'OUTSIDE':
        sortedChunks.reverse()

    sys.setrecursionlimit(1000)
    if operation.strategy != 'DRILL' and operation.strategy != 'OUTLINEFILL':
        # THIS SHOULD AVOID ACTUALLY MOST STRATEGIES, THIS SHOULD BE DONE MANUALLY,
        # BECAUSE SOME STRATEGIES GET SORTED TWICE.
        sortedChunks = connectChunksLow(sortedChunks, operation)
    return sortedChunks

def getVectorRight(lastVector, verts):  # most right vector from a set regarding angle..
    defa = 100
    v1 = Vector(lastVector[0])
    v2 = Vector(lastVector[1])
    va = v2 - v1
    for i, v in enumerate(verts):
        if v != lastVector[0]:
            vb = Vector(v) - v2
            a = va.angle_signed(Vector(vb))

            if a < defa:
                defa = a
                returnvec = i
    return returnvec

def cleanUpDict(ndict):
    print('removing lonely points')  # now it should delete all junk first, iterate over lonely verts.
    # found_solitaires=True
    # while found_solitaires:
    found_solitaires = False
    keys = []
    keys.extend(ndict.keys())
    removed = 0
    for k in keys:
        print(k)
        print(ndict[k])
        if len(ndict[k]) <= 1:
            newcheck = [k]
            while (len(newcheck) > 0):
                v = newcheck.pop()
                if len(ndict[v]) <= 1:
                    for v1 in ndict[v]:
                        newcheck.append(v)
                    dictRemove(ndict, v)
            removed += 1
            found_solitaires = True
    print(removed)

def dictRemove(dict, val):
    for v in dict[val]:
        dict[v].remove(val)
    dict.pop(val)

def addLoop(parentloop, start, end):
    added = False
    for l in parentloop[2]:
        if l[0] < start and l[1] > end:
            addLoop(l, start, end)
            return
    parentloop[2].append([start, end, []])

def cutloops(csource, parentloop, loops):
    copy = csource[parentloop[0]:parentloop[1]]

    for li in range(len(parentloop[2]) - 1, -1, -1):
        l = parentloop[2][li]
        # print(l)
        copy = copy[:l[0] - parentloop[0]] + copy[l[1] - parentloop[0]:]
    loops.append(copy)
    for l in parentloop[2]:
        cutloops(csource, l, loops)

def getOperationSilhouete(operation):
    if operation.update_silhouete_tag:
        stype = "IMAGE"
        if operation.geometry_source in ["OBJECT", "COLLECTION"]:
            if not operation.onlycurves:
                stype = 'OBJECTS'
            else:
                stype = 'CURVES'

        totfaces = 0
        if stype == 'OBJECTS':
            for ob in operation.objects:
                if ob.type == 'MESH':
                    totfaces += len(ob.data.polygons)

        if stype == 'IMAGE':
            print('image method')
            samples = renderSampleImage(operation)
            if stype == 'OBJECTS':
                i = samples > operation.minz - 0.0000001
                # numpy.min(operation.zbuffer_image)-0.0000001#
                # #the small number solves issue with totally flat meshes, which people tend to mill instead of
                # proper pockets. then the minimum was also maximum, and it didn't detect contour.
            else:
                i = samples > numpy.min(operation.zbuffer_image)  # this fixes another numeric imprecision.

            chunks = imageToChunks(operation, i)
            operation.silhouete = chunksToShapely(chunks)
        else:
            print('object method for retrieving silhouette')  #
            operation.silhouete = getObjectSilhouete(stype, objects=operation.objects,
                                                     use_modifiers=operation.use_modifiers)

        operation.update_silhouete_tag = False
    return operation.silhouete

def getObjectSilhouete(stype, objects=None, use_modifiers=False):
    if stype == 'CURVES': 
        allchunks = []
        for object in objects:
            chunks = curveToChunks(object)
            allchunks.extend(chunks)
        silhouete = chunksToShapely(allchunks)

    elif stype == 'OBJECTS':
        totalFaces = 0
        for object in objects:
            totalFaces += len(object.data.polygons)

        expiredTime = time.time()
        print('shapely getting silhouette')
        polys = []
        for object in objects:
            if use_modifiers:
                object = object.evaluated_get(bpy.context.evaluated_depsgraph_get())
                mesh = object.to_mesh()
            else:
                mesh = object.data
            matrixWorld = object.matrix_world

            mesh.calc_loop_triangles()

            print("TRANSFORM TRIANGLES")
            transformedTriangle = (
                (
                    (matrixWorld @ mesh.vertices[triangle.vertices[0]].co).xy,
                    (matrixWorld @ mesh.vertices[triangle.vertices[1]].co).xy,
                    (matrixWorld @ mesh.vertices[triangle.vertices[2]].co).xy
                )
                for triangle in mesh.loop_triangles)

            print("FILTER TRIANGLES")
            triangleIndexSequenceWithArea = (
                (triangle)
                for triangle in transformedTriangle
                if mathutils.geometry.area_tri(
                    triangle[0],
                    triangle[1],
                    triangle[2],
                ) > 0)

            print("CREATE POLYGONS FROM TRIANGLES")
            createdPolygons = (
                spolygon.Polygon(triangle)
                for triangle in triangleIndexSequenceWithArea
                )
            
            polys.extend(createdPolygons)

        if totalFaces < 2000000000000:
            print('Unary')
            time.sleep(5)
            polygon = sops.unary_union(polys)
        else:
            print('computing in parts')
            time.sleep(5)
            bigshapes = []
            i = 1
            part = 20000
            while i * part < totalFaces:
                print(i)
                ar = polys[(i - 1) * part:i * part]
                bigshapes.append(sops.unary_union(ar))
                i += 1
            if (i - 1) * part < totalFaces:
                last_ar = polys[(i - 1) * part:]
                bigshapes.append(sops.unary_union(last_ar))
            print('joining')
            polygon = sops.unary_union(bigshapes)

        print(time.time() - expiredTime)

        expiredTime = time.time()
        silhouete = [polygon]

    return silhouete

def getAmbient(operation):
    if operation.update_ambient_tag:

        m = 0
        if operation.ambient_cutter_restrict:
            m = operation.cutter_diameter / 2

        if operation.ambient_behaviour == 'AROUND':
            radius = operation.ambient_radius - m
            operation.ambient = getObjectOutline(radius, operation, True)
        else:
            operation.ambient = spolygon.Polygon(((operation.min.x + m, operation.min.y + m), (operation.min.x + m, operation.max.y - m),
                                          (operation.max.x - m, operation.max.y - m), (operation.max.x - m, operation.min.y + m)))

        if operation.use_limit_curve:
            if operation.limit_curve != '':
                limit_curve = bpy.data.objects[operation.limit_curve]
                polys = curveToShapely(limit_curve)
                operation.limit_poly = shapely.ops.unary_union(polys)

                if operation.ambient_cutter_restrict:
                    operation.limit_poly = operation.limit_poly.buffer(operation.cutter_diameter / 2, resolution=operation.optimisation.circle_detail)
            operation.ambient = operation.ambient.intersection(operation.limit_poly)
    operation.update_ambient_tag = False

def getObjectOutline(radius, operation, offset):

    offset = 1 if offset else -1
    join = 2 if operation.straight else 1
    outlines = []

    print("GET OPERATION SILHOUETTE")
    polygons = getOperationSilhouete(operation)

    print("CHECK IF IS INSTANCE")
    polygon_list = polygons if isinstance(polygons, list) else polygons.geoms

    print("SET POLYGONS")
    for polygon in polygon_list:
        if radius > 0:
            polygon = polygon.buffer(radius * offset, resolution=operation.optimisation.circle_detail, join_style=join, mitre_limit=2)
        outlines.append(polygon)

    print("MERGE OR DON'T MERGE")
    if operation.dont_merge:
        outline = sgeometry.MultiPolygon(outlines)
    else:
        outline = shapely.ops.unary_union(outlines)
    return outline


def addOrientationObject(o):
    """the orientation object should be used to set up orientations of the object for 4 and 5 axis milling."""
    name = o.name + ' orientation'
    s = bpy.context.scene
    if s.objects.find(name) == -1:
        bpy.ops.object.empty_add(type='ARROWS', align='WORLD', location=(0, 0, 0))

        ob = bpy.context.active_object
        ob.empty_draw_size = 0.05
        ob.show_name = True
        ob.name = name
    ob = s.objects[name]
    if o.machine_axes == '4':

        if o.rotary_axis_1 == 'X':
            ob.lock_rotation = [False, True, True]
            ob.rotation_euler[1] = 0
            ob.rotation_euler[2] = 0
        if o.rotary_axis_1 == 'Y':
            ob.lock_rotation = [True, False, True]
            ob.rotation_euler[0] = 0
            ob.rotation_euler[2] = 0
        if o.rotary_axis_1 == 'Z':
            ob.lock_rotation = [True, True, False]
            ob.rotation_euler[0] = 0
            ob.rotation_euler[1] = 0
    elif o.machine_axes == '5':
        ob.lock_rotation = [False, False, True]

        ob.rotation_euler[2] = 0  # this will be a bit hard to rotate.....


# def addCutterOrientationObject(o):

def getCAMPathObjectNameConventionFrom(name):
    return f"CAMPath_{name}"

def getCAMMachineObjectName():
    return f"CAMMachine"

def getCAMMaterialObjectName():
    return f"CAMMaterial"

def getCAMSimulationObjectNameConventionFrom(name):
    return f"CAMSimulation_{name}"

def removeOrientationObject(object):  # not working
    name = f"{object.name} orientation"
    if bpy.context.scene.objects.find(name) > -1:
        ob = bpy.context.scene.objects[name]
        delob(ob)

def addTranspMat(ob, mname, color, alpha):
    if mname in bpy.data.materials:
        mat = bpy.data.materials[mname]
    else:
        mat = bpy.data.materials.new(name=mname)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]

        # Assign it to object
        if ob.data.materials:
            ob.data.materials[0] = mat
        else:
            ob.data.materials.append(mat)

def getCentroidOfPoints(points):
    """
    Calculates and returns the centroid of the given points.

    Keyword arguments:
    points -- The points, where the centroid should be caluclated.
    """
    pointSummation = mathutils.Vector([0.0, 0.0])
    
    for point in points:
        pointSummation += point;
        
    pointCount = len(points)
    
    return pointSummation/pointCount

def createMeshWithConvexHullAndCentroid(convexHullPath, centroid):
    """
    Creates a convex hull mesh with the centroid given as the center point of the triangle fan.
    """
    pointCount = len(convexHullPath)
    
    mesh = []
    for i in range(pointCount):
        mesh.append([convexHullPath[i], convexHullPath[(i+1)%pointCount], centroid])
    
    return mesh
    
def getConvexHullMesh2D(objectPoints):
    """
    Creates a 2D convex hull based on the x and y components of the object points.
    """
    uniquePoints = numpy.unique(objectPoints, axis=0)
    uniquePoints = [mathutils.Vector(point).xy for point in uniquePoints]
    
    convexHullIndices = mathutils.geometry.convex_hull_2d(uniquePoints)
    
    convexHullPath = [uniquePoints[index] for index in convexHullIndices]
    centroidPoint = getCentroidOfPoints(convexHullPath)
    
    convexHullMesh = createMeshWithConvexHullAndCentroid(convexHullPath, centroidPoint)
    
    return convexHullMesh
    
def isPointInMesh(point, mesh):
    """
    Checks if the given point is in the 2D mesh. The mesh must conists as a series of triangles.
    """
    for face in mesh:
        isInFace = mathutils.geometry.intersect_point_tri_2d(point, face[0], face[1], face[2])
        
        if isInFace: return True
        
    return False

def placeObjectsUnder(sourceObjects, targetObject, offset):
    """
    Places a given set of source objects under a target object.
    The source objects are placed such that the bounding boxes of the source object are touching target object.
    The offset additionaly moves the source objects along the z axis.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    targetObjectWithModifiers = targetObject.evaluated_get(depsgraph) 
    targetObjectMatrix = targetObject.matrix_world
    targetObjectMesh = [(targetObjectMatrix @ vertex.co) for vertex in targetObjectWithModifiers.data.vertices]
    
    sourceObjectCount = len(sourceObjects)
    for objectIndex, sourceObject in enumerate(sourceObjects):

        print(f"({objectIndex+1}/{sourceObjectCount}) Placing object: {sourceObject.name}")
        sourceObjectBoundingBox = [mathutils.Vector(point) for point in sourceObject.bound_box]
        sourceObjectMatrix = sourceObject.matrix_world
        
        sourceObjectTransformedBoundingBox = [sourceObjectMatrix @ point for point in sourceObjectBoundingBox]
        sourceObjectMesh = getConvexHullMesh2D(sourceObjectTransformedBoundingBox)
        
        filteredVertices = filter(lambda vertex: isPointInMesh(vertex, sourceObjectMesh), targetObjectMesh)
        
        nextObject = next(filteredVertices, None)
        
        if nextObject == None:
            continue
        
        lowestDepth = nextObject.z
        
        for vertex in filteredVertices:
            if vertex.z < lowestDepth:
                lowestDepth = vertex.z
            
        sourceObject.location.z = lowestDepth - offset

def addMachineAreaObject():
    scene = bpy.context.scene
    machineName = getCAMMachineObjectName()  
    if scene.objects.get(machineName) is not None:
        object = scene.objects[machineName]
    else:
        oldunits = scene.unit_settings.system
        oldLengthUnit = scene.unit_settings.length_unit
        # need to be in metric units when adding machine mesh object
        # in order for location to work properly
        scene.unit_settings.system = 'METRIC'
        bpy.ops.mesh.primitive_cube_add(align='WORLD', enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))
        object = bpy.context.active_object
        object.name = machineName
        object.data.name = machineName
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE', action='TOGGLE')
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.subdivide(number_cuts=32, smoothness=0, quadcorner='STRAIGHT_CUT', fractal=0,
                               fractal_along_normal=0, seed=0)
        bpy.ops.mesh.select_nth(nth=2, offset=0)
        bpy.ops.mesh.delete(type='EDGE')
        bpy.ops.mesh.primitive_cube_add(align='WORLD', enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))

        bpy.ops.object.editmode_toggle()
        object.display_type = 'BOUNDS'
        object.hide_render = True
        object.hide_select = True
        scene.unit_settings.system = oldunits
        scene.unit_settings.length_unit = oldLengthUnit

    camRootCollection = getCAMRootCollection()
    reassignObjectsToCollection([object], camRootCollection)

    activeObject = bpy.context.active_object
    object.dimensions = bpy.context.scene.cam_machine.working_area
    if activeObject is not None:
        activeObject.select_set(True)

def reassignObjectsToCollection(objects, targetCollection):

    for object in objects:
        for collection in object.users_collection:
            collection.objects.unlink(object)
    
        targetCollection.objects.link(object)

def reassignCollectionsToCollection(collections, targetCollection):

    childrenCollectionNames = [collection.name for collection in collections]

    potentialParentCollections = list([collection for collection in bpy.data.collections if collection.name not in childrenCollectionNames])
    potentialParentCollections.append(bpy.context.scene.collection)

    for parentCollection in potentialParentCollections:
        childrenCollections = parentCollection.children
        for childCollection in collections:

            foundChildCollection = childrenCollections.get(childCollection.name)

            if foundChildCollection != None:
                childrenCollections.unlink(childCollection)

    for collection in collections:
        targetCollection.children.link(collection)

def createCollectionIfNotExists(collectionName):
    collection = bpy.data.collections.get(collectionName, None)

    if collection == None:
        collection = bpy.data.collections.new(collectionName)
        bpy.context.scene.collection.children.link(collection)

    return collection

def getCAMPathCollection():
    camPathCollectionName = "CAMPaths"
    camPathCollection = createCollectionIfNotExists(camPathCollectionName)

    camRootCollection = getCAMRootCollection()
    reassignCollectionsToCollection([camPathCollection], camRootCollection)
    return camPathCollection

def getCAMSimulationCollection():
    camSimulationCollectionName = "CAMSimulations"
    camSimulationCollection = createCollectionIfNotExists(camSimulationCollectionName)

    camRootCollection = getCAMRootCollection()
    reassignCollectionsToCollection([camSimulationCollection], camRootCollection)
    return camSimulationCollection

def getCAMRootCollection():
    rootCollectioName = "CAMRoot"
    rootCollection = createCollectionIfNotExists(rootCollectioName)
    return rootCollection

def addMaterialAreaObject():
    scene = bpy.context.scene
    operation = scene.cam_operations[scene.cam_active_operation]
    getOperationSources(operation)
    getBounds(operation)

    materialObjectName = getCAMMaterialObjectName()
    activeObject = bpy.context.active_object
    if scene.objects.get(materialObjectName) is not None:
        object = scene.objects[materialObjectName]
    else:
        bpy.ops.mesh.primitive_cube_add(align='WORLD', enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))
        object = bpy.context.active_object
        object.name = materialObjectName
        object.data.name = materialObjectName
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

        # addTranspMat(o, 'blue_transparent', (0.458695, 0.794658, 0.8), 0.1)
        object.display_type = 'BOUNDS'
        object.hide_render = True
        object.hide_select = True
        object.select_set(state=True, view_layer=None)
    # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    camRootCollection = getCAMRootCollection()
    reassignObjectsToCollection([object], camRootCollection)

    object.dimensions = bpy.context.scene.cam_machine.working_area

    object.dimensions = (
        operation.max.x - operation.min.x, operation.max.y - operation.min.y, operation.max.z - operation.min.z)
    object.location = (operation.min.x, operation.min.y, operation.max.z)

    if activeObject is not None:
        activeObject.select_set(True)

def getContainer():
    scene = bpy.context.scene
    if scene.objects.get('CAM_OBJECTS') is None:
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD')
        container = bpy.context.active_object
        container.name = 'CAM_OBJECTS'
        container.location = [0, 0, 0]
        container.hide = True
    else:
        container = scene.objects['CAM_OBJECTS']

    return container

# tools for voroni graphs all copied from the delaunayVoronoi addon:
class Point:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


def unique(L):
    """Return a list of unhashable elements in s, but without duplicates.
    [[1, 2], [2, 3], [1, 2]] >>> [[1, 2], [2, 3]]"""
    # For unhashable objects, you can sort the sequence and then scan from the end of the list,
    # deleting duplicates as you go
    nDupli = 0
    nZcolinear = 0
    L.sort()  # sort() brings the equal elements together; then duplicates are easy to weed out in a single pass.
    last = L[-1]
    for i in range(len(L) - 2, -1, -1):
        if last[:2] == L[i][:2]:  # XY coordinates compararison
            if last[2] == L[i][2]:  # Z coordinates compararison
                nDupli += 1  # duplicates vertices
            else:  # Z colinear
                nZcolinear += 1
            del L[i]
        else:
            last = L[i]
    return (nDupli,
            nZcolinear)  # list data type is mutable,
    # input list will automatically update and doesn't need to be returned


def checkEqual(lst):
    return lst[1:] == lst[:-1]

def prepareIndexed(o):
    scene = bpy.context.scene
    # first store objects positions/rotations
    o.matrices = []
    o.parents = []
    for object in o.objects:
        o.matrices.append(object.matrix_world.copy())
        o.parents.append(object.parent)

    # then rotate them
    for object in o.objects:
        object.select = True
    scene.objects.active = object
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    scene.cursor.location = (0, 0, 0)
    oriname = o.name + ' orientation'
    ori = scene.objects[oriname]
    o.orientation_matrix = ori.matrix_world.copy()
    o.rotationaxes = rotTo2axes(ori.rotation_euler, 'CA')
    ori.select = True
    scene.objects.active = ori
    # we parent all objects to the orientation object
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    for object in o.objects:
        object.select = False
    # then we move the orientation object to 0,0
    bpy.ops.object.location_clear()
    bpy.ops.object.rotation_clear()
    ori.select = False
    for object in o.objects:
        activate(object)

        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    # rot=ori.matrix_world.inverted()
    # #rot.x=-rot.x
    # #rot.y=-rot.y
    # #rot.z=-rot.z
    # rotationaxes = rotTo2axes(ori.rotation_euler,'CA')
    #
    # #bpy.context.space_data.pivot_point = 'CURSOR'
    # #bpy.context.space_data.pivot_point = 'CURSOR'
    #
    # for ob in o.objects:
    #     ob.rotation_euler.rotate(rot)


def cleanupIndexed(operation):
    s = bpy.context.scene
    oriname = operation.name + 'orientation'

    ori = s.objects[oriname]
    path = s.objects["cam_path_{}{}".format(operation.name)]

    ori.matrix_world = operation.orientation_matrix
    # set correct path location
    path.location = ori.location
    path.rotation_euler = ori.rotation_euler

    print(ori.matrix_world, operation.orientation_matrix)
    for i, ob in enumerate(operation.objects):  # TODO: fix this here wrong order can cause objects out of place
        ob.parent = operation.parents[i]
    for i, ob in enumerate(operation.objects):
        ob.matrix_world = operation.matrices[i]


def rotTo2axes(e, axescombination):
    """converts an orientation object rotation to rotation defined by 2 rotational axes on the machine -
    for indexed machining.
    attempting to do this for all axes combinations.
    """
    v = Vector((0, 0, 1))
    v.rotate(e)
    # if axes
    if axescombination == 'CA':
        v2d = Vector((v.x, v.y))
        a1base = Vector((0, -1))  # ?is this right?It should be vector defining 0 rotation
        if v2d.length > 0:
            cangle = a1base.angle_signed(v2d)
        else:
            return (0, 0)
        v2d = Vector((v2d.length, v.z))
        a2base = Vector((0, 1))
        aangle = a2base.angle_signed(v2d)
        print('angles', cangle, aangle)
        return (cangle, aangle)

    elif axescombination == 'CB':
        v2d = Vector((v.x, v.y))
        a1base = Vector((1, 0))  # ?is this right?It should be vector defining 0 rotation
        if v2d.length > 0:
            cangle = a1base.angle_signed(v2d)
        else:
            return (0, 0)
        v2d = Vector((v2d.length, v.z))
        a2base = Vector((0, 1))

        bangle = a2base.angle_signed(v2d)

        print('angles', cangle, bangle)

        return (cangle, bangle)

    # v2d=((v[a[0]],v[a[1]]))
    # angle1=a1base.angle(v2d)#C for ca
    # print(angle1)
    # if axescombination[0]=='C':
    #     e1=Vector((0,0,-angle1))
    # elif axescombination[0]=='A':#TODO: finish this after prototyping stage
    #     pass;
    # v.rotate(e1)
    # vbase=Vector(0,1,0)
    # bangle=v.angle(vzbase)
    # print(v)
    # print(bangle)

    return (angle1, angle2)


def reload_pathss(o):
    oname = "cam_path_" + o.name
    s = bpy.context.scene
    # for o in s.objects:
    ob = None
    old_pathmesh = None
    if oname in s.objects:
        old_pathmesh = s.objects[oname].data
        ob = s.objects[oname]

    picklepath = getCachePath(o) + '.pickle'
    f = open(picklepath, 'rb')
    d = pickle.load(f)
    f.close()

    # passed=False
    # while not passed:
    #     try:
    #         f=open(picklepath,'rb')
    #         d=pickle.load(f)
    #         f.close()
    #         passed=True
    #     except:
    #         print('sleep')
    #         time.sleep(1)

    o.info.warnings = d['warnings']
    o.info.duration = d['duration']
    verts = d['path']

    edges = []
    for a in range(0, len(verts) - 1):
        edges.append((a, a + 1))

    oname = "cam_path_" + o.name
    mesh = bpy.data.meshes.new(oname)
    mesh.name = oname
    mesh.from_pydata(verts, edges, [])

    if oname in s.objects:
        s.objects[oname].data = mesh
    else:
        object_utils.object_data_add(bpy.context, mesh, operator=None)
        ob = bpy.context.active_object
        ob.name = oname
    ob = s.objects[oname]
    ob.location = (0, 0, 0)
    o.path_object_name = oname
    o.changed = False

    if old_pathmesh is not None:
        bpy.data.meshes.remove(old_pathmesh)
