The yaml and txt files include an overview of the package versions used in this project.

# Top level

* WritingAssistantInterface-env-top-level.yml contains the packages that can be installed from conda-forge.
* WritingAssistantInterface-pip-top-level.pip contains the packages that can be installed with pip.

Both files contain top-level packages; dependencies are not 
included. The files can be used to create a conda environment by running:

1-setup-top-level.bat

# Export

Exporting the environment to a file can be done with:

2-export-environment.bat

This script will create yaml file that contains all packages installed from conda-forge and pip, including their dependencies.
For the environment that is created from the above mentioned files, the export can be found in:

* WritingAssistantInterface-env-explicit.yml
* WritingAssistantInterface-pip-explicit.yml

# Explicit

In case the virtual environment cannot be created from the top-level files, the explicit files included can be used to re-create the conda environment with all packages and dependencies included.

To re-create the environment from the explicit files, run:

* 3-setup-explicit-versions.bat

In case a dependency is no longer available, the top-level files can be altered and when a working environment is set up, a snapshot of the environment can be created with the above mentioned export script.  

