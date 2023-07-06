# blender CAM pattern.py (c) 2012 Vilem Novak
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

import time
import mathutils
from mathutils import *

from cam.simple import *
from cam.chunk import *
from cam import polygon_utils_cam
from cam.polygon_utils_cam import *
import shapely
from shapely import geometry as sgeometry
import numpy


def getPathPatternParallel(operation, angle):
    zlevel = 1
    pathDistance = operation.dist_between_paths
    pathstep = operation.dist_along_paths
    pathchunks = []

    xm = (operation.max.x + operation.min.x) / 2
    ym = (operation.max.y + operation.min.y) / 2
    vm = Vector((xm, ym, 0))
    xdim = operation.max.x - operation.min.x
    ydim = operation.max.y - operation.min.y
    dim = (xdim + ydim) / 2.0
    e = Euler((0, 0, angle))
    reverse = False
    if bpy.app.debug_value == 0:  
        dirvect = Vector((0, 1, 0))
        dirvect.rotate(e)
        dirvect.normalize()
        dirvect *= pathstep
        for a in range(int(-dim / pathDistance),
                       int(dim / pathDistance)):
            chunk = camPathChunk([])
            v = Vector((a * pathDistance, int(-dim / pathstep) * pathstep, 0))
            v.rotate(e)
            v += vm  # shifting for the rotation, so pattern rotates around middle...
            for b in range(int(-dim / pathstep), int(dim / pathstep)):
                v += dirvect

                if v.x > operation.min.x and v.x < operation.max.x and v.y > operation.min.y and v.y < operation.max.y:
                    chunk.points.append((v.x, v.y, zlevel))
            if (reverse and operation.movement_type == 'MEANDER') or (
                    operation.movement_type == 'CONVENTIONAL' and operation.spindle_rotation_direction == 'CW') or (
                    operation.movement_type == 'CLIMB' and operation.spindle_rotation_direction == 'CCW'):
                chunk.points.reverse()

            if len(chunk.points) > 0:
                pathchunks.append(chunk)
            if len(pathchunks) > 1 and reverse and operation.parallel_step_back and not operation.use_layers:
                # parallel step back - for finishing, best with climb movement, saves cutter life by going into
                # material with climb, while using move back on the surface to improve finish
                # (which would otherwise be a conventional move in the material)

                if operation.movement_type == 'CONVENTIONAL' or operation.movement_type == 'CLIMB':
                    pathchunks[-2].points.reverse()
                changechunk = pathchunks[-1]
                pathchunks[-1] = pathchunks[-2]
                pathchunks[-2] = changechunk

            reverse = not reverse
        # print (chunk.points)
    else:  # alternative algorithm with numpy, didn't work as should so blocked now...

        v = Vector((0, 1, 0))
        v.rotate(e)
        e1 = Euler((0, 0, -math.pi / 2))
        v1 = v.copy()
        v1.rotate(e1)

        axis_across_paths = numpy.array((numpy.arange(int(-dim / pathDistance), int(dim / pathDistance)) * pathDistance * v1.x + xm,
                                         numpy.arange(int(-dim / pathDistance), int(dim / pathDistance)) * pathDistance * v1.y + ym,
                                         numpy.arange(int(-dim / pathDistance), int(dim / pathDistance)) * 0))

        axis_along_paths = numpy.array((numpy.arange(int(-dim / pathstep), int(dim / pathstep)) * pathstep * v.x,
                                        numpy.arange(int(-dim / pathstep), int(dim / pathstep)) * pathstep * v.y,
                                        numpy.arange(int(-dim / pathstep),
                                                     int(dim / pathstep)) * 0 + zlevel))  # rotate this first
        progress(axis_along_paths)
        chunks = []
        for a in range(0, len(axis_across_paths[0])):
            nax = axis_along_paths.copy()
            nax[0] += axis_across_paths[0][a]
            nax[1] += axis_across_paths[1][a]

            xfitmin = nax[0] > operation.min.x
            xfitmax = nax[0] < operation.max.x
            xfit = xfitmin & xfitmax

            nax = numpy.array([nax[0][xfit], nax[1][xfit], nax[2][xfit]])
            yfitmin = nax[1] > operation.min.y
            yfitmax = nax[1] < operation.max.y
            yfit = yfitmin & yfitmax
            nax = numpy.array([nax[0][yfit], nax[1][yfit], nax[2][yfit]])
            chunks.append(nax.swapaxes(0, 1))

        pathchunks = []
        for ch in chunks:
            ch = ch.tolist()
            pathchunks.append(camPathChunk(ch))

    return pathchunks


