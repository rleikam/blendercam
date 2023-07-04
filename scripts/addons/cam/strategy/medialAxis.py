import bpy
from bpy.props import *
from math import *
from bpy_extras import object_utils
from cam.chunk import *
from cam.collision import *
from cam import simple
from cam.simple import *
from cam.pattern import *
from cam import utils
from cam.utils import *
from cam import polygon_utils_cam
from cam.polygon_utils_cam import *
from cam.image_utils import *
from cam.strategy.utility import *
from concurrent.futures import ThreadPoolExecutor
from shapely import geometry as sgeometry

def medialAxis(operation):

    printProgressionTitle("OPERATION: MEDIAL AXIS")
    simple.remove_multiple("medialMesh")

    from cam.voronoi import computeVoronoiDiagram
    
    if not ToolManager.isToolSupported(operation.cutter_type):
        supportedTypes = ToolManager.getSupportedTools()
        supportedTypes = [typeName.lower().capitalize() for typeName in supportedTypes]
        supportedTypes = ", ".join(supportedTypes)

        operation.info.warnings += f"Only the following cutters are supported\n{supportedTypes}"
        return

    # remember resolutions of curves, to refine them,
    # otherwise medial axis computation yields too many branches in curved parts
    originalObjectResolutions = [
        (object, object.data.resolution_u)
        for object in operation.objects
        if object.type in ["CURVE", "FONT"]
        if object.data.resolution_u < 64
    ]

    for object, _ in originalObjectResolutions:
        object.data.resolution_u = 64
    print()

    printProgressionTitle("REFINING POLYGONS")

    polygons = utils.getOperationSilhouete(operation)
    polygonChunks = [shapelyToChunks(polygon, - 1) for polygon in polygons.geoms]
    polygonChunks = [
        chunksRefineThreshold(chunk, operation.medial_axis_subdivision, operation.medial_axis_threshold)
        for chunk in polygonChunks
    ]

    polygonVertices = list([
        list((point for chunk in polygonChunk for point in chunk.points))
        for polygonChunk in polygonChunks
    ])

    for vertice in polygonVertices:
        countDuplicatedPoints, countColinearPoints = unique(vertice)
        print(f"{countDuplicatedPoints} duplicates points ignored")
        print(f"{countColinearPoints} z colinear points excluded")

    print()

    printProgressionTitle("CHECK POLYGON VALIDITY")

    hasNotEnoughPoints = any([len(polygonVertice) < 3 for polygonVertice in polygonVertices])
    if hasNotEnoughPoints:
        print("Not enough points")
        return {'FINISHED'}
    
    for vertices in polygonVertices:
        xValues = [vertice[0] for vertice in vertices]
        yValues = [vertice[1] for vertice in vertices]
        if checkEqual(xValues) or checkEqual(yValues):
            print("Points are colinear")
            return {'FINISHED'}

    print("No errors")
    print()


    printProgressionTitle("TESSELATE POLYGONS")
    def tesselatePoints(verticePoints):
        verticeCount = len(verticePoints)
        print(F"Tesselate polygon with {verticeCount} points")

        xbuff, ybuff = 5, 5
        points = [Point(vertice[0], vertice[1]) for vertice in verticePoints]
        voronoiPoints, voronoiEdges = computeVoronoiDiagram(points, xbuff, ybuff, polygonsOutput=False, formatOutput=True)
        return [voronoiPoints, voronoiEdges]

    result = []
    polygonVoronoiPoints = []
    polygonVoronoiEdges = []
    with ThreadPoolExecutor() as executor:
        result = list(executor.map(tesselatePoints, polygonVertices))
        polygonVoronoiPoints = [diagram[0] for diagram in result]
        polygonVoronoiEdges = [diagram[1] for diagram in result]

    print()

    printProgressionTitle("MARK POINTS AND CALCULATE DEPTH")
    # Prepare tool specific data
    tool = ToolManager.constructToolFromOperation(operation)

    multiPolygon = sgeometry.shape(polygons)
    polygonMarkedPoints = []
    polygonCalculatedToolDepths = []
    for polygonIndex, (polygon, voronoiPoints) in enumerate(zip(polygons.geoms, polygonVoronoiPoints), 1):
        print("Polygon:", polygonIndex)

        startDepthOfPolygon = polygon.exterior.coords[0][2]

        print(f"Amount of points: {len(list(voronoiPoints))}")
        def processPoints(point):
            currentPoint = sgeometry.Point(point)
            pointIsInPolygon = polygon.contains(currentPoint)

            if pointIsInPolygon:
                pointDistance = multiPolygon.boundary.distance(currentPoint)
                pointToolDepth = -tool.calculateMillDepthFor(pointDistance*2) + startDepthOfPolygon
            else:
                pointToolDepth = None

            return [pointIsInPolygon, pointToolDepth]

        with ThreadPoolExecutor() as executor:
            result = list(executor.map(processPoints, voronoiPoints))

        markedPoints = [resultPoint[0] for resultPoint in result]
        calculatedToolDepth = [resultPoint[1] for resultPoint in result]

        polygonMarkedPoints.append(markedPoints)
        polygonCalculatedToolDepths.append(calculatedToolDepth)

    print()

    printProgressionTitle("FILTERING EDGES")
    filteredPolygonEdges = []
    for polygonIndex, (markedPoints, voronoiPoints, voronoiEdges) in enumerate(zip(polygonMarkedPoints, polygonVoronoiPoints, polygonVoronoiEdges), 1):
        print("Polygon:", polygonIndex)

        polygonEdges = [
            edge
            for edge in voronoiEdges
            if markedPoints[edge[0]] and markedPoints[edge[1]]
        ]

        filteredPolygonEdges.append(polygonEdges)

    print()

    printProgressionTitle("CONSTRUCT EDGE PATHS")
    polygonLines = []
    for polygonIndex, (voronoiPoints, polygonEdges, toolDepths) in enumerate(zip(polygonVoronoiPoints, filteredPolygonEdges, polygonCalculatedToolDepths), 1):
        print("Polygon:", polygonIndex)

        lines = []
        for polygonEdge in polygonEdges:

            firstEdgePoint = voronoiPoints[polygonEdge[0]]
            secondEdgePoint = voronoiPoints[polygonEdge[1]]

            firstEdgePointDepth = toolDepths[polygonEdge[0]]
            secondEdgePointDepth = toolDepths[polygonEdge[1]]

            firstLineStringPoint = [firstEdgePoint[0], firstEdgePoint[1], firstEdgePointDepth]
            secondLineStringPoint = [secondEdgePoint[0], secondEdgePoint[1], secondEdgePointDepth]

            line = sgeometry.LineString((firstLineStringPoint, secondLineStringPoint))
            lines.append(line)

        lines = shapely.ops.linemerge(lines)
        polygonLines.append(lines)

    print()

    printProgressionTitle("APPLY BUFFER POLYGON")
    operationDepth = abs(operation.minz)
    maximumToolDepth = tool.getMaximumToolLength()
    allowedToolDepth = operationDepth if maximumToolDepth > operationDepth else maximumToolDepth
    chunks = []
    for polygonIndex, (polygon, lines) in enumerate(zip(polygons.geoms, polygonLines)):
        bufferDistance = -tool.calculateMillDiameterFor(allowedToolDepth)/2
        bufferPolygon = polygon.buffer(bufferDistance, resolution=64)
        startDepthOfPolygon = polygon.exterior.coords[0][2]
        
        if bufferPolygon.geom_type in ["Polygon", "MultiPolygon"]:
            lines = lines.difference(bufferPolygon)
            chunks.extend(shapelyToChunks(bufferPolygon, -allowedToolDepth + startDepthOfPolygon))
        chunks.extend(shapelyToChunks(lines, 0))

        if operation.add_mesh_for_medial:
            polygon_utils_cam.shapelyToCurve('medialMesh', lines, 0.0)
            bpy.ops.object.convert(target='MESH')
    
    print()

    printProgressionTitle("SORTING CHUNKS")
    chunks = utils.sortChunks(chunks, operation)

    print()

    printProgressionTitle("SETTING LAYERS")
    layers = getLayers(operation, operation.maxz, operation.min.z)
    chunklayers = []

    for layer in layers:
        for chunk in chunks:
            if chunk.isbelowZ(layer[0]):
                newchunk = chunk.copy()
                newchunk.clampZ(layer[1])
                chunklayers.append(newchunk)

    if operation.first_down:
        chunklayers = utils.sortChunks(chunklayers, operation)

    if operation.add_mesh_for_medial:
        simple.join_multiple("medialMesh")

    printProgressionTitle("GENERATE MESH")
    chunksToMesh(chunklayers, operation)

    printProgressionTitle("ADD POCKET")
    if operation.add_pocket_for_medial:
        sourceName = None
        sourceType = None
        match operation.geometry_source:
            case "OBJECT":
                sourceName = operation.object_name
                sourceType = "OBJECT"
            case "COLLECTION":
                sourceName = operation.collection_name
                sourceType = "COLLECTION"
        Add_Pocket(sourceName, sourceType, maximumToolDepth, tool.calculateMillDiameterFor(allowedToolDepth))