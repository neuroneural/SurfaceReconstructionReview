# Conda

```markdown
You will need to modify the conda path in `findallwpc.sbatch`.
`which conda` helps locate your conda installation,
and `conda env export` helps locate the path to your conda environment.
``` 
# Permissions
Also, you will need to change permissions on all files in this folder:
```bash
chmod 777 * 
```
```markdown
inside of `meshlibanalysis`.

```
# Slurm Submission/Execution
```bash
sbatch --array=1-107 findallwpc.sbatch
```
```markdown
# Jobs Directory
Create a `jobs` folder in `meshlibanalysis` if it isn't there already.
```

