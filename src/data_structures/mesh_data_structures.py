from glm import vec3, normalize

class Vertex:
    def __init__(self, position: vec3 = vec3([0, 0, 0]), normal: vec3 = vec3([1, 1, 1]), used: bool = False, edges: list = None):
    self.position = position
    self.normal = normal
    self.used = False
    self.edges = []


class EdgeStatus(Enum):
    ACTIVE = 'active'
    INNER = 'inner'
    BOUNDARY = 'boundary'

class Edge:
    def __init__(self):
    self.startVertex = None
    self.endVertex = None
    self.oppVertex = None
    self.prev = None
    self.next = None
    self.edgeStatus = EdgeStatus.ACTIVE
    self.center = None

class Face:
    def __init__(self, vertex1: Vertex, vertex2: Vertex, vertex3: Vertex):
        self.vertices = [vertex1, vertex2, vertex3]
    
    def normal(self)-> vec3:
        edgeDirection1 = self.points[0].position - self.points[1].position
        edgeDirection2 = self.points[0].position - self.points[2].position
        return normalize(edgeDirection1 - edgeDirection2)
