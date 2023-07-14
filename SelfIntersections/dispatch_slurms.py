import json
import os
import subprocess
import sys


def process_data(data):
    # Put your processing code here
    print(data)
data = None
with open('modelpath.json', 'r') as f:
    data = json.load(f)


enums = ['lh_white','lh_pial']
# Or if the JSON file contains a dict
for key, value in data.items():
    assert type(value) == dict
    
    dir_name = key

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    for e in enums:
    
        whitepial = "white" if "white" in e else "pial"
        path = value[e]  # Replace with the correct value
        
        cmd = [
            "python",
            "/data/users2/washbee/speedrun/SurfaceReconstructionReview/SelfIntersections/selfIntersections.py",
            "--file1",
            sys.argv[1],
            "--path",
            path,
            "-t",
            whitepial,
            "-m",
            key
        ]

        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"The command '{' '.join(cmd)}' executed successfully.")
        else:
            print(f"The command '{' '.join(cmd)}' failed to execute.")
