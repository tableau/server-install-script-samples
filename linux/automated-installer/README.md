# Linux automated-installer
[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
----

Getting Started
---------------
This directory includes a sample Bash script for performing installs of Tableau Server on Linux in an automated fashion. This script supports both single and multi-node instances of Tableau Server. We have also included sample input files to the installer script.

The Tableau online help page [Automated Installation of Tableau Server](https://onlinehelp.tableau.com/current/server-linux/en-us/automated_install_linux.htm) explains how to use the automated-installer in detail. The packages subdirectory contains RPM & deb packages that install the scripts and template files as referenced in the documentation.

Please use GitHub 'Issues' to note any bugs or make suggestions.  

### Command line options

Many command line options mirror the options provided by `initialize-tsm` because they are passed through to that command. The current command line options are (as shown by the `-h` option):

```
  Usage: automated-installer -s secrets-file -f config-file -r registration-file --accepteula [optional arguments] package-file

  Installs the package and sets up directories and permissions to properly run Tableau Server, then
  begins Tableau Services Manager setup. After successful completion, Tableau Server should be fully operational.

  If you wish this system to be added as an additional node in an existing cluster, provide the -b bootstrap flag
  and the bootstrap file from the initial server.

  REQUIRED
    -s secrets-file                         The name of the secrets file, which provides the usernames for
                                            the TSM adminstrative user and Tableau Server administrator, and optionally
                                            their passwords. If passwords are not found in the secrets file,
                                            this script will prompt for them (not suitable for unattended
                                            installs).
                                            Tableau provides "secrets" as a template.

    -f config-file                          The name of the configuration and topology JSON file.
                                            Tableau provides "config.json" as a template.

    -r registration-file                    The name of the registration file.
                                            Tableau provides "reg_templ.json" as a template.

    --accepteula                            Indicate that you have accepted the End User License Agreement.

    package-file                            The rpm or deb file to install (e.g., tableau-server-10.0.0-1.x86_64.rpm

  OPTIONAL
    -d data-directory                       Set a custom location for the data directory if it's not already set.
                                            When not set, the initialize-tsm script uses its default value.

    -c config-name                          Set the service configuration name.
                                            When not set, the initialize-tsm script uses its default value.

    -k license-key                          Specify product key used to activate Tableau Server.
                                            When not set, trial license will be activated.

    -g                                      Do NOT add the current user to the "tsmadmin" administrative
                                            group, used for default access to Tableau Services Manager, or
                                            to the "tableau" group, used for easier access to log files.

    -a username                             The provided username will be used as the user to be added
                                            to the appropriate groups, instead of the user running this
                                            script. Providing both -a and -g is not allowed.

    -b bootstrap-file                       Location of the bootstrap file downloaded from the Tableau Services Manager
                                            on existing node. If this flag is provided, this node will be configured
                                            as an additional node for an existing cluster.

    -v                                      Verbose output.

    --force                                 Bypass warning messages.

    -i coordinationservice-client-port      Client port for the coordination service


    -e coordinationservice-peer-port        Peer port for the coordination service


    -m coordinationservice-leader-port      Leader port for the coordination service

    -n agent-filetransfer-port              Filetransfer port for the agent service

    -o controller-port                      Https port for the controller service

    -l port-range-min                       Lower port bound for automatic selection

    -x port-range-max                       Upper port bound for automatic selection

    --disable-port-remapping                Disable automatic port selection

    --unprivileged-user=<value>             Name of the unprivileged account to run Tableau Server.
                                            When not set, the initialize-tsm script uses its default value.

    --tsm-authorized-group=<value>          Name of the group(s) granted authorization to access Tableau Services Manager.
                                            When not set, the initialize-tsm script uses its default value.

    --disable-account-creation              Do not create groups or the user account. This option will prevent any calls to useradd
                                            or usermod (no users or groups will be created/edited). However, the values in: unprivileged-user,
                                            privileged-user and tsm-authorized-group will still be passed
                                            through for system configuration.

    --debug                                 Print each command as it is run for debugging purposes. Produces extensive
                                            output.
```

### Known Issues/Troubleshooting

* If automated-installer is not working properly in your environment, you can use the `--debug` option to echo every command run to stdout, which can be helpful in tracking down the issue.
* For additional troubleshotting tips for Tableau Server on Linux , See [Troubleshooting](https://onlinehelp.tableau.com/current/server-linux/en-us/trouble.htm)
