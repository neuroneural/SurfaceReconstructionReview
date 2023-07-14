import pyvista as pv
import numpy as np
from scipy.spatial import cKDTree
import trimesh
import vtk
import sys

vtk.vtkLogger.SetStderrVerbosity(vtk.vtkLogger.VERBOSITY_OFF)

def triangles_intersect(triangle1, triangle2):
    faces = np.array([3, 0, 1, 2])
    surface1 = pv.PolyData(triangle1[0], faces)
    surface2 = pv.PolyData(triangle2[0], faces)
    return surface1.collision(surface2)[1] > 0

def compute_triangle_center(mesh, triangle):
    vertex_indices = mesh.faces[triangle]
    vertices = mesh.points[vertex_indices]
    return np.mean(vertices, axis=0)

def mesh2triangles(mesh):
    return mesh.vertices[mesh.faces]

def mesh2tricenters(mesh, triangles=None):
    if triangles is None:
        triangles = mesh2triangles(mesh)
    centers = np.mean(triangles, axis=1)
    return centers

def count_collisions(mesh1, mesh2, k=5):
    # Compute triangle centers and construct KDTree for mesh2
    triangles2 = mesh2triangles(mesh2)
    centers2 = mesh2tricenters(mesh2, triangles=triangles2)
    triangles1 = mesh2triangles(mesh1)
    centers1 = mesh2tricenters(mesh1, triangles=triangles1)

    tree = cKDTree(centers2)

    # Iterate through triangles of mesh1 and check for collisions
    collision_count = 0
    bad1 = []
    bad2 = []
    for idx, triangle in enumerate(centers1):
        # Find K nearest neighbors
        dists, indices = tree.query(triangle.reshape(1,-1), k=k)
        # Check collision with each nearest neighbor triangle
        for index in indices:
            collision = triangles_intersect(triangles1[idx,:,:],
                                            triangles2[index,:,:])
            if collision:
                collision_count += 1
                bad1.append(idx)
                bad2.append(index)
                #print(idx, collision_count)
                break
    return collision_count, bad1, bad2

def get_triangle_count(filepath):
    mesh = trimesh.load_mesh(filepath)
    return len(mesh.faces)

def getSelfIntersections(filepath, k = 1):
    mesh = trimesh.load_mesh(filepath)
    return count_self_collisions(mesh, k=k)#collision_count, bad1, bad2 
        

def count_self_collisions(mesh, k=5):
    # Compute triangle centers and construct KDTree for mesh2
    faces = mesh.faces
    triangles = mesh2triangles(mesh)
    centers = mesh2tricenters(mesh, triangles=triangles)
    tree = cKDTree(centers)

    # Iterate through triangles of mesh1 and check for collisions
    collision_count = 0
    bad1 = []
    bad2 = []
    for idx, triangle in enumerate(centers):
        # Find K nearest neighbors
        dists, indices = tree.query(triangle.reshape(1,-1), k=k)
        # Check collision with each nearest neighbor triangle
        for index in indices[0][1:]:
            if set(faces[idx]).intersection(faces[index]): continue
            collision = triangles_intersect(triangles[idx,:,:],
                                            triangles[index,:,:])
            if collision:
                collision_count += 1
                bad1.append(idx)
                bad2.append(index)
                #print(idx, collision_count)
                break
    return collision_count, bad1, bad2

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python collision_detection.py <mesh1.stl> <mesh2.stl>")
        sys.exit(1)

    mesh1_filename = sys.argv[1]
    mesh2_filename = sys.argv[2]
    print(mesh1_filename, mesh2_filename)
    
    # Load meshes
    if mesh1_filename == mesh2_filename:
        print("looking for self collisions")
        mesh = trimesh.load_mesh(mesh1_filename)
        collision_count, bad1, bad2 = count_self_collisions(mesh, k=10)
        mesh1 = mesh2 = mesh
    else:
        mesh1 = trimesh.load_mesh(mesh1_filename)
        mesh2 = trimesh.load_mesh(mesh2_filename)
        # Compute collision count
        collision_count, bad1, bad2 = count_collisions(mesh1, mesh2, k=1)

    # plotting
    selected_faces = mesh1.faces[bad1]
    unique_vertices, inverse = np.unique(selected_faces,
                                         return_inverse=True)
    collisions1 = trimesh.Trimesh(vertices=mesh1.vertices[unique_vertices], faces=inverse.reshape((-1, 3)))
    selected_faces = mesh2.faces[bad2]
    unique_vertices, inverse = np.unique(selected_faces,
                                         return_inverse=True)
    collisions2 = trimesh.Trimesh(vertices=mesh2.vertices[unique_vertices], faces=inverse.reshape((-1, 3)))

    # Print the number of collisions
    print("Number of collisions:", collision_count)

    plotter = pv.Plotter()
    plotter.add_mesh(collisions1, color='r', opacity=0.5)
    plotter.add_mesh(collisions2, color='g', opacity=0.5)
    if mesh1_filename != mesh2_filename:
        plotter.add_mesh(mesh1, color='r', opacity=0.1)
        plotter.add_mesh(mesh2, color='g', opacity=0.1)
    else:
        plotter.add_mesh(mesh1, color='b', opacity=0.05)
    plotter.show()
