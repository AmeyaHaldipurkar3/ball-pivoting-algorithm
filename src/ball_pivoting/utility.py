from glm import vec3, normalize, ivec3, cross, dot, distance
from data_structures.mesh_data_structures import *
from data_structures.grid import *
from math import sqrt, acos, pi
from typing import Optional, List, Deque
from collections import deque

def calculateBallCenter(face: Face, radius: float)-> Optional[vec3]:
    edge1: vec3 = face.vertices[2].position - face.vertices[0].position
    edge2: vec3 = face.vertices[1].position - face.vertices[0].position
    crossProduct: vec3 = cross(edge2, edge1)
    toCircumCircleCenter: vec3 = (cross(crossProduct, edge2)*dot(edge1, edge1) + cross(edge1, crossProduct)*dot(edge2, edge2)) / (2 * dot(crossProduct, crossProduct))
    circumCircleCenter: vec3 = face.vertices[0].position + toCircumCircleCenter

    hSquared: float = (radius*radius) - dot(toCircumCircleCenter, toCircumCircleCenter)
    if hSquared < 0:
        return None
    
    ballCenter: vec3 = circumCircleCenter + face.normal()*sqrt(hSquared)
    return ballCenter

def isBallEmpty(ballCenter: vec3, vertices: list[Vertex], radius: float)-> bool:
    epsilon: float = 1e-4
    for vertex in vertices:
        if distance(vertex.position, ballCenter) < (radius*radius - epsilon):
            return False
    
    return True
    
def findSeedTriangle(grid: Grid, radius: float)-> Optional[SeedResult]:
    for voxel in grid.voxels:
        avgNormal: vec3 = vec3([0, 0, 0])
        for vertex in voxel.vertices:
            avgNormal += vertex.normal
        avgNormal = normalize(avgNormal)

        for vertex1 in voxel.vertices:
            neighbors: list[Vertex] = grid.neighborhood(vertex1.position, [vertex1.position])
            if not neighbors:
                continue
            neighbors.sort(key = lambda vertex: distance(vertex.position, vertex1.position))
            
            for vertex2 in neighbors:
                for vertex3 in neighbors:
                    if vertex2 == vertex3:
                        continue
                    face: Face = Face(vertex1, vertex2, vertex3)
                    if(dot(face.normal(), avgNormal) < 0):
                        continue

                    ballCenter: Optional[vec3] = calculateBallCenter(face, radius)
                    if ballCenter and isBallEmpty(ballCenter, neighbors, radius):
                        vertex1.used = True
                        vertex2.used = True
                        vertex3.used = True
                        return SeedResult(face, ballCenter)
        
    return
    
def getActiveEdge(front: list[Edge])-> Optional[Edge]:
    while len(front) != 0:
        edge: Edge = front[-1]
        if edge.edgeStatus == EdgeStatus.ACTIVE:
            return edge
        front.pop()
    
    return

def ballPivot(edge: Edge, grid: Grid, radius: float)-> Optional[PivotResult]:
    edgeMidPoint: vec3 = (edge.startVertex.position + edge.endVertex.position) / 2.0
    oldCenter: vec3 = normalize(edge.center - edgeMidPoint)

    neighbors: list[Vertex] = grid.neighborhood(edgeMidPoint, [edge.startVertex.position, edge.endVertex.position, edge.oppVertex.position])

    #Debug logic needs to be added

    smallestAngle: float = float("inf")
    vertexWithSmallestAngle: Optional[Vertex] = None
    i: int = 0
    smallestNumber: int = 0
    
    for vertex in neighbors:
        i += 1
        newFaceNormal: Triangle = Triangle([edge.endVertex.position, edge.startVertex.position, vertex.position]).normal()
        if dot(newFaceNormal, vertex.normal) < 0:
            continue

        ballCenter: Optional[vec3] = calculateBallCenter(Face(edge.endVertex, edge.startVertex, vertex), radius)
        if not ballCenter:
            print("Issue with center computation")
            continue
        newCenter: vec3 = normalize(ballCenter - edgeMidPoint)
        newCenterFaceDotProduct:vec3 = dot(newCenter, newFaceNormal) #For debugging

        for e in vertex.edges:
            otherEndVertex: Vertex = e.endVertex if e.startVertex == vertex else e.startVertex
            if e.edgeStatus == EdgeStatus.INNER and (otherEndVertex == e.startVertex or otherEndVertex == e.endVertex):
                angle: float = acos(clamp(dot(oldCenter, newCenter), -1.0, 1.0))
                if (dot(cross(newCenter, oldCenter), e.startVertex.position - e.endVertex.position) < 0):
                    angle += pi
                if angle < smallestAngle:
                    smallestAngle = angle
                    vertexWithSmallestAngle = vertex
                    centerOfSmallest = ballCenter
                    smallestNumber = i

    if smallestAngle != float("inf"):
        if isBallEmpty(centerOfSmallest, neighbors, radius):
            return PivotResult(vertexWithSmallestAngle, centerOfSmallest)
    
    return []

