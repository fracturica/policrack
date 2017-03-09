# Policrack

**Policrack is an Abaqus/CAE plugin aiming to facilitate and automate the analysis workflow and visualization of elliptic cracks.**

Copyright &copy; 2010, 2011 Dimitar Danov, Prof. Mario Giagliano, [Politecnico di Milano](http://www.polimi.it)

Distributed under the terms of MIT License.


## Overview

Policrack is a toolset geared towards the analysis of elliptic crack in Abaqus.

It can generate specialized model databases, post-process, store results data, create visualizations and automate the analysis.

The specialized model databases or Policrack Models `PM` are FEM or XFEM models with different meshing strategies, of embedded, surface or corner cracks. `PM` can be used as part of a sub-modeling procedure.

Policrack visualization is an intuitive 3D representation of K-Factors, crack propagation direction and other crack parameters on the crack front geometry.


## Installation

1. Locate the Abaqus/CAE plugin directory. It is probably called `abaqus_plugins` and on a Windows machine it is in the user home directory.
2. Download and unzip Policrack.
3. Move the `policrack` directory into the Abaqus/CAE plugin directory.
4. Start Abaqus.
5. You can access Policrack through the menu `Plug-ins -> Policrack`. If there is no such menu item consult the Abaqus/CAE documentation for the plugins directory and check the directory structure.


## Guide

This is a short introduction, a more detailed resource of the model databases, meshing strategies and Policrack's inner workings can be found in the thesis: [An automated method for the FE analysis of 3D cracks under mixed mode loading](https://www.politesi.polimi.it/handle/10589/23945).


### Analysis workflow with Policrack

The analysis workflow with Policrack consists of five stages in the following sequence:

`1. preprocessing` -> `2. analysis` -> `3. postprocessing` -> `4.data storage` -> `5.visualization`


#### 1. Preprocessing
The preprocessing stage is the generation of a Policrack Model `PM` from a set of input parameters.
The parameters required to fully define a `PM` are called a set of input parameters.


#### 2. Analysis
The analysis stage is the submission of an Abaqus job, waiting for it to finish and proceeding with the next step of the workflow.


#### 3. Postprocessing
The postprocessing stage is the extraction of the `History Output Requests` values from an Abaqus output database. These are the Stress Intensity Factors (SIFs), J-Integral, etc. and the coordinates of the corresponding nodes of the crack front.


#### 4. Data Storage
In the data storage step the results obtained in the postprocessing stage and the corresponding set of input parameters are saved as a record in a Policrack database.


#### 5. Visualization
In the visualization stage the analyst can browse the available Policrack databases, create 2D plots of the crack parameters and create a Policrack 3D visualization of the crack front and the calculated values associated with the crack.




### Policrack Toolset

Policrack is composed of four tools all accessible from the `Plug-ins -> Policrack` submenu:
 - Database browser &mdash; `Browse Database...`
 - Automated Batch &mdash; `Create a Batch...`
 - Single Crack Model &mdash; `Create Crack Model...`
 - Postprocessor &mdash; `Postprocess...`


#### Database Browser

The Database Browser tool performs three tasks:
1. Lists the available Policrack databases.
2. Organizes the records of a selected database in a tree built from their input parameters.
3. Creates 2D plots and 3D Policrack Visualizations.


When invoked, the Database Browser displays a list of the available Policrack databases and metadata about the selected database (Figure&nbsp;1).

[selectDb1]: docs/img/dbBrowser1.png "Select a Policrack database"
![Image of a "Select database window"][selectDb1]
<br>Figure&nbsp;1. Select a Policrack database.


In the next step the Database Browser (Figure&nbsp;2) displays a tree representation of the selected database and results options.
The the root of the tree is the analysis type (FEM/XFEM). Each tree branch is either a parameter name or value. Every parameter name branch is direct parent of its value branches. The leaves of the tree are the database record `id`s. Only `id`s are selectable. An `id` that cannot be selected signifies a failed simulation.

To create a 2D plot or a Policrack Visualization, select one or more database record `id`s from the tree, set the results options and click create.

[selectDb2]: docs/img/dbBrowser2.png "Policrack Database Browser dialog"
![Image of a "Database Browser" dialog][selectDb2]
<br>Figure&nbsp;2. Policrack Database Browser dialog.


#### Automated Batch

The Automated Batch tool runs steps `1`, `2`, `3` and `4` of the Policrack Analysis Workflow in loop without intervention.

It determines input parameters for the standardized model from a batch config file and executes the loop. If more than one value is given per parameter, Policrack will loop over all possible combinations of input parameter values.

A batch config file specifies the required input parameters for a standardized model. A batch config file corresponds to a type of Policrack model. Samples of all types of batch config files located in the `policrack/samples/batch_config` directory.

The Automated Batch tool works in two steps:
1. Asks for batch config file Figure&nbsp;3.
2. Displays the combinations of parameters to loop over Figure&nbsp;4.

[batch1]: docs/img/batch1.png "Select Batch Config File"
![Image of a "Select Batch Config File" window][batch1]
<br>Figure&nbsp;3. Select Batch Config File dialog.


[batch2]: docs/img/batch2.png "Preview and Create dialog"
![Image of a "Preview and Create" dialog][batch2]
<br>Figure&nbsp;4. Preview and Create dialog.


#### Single Crack Model

The Single Crack tool is a visual tool for defining all parameters for any Policrack standardized model and creating it, Figure&nbsp;5.

It provides a visual description of the parameters in the batch config files.

[crackMdb]: docs/img/createMdb.png "Create Crack Model dialog"
![Image of a "Create Crack Model" dialog][crackMdb]
<br>Figure&nbsp;5. Create Crack Model dialog.


#### Postprocessor

The Postprocessor tool is used when a standardized model has been calculated and the results need to be extracted and stored in a Policrack database.

Saving results in a Policrack database with the Postprocessor tool is a two step procedure:
1. Select an open output database for a standardized model and the corresponding `pickle` file Figure&nbsp;6. The concept is to couple the output database (i.e. results) with its set of input parameters.
2. Select a Policrack database from the list or create new one to store the data, Figure&nbsp;7.


[postprocessor1]: docs/img/postprocess1.png "Select Output Database and Config File dialog"
![Image of "Select Output Database and Config File" dialog][postprocessor1]
<br>Figure&nbsp;6. Select Output Database and Config File dialog.


[postprocessor2]: docs/img/postprocess2.png "Preview and Save Results to Database dialog"
![Image of "Preview and Save Results to Database" dialog][postprocessor2]
<br>Figure&nbsp;7. Preview and Save Results to Database dialog.


### Policrack Input `pickle` File

The file is created with each Policrack Model and contains the set of input parameters for the `PM`. It is stored in the Abaqus working directory along the `PM` with the same name, but with `.pickle` extension.


### Policrack Visualization

Policrack Visualizations are created with the Database Browser from Policrack database records.

To view an overlay of K-factors and Crack Propagation Direction, Figure&nbsp;8:
1. Select `Plot -> Allow Multiple Plot States`.
2. Select `Plot -> Symbols -> On Deformed Shape`.
3. From `Result -> Field Output` select `cpd_vect` as output variable and `Magnitude` as invariant.
4. Select `Plot -> Contours -> On Deformed Shape`.
5. From `Result -> Field Output` select `SIFs`.
6. You may modify the color map for either the contours and symbols from the `Options -> Contours` and `Options -> Symbols` menus.


[policrackVisualization]: docs/img/policrackVisualization.png "Policrack Visualization"
![Policrack Visualization][policrackVisualization]
<br>Figure&nbsp;8. Policrack Visualization.


### Policrack Database
Policrack databases are stored as subdirectories in the `policrack\db` directory.
The directory structure of a Policrack database is designed to be self-contained and accommodate additional information and analyses, pertaining to the database.
At the backend Policrack uses `Python shelve`.


#### New Policrack Database
When Policrack creates a new database, it creates a directory with a given name `database_name` in the `policrack\db\` directory. Then copies the contents of `policrack\templates\resultsRepo` to the new `policrack\db\database_name` directory.
A database is created when necessary by the Automated Batch tool or on demand with the Postprocessor tool.


#### Database Structure
Policrack stores database data file in the `policrack\db\database_name\resultsDb\` directory. The data file bears the name of the database `database_name`.

The `policrack\db\database_name\scripts` stores `Python` scripts and data required by the scripts. It contains the following scripts:
- `errors.py` &mdash; used to create a database record for a failed simulation.
- `verifyMergedNodes.py` &mdash; used to check the integrity of FEM simulations results data.


#### Creating a Record for a Failed Simulation
The `errors.py` script provides a way to create a database record with certain input parameters signifying an invalid parameter configuration. The record is designated as a failed simulation.

The script reads the `pickle` files from the `inputPickleFiles` directory and creates a database record for each file.

The utility of the script comes when a certain configuration of input parameters results in invalid model or should be skipped by Policrack.

The script is handy when using the Automated Batch tool and Policrack tries to generate a model that crashes Abaqus repeatedly or for whatever reason a record with that particular configuration of input parameters cannot be stored in the Policrack database automatically.

**Usage:** Copy the input `pickle` file in the `scripts\inputPickleFiles` directory of the database and run the `errors.py` script.


#### Database Integrity Checks for FEM Models
The `verifyMergedNodes.py` script verifies the merging of inner cylinder nodes of FEM models by evaluating log files. The check can only verify whether equal number of nodes have been merged on both sides of the crack. If numbers do not match or there is no log information about a database record, the script can delete the record.

Log files are `.txt` files stored in the `scripts\messages` directory. To create a log file, manually copy the output from the `Message Area` of the Abaqus/CAE window to a text file.

**Note:** Database records created by the `errors.py` may not have matching log information and `verifyMergedNodes.py` will remove them. You may need to rerun the `errors.py` after `verifyMergedNodes.py`.


#### Database Metadata
The database `id` &mdash; `metadata` is reserved for internal use. Each Policrack database has record with `metadata` `id`.
The record specifies crack type, load case string, and `History Output`s for all records in the database.
It also provides description and database version.

**Note:** The `metadata` `id` is for internal use. Do not create a Policrack model called `metadata`.


#### Security Warning

**Only use trusted sources, if you exchange Policrack databases or input `pickle` files.**



**NOTES:**
1. Abaqus is a commercial software from [Dassault Sytemes](https://www,3ds.com).
2. Policrack is not associated with Abaqus or Dassault Systemes.
