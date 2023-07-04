# blender CAM ops.py (c) 2012 Vilem Novak
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# blender operators definitions are in this file. They mostly call the functions from utils.py


import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

import threading
from cam import utils
from cam.exception import *

class threadCom:  # object passed to threads to read background process stdout info
    def __init__(self, o, proc):
        self.opname = o.name
        self.outtext = ''
        self.proc = proc
        self.lasttext = ''

def threadread(tcom):
    """reads stdout of background process, done this way to have it non-blocking"""
    inline = tcom.proc.stdout.readline()
    inline = str(inline)
    s = inline.find('progress{')
    if s > -1:
        e = inline.find('}')
        tcom.outtext = inline[s + 9:e]

@bpy.app.handlers.persistent
def timer_update(context):
    """monitoring of background processes"""

    scene = bpy.context.scene
    if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, 'cam_processes'):
        processes = bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
        for process in processes:
            # proc=p[1].proc
            readthread = process[0]
            tcom = process[1]
            if not readthread.is_alive():
                readthread.join()
                # readthread.
                tcom.lasttext = tcom.outtext
                if tcom.outtext != '':
                    print(tcom.opname, tcom.outtext)
                    tcom.outtext = ''

                if 'finished' in tcom.lasttext:
                    processes.remove(process)

                    o = scene.cam_operations[tcom.opname]
                    o.computing = False
                    utils.reload_paths(o)
                    update_zbufferimage_tag = False
                    update_offsetimage_tag = False
                else:
                    readthread = threading.Thread(target=threadread, args=([tcom]), daemon=True)
                    readthread.start()
                    process[0] = readthread
            o = scene.cam_operations[tcom.opname]  # changes
            o.outtext = tcom.lasttext  # changes

def getChainOperations(chain):
    """return chain operations, currently chain object can't store operations directly due to blender limitations"""
    chainOperations = []
    for operationReference in chain.operations:
        for operation in bpy.context.scene.cam_operations:
            if operation.name == operationReference.name:
                chainOperations.append(operation)
    return chainOperations

def fixUnits():
    """Sets up units for blender CAM"""
    scene = bpy.context.scene

    scene.unit_settings.system_rotation = 'DEGREES'

    scene.unit_settings.scale_length = 1.0
    # Blender CAM doesn't respect this property and there were users reporting problems, not seeing this was changed.

# move cam operation in the list up or down


