import os
import argparse 
import socket
from csv import writer
import meshlib.mrmeshpy as mrmesh
from tqdm import tqdm
import sergeyutils as su
import pickle

hostname = socket.gethostname()

def write_intersections2csv(model_name,meshlibCollisions, sergeyCollisions,surface = 'pial',subject=None,f1=None):
    #base_path = '/data/users2/llu13/FStutorial/Jul12'
    base_path = '/data/users2/washbee/speedrun/'
    filename = 'rulethemallselfintersections.csv'
    filename = base_path + filename
    List = [model_name, meshlibCollisions, sergeyCollisions, surface, hostname,subject, f1]
    
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            print("File created.")

    with open(filename, 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(List)

dic = dict()


# model, p, w = 'deepcsr', 'lh_pial', 'lh_white'

# dic[model] = {
#     p: "/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_pial",
#     w: "/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_white",
# }

def get_white_from_pial(pialfile):
    # deepcsr
    return pialfile[:6]+'_lh_white.stl'

#list1 = os.listdir(dic[model][p])
parser = argparse.ArgumentParser(description='Example script to handle arguments.')
parser.add_argument('-f1', '--file1', type=str, help='Path to the input file.')
parser.add_argument('-m', '--model', type=str, help='Path to the input file.')
parser.add_argument('-p', '--path', type=str, help='Path to the input file.')
parser.add_argument('-t', '--type', type=str, choices=['pial', 'white'], help='Type of data')

args = parser.parse_args()

#filepath = os.path.join(dic[model][p],args.file1)
subj = args.file1[:6]
filepath = None
list1 = os.listdir(args.path)
filePassed = None
for file in list1:
    if args.type in file and subj in file:
        filepath = os.path.join(args.path,file)
        filePassed = file
        break

def printSelfIntersections(path, surface = 'pial'):
    
    # Load the meshes from the STL files
    #mesh1 = mrmesh.loadMesh(filepath)
    #mesh2 = mrmesh.loadMesh(filepath)#self intersections

    #pairsMeshlib = mrmesh.findCollidingTriangles(mrmesh.MeshPart(mesh1), mrmesh.MeshPart(mesh2))
    faces = su.get_triangle_count(filepath)

    collision_count, bad1, bad2 = su.getSelfIntersections(filepath, k = 10)
    
    with open(os.path.splitext(os.path.basename(filepath))[0] + '.pkl', 'wb') as f:
        pickle.dump((collision_count, bad1, bad2), f)


    #write_intersections2csv(f"{model}", len(pairsMeshlib), collision_count, surface=surface, subject=subj, f1 = args.file1)

    write_intersections2csv(args.model, faces, collision_count, surface=surface, subject=subj, f1 = filePassed)

printSelfIntersections(filepath,surface = args.type)
