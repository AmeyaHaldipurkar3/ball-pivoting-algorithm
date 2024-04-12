from enum import Enum
from typing import List

from glm import vec3, normalize, cross

class Vertex:
    def __init__(self, position: vec3 = vec3([0, 0, 0]), normal: vec3 = vec3([1, 1, 1]), used: bool = False, edges: List['Edge'] = None):
        self.position: vec3 = position
        self.normal: vec3 = normal
        self.used: bool = False
        self.edges: List[Edge] = []

class EdgeStatus(Enum):
    ACTIVE = 'active'
    INNER = 'inner'
    BOUNDARY = 'boundary'

class Edge:
    def __init__(self, start_vertex: Vertex = None, end_vertex: Vertex = None, opposite_vertex: Vertex = None, center: vec3 = None):
        self.start_vertex: Vertex = start_vertex
        self.end_vertex: Vertex = end_vertex
        self.opposite_vertex: Vertex = opposite_vertex
        self.prev: Edge = None
        self.next: Edge = None
        self.edge_status: EdgeStatus = EdgeStatus.ACTIVE
        self.center: vec3 = center

class Face:
    def __init__(self, vertex1: Vertex, vertex2: Vertex, vertex3: Vertex):
        self.vertices: List[Vertex] = [vertex1, vertex2, vertex3]
    
    def normal(self)-> vec3:
        edge_direction_1: vec3 = self.vertices[0].position - self.vertices[1].position
        edge_direction_2: vec3 = self.vertices[0].position - self.vertices[2].position
        cross_product: vec3 = cross(edge_direction_1, edge_direction_2)
        return normalize(cross_product)

class Triangle:
    def __init__(self, vertices: List[vec3] = None):
        self.vertices: List[vec3] = vertices
    
    def normal(self)-> vec3:
        edge_1_direction: vec3 = self.vertices[0] - self.vertices[1]
        edge_2_direction: vec3 = self.vertices[0] - self.vertices[2]
        cross_product: vec3 = cross(edge_1_direction, edge_2_direction)
        return normalize(cross_product)