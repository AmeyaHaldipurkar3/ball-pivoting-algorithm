from math import sqrt, acos, pi
from typing import Optional, List, Tuple, Deque
from collections import deque

from glm import dot, distance

from data_structures.mesh import *
from data_structures.grid import *
from operation_output.operation_output import *

def calculate_ball_center(face: Face, radius: float)-> Optional[vec3]:
    edge1: vec3 = face.vertices[2].position - face.vertices[0].position
    edge2: vec3 = face.vertices[1].position - face.vertices[0].position
    cross_product: vec3 = cross(edge2, edge1)
    circumradius_vec: vec3 = (cross(cross_product, edge2)*dot(edge1, edge1) + cross(edge1, cross_product)*dot(edge2, edge2)) / (2 * dot(cross_product, cross_product))
    circumcenter: vec3 = face.vertices[0].position + circumradius_vec

    h_squared: float = (radius*radius) - dot(circumradius_vec, circumradius_vec)
    if h_squared < 0:
        return None
    
    ball_center: vec3 = circumcenter + face.normal()*sqrt(h_squared)

    return ball_center

def is_ball_empty(ball_center: vec3, vertices: List[Vertex], radius: float)-> bool:
    epsilon: float = 1e-4
    for vertex in vertices:
        if length2(vertex.position - ball_center) < (radius*radius - epsilon):
            return False
    
    return True
    
def find_seed_triangle(grid: Grid, radius: float)-> Optional[SeedTriangleOutput]:
    for voxel in grid.voxels:
        avg_normal: vec3 = vec3([0, 0, 0])
        for vertex in voxel.vertices:
            avg_normal += vertex.normal
        avg_normal = normalize(avg_normal)

        for vertex1 in voxel.vertices:
            neighbors: List[Vertex] = grid.neighborhood(vertex1.position, [vertex1.position])
            if not neighbors:
                continue
            neighbors.sort(key = lambda vertex: distance(vertex.position, vertex1.position))
            
            for vertex2 in neighbors:
                for vertex3 in neighbors:
                    if vertex2 == vertex3:
                        continue
                    face: Face = Face(vertex1, vertex2, vertex3)
                    if(dot(face.normal(), avg_normal) < 0):
                        continue
                    
                    ball_center: Optional[vec3] = calculate_ball_center(face, radius)
                    if ball_center and is_ball_empty(ball_center, neighbors, radius):
                        vertex1.used = True
                        vertex2.used = True
                        vertex3.used = True
                        return SeedTriangleOutput(face, ball_center)
        
    return
    
def get_active_edge(front: List[Edge])-> Optional[Edge]:
    while len(front) != 0:
        edge: Edge = front[-1]
        if edge.edge_status == EdgeStatus.ACTIVE:
            return edge
        front.pop()
    
    return

def ball_pivot(edge: Edge, grid: Grid, radius: float)-> Optional[BallPivotOutput]:
    edge_mid_point: vec3 = (edge.start_vertex.position + edge.end_vertex.position) / 2.0
    old_center: vec3 = normalize(edge.center - edge_mid_point)

    neighbors: List[Vertex] = grid.neighborhood(edge_mid_point, [edge.start_vertex.position, edge.end_vertex.position, edge.opposite_vertex.position])

    min_angle: float = float("inf")
    min_angle_associated_vertex: Vertex = None
    i: int = 0
    
    for vertex in neighbors:
        i += 1
        new_face_normal: vec3 = Triangle([edge.end_vertex.position, edge.start_vertex.position, vertex.position]).normal()
        if dot(new_face_normal, vertex.normal) < 0:
            continue

        ball_center: Optional[vec3] = calculate_ball_center(Face(edge.end_vertex, edge.start_vertex, vertex), radius)
        if not ball_center:
            continue

        new_center: vec3 = normalize(ball_center - edge_mid_point)

        next_neighbor_flag: bool = False
        for e in vertex.edges:
            vertex_at_other_end: Vertex = e.end_vertex if e.start_vertex == vertex else e.start_vertex
            if e.edge_status == EdgeStatus.INNER and (vertex_at_other_end == edge.start_vertex or vertex_at_other_end == edge.end_vertex):
                next_neighbor_flag = True
                break
        
        if next_neighbor_flag == True:
            continue
        
        angle: float = acos(clamp(dot(old_center, new_center), -1.0, 1.0))
        if (dot(cross(new_center, old_center), edge.start_vertex.position - edge.end_vertex.position) < 0):
            angle += pi
        if angle < min_angle:
            min_angle = angle
            min_angle_associated_vertex = vertex
            min_angle_associated_center: vec3 = ball_center

    if min_angle != float("inf"):
        if is_ball_empty(min_angle_associated_center, neighbors, radius):
            return BallPivotOutput(min_angle_associated_vertex, min_angle_associated_center)
    
    return []

