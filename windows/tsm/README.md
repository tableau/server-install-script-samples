# Windows TSM SilentInstaller
[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
----

The Tableau Services Manager on Windows uses a web UI approach to installing and configuring Tableau server. This approach works well for many users and administrators, but limits the ability to perform automated deployments using tools like Chef or Puppet.

We are providing some reference implementations to show users and organizations how they can automate deployment of Tableau Server on Windows, using scripts to prepare the installation and run the installer executable with appropriate command-line arguments.  

See also [Automated Installation of Tableau Services Manager]() for general documentation regarding these scripts.

Please use 'Issues' to note any bugs or make suggestions.  

Getting Started
---------------
This repository includes a sample Python script for performing installation of Tableau Services Manager.  This script supports both single and multi-node instances of Tableau Server. We have also included several samples of the input files to the installer script.

<a name="SilentInstaller"></a> SilentInstaller.py
----
This is a reference Python script to install Tableau Services Manager.

### Requirements
This script targets Python version 3.5 or later. 

### Usage examples

### Script arguments
Run SilentInstaller.py -h and SilentInstaller.py install –h to find out the most up-to-date list of options and their default values.
 
The script requires the following files:
•	Secrets file. Contains the username and password used to authenticate to the Tableau Services Manager, as well as the username and password desired for the initial administrator user for Tableau Server. Also the product key you would like to use to activate Tableau Server. The secrets template file contains a trial license by default. 
•	Registration file. Contains information about your organization to register Tableau Server.
•	Configuration file. Contains an example configuration for the server using local authentication. 
•	Bootstrap file. An optional json file that can specify paths to all the required files listed above (so that they don't have to be typed through the command line manually).
The script can also take the following optional parameters:
•  --installDir: installation location (binaries, including tsm.cmd)
•  --dataDir: data location (service directories, logs, etc. )
•  --controllerPort: the port on which the TSM Controller should run
•  --coordinationserviceClientPort: ZooKeeper client port
•  --coordinationservicePeerPort: ZooKeeper peer port
•  --coordinationserviceLeaderPort: ZooKeeper leader port
•  --start: whether the server should be started at the end of setup
 
The automated installer script runs the proper tsm commands to install, activate license, configure, and start Tableau Server. 
 
Since the automated installer is meant to run without user interaction, you must input all parameters into the required files that are passed to the script. You can use the file templates provided for each type of files above.
To run the automated installer, run the following command: 
   Python.exe SilentInstaller.py --bootstrapFile <bootstrap file path>
Or alternatively, run the following command:
   Python.exe SilentInstaller.py install --secretsFile <secrets file path> --registrationFile <registration file path>  --configFile <configuration file path>  <installer exe path>

To install additional node in the cluster, run SilentInstaller.py installWorker –h to find out the most up-to-date list of options and their default values. You can run the following on each worker node: 
   Python.exe SilentInstaller.py --bootstrapFile <worker bootstrap file path>
Or alternatively, run the following command:
   Python.exe SilentInstaller.py installWorker --secretsFile <secrets file path> --nodeConfigurationFile <node configuration file path>  <installer exe path>
   Note: the node configuration file is automatically saved after installing the first node using SilentInstaller.py. You can find it under the working directory of the script.
   
To update cluster topology after installing all nodes in the cluster, run SilentInstaller.py updateTopology –h to find out the most up-to-date list of options and their default values. You can run the following on the first node: 
   Python.exe SilentInstaller.py --bootstrapFile <worker bootstrap file path>
Or alternatively, run the following command:
   Python.exe SilentInstaller.py updateTopology --secretsFile <secrets file path> --configFile <configuration file path>