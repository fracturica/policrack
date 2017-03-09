

submenu = 'Policrack|'
version = '1.0'
dbVersion = '1'
authors = 'Dimitar Danov,\nProf. Mario Guagliano'
helpUrl = 'www.fracturica.com/policrack'


browser = """\
Policrack* Database Browser allows to review
results extracted from model databases, created with the Policrack suite.

Specifically, the browser allows to:
 - see the available databases
 - organize the data in a tree structure based on the input parameters
 - create 2D plots from the results in the stored database
 - create visualization of the crack front and crack parameters
"""

batch = """\
The Policrack* Create a Batch plugin is an automated
procedure to preprocess, process, postprocess and store the results and
the corresponding input parameters to a database.

The plugin determines all the combinations of values for the input parameters
from the user-specified configuration file and iterates through each
combination performing a simulation for each combination.

Sample configuration files are provided in:
abaqus_plugins/policrack/samples/batch_config/ directory.
"""

preprocessor = """\
Policrack* Create Crack Mbd is a visual tool specify and create any Mdb
Policrack understands, one at a time.

The plugin can also be used as a visual guide, when creating a batch config file.
"""

postprocessor = """\
Policrack* Postprocess Odb is utilized to extract crack results from Odb of a
model, created with Policrack. The Odb has to be open and a pickle file
containing the input parameters of the model has to be specified.

Results are stored in an existing database or a new one can be created.
"""

about = """\

-----
* Policrack is a suite of plugins aiming to facilitate the fracture analysis
workflow and visualization of elliptic cracks under mixed-mode loading cases.

The suite of plugins provides tools for automation of the FE analysis, storage
of results, validation of models (by comparison with known analytical
solutions), automated plotting and a novel approach to visualization of
crack parameters.

Policrack has been developed as part of the MSc thesis:
"An automated method for the FE analysis of 3D cracks under mixed mode loading"
at Politecnico di Milano, available at:
https://www.politesi.polimi.it/handle/10589/23945
"""

description = {
    'browser': browser + about,
    'batch': batch + about,
    'preprocessor': preprocessor + about,
    'postprocessor': postprocessor + about
}