def notUsed(vertex: Vertex)-> bool:
    return not vertex.used

def onFront(vertex: Vertex)-> bool:
    for edge in vertex.edges:
        if edge.edgeStatus == EdgeStatus.ACTIVE:
            return True
    return False

def remove(edge: Edge)-> None:
    edge.edgeStatus = EdgeStatus.INNER

def outputTriangle(face: Face, triangles: list[Triangle])-> None:
    triangles.append(Triangle([face.vertices[0].position, face.vertices[1].position, face.vertices[2].position]))

def join(e_ij: Edge, o_k: Vertex, ballCenter: vec3, front: list[Edge], edges: deque[Edge])-> tuple[Edge, Edge]:
    e_ik = Edge(e_ij.startVertex, o_k, e_ij.endVertex, ballCenter)
    e_kj = Edge(o_k, e_ij.endVertex, e_ij.startVertex, ballCenter)
    
    edges.append(e_ik)
    edges.append(e_kj)

    e_ik.next = e_kj
    e_ik.prev = e_ij.prev
    e_ij.prev.next = e_ik
    e_ij.startVertex.edges.append(e_ik)

    e_kj.prev = e_ik
    e_kj.next = e_ij.next
    e_ij.next.prev = e_kj
    e_ij.endVertex.edges.append(e_kj)

    o_k.used = True
    o_k.edges.append(e_ik)
    o_k.edges.append(e_kj)

    front.append(e_ik)
    front.append(e_kj)

    remove(e_ij)

    return (e_ik, e_kj)

def glue(edge1: Edge, edge2: Edge, front: list[Edge])-> None:
    if edge1.next == edge2 and edge1.prev == edge2 and edge2.next == edge1 and edge2.prev == edge1:
        remove(edge1)
        remove(edge2)
        return

    if edge1.next == edge2 and edge2.prev == edge1:
        edge1.prev.next = edge2.next
        edge2.next.prev = edge1.prev
        remove(edge1)
        remove(edge2)
        return 

    if edge1.prev == edge2 and edge2.next == edge1:
        edge1.next.prev = edge2.prev
        edge2.prev.next = edge1.next
        remove(edge1)
        remove(edge2)
        return 
    
    edge1.prev.next = edge2.next
    edge2.next.prev = edge1.prev
    edge1.next.prev = edge2.prev
    edge2.prev.next = edge1.next

    remove(edge1)
    remove(edge2)

def findReverseEdgeOnFront(edge: Edge)-> Optional[Edge]:
    for e in edge.startVertex.edges:
        if e.startVertex == edge.endVertex:
            return e 
    return None
    
def reconstruct(vertices: List[Vertex], radius: float)-> List[Triangle]:
    gridObj: Grid = Grid(vertices, radius)

    seedResult = findSeedTriangle(gridObj, radius)
    if not seedResult:
        print("No seed triangle found")
        return []
    
    seed, ballCenter = seedResult.face, seedResult.ballCenter
    if not ballCenter:
        print("Figure out what to do")
        return
    
    triangles: List[Triangle] = []
    outputTriangle(seed, triangles)

    edges: Deque[Edge] = deque()

    e0 = Edge(seed.vertices[0], seed.vertices[1], seed.vertices[2], ballCenter)
    e1 = Edge(seed.vertices[1], seed.vertices[2], seed.vertices[0], ballCenter)
    e2 = Edge(seed.vertices[2], seed.vertices[0], seed.vertices[1], ballCenter)

    edges.append(e0)
    edges.append(e1)
    edges.append(e2)

    e0.prev = e1.next = e2
    e0.next = e2.prev = e1
    e1.prev = e2.next = e0

    seed.vertices[0].edges = [e0, e2]
    seed.vertices[1].edges = [e0, e1]
    seed.vertices[2].edges = [e1, e2]

    front: List[Edge] = [e0, e1, e2]

    while True:
        e_ij = getActiveEdge(front)
        if not e_ij:
            break

        o_k = ballPivot(e_ij, gridObj, radius)

        if (o_k and (notUsed(o_k.vertex) or onFront(o_k.vertex))):
            outputTriangle(Face([e_ij.startVertex, o_k.vertex, e_ij.endVertex]), triangles)
            e_ik, e_kj = join(e_ij, o_k.vertex, o_k.ballCenter, front, edges)
            
            e_ki = findReverseEdgeOnFront(e_ik)
            if e_ki is not None:
                glue(e_ik, e_ki, front)

            e_jk = findReverseEdgeOnFront(e_kj)
            if e_jk is not None:
                glue(e_kj, e_jk, front)
        
        else:
            e_ij.edgeStatus = EdgeStatus.BOUNDARY

    return triangles



    