def getPathPattern(operation):
    operation = operation
    t = time.time()
    progress('building path pattern')
    minx, miny, minz, maxx, maxy, maxz = operation.min.x, operation.min.y, operation.min.z, operation.max.x, operation.max.y, operation.max.z

    pathchunks = []

    zlevel = 1  # minz#this should do layers...
    if operation.strategy == 'PARALLEL':
        pathchunks = getPathPatternParallel(operation, operation.parallel_angle)
    elif operation.strategy == 'CROSS':

        pathchunks.extend(getPathPatternParallel(operation, operation.parallel_angle))
        pathchunks.extend(getPathPatternParallel(operation, operation.parallel_angle - math.pi / 2.0))

    elif operation.strategy == 'BLOCK':

        pathd = operation.dist_between_paths
        pathstep = operation.dist_along_paths
        maxxp = maxx
        maxyp = maxy
        minxp = minx
        minyp = miny
        x = 0.0
        y = 0.0

        chunk = camPathChunk([])
        i = 0
        while maxxp - minxp > 0 and maxyp - minyp > 0:

            y = minyp
            for a in range(ceil(minxp / pathstep), ceil(maxxp / pathstep), 1):
                x = a * pathstep
                chunk.points.append((x, y, zlevel))

            if i > 0:
                minxp += pathd
            chunk.points.append((maxxp, minyp, zlevel))

            x = maxxp

            for a in range(ceil(minyp / pathstep), ceil(maxyp / pathstep), 1):
                y = a * pathstep
                chunk.points.append((x, y, zlevel))

            minyp += pathd
            chunk.points.append((maxxp, maxyp, zlevel))

            y = maxyp
            for a in range(floor(maxxp / pathstep), ceil(minxp / pathstep), -1):
                x = a * pathstep
                chunk.points.append((x, y, zlevel))

            maxxp -= pathd
            chunk.points.append((minxp, maxyp, zlevel))

            x = minxp
            for a in range(floor(maxyp / pathstep), ceil(minyp / pathstep), -1):
                y = a * pathstep
                chunk.points.append((x, y, zlevel))
            chunk.points.append((minxp, minyp, zlevel))

            maxyp -= pathd

            i += 1
        if operation.movement_insideout == 'INSIDEOUT':
            chunk.points.reverse()
        if (operation.movement_type == 'CLIMB' and operation.spindle_rotation_direction == 'CW') or (
                operation.movement_type == 'CONVENTIONAL' and operation.spindle_rotation_direction == 'CCW'):
            for si in range(0, len(chunk.points)):
                s = chunk.points[si]
                chunk.points[si] = (operation.max.x + operation.min.x - s[0], s[1], s[2])
        pathchunks = [chunk]

    elif operation.strategy == 'SPIRAL':
        chunk = camPathChunk([])
        pathd = operation.dist_between_paths
        pathstep = operation.dist_along_paths
        midx = (operation.max.x + operation.min.x) / 2
        midy = (operation.max.y + operation.min.y) / 2
        x = pathd / 4
        y = pathd / 4
        v = Vector((pathd / 4, 0, 0))

        # progress(x,y,midx,midy)
        e = Euler((0, 0, 0))
        pi = math.pi
        chunk.points.append((midx + v.x, midy + v.y, zlevel))
        while midx + v.x > operation.min.x or midy + v.y > operation.min.y:
            # v.x=x-midx
            # v.y=y-midy
            offset = 2 * v.length * pi
            e.z = 2 * pi * (pathstep / offset)
            v.rotate(e)

            v.length = (v.length + pathd / (offset / pathstep))
            # progress(v.x,v.y)
            if operation.max.x > midx + v.x > operation.min.x and operation.max.y > midy + v.y > operation.min.y:
                chunk.points.append((midx + v.x, midy + v.y, zlevel))
            else:
                pathchunks.append(chunk)
                chunk = camPathChunk([])
        if len(chunk.points) > 0:
            pathchunks.append(chunk)
        if operation.movement_insideout == 'OUTSIDEIN':
            pathchunks.reverse()
        for chunk in pathchunks:
            if operation.movement_insideout == 'OUTSIDEIN':
                chunk.points.reverse()

            if (operation.movement_type == 'CONVENTIONAL' and operation.spindle_rotation_direction == 'CW') or (
                    operation.movement_type == 'CLIMB' and operation.spindle_rotation_direction == 'CCW'):
                for si in range(0, len(chunk.points)):
                    s = chunk.points[si]
                    chunk.points[si] = (operation.max.x + operation.min.x - s[0], s[1], s[2])

    elif operation.strategy == 'CIRCLES':

        pathd = operation.dist_between_paths
        pathstep = operation.dist_along_paths
        midx = (operation.max.x + operation.min.x) / 2
        midy = (operation.max.y + operation.min.y) / 2
        rx = operation.max.x - operation.min.x
        ry = operation.max.y - operation.min.y
        maxr = math.sqrt(rx * rx + ry * ry)

        # progress(x,y,midx,midy)
        e = Euler((0, 0, 0))
        pi = math.pi
        chunk = camPathChunk([])
        chunk.points.append((midx, midy, zlevel))
        pathchunks.append(chunk)
        r = 0

        while r < maxr:
            r += pathd
            chunk = camPathChunk([])
            firstchunk = chunk
            v = Vector((-r, 0, 0))
            steps = 2 * pi * r / pathstep
            e.z = 2 * pi / steps
            laststepchunks = []
            currentstepchunks = []
            for a in range(0, int(steps)):
                laststepchunks = currentstepchunks
                currentstepchunks = []

                if operation.max.x > midx + v.x > operation.min.x and operation.max.y > midy + v.y > operation.min.y:
                    chunk.points.append((midx + v.x, midy + v.y, zlevel))
                else:
                    if len(chunk.points) > 0:
                        chunk.closed = False
                        pathchunks.append(chunk)
                        currentstepchunks.append(chunk)
                        chunk = camPathChunk([])
                v.rotate(e)

            if len(chunk.points) > 0:
                chunk.points.append(firstchunk.points[0])
                if chunk == firstchunk:
                    chunk.closed = True
                pathchunks.append(chunk)
                currentstepchunks.append(chunk)
                chunk = camPathChunk([])
            for ch in laststepchunks:
                for p in currentstepchunks:
                    parentChildDist(p, ch, operation)

        if operation.movement_insideout == 'OUTSIDEIN':
            pathchunks.reverse()
        for chunk in pathchunks:
            if operation.movement_insideout == 'OUTSIDEIN':
                chunk.points.reverse()
            if (operation.movement_type == 'CONVENTIONAL' and operation.movement.spindle_rotation_direction == 'CW') or (
                    operation.movement_type == 'CLIMB' and operation.movement.spindle_rotation_direction == 'CCW'):
                chunk.points.reverse()
            # for si in range(0,len(chunk.points)):
            # s=chunk.points[si]
            # chunk.points[si]=(o.max.x+o.min.x-s[0],s[1],s[2])
    # pathchunks=sortChunks(pathchunks,o)not until they get hierarchy parents!
    elif operation.strategy == 'OUTLINEFILL':

        polys = operation.silhouete
        pathchunks = []
        chunks = []
        for p in polys:
            p = p.buffer(-operation.dist_between_paths / 10, operation.optimisation.circle_detail)
            # first, move a bit inside, because otherwise the border samples go crazy very often changin between
            # hit/non hit and making too many jumps in the path.
            chunks.extend(shapelyToChunks(p, 0))

        pathchunks.extend(chunks)
        lastchunks = chunks
        firstchunks = chunks

        approxn = (min(maxx - minx, maxy - miny) / operation.dist_between_paths) / 2
        i = 0

        for porig in polys:
            p = porig
            while not p.is_empty:
                p = p.buffer(-operation.dist_between_paths, operation.optimisation.circle_detail)
                if not p.is_empty:

                    nchunks = shapelyToChunks(p, zlevel)

                    if operation.movement_insideout == 'INSIDEOUT':
                        parentChildDist(lastchunks, nchunks, operation)
                    else:
                        parentChildDist(nchunks, lastchunks, operation)
                    pathchunks.extend(nchunks)
                    lastchunks = nchunks
                percent = int(i / approxn * 100)
                progress('outlining polygons ', percent)
                i += 1
        pathchunks.reverse()
        if not operation.inverse:  # dont do ambient for inverse milling
            lastchunks = firstchunks
            for p in polys:
                d = operation.dist_between_paths
                steps = operation.ambient_radius / operation.dist_between_paths
                for a in range(0, int(steps)):
                    dist = d
                    if a == int(operation.cutter_diameter / 2 / operation.dist_between_paths):
                        if operation.optimisation.use_exact:
                            dist += operation.optimisation.pixsize * 0.85
                            # this is here only because silhouette is still done with zbuffer method,
                            # even if we use bullet collisions.
                        else:
                            dist += operation.optimisation.pixsize * 2.5
                    p = p.buffer(dist, operation.optimisation.circle_detail)
                    if not p.is_empty:
                        nchunks = shapelyToChunks(p, zlevel)
                        if operation.movement_insideout == 'INSIDEOUT':
                            parentChildDist(nchunks, lastchunks, operation)
                        else:
                            parentChildDist(lastchunks, nchunks, operation)
                        pathchunks.extend(nchunks)
                        lastchunks = nchunks

        if operation.movement_insideout == 'OUTSIDEIN':
            pathchunks.reverse()

        for chunk in pathchunks:
            if operation.movement_insideout == 'OUTSIDEIN':
                chunk.points.reverse()
            if (operation.movement_type == 'CLIMB' and operation.movement.spindle_rotation_direction == 'CW') or (
                    operation.movement_type == 'CONVENTIONAL' and operation.movement.spindle_rotation_direction == 'CCW'):
                chunk.points.reverse()

        chunksRefine(pathchunks, operation)
    progress(time.time() - t)
    return pathchunks


