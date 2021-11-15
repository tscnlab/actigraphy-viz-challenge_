Submission to ADVAnCe - Actigraphy Data Visualization and Analysis Challenge by Glenn van der Lande.

This folder contains the code to create and reproduce figures (like) those in the output folder.
Code heavily draws from on the beautiful open-source actigraphy package pyActigraphy developed by Gregory Hammad, found here: https://github.com/ghammad/pyActigraphy

To run the code:
1) Clone the repository
2) Download the example data if necessary (can also be performed on own data), here: https://datadryad.org/stash/dataset/doi:10.5061/dryad.b8gtht7bh
3) Install dependencies.

    3.1) Create a new python environment (for instance using anaconda)
  
    3.2) Activate the environment and run 'pip install -r /path/to/requirements.txt' (where path/to/requirements.txt is replaced with the path to the requirements.txt file in this folder.

4) Change paths:

    4.1) to the path of your data in line 308
  
    4.2) To the path of your desired figure save location on line 323 and 342
  
5) Import all depedencies
6) Run all functions to import them


A. Run the block of code to generate all submitted figures OR

B. Run the single file analyzer on a file of your choosing
