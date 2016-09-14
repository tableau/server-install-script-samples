# server-install-script-samples
----

The Tableau Server installer uses a wizard-like approach to installing and configuring Tableau server. 
This approach works well for many users and administrators, but limits the ability to perform automated deployments using tools like Chef or Puppet.

We're providing some reference material here to show users and organizations how they can automate deployment
of Tableau Server, using scripts to prepare the installation and run the installer executable with appropriate command-line arguments.  

See also [Automated Unattended Installation of Tableau Server](http://onlinehelp.tableau.com/v10.1/server/en-us/server_install_unattended.htm) for general documentation regarding this feature.  

***Note: The samples contained in this repository only work with the Tableau Server 10.1 Beta 2 Installer.  For more information or to join the beta, please visit [http://www.tableau.com/tableau-10-beta-program](http://www.tableau.com/tableau-10-beta-program).***

Please use 'Issues' to note any bugs or make suggestions.  You can also e-mail [beta@tableau.com](mailto:beta@tableau.com) during the 10.1 Beta to provide additional feedback or receive support. 

Getting Started
---------------
This repository has the following samples for performing installs and/or upgrades of Tableau Server:

* **[ScriptedInstaller.py:](#ScriptedInstaller)** Python script for installing or upgrading Tableau Server.  This script supports both single and multi-node instances of Tableau Server. We have also included several samples of the input files to the installer script.
* **[public-sample-single-server.cfn:](#CloudFormationTemplate)** AWS Cloud Formation template for deploying a single-node instance of Tableau Server to Amazon AWS.

<a name="ScriptedInstaller"></a> ScriptedInstaller.py
----
This is a reference Python script to install or upgrade Tableau Server.

### Requirements
This script targets Python version 2.7.12. It also requires the PyYaml module which can be installed as follows:

`pip install pyyaml`

### Usage examples

The script has two "modes"; _install_ and _upgrade_ ; each mode can have several arguments.

For a new install:

`python ScriptedInstaller.py install --installerLog C:\Temp\tabinstall.txt --installDir C:\TableauServer --secretsFile secrets.json --configFile myconfig.yml --registrationFile registration.json --licenseKey THIS-IS-MYLI-CENS-EKEY Setup-Server-x64.exe`

*Special Note: When doing an installation on a distributed cluster, you will need to first run the Tableau Server Worker Installer on each worker machine and use the /PRIMARYIP switch to specify the IP Address/Hostname of the primary machine. Then run the Python script as shown above on the primary once all the software has been successfully installed on all workers.*

For an upgrade:

`python ScriptedInstaller.py upgrade --fastuninstall --installerLog C:\Temp\tabupgrade.txt --installDir C:\TableauServer  Setup-Server-x64.exe`

The script currently only supports upgrades from version 9.3.x or higher.


### Script arguments

#### _install_ mode

Option|Argument|Required|Description
----|----------|---------|-------
--installDir|[FILE PATH]|Optional|The Tableau installation directory. The software binaries, configuration, and data will all live in a a directory tree rooted here. _If omitted, the default directory C:\Program Files\Tableau\Tableau Server will be used for the binaries, and configuration and data will live under C:\Program Data\Tableau_
--configFile|[FILE PATH]|Optional|Path to a .yml [Server Configuration File](#ConfigFile) (relative or absolute) describing the Tableau Server configuration. This file's content is the same as the tabsvc.yml file. _If this argument is omitted, all Tableau defaults will be used for configuration._
--installerLog|[FILE PATH]|Optional|Path to where the installer executable should write its log file. The directory must already exist. _If omitted, the log will be written under the user's TEMP directory._
--enablePublicFwRule||Optional|Use this to specify that a firewall rule to enable connections to the Gateway process (if configured to be created at all), should also be enabled on the Windows "public" profile. _If omitted, the firewall rule, if created at all, will default to the private and domain profiles only_ 
--noAutorun| |Optional|Use this to skip setting up Tableau Server as a service to start on system boot. _If omitted, the server will be set up as a service to start on boot_
--secretsFile|[FILE PATH]|**Required**|Path to a .json file (relative or absolute) that describes both the credentials of the Windows account that Tableau Server will run as, and the username/password of the initial admin user for Tableau Server.  See [Secrets File](#SecretsFile) for more information.
--registrationFile|[FILE PATH]|**Required**|Path to a .json file (relative or absolute) describing the Tableau Server registration information. See [Server Registration File](#RegFile) for more information.
--licenseKey|[KEY]|**Required**|Your server license key, acquired through the usual channels.
(installer executable)|[FILE PATH]|**Required**|The final argument to the script is simply the path, absolute or relative, to the Tableau Server installer executable, acquired through usual channels such as downloaded from the Tableau Website. _This script is only supported for use with Tableau Server v10.1 and higher._ 

#### _upgrade_ mode

A quick note: the same installer executable used to perform a fresh install is used to perform an upgrade. The word 'install' in this section can be considered synonymous with 'upgrade'

Option|Argument|Required|Description
----|----------|---------|-------
--installDir|[FILE PATH]|Optional|The current Tableau installation directory. The software binaries, configuration, and data will all live in a a directory tree rooted here. If the script does not find an existing installation at this directory, it will abort. _If omitted, the default directory C:\Program Files\Tableau\Tableau Server will be used for the binaries, and configuration and data will live under C:\Program Data\Tableau_
--installerLog|[FILE PATH]|Optional|Path to where the installer executable should write its log file. The directory must already exist. _If omitted, the log will be written under the user's TEMP directory._
--fastuninstall| |Optional|  If specified, this will perform the upgrade using the /FASTUNINSTALL switch, which skips creating a backup before performing the upgrade (which uninstalls the old version and then installs the new version). This greatly speeds up the upgrade process; consider using this if you already have a recent backup or feel particularly lucky today. _If omitted, the upgrade process will not use /FASTUNINSTALL and a backup will be created before the upgrade is performed__
(installer_executable)|[FILE PATH]|**Required**|The final argument to the script is simply the path, absolute or relative, to the Tableau Server installer executable, acquired through usual channels such as downloaded from the Tableau Website. _This script is only supported for use with Tableau Server v10.1 and higher._ 

### Input File Samples 

#### <a name="SecretsFile"></a> Secrets file example
```
{
	"runas_user":"workgroup\serviceuser",
	"runas_pass":"password",
	"content_admin_user":"admin",
	"content_admin_pass":"password"
}
```
If _runas_user_ is not set, the system will use the Windows built-in user _NT AUTHORITY\NETWORK SERVICE_. If _runas_pass_ is not set, the system will assume the password is blank.

The admin user is the initial user, who acts as a superuser for the whole Tableau Server in regards to creating users, creating sites, etc.

#### <a name="ConfigFile"></a> Server Configuration file example
```
---
config.version: 15
vizqlserver.data_refresh: 6
worker0.backgrounder.procs: 3
worker0.cacheserver.procs: 3
worker0.dataengine.procs: 2
worker0.dataserver.procs: 3
worker0.gateway.port: 88
worker0.vizportal.procs: 4
worker0.vizqlserver.procs: 3
storage.monitoring.critical_percent: 12
storage.monitoring.email_enabled: true
storage.monitoring.email_interval_min: 65
storage.monitoring.warning_percent: 22
subscriptions.enabled: true
svcmonitor.notification.smtp.canonical_url: http://mylinkurl.example.com
svcmonitor.notification.smtp.enabled: true
svcmonitor.notification.smtp.from_address: donotreply@example.com
svcmonitor.notification.smtp.password: smtppassword
svcmonitor.notification.smtp.send_account: smtpuser
svcmonitor.notification.smtp.server: mail.example.com
svcmonitor.notification.smtp.target_addresses: heeeeelp@example.com
vizqlserver.data_refresh: 6
service.init.state: start
```


Hint: To install a server with the same configuration as an existing server, you can just copy the contents of the existing server's _tabsvc.yml_ file. By default this is located in `C:\ProgramData\Tableau\Tableau Server\config` . If you use an existing file, you need to add the _config.version:_ (15 for 10.1) so the server can handle any conversions, updates, or configuration options.

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

* If you use the `--configfile` option to specify a custom configuration file, verify that the .yml file that you provide is valid for your Tableau Server installation.  Pay special attention that hostnames and IP addresses match those of the cluster that you are deploying to.
* Upgrades using the Python script only work for upgrades from v9.3 and higher.  For previous version of Tableau Server, you will need to first uninstall Tableau Server from the primary machine and all worker machines.  Then, proceed as you would for a multi-node install of Tableau Server.

<a name="CloudFormationTemplate"></a> public-sample-single-server.cfn
-----------------
This is a sample [Cloud Formation Template](https://aws.amazon.com/cloudformation/) for automating the deployment of Tableau Server to Amazon AWS.  This Cloud Formation template will deploy a default single-node instance using local authentication and default configurations.  The template allows for minimal customization of the Gateway port and process counts on the server.

Time to Deploy: Approximately 30 minutes.
### Requirements
* You must have your own provisioned AWS account.
* You must have a [Amazon EC2 Key Pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html).
* You must create an named [AWS S3](https://aws.amazon.com/s3/) bucket containing the following items:
	* A copy of ScriptedInstaller.py
	* Python 2.7.12.msi installer
	* A copy of the Tableau Server 10.1 Beta 2 installer 
	* A copy of public-sample-single-server.cfn *(Optional)* 

### Usage

1. On the AWS Console go to CloudFormation > Create Stack.
2. Select the template file (public-sample-single-server.cfn) > Click Next.
3. Provide a "Stack name" and fill out the rest of the parameters including License, Registration, and Admin account information for your Tableau Server installation.
4. Continue through the rest of the screens and Accept the IAM warning and click Submit.
5. Once the status has changed to CREATE_COMPLETE. Click on the Outputs tab and copy the PublicDNSName and/or PublicIpAddress.
6. Verify that you can connect to Tableau Server by navigating to the PublicDNSName/PublicIpAddress and logging in with the admin account that you specified.

### Known Issues/Troubleshooting Steps

None as of this writing.