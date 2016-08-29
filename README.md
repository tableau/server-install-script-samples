# server-install-script-examples
----

The Tableau Server installer uses a wizard-like approach to installing and configuring Tableau server. 
This approach works well for many users and administrators, but limits the ability to perform automated deployments
using tools like Chef or Puppet.

We're providing some reference material here to show users and organizations how they can automate deployment
of Tableau Server, using scripts to prepare the installation and run the installer executable with appropriate command-line arguments.

## ScriptedInstaller.py
----
This is a reference Python script to install a single-node Tableau Server. This script targets Python version 2.7.2; it's unknown if/how it will work with other versions. No modules outside of the default installation are needed.

Usage example:

`python ScriptedInstaller.py --installerLog C:\Temp\tabinstall.txt --installDir C:\TableaServer --autorun --secretsFile secrets.json --configFile myconfig.yml --registrationFile registration.json --licenseKey THIS-IS-MYLI-CENS-EKEY Setup-Server-x64.exe`

### Script arguments
* --installerLog  _**Not required**_

  Path to where the installer executable should write its log file. The directory must already exist. _If omitted, the log will be written under the user's TEMP directory._

* --installDir  _**Not Required**_

  The Tableau installation directory. The software binaries, configuration, and data will all live in a a directory tree rooted here. _If omitted, the default directory C:\Program Files\Tableau\Tableau Server will be used for the binaries, and configuration and data will live under C:\Program Data\Tableau_

* --autorun | --no-autorun _**Not required**_

  Whether or not to configure Tableau Server to run automatically on system bootup. _If omitted, this defaults to True._

* --secretsFile _**Required**_

  Path to a .json file (relative or absolute) that describes both the credentials of the Windows account that Tableau Server will run as, and the username/password of the initial admin user for Tableau Server.

* --configFile _**Not Required**_

  Path to a .yml file (relative or absolute) describing the Tableau Server configuration. This file's content is the same as the tabsvc.yml file. _If this argument is omitted, all Tableau defaults will be used for configuration._

* --registrationFile _**Required**_

  Path to a .json file (relative or absolute) describing the Tableau Server registration information. 

* --licenseKey _**Required**_

  Your server license key, acquired through the usual channels.

* installer_executable _**Required**_

  The final argument to the script is simply the path, absolute or relative, to the Tableau Server installer executable, acquired through usual channels such as downloaded from the Tableau Website.

### File Structure

#### Secrets file example
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

#### Server Configuration file example
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
The config options available are beyond the scope of this document. Hint: To install a server with the same configuration as an existing server, you can just copy the contents of the existing server's _\<TopLevelDir>/config/tabsvc.yml_ . You do need the _config.version_ so the server can handle any conversions or updates or configuration options, if required.

#### Server registration file example
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

	