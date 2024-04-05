from ball_pivoting import *
from data_structures.mesh_data_structures import *
from data_structures.grid import *
from typing import Optional, List, Deque, Tuple

import os
import numpy as np
from stl import mesh
from plyfile import PlyData, PlyElement

def saveTriangles(filePath: str, triangles: List[Triangle])-> None:
    meshData = np.zeros(len(triangles), dtype = mesh.Mesh.dtype)
    print(len(triangles))
    meshObj = mesh.Mesh(meshData)
    meshObj.vectors = np.array(triangles)
    meshObj.save(filePath)

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
    with open(filePath, 'r') as f:
        lines = f.readlines()
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
            