from glm import vec3, normalize, ivec3, cross, dot, distance
from math import ceil, sqrt
from mesh_data_structures import Vertex, Edge, Face

def clamp(value, minVal, maxVal):
    return max(minVal, min(value, maxVal))

class Voxel:
    def __init__(self, vertices: vec3 = None):
        self.vertices = vertices

class Grid:
    def __init__(self, vertices: vec3, radius: float):
        self.voxelSize = radius*2
        self.minCorner = vec3(vertices[0].position)
        self.maxCorner = vec3(vertices[0].position)
        self.dims = ivec3(3)
        self.voxels = []

        for vertex in vertices:
            for i in range(3):
                self.minCorner[i] = min(self.minCorner[i], vertex.position[i])
                self.maxCorner[i] = min(self.maxCorner[i], vertex.position[i])
        
        dims = max(ivec3(ceil(self.maxCorner - self.minCorner) / self.voxelSize), ivec3(1))
        self.voxels = [Voxel() for i in range(dims[0]*dims[1]*dims[2])]
    
    def voxelIndex(self, point: vec3)-> ivec3:
        index = ivec3((point - self.minCorner) / self.voxelSize)
        
        return clamp(index, ivec3(), self.dims - 1)

    def voxel(self, index: ivec3)-> Voxel:
        return self.voxels[index[2]*self.dims[0]*self.dims[1] + index[1]*self.dims[0] + index[0]]

    def neighborhood(vertex: vec3, verticesToBeIgnored: list[Vertex])-> list[Vertex]:
        vertexVoxelIndex = self.voxelIndex(vertex)
        result = []
        for xNeigh in [-1, 0, 1]:
            for yNeigh in [-1, 0, 1]:
                for zNeigh in [-1, 0, 1]:
                    index = ivec3([pointIndex[0] + xNeigh, pointIndex[1] + yNeigh, pointIndex[2] + zNeigh])
                    if not (0 <= index[0] < self.dims[0] and 0 <= index[1] < self.dims[1] and 0 <= index[2] < self.dims[2]):
                        continue
                    for vert in self.voxel(index):
                        if ((vert.position - vertex) < self.voxelSize*self.voxelSize) and(vert.position not in verticesToBeIgnored):
                            result.append(vert)
        
        return result

class SeedResult:
    def __init__(face: Face = None, ballCenter: vec3 = None):
        self.face = face
        self.ballCenter = ballCenter

class PivotResult:
    def __init__(vertex: Vertex = None, ballCenter: vec3 = None):
        self.vertex = vertex
        self.ballCenter = ballCenter
    
class Triangle:
    def __init__(self, vertices: list[vec3] = None):
        self.vertices = vertices
    
    def normal():
        return normalize(self.vertices[0] - self.vertices[1], self.vertices[0] - self.vertices[2])