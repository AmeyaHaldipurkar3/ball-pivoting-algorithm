from glm import vec3, normalize, ivec3, cross, dot, distance, length2
from math import ceil, sqrt, isnan
from data_structures.mesh_data_structures import Vertex, Edge, Face

from typing import List

def clamp(value, minVal, maxVal):
    if isnan(value):
        return value
    return max(minVal, min(value, maxVal))

class Voxel:
    def __init__(self, vertices: List[Vertex] = None):
        if vertices:
            self.vertices = vertices
        else:
            self.vertices = []

class Grid:
    def __init__(self, vertices: List[vec3], radius: float):
        self.voxelSize = radius*2
        self.minCorner = vec3(vertices[0].position)
        self.maxCorner = vec3(vertices[0].position)
        self.dims = ivec3(3)
        self.voxels = []

        for vertex in vertices:
            for i in range(3):
                self.minCorner[i] = min(self.minCorner[i], vertex.position[i])
                self.maxCorner[i] = max(self.maxCorner[i], vertex.position[i])
        
        max_min_diff = vec3([0, 0, 0])
        for i in range(3):
            max_min_diff[i] = ceil((self.maxCorner[i] - self.minCorner[i]) / self.voxelSize) 

        dimSize = vec3(max_min_diff)
        self.dims: ivec3 = ivec3([max(dimSize[0], 1), max(dimSize[1], 1), max(dimSize[2], 1)])
        print("dims", self.dims)
        self.voxels = [Voxel() for i in range(self.dims[0]*self.dims[1]*self.dims[2])]
        print("Voxel Length", len(self.voxels))
        for vertex in vertices:
            voxel_index = self.voxelIndex(vertex.position)
            voxel_index_scalar = self.get_voxel_index_scalar(voxel_index)
            self.voxels[voxel_index_scalar].vertices.append(vertex)
    
    def voxelIndex(self, point: vec3)-> ivec3:
        index = ivec3((point - self.minCorner) / self.voxelSize)
        indexClamped = ivec3()
        for i in range(3):
            indexClamped[i] = clamp(index[i], 0, self.dims[i] - 1)
        return indexClamped
    
    def get_voxel_index_scalar(self, index: ivec3)-> int:
        return index[2]*self.dims[0]*self.dims[1] + index[1]*self.dims[0] + index[0]

    def voxel(self, index: ivec3)-> Voxel:
        return self.voxels[index[2]*self.dims[0]*self.dims[1] + index[1]*self.dims[0] + index[0]]

    def neighborhood(self, vertex: vec3, verticesToBeIgnored: list[Vertex])-> list[Vertex]:
        vertexVoxelIndex = self.voxelIndex(vertex)
        result = []
        for xNeigh in [-1, 0, 1]:
            for yNeigh in [-1, 0, 1]:
                for zNeigh in [-1, 0, 1]:
                    index = ivec3([vertexVoxelIndex[0] + xNeigh, vertexVoxelIndex[1] + yNeigh, vertexVoxelIndex[2] + zNeigh])
                    if (index[0] < 0 or index[0] >= self.dims[0]):
                        continue
                    if (index[1] < 0 or index[1] >= self.dims[1]):
                        continue
                    if (index[2] < 0 or index[2] >= self.dims[2]):
                        continue
                    for vert in self.voxel(index).vertices:
                        if (length2(vert.position - vertex) < self.voxelSize*self.voxelSize) and(vert.position not in verticesToBeIgnored):
                            result.append(vert)
        
        return result

class SeedResult:
    def __init__(self, face: Face = None, ballCenter: vec3 = None):
        self.face = face
        self.ballCenter = ballCenter

class PivotResult:
    def __init__(self, vertex: Vertex = None, ballCenter: vec3 = None):
        self.vertex = vertex
        self.ballCenter = ballCenter
    
class Triangle:
    def __init__(self, vertices: list[vec3] = None):
        self.vertices = vertices
    
    def normal(self):
        return normalize(cross(self.vertices[0] - self.vertices[1], self.vertices[0] - self.vertices[2]))