def not_used(vertex: Vertex)-> bool:
    return not vertex.used

def on_front(vertex: Vertex)-> bool:
    for edge in vertex.edges:
        if edge.edge_status == EdgeStatus.ACTIVE:
            return True
        
    return False

def remove(edge: Edge)-> None:
    edge.edge_status = EdgeStatus.INNER

def output_triangle(face: Face, triangles: List[Triangle]):
    triangles.append(Triangle([face.vertices[0].position, face.vertices[1].position, face.vertices[2].position]))

def join(e_ij: Edge, o_k: Vertex, ball_center: vec3, front: List[Edge], edges: Deque[Edge])-> Tuple[Edge, Edge]:
    e_ik: Edge = Edge(e_ij.start_vertex, o_k, e_ij.end_vertex, ball_center)
    e_kj: Edge = Edge(o_k, e_ij.end_vertex, e_ij.start_vertex, ball_center)
    
    edges.append(e_ik)
    edges.append(e_kj)

    e_ik.next = e_kj
    e_ik.prev = e_ij.prev
    e_ij.prev.next = e_ik
    e_ij.start_vertex.edges.append(e_ik)

    e_kj.prev = e_ik
    e_kj.next = e_ij.next
    e_ij.next.prev = e_kj
    e_ij.end_vertex.edges.append(e_kj)

    o_k.used = True
    o_k.edges.append(e_ik)
    o_k.edges.append(e_kj)

    front.append(e_ik)
    front.append(e_kj)

    remove(e_ij)

    return (e_ik, e_kj)

def glue(edge1: Edge, edge2: Edge, front: List[Edge]):
    if edge1.next == edge2 and edge1.prev == edge2 and edge2.next == edge1 and edge2.prev == edge1:
        remove(edge1)
        remove(edge2)
        return

    if edge1.next == edge2 and edge2.prev == edge1:
        edge1.prev.next = edge2.next
        edge2.next.prev = edge1.prev
        remove(edge1)
        remove(edge2)
        return 

    if edge1.prev == edge2 and edge2.next == edge1:
        edge1.next.prev = edge2.prev
        edge2.prev.next = edge1.next
        remove(edge1)
        remove(edge2)
        return 
    
    edge1.prev.next = edge2.next
    edge2.next.prev = edge1.prev
    edge1.next.prev = edge2.prev
    edge2.prev.next = edge1.next

    remove(edge1)
    remove(edge2)

def find_reverse_edge_on_front(edge: Edge)-> Optional[Edge]:
    for e in edge.start_vertex.edges:
        if e.start_vertex == edge.end_vertex:
            return e 
        
    return None
    
def reconstruct(vertices: List[Vertex], radius: float)-> List[Triangle]:
    gridObj: Grid = Grid(vertices, radius)

    seed_triangle_output: SeedTriangleOutput = find_seed_triangle(gridObj, radius)
    if not seed_triangle_output:
        print("No seed triangle found")
        return []
    
    seed: Face = seed_triangle_output.face
    ball_center: vec3 = seed_triangle_output.ball_center
    if not ball_center:
        return
    
    triangles: List[Triangle] = []
    output_triangle(seed, triangles)

    edges: Deque[Edge] = deque()

    e0: Edge = Edge(seed.vertices[0], seed.vertices[1], seed.vertices[2], ball_center)
    e1: Edge = Edge(seed.vertices[1], seed.vertices[2], seed.vertices[0], ball_center)
    e2: Edge = Edge(seed.vertices[2], seed.vertices[0], seed.vertices[1], ball_center)

    edges.append(e0)
    edges.append(e1)
    edges.append(e2)

    e0.prev = e1.next = e2
    e0.next = e2.prev = e1
    e1.prev = e2.next = e0

    seed.vertices[0].edges = [e0, e2]
    seed.vertices[1].edges = [e0, e1]
    seed.vertices[2].edges = [e1, e2]

    front: List[Edge] = [e0, e1, e2]

    while True:
        e_ij: Edge = get_active_edge(front)
        if not e_ij:
            break

        o_k: BallPivotOutput = ball_pivot(e_ij, gridObj, radius)

        if (o_k and (not_used(o_k.vertex) or on_front(o_k.vertex))):
            output_triangle(Face(e_ij.start_vertex, o_k.vertex, e_ij.end_vertex), triangles)
            e_ik, e_kj = join(e_ij, o_k.vertex, o_k.ball_center, front, edges)
            
            e_ki: Edge = find_reverse_edge_on_front(e_ik)
            if e_ki is not None:
                glue(e_ik, e_ki, front)

            e_jk: Edge = find_reverse_edge_on_front(e_kj)
            if e_jk is not None:
                glue(e_kj, e_jk, front)
        
        else:
            e_ij.edge_status = EdgeStatus.BOUNDARY

    return triangles



    

