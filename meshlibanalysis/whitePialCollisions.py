import os
import re
import argparse 
import socket
from csv import writer
import meshlib.mrmeshpy as mrmesh

hostname = socket.gethostname()


def write_intersections2csv(model_name,intersections=None,f1=None, f2=None):
    base_path = '/data/users2/washbee/speedrun/'

    filename = 'intersections.csv'
    filename = base_path + filename

    # Define initial list
    List = [model_name, intersections, hostname,f1,f2]

    # If memory flag is true, append memory related info
    
    if not os.path.exists(filename):
        # Create the file
        with open(filename, 'w') as file:
            # Perform any initial operations on the file, if needed
            print("File created.")

    with open(filename, 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(List)


dic = dict()
dic['deepcsr'] = {
    "lh_pial": "/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_pial",
    "lh_white": "/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_white",
}

# Provide the directory path
directory_path = dic["deepcsr"]['lh_pial']

# Call the function to list STL files in the directory


parser = argparse.ArgumentParser(description='Example script to handle arguments.')
parser.add_argument('-f1', '--file1', type=str, help='Path to the input file.')
parser.add_argument('-f2', '--file2', type=str, help='Path to input file.')

args = parser.parse_args()

mesh1_filename= dic['deepcsr']['lh_pial']+'/'+args.file1
mesh2_filename= dic['deepcsr']['lh_white']+'/'+args.file2

#s1, s2 = pv.read(mesh1_filename), pv.read(mesh2_filename)
#intersection, _, _ = s1.intersection(s2);

################################begin example (replace this code) 
#TODO: NEED TO OPEN MESH INSTEAD OF USE TORUS
torus = mrmesh.makeTorus(2, 1, 10, 10, None)
torus2 = mrmesh.makeTorus(2, 1, 10, 10, None)

transVector = mrmesh.Vector3f()
transVector.x = 0.5
transVector.y = 1
transVector.z = 1
diffXf = mrmesh.AffineXf3f.translation(transVector)
torus2.transform(diffXf)

xf = mrmesh.AffineXf3f()
torus1 = torus
pairs = mrmesh.findCollidingTriangles(
    mrmesh.MeshPart(torus1), mrmesh.MeshPart(torus2))
# at least 100 triangles should collide for that transforms
assert (len(pairs) > 103)
#######END EXAMPLE
write_intersections2csv("Torus",intersections=len(pairs), f1=args.file1,f2=args.file2)#change torus to project
print ('file 1', args.file1)
print ('file 2', args.file2)
#print('intersection',intersection)

