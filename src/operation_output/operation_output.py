from glm import vec3

from data_structures.mesh import Vertex, Face

class SeedTriangleOutput:
    def __init__(self, face: Face = None, ball_center: vec3 = None):
        self.face: Face = face
        self.ball_center: vec3 = ball_center

class BallPivotOutput:
    def __init__(self, vertex: Vertex = None, ball_center: vec3 = None):
        self.vertex: Vertex = vertex
        self.ball_center: vec3 = ball_center