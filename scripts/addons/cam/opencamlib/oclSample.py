try:
    import ocl
except ImportError:
    try:
        import opencamlib as ocl
    except ImportError:
        pass

from io_mesh_stl import blender_utils
import mathutils
import math
from cam.exception import *

OCL_SCALE = 1000.0

def get_oclSTL(operation):

    oclSTL = ocl.STLSurf()

    found_mesh=False
    for collision_object in operation.objects:
        if collision_object.type in ["MESH", "CURVE", "FONT", "SURFACE"]:
            found_mesh=True
            global_matrix = mathutils.Matrix.Identity(4)

            print("GENERATE MESH")
            faces = blender_utils.faces_from_mesh(collision_object, global_matrix, operation.use_modifiers)

            print("CALCULATE FACES")
            triangles = (
                ocl.Triangle(
                    ocl.Point(face[0][0]*OCL_SCALE, face[0][1]*OCL_SCALE, (face[0][2]+operation.skin)*OCL_SCALE),
                    ocl.Point(face[1][0]*OCL_SCALE, face[1][1]*OCL_SCALE, (face[1][2]+operation.skin)*OCL_SCALE),
                    ocl.Point(face[2][0]*OCL_SCALE, face[2][1]*OCL_SCALE, (face[2][2]+operation.skin)*OCL_SCALE)
                )
                for face in faces
            )

            print("ADD FACES")
            for triangle in triangles:
                oclSTL.addTriangle(triangle)

    if not found_mesh:
        raise CamException("This operation requires a mesh or curve object or equivalent (e.g. text, volume).")
    
    return oclSTL

def ocl_sample(operation, chunks):

    print("GET OCLSTL")
    oclSTL = get_oclSTL(operation)

    op_cutter_diameter = operation.cutter_diameter
    op_cutter_tip_angle = math.radians(operation.cutter_tip_angle)/2

    cutter_length = 10
    if operation.cutter_type == "VCARVE": 
        cutter_length = (op_cutter_diameter/math.tan(op_cutter_tip_angle))/2
     
    cutter = None
    match operation.cutter_type:
        case "END":
            cutter = ocl.CylCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
        case "BALLNOSE":
            cutter = ocl.BallCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
        case "VCARVE":
            cutter = ocl.ConeCutter((op_cutter_diameter + operation.skin * 2) * 1000, op_cutter_tip_angle, cutter_length)
        case "CYLCONE":
            cutter = ocl.CylConeCutter((operation.cylcone_diameter/2+operation.skin)*2000, (op_cutter_diameter + operation.skin * 2) * 1000, op_cutter_tip_angle)
        case "BALLCONE":
            cutter = ocl.BallConeCutter((operation.ball_radius + operation.skin) * 2000,
                                    (op_cutter_diameter + operation.skin * 2) * 1000, op_cutter_tip_angle)
        case "BULLNOSE":
            cutter = ocl.BullCutter((op_cutter_diameter + operation.skin * 2) * 1000, operation.bull_corner_radius*1000, cutter_length)
        case _:
            print(f"Cutter unsupported: {operation.cutter_type}")
            quit()

    batchDropCutter = ocl.BatchDropCutter()
    batchDropCutter.setSTL(oclSTL)
    batchDropCutter.setCutter(cutter)

    print("APPEND POINTS")
    op_minz = operation.minz
    for chunk in chunks:
        for coord in chunk.points:
            batchDropCutter.appendPoint(ocl.CLPoint(coord[0] * 1000, coord[1] * 1000, op_minz * 1000))

    print("RUN OCL DROP CUTTER ALGORITHM")
    batchDropCutter.run()
    cl_points = batchDropCutter.getCLPoints()

    return cl_points
