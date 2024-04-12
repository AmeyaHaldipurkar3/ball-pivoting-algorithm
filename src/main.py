import sys
import os
from typing import List, Tuple

from glm import silence

from ball_pivoting.ball_pivoting import reconstruct
from data_structures.mesh import Vertex, Triangle
from io_handling.io import load_xyz, save_triangles, populate_vertices

def main(argv):
    if len(argv) != 3 and len(argv) != 4:
        print("Usage:", argv[0], "<input_file> <ball_radius> [<output_file>]")
        return 1
    
    input_file: str = argv[1]
    radius: float = float(argv[2])
    output_file: str = argv[3] if len(argv) == 4 else os.path.splitext(input_file)[0] + ".stl"

    silence(2) #glm function to silence the warning for division by 0
    loadedData: Tuple[List[float], List[float]] = load_xyz(input_file)
    vertices: List[Vertex] = populate_vertices(loadedData)
    triangles: List[Triangle] = reconstruct(vertices, radius)

    print("Number of mesh faces created:", len(triangles))

    save_triangles(output_file, triangles)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
