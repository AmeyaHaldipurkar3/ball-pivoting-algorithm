import struct
from typing import List, Tuple
# import numpy as np
# from plyfile import PlyData, PlyElement

from data_structures.mesh import Triangle
from data_structures.grid import *

def save_triangles(file_name: str, triangles: List[Triangle]):
    with open(file_name, 'wb') as f:
        f.write(struct.pack('<80s', b'STL File Header'))
        f.write(struct.pack('<I', len(triangles)))

        for triangle in triangles:
            normal: vec3 = triangle.normal()
            f.write(struct.pack('<3f', *normal))

            for vertex in triangle.vertices:
                f.write(struct.pack('<3f', *vertex))
                
            f.write(struct.pack('<H', 0))

def load_xyz(file_path: str)-> Tuple[List[float], List[float]]:
    with open(file_path, 'rb') as f:
        lines: str = f.readlines()
    result: Tuple[List[float], List[float]] = []

    for line in lines:
        vertex_data: List[float] = list(map(float, line.strip().split()))
        result.append((vertex_data[:3], vertex_data[3:]))
    
    return result

def save_xyz(file_path: str, vertices: List[Vertex]):
    with open(file_path, 'w') as f:
        for vertex in vertices:
            f.write(f"{vertex[0][0]} {vertex[0][1]} {vertex[0][2]} {vertex[1][0]} {vertex[1][1]} {vertex[1][2]}\n")

def populate_vertices(input: Tuple)-> List[Vertex]:
    vertices: List[Vertex] = []
    for position, normal in input:
        vertex: Vertex = Vertex(vec3(position), vec3(normal))
        vertices.append(vertex)
    
    return vertices

# def saveVerticesWithNormals(filePath: str, vertices: List[Vertex])-> None:
#     verticesNp = np.zeros(len(vertices), dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4')])
#     for i, vertex in enumerate(vertices):
#         verticesNp[i] = (vertex.position[0], vertex.position[1], vertex.position[2], vertex.normal[0], vertex.normal[1], vertex.normal[2])
#     PlyData([PlyElement.describe(vertex, 'vertex')], text = False).write(filePath)

# def saveVerticesWithNormals(filePath: str, vertices: List[Vertex])-> None:
#     verticesNp = np.zeros(len(vertices), dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
#     for i, vertex in enumerate(vertices):
#         verticesNp[i] = (vertex.position[0], vertex.position[1], vertex.position[2])
#     PlyData([PlyElement.describe(vertex, 'vertex')], text = False).write(filePath)
            