from math import ceil, isnan
from typing import List

from glm import vec3, normalize, ivec3, cross, length2

from data_structures.mesh import Vertex

def clamp(value: float, min_val: float, max_val: float)-> float:
    if isnan(value):
        return value
    return max(min_val, min(value, max_val))

class Voxel:
    def __init__(self, vertices: List[Vertex] = None):
        if vertices:
            self.vertices: List[Vertex] = vertices
        else:
            self.vertices: List[Vertex] = []

class Grid:
    def __init__(self, vertices: List[vec3], radius: float):
        self.voxel_size: float = radius*2
        self.min_corner: vec3 = vec3(vertices[0].position)
        self.max_corner: vec3 = vec3(vertices[0].position)
        self.grid_dimensions: ivec3 = ivec3(3)
        self.voxels: List[Voxel] = []

        for vertex in vertices:
            for i in range(3):
                self.min_corner[i] = min(self.min_corner[i], vertex.position[i])
                self.max_corner[i] = max(self.max_corner[i], vertex.position[i])
        
        max_min_diff: vec3 = vec3([0, 0, 0])
        for i in range(3):
            max_min_diff[i] = ceil((self.max_corner[i] - self.min_corner[i]) / self.voxel_size) 

        dim_size: vec3 = vec3(max_min_diff)
        self.grid_dimensions: ivec3 = ivec3([max(dim_size[0], 1), max(dim_size[1], 1), max(dim_size[2], 1)])

        print("Grid dimensions: ", self.grid_dimensions[0], "x", self.grid_dimensions[1], "x", self.grid_dimensions[2])

        self.voxels = [Voxel() for i in range(self.grid_dimensions[0]*self.grid_dimensions[1]*self.grid_dimensions[2])]

        print("Number of voxels created:", len(self.voxels))

        for vertex in vertices:
            voxel_index: ivec3 = self.voxel_index(vertex.position)
            voxel_index_scalar: int = self.get_voxel_index_scalar(voxel_index)
            self.voxels[voxel_index_scalar].vertices.append(vertex)
    
    def voxel_index(self, point: vec3)-> ivec3:
        index: ivec3 = ivec3((point - self.min_corner) / self.voxel_size)
        index_clamped: ivec3 = ivec3()
        for i in range(3):
            index_clamped[i] = clamp(index[i], 0, self.grid_dimensions[i] - 1)
        return index_clamped
    
    def get_voxel_index_scalar(self, index: ivec3)-> int:
        return index[2]*self.grid_dimensions[0]*self.grid_dimensions[1] + index[1]*self.grid_dimensions[0] + index[0]

    def voxel(self, index: ivec3)-> Voxel:
        return self.voxels[index[2]*self.grid_dimensions[0]*self.grid_dimensions[1] + index[1]*self.grid_dimensions[0] + index[0]]

    def neighborhood(self, vertex: vec3, vertices_to_be_ignored: List[Vertex])-> List[Vertex]:
        vertex_voxel_index: ivec3 = self.voxel_index(vertex)
        result: List[Vertex] = []
        for x_neigh in [-1, 0, 1]:
            for y_neigh in [-1, 0, 1]:
                for z_neigh in [-1, 0, 1]:
                    index: ivec3 = ivec3([vertex_voxel_index[0] + x_neigh, vertex_voxel_index[1] + y_neigh, vertex_voxel_index[2] + z_neigh])
                    if (index[0] < 0 or index[0] >= self.grid_dimensions[0]):
                        continue
                    if (index[1] < 0 or index[1] >= self.grid_dimensions[1]):
                        continue
                    if (index[2] < 0 or index[2] >= self.grid_dimensions[2]):
                        continue
                    for vert in self.voxel(index).vertices:
                        if (length2(vert.position - vertex) < self.voxel_size*self.voxel_size) and(vert.position not in vertices_to_be_ignored):
                            result.append(vert)
        
        return result
    
class Triangle:
    def __init__(self, vertices: List[vec3] = None):
        self.vertices: List[vec3] = vertices
    
    def normal(self)-> vec3:
        edge_1_direction: vec3 = self.vertices[0] - self.vertices[1]
        edge_2_direction: vec3 = self.vertices[0] - self.vertices[2]
        cross_product: vec3 = cross(edge_1_direction, edge_2_direction)
        return normalize(cross_product)