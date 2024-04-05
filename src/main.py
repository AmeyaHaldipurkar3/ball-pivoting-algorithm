import sys
import os
import numpy as np
from typing import List

from ball_pivoting.utility import reconstruct
from data_structures.grid import *
from io_handling.mesh_io import loadXYZ, saveTriangles, populate_vertices

def main(argv):
    if len(argv) != 3 and len(argv) != 4:
        print("Usage:", argv[0], "<inputPointCloudFile> <radius> [<outputMeshFile>]")
        return 1
    
    input_file: str = argv[1]
    radius: float = float(argv[2])
    output_file: str = argv[3] if len(argv) == 4 else os.path.splittext(input_file)[0] + ".stl"

    loadedData = loadXYZ(input_file)
    vertices = populate_vertices(loadedData)
    triangles: List[Triangle] = reconstruct(vertices, radius)
    print("Number of triangles", len(triangles))
    # saveTriangles(output_file, triangles)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