def getPathPattern4axis(operation):
    operation = operation
    t = time.time()
    progress('building path pattern')
    minx, miny, minz, maxx, maxy, maxz = operation.min.x, operation.min.y, operation.min.z, operation.max.x, operation.max.y, operation.max.z
    pathchunks = []
    zlevel = 1  # minz#this should do layers...

    # set axes for various options, Z option is obvious nonsense now.
    if operation.rotary_axis_1 == 'X':
        a1 = 0
        a2 = 1
        a3 = 2
    if operation.rotary_axis_1 == 'Y':
        a1 = 1
        a2 = 0
        a3 = 2
    if operation.rotary_axis_1 == 'Z':
        a1 = 2
        a2 = 0
        a3 = 1

    operation.max.z = operation.maxz
    # set radius for all types of operation
    radius = max(operation.max.z, 0.0001)
    radiusend = operation.min.z

    mradius = max(radius, radiusend)
    circlesteps = (mradius * pi * 2) / operation.dist_along_paths
    circlesteps = max(4, circlesteps)
    anglestep = 2 * pi / circlesteps
    # generalized rotation
    e = Euler((0, 0, 0))
    e[a1] = anglestep

    # generalized length of the operation
    maxl = operation.max[a1]
    minl = operation.min[a1]
    steps = (maxl - minl) / operation.dist_between_paths

    # set starting positions for cutter e.t.c.
    cutterstart = Vector((0, 0, 0))
    cutterend = Vector((0, 0, 0))  # end point for casting

    if operation.strategy4axis == 'PARALLELR':

        for a in range(0, floor(steps) + 1):
            chunk = camPathChunk([])

            cutterstart[a1] = operation.min[a1] + a * operation.dist_between_paths
            cutterend[a1] = cutterstart[a1]

            cutterstart[a2] = 0  # radius
            cutterend[a2] = 0  # radiusend

            cutterstart[a3] = radius
            cutterend[a3] = radiusend

            for b in range(0, floor(circlesteps) + 1):
                # print(cutterstart,cutterend)
                chunk.startpoints.append(cutterstart.to_tuple())
                chunk.endpoints.append(cutterend.to_tuple())
                rot = [0, 0, 0]
                rot[a1] = a * 2 * pi + b * anglestep

                chunk.rotations.append(rot)
                cutterstart.rotate(e)
                cutterend.rotate(e)

            chunk.depth = radiusend - radius
            # last point = first
            chunk.startpoints.append(chunk.startpoints[0])
            chunk.endpoints.append(chunk.endpoints[0])
            chunk.rotations.append(chunk.rotations[0])

            pathchunks.append(chunk)

    if operation.strategy4axis == 'PARALLEL':
        circlesteps = (mradius * pi * 2) / operation.dist_between_paths
        steps = (maxl - minl) / operation.dist_along_paths

        anglestep = 2 * pi / circlesteps
        # generalized rotation
        e = Euler((0, 0, 0))
        e[a1] = anglestep

        reverse = False

        for b in range(0, floor(circlesteps) + 1):
            chunk = camPathChunk([])
            cutterstart[a2] = 0
            cutterstart[a3] = radius

            cutterend[a2] = 0
            cutterend[a3] = radiusend

            e[a1] = anglestep * b

            cutterstart.rotate(e)
            cutterend.rotate(e)

            for a in range(0, floor(steps) + 1):
                cutterstart[a1] = operation.min[a1] + a * operation.dist_along_paths
                cutterend[a1] = cutterstart[a1]
                chunk.startpoints.append(cutterstart.to_tuple())
                chunk.endpoints.append(cutterend.to_tuple())
                rot = [0, 0, 0]
                rot[a1] = b * anglestep
                chunk.rotations.append(rot)

            chunk.depth = radiusend - radius
            pathchunks.append(chunk)

            if (reverse and operation.movement_type == 'MEANDER') or (
                    operation.movement_type == 'CONVENTIONAL' and operation.spindle_rotation_direction == 'CW') or (
                    operation.movement_type == 'CLIMB' and operation.spindle_rotation_direction == 'CCW'):
                chunk.reverse()

            reverse = not reverse

    if operation.strategy4axis == 'HELIX':
        print('helix')

        a1step = operation.dist_between_paths / circlesteps

        chunk = camPathChunk([])  # only one chunk, init here

        for a in range(0, floor(steps) + 1):

            cutterstart[a1] = operation.min[a1] + a * operation.dist_between_paths
            cutterend[a1] = cutterstart[a1]
            cutterstart[a2] = 0
            cutterstart[a3] = radius
            cutterend[a3] = radiusend

            for b in range(0, floor(circlesteps) + 1):
                # print(cutterstart,cutterend)
                cutterstart[a1] += a1step
                cutterend[a1] += a1step
                chunk.startpoints.append(cutterstart.to_tuple())
                chunk.endpoints.append(cutterend.to_tuple())

                rot = [0, 0, 0]
                rot[a1] = a * 2 * pi + b * anglestep
                chunk.rotations.append(rot)

                cutterstart.rotate(e)
                cutterend.rotate(e)

            chunk.depth = radiusend - radius

        pathchunks.append(chunk)
    # print(chunk.startpoints)
    # print(pathchunks)
    # sprint(len(pathchunks))
    # print(o.strategy4axis)
    return pathchunks
