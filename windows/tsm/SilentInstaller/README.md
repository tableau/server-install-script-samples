# Windows TSM SilentInstaller
[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
----

The Tableau Services Manager on Windows uses a web UI approach to installing and configuring Tableau server. This approach works well for many users and administrators, but limits the ability to perform automated deployments using tools like Chef or Puppet.

We are providing some reference implementations to show users and organizations how they can automate deployment of Tableau Server on Windows, using scripts to prepare the installation and run the installer executable with appropriate command-line arguments.  

See also [Automated Installation of Tableau Services Manager](https://onlinehelp.tableau.com/current/server/en-us/automated_install_windows.htm) for general documentation regarding these scripts.

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
The script has three "modes"; _install_ _workerInstall_ and _updateTopology_; each mode can have several arguments. Since the automated installer is meant to run without user interaction, you must input all parameters into the required arguments that are passed to the script. Alternatively, you can also put the required arguments into the bootstrap file. You can use the file templates provided for each type of files below.

1. For installing initial node:

`python SilentInstaller.py install --secretsFile secrets.json --configFile myconfig.json --registrationFile registration.json Setup-Tabadmin-Webapp-x64.exe`
Or alternatively:
`python SilentInstaller.py --bootstrapFile <bootstrap file path>`

2. For installing additional nodes:

`python SilentInstaller.py workerInstall --secretsFile secrets.json --nodeConfigurationFile nodeConfiguration.json Setup-Tabadmin-Webapp-x64.exe`
Or alternatively:
`python SilentInstaller.py --bootstrapFile <bootstrap file path>`

3. For updating cluster topology: 

`python SilentInstaller.py updateTopology --secretsFile secrets.json --configFile myconfig.json`
Or alternatively:
`python SilentInstaller.py --bootstrapFile <bootstrap file path>`

*Special Note: When doing an installation for a distributed cluster, you will need to run install mode on the initial node, workerInstall mode on each additional node and updateTopology mode back on the initial node to update the cluster topology as desired.*

### Script arguments
#### _install_ mode
The automated installer script runs the proper commands to install, activate license, configure, and start Tableau Services Manager. 
Run SilentInstaller.py -h and SilentInstaller.py install –h to find out the most up-to-date list of options and their default values.

Option|Argument|Required|Description
----|----------|---------|-------
--installDir|[FILE PATH]|Optional|The Tableau installation directory. The software binaries will all live in a directory tree rooted here. _If omitted, the default directory C:\Program Files\Tableau\Tableau Server will be used for the binaries.
--dataDir|[FILE PATH]|Optional|The Tableau data location. The software configuration and data will all live in a directory tree rooted here. _If omitted, the default directory C:\ProgramData\Tableau_ will be used for the configuration and data files.
--installerLog|[FILE PATH]|Optional|Path to where the installer executable should write its log file. The directory must already exist. _If omitted, the log will be written under the user's TEMP directory._
--configFile|[FILE PATH]|**Required**| Path to a .json [Server Configuration File](#ConfigFile) (relative or absolute) describing the Tableau Server configuration. 
--secretsFile|[FILE PATH]|**Required**|Path to a .json file (relative or absolute) that describes both the credentials of the Windows account to authenticate to the Tableau Services Manager, and the username/password of the initial admin user for Tableau Server. Also the product key you would like to use to activate Tableau Server. The secrets template file contains a trial license by default.  See [Secrets File](#SecretsFile) for more information.
--registrationFile|[FILE PATH]|**Required**|Path to a .json file (relative or absolute) describing the Tableau Services Manager registration information. See [Server Registration File](#RegFile) for more information.
--controllerPort|[PORT]|Optional|The port on which the TSM Controller should run
--coordinationserviceClientPort|[PORT]|Optional|ZooKeeper client port
--coordinationservicePeerPort|[PORT]|Optional|ZooKeeper peer port
--coordinationserviceLeaderPort|[PORT]|Optional|ZooKeeper leader port
--start||Optional| Whether the server should be started at the end of setup
(installer executable)|[FILE PATH]|**Required**|The final argument to the script is simply the path, absolute or relative, to the Tableau Services Manager installer executable, acquired through usual channels such as downloaded from the Tableau Website. _This script is only supported for use with Tableau Services Manager._ 

#### _workerInstall_ mode
The automated installer script runs the proper commands to install Tableau Services Manager on the additional node. 
Run SilentInstaller.py installWorker –h to find out the most up-to-date list of options and their default values. 

Option|Argument|Required|Description
----|----------|---------|-------
--installDir|[FILE PATH]|Optional|The Tableau installation directory. The software binaries will all live in a directory tree rooted here. _If omitted, the default directory C:\Program Files\Tableau\Tableau Server will be used for the binaries.
--dataDir|[FILE PATH]|Optional|The Tableau data location. The software configuration and data will all live in a directory tree rooted here. _If omitted, the default directory C:\ProgramData\Tableau_ will be used for the configuration and data files.
--installerLog|[FILE PATH]|Optional|Path to where the installer executable should write its log file. The directory must already exist. _If omitted, the log will be written under the user's TEMP directory._
--secretsFile|[FILE PATH]|**Required**|Path to a .json file (relative or absolute) that describes both the credentials of the Windows account to authenticate to the Tableau Services Manager, and the username/password of the initial admin user for Tableau Server. Also the product key you would like to use to activate Tableau Server. The secrets template file contains a trial license by default.  See [Secrets File](#SecretsFile) for more information.
--nodeConfigurationFile|[FILE PATH]|**Required**|Path to the node configuration file for installing the additional node. 
(installer executable)|[FILE PATH]|**Required**|The final argument to the script is simply the path, absolute or relative, to the Tableau Services Manager installer executable, acquired through usual channels such as downloaded from the Tableau Website. _This script is only supported for use with Tableau Services Manager._ 

*Special Note: The node configuration file is automatically saved after installing the first node using SilentInstaller.py. You can find it under the working directory of the script.*

#### _updateTopology_ mode
The automated installer script runs the proper commands to update the cluster topology as desired for Tableau Services Manager. 
Run SilentInstaller.py updateTopology –h to find out the most up-to-date list of options and their default values. 

Option|Argument|Required|Description
----|----------|---------|-------
--secretsFile|[FILE PATH]|**Required**|Path to a .json file (relative or absolute) that describes both the credentials of the Windows account to authenticate to the Tableau Services Manager, and the username/password of the initial admin user for Tableau Server. Also the product key you would like to use to activate Tableau Server. The secrets template file contains a trial license by default.  See [Secrets File](#SecretsFile) for more information.
--configFile|[FILE PATH]|**Required**|Path to a .json [Server Topology File](#ConfigFile) (relative or absolute) describing the Tableau Server topology to update to. Only the topologyVersion part of the file will be applied, other configurations will be ignored in this mode. 

### Input File Samples 

#### <a name="SecretsFile"></a> Secrets file example
```
{
    "local_admin_user":"",
    "local_admin_pass":"",
    "content_admin_user":"",
    "content_admin_pass":"",
    "product_keys":["trial"]
}
```
The _local_admin_user_ is the Windows account to authenticate to the Tableau Services Manager.
The _content_admin_user_ is the initial administrative user, who acts as a superuser for all of Tableau Server with respect to creating and managing users, sites, etc. In the case of non _install_ mode, these credentials are ignored because the initial admin user has already been created.
The _product_keys_ is the key used to activate Tableau Services Manager. If multiple keys are specified, they will be activated one by one. In the case of non _install_ mode, these keys are ignored because the licenses have already been activated.

#### <a name="ConfigFile"></a> Server Configuration file example
```
{
   "configEntities":{
      "runAsUser":{
         "_type":"runAsUserType",
         "name":"NT AUTHORITY\\NetworkService"
      },
      "gatewaySettings":{
         "_type":"gatewaySettingsType",
         "port":80,
         "firewallOpeningEnabled":true,
         "sslRedirectEnabled":true,
         "publicHost":"****replace me****",
         "publicPort":80,
         "sslEnabled":false,
         "sslPort":443
      },
      "identityStore":{
         "_type":"identityStoreType",
         "type":"local",
         "domain":"****Domain Name Here****",
         "nickname":"****Domain Nickname Here****"
      }
   },
    "topologyVersion":{
        "nodes":{
            "****insert nodeId (lowercase) here****": {
                "services": {
                    "filestore": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "tabadmincontroller": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "clientfileservice": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "dataserver": {
                        "instances":[
                            {
                            "instanceId":"0"
                            },
                            {
                            "instanceId":"1"
                            }
                        ]
                    },
                    "cacheserver": {
                        "instances":[
                            {
                            "instanceId":"0"
                            },
                            {
                            "instanceId":"1"
                            }
                        ]
                    },
                    "vizqlserver": {
                        "instances":[
                            {
                            "instanceId":"0"
                            },
                            {
                            "instanceId":"1"
                            }
                        ]
                    },
                    "backgrounder": {
                        "instances":[
                            {
                            "instanceId":"0"
                            },
                            {
                            "instanceId":"1"
                            }
                        ]
                    },
                    "appzookeeper": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "pgsql": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "dataengine": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "licenseservice": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "searchserver": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "clustercontroller": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "tabsvc": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "vizportal": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "tabadminagent": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "clientfileservice": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    },
                    "gateway": {
                        "instances":[
                            {
                            "instanceId":"0"
                            }
                        ]
                    }
                }
            }
        }
    }
}
```
#### <a name="RegFile"></a> Server registration file example
```
{
    "first_name" : "John",
    "last_name" : "Smith",
    "email" : "john.smith@example.com",
    "company" : "Example, Inc",
    "title" : "Head Cat Herder",
    "department" : "Engineering",
    "industry" : "Finance",
    "phone" : "123-555-1212",
    "city" : "Kirkland",
    "state" : "WA",
    "zip" : "98034",
    "country" : "United States"
}
```

### Known Issues/Troubleshooting