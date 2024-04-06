from ball_pivoting import *
from data_structures.mesh_data_structures import *
from data_structures.grid import *
from typing import Optional, List, Deque, Tuple

import os
import numpy as np
from stl import mesh
from plyfile import PlyData, PlyElement

import struct

def save_triangles(filename, triangles):
    with open(filename, 'wb') as f:
        # Write the header (80 bytes)
        f.write(struct.pack('<80s', b'STL File Header'))

        # Write the number of triangles (4 bytes)
        f.write(struct.pack('<I', len(triangles)))

        # Write each triangle
        for triangle in triangles:
            # Write the normal vector of the triangle (12 bytes)
            normal = triangle.normal()
            f.write(struct.pack('<3f', *normal))

            # Write the vertices of the triangle (36 bytes)
            for vertex in triangle.vertices:
                f.write(struct.pack('<3f', *vertex))

            # Write attribute byte count (2 bytes, unused)
            f.write(struct.pack('<H', 0))

def saveVerticesWithNormals(filePath: str, vertices: List[Vertex])-> None:
    verticesNp = np.zeros(len(vertices), dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4')])
    for i, vertex in enumerate(vertices):
        verticesNp[i] = (vertex.position[0], vertex.position[1], vertex.position[2], vertex.normal[0], vertex.normal[1], vertex.normal[2])
    PlyData([PlyElement.describe(vertex, 'vertex')], text = False).write(filePath)

def saveVerticesWithNormals(filePath: str, vertices: List[Vertex])-> None:
    verticesNp = np.zeros(len(vertices), dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
    for i, vertex in enumerate(vertices):
        verticesNp[i] = (vertex.position[0], vertex.position[1], vertex.position[2])
    PlyData([PlyElement.describe(vertex, 'vertex')], text = False).write(filePath)

def loadXYZ(filePath: str):
    print(os.getcwd())
    # with open(filePath, 'rb', encoding = 'UTF-32-LE') as f:
    with open(filePath, 'rb') as f:
        lines = f.readlines()
        # lines = f.read().decode('utf-8')
        # convert binary to utf-8
        # print(lines)
        # exit()
    result = []

    for line in lines:
        vertexData = list(map(float, line.strip().split()))
        result.append((vertexData[:3], vertexData[3:]))
    
    return result

def save_xyz(filePath: str, vertices: List[Vertex]):
    with open(filePath, 'w') as f:
        for vertex in vertices:
            f.write(f"{vertex[0][0]} {vertex[0][1]} {vertex[0][2]} {vertex[1][0]} {vertex[1][1]} {vertex[1][2]}\n")

def populate_vertices(input: Tuple):
    vertices = []
    for position, normal in input:
        vertex = Vertex(vec3(position), vec3(normal))
        vertices.append(vertex)
    
    return vertices
            