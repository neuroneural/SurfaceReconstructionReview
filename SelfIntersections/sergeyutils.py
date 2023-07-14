import pyvista as pv
import numpy as np
from scipy.spatial import cKDTree
import trimesh
import vtk
import sys

vtk.vtkLogger.SetStderrVerbosity(vtk.vtkLogger.VERBOSITY_OFF)

import hashlib
import os


def triangles_intersect(triangle1, vertices, faces):
    face = np.array([3, 0, 1, 2])
    labelmap = {x: idx for idx, x in enumerate(np.unique(faces))}
    @np.vectorize
    def relabel(x):
        y = 0
        if x in labelmap:
            y = labelmap[x]
        return y
    faces = relabel(faces)
    new_column = np.full((faces.shape[0], 1), 3)
    faces = np.hstack((new_column, faces))

    surface1 = pv.PolyData(triangle1, face)
    surface2 = pv.PolyData(vertices, faces.flatten())

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
        collision = triangles_intersect(triangles1[idx,:,:],
            mesh2.vertices[np.sort(np.unique(mesh2.faces[indices[0]].flatten()))],
            mesh2.faces[indices[0]])
        if collision:
            collision_count += 1
            bad1.append(idx)

    return collision_count, bad1, bad2

def get_triangle_count(filepath):
    print('trimesh file path', filepath)
    mesh = None
    try:
        mesh = trimesh.load_mesh(filepath)
    except:
        print('filepath caused error: \n', filepath)
        random_string = os.urandom(32)
        # Compute the hash of the random string
        seed = hashlib.sha256(random_string).hexdigest()
        tmpname = "tmp"+seed+".stl"
        mesh = pv.read(filepath)
        mesh.save(tmpname)
        mesh = trimesh.load_mesh(tmpname)
   
    return len(mesh.faces)
    
def getSelfIntersections(filepath, k = 1):
    mesh = None
    try:
        mesh = trimesh.load_mesh(filepath)
    except:
        print('filepath caused error: \n', filepath)
        random_string = os.urandom(32)
        # Compute the hash of the random string
        seed = hashlib.sha256(random_string).hexdigest()
        tmpname = "tmp"+seed+".stl"
        mesh = pv.read(filepath)
        mesh.save(tmpname)
        mesh = trimesh.load_mesh(tmpname)
    return count_self_collisions(mesh, k=k)#collision_count, bad1, bad2 

def detachedtriangles(mesh, triangle_id, other_ids):
    # Remove rows based on the mask
    mask = np.any(np.isin(mesh.faces[other_ids],
            mesh.faces[triangle_id]), axis=1)
    faces = mesh.faces[other_ids][~mask]
    return faces        

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
        # Remove rows based on the mask
        faces = detachedtriangles(mesh, idx, indices[0][1:])
        # mask = np.any(np.isin(mesh.faces[indices[0][1:]], mesh.faces[idx]), axis=1)
        # faces = mesh.faces[indices[0][1:]][~mask]
        if faces.size == 0:
            print('k is too small')
            continue
        # Check collision with each nearest neighbor triangle
        collision = triangles_intersect(triangles[idx,:,:],
            mesh.vertices[np.sort(np.unique(faces.flatten()))],
            faces)
        if collision:
            collision_count += 1
            #print(idx)
            bad1.append(idx)

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
        filepath = mesh1_filename
        mesh = None
        try:
            mesh = trimesh.load_mesh(filepath)
        except:
            print('filepath caused error: \n', filepath)
            random_string = os.urandom(32)
            # Compute the hash of the random string
            seed = hashlib.sha256(random_string).hexdigest()
            tmpname = "tmp"+seed+".stl"
            mesh = pv.read(filepath)
            mesh.save(tmpname)
            mesh = trimesh.load_mesh(tmpname)
    
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
