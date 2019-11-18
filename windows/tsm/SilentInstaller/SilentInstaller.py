from __future__ import print_function
import sys
import os
import argparse
import subprocess
import tempfile
import json
import socket
import unicodedata

try:
    import winreg
except ImportError:
    import _winreg as winreg

class Options(object):
    ''' Contains the user-configurable options for the installation,
    either specified directly on the command line, or in a bootstrap file '''

    defaults = {
        'installDir': r'C:\Program Files\Tableau\Tableau Server',
        'dataDir': r'C:\ProgramData\Tableau\Tableau Server',
        'controllerPort': '8850',
        'coordinationserviceClientPort': None,
        'coordinationservicePeerPort': None,
        'coordinationserviceLeaderPort': None,
        'licenseserviceVendorDaemonPort': None,
        'agentFileTransferPort': None,
        'portRangeMin': None,
        'portRangeMax': None,
        'portRemappingEnabled': None,
        'start': 'yes',
        'saveNodeConfiguration': 'yes',
        'nodeConfigurationDirectory': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nodeConfiguration.json'),
        'type': 'install'
    }

    updateTopologyRequired = [
        'secretsFile',
        'configFile'
    ]

    installRequired = [
        'secretsFile',
        'registrationFile',
        'configFile',
        'installer'
    ]

    installWorkerRequired = [
        'secretsFile',
        'nodeConfigurationFile',
        'installer'
    ]


    def __init__(self, user_options):

        # set the optional flags to their default values if not specified by the user
        for default_option in Options.defaults:
            if default_option in user_options:
                setattr(self, default_option, user_options[default_option])
            else:
                setattr(self, default_option, Options.defaults[default_option])

        # set the required options
        required_options = []
        if self.type == 'installWorker':
            required_options = Options.installWorkerRequired
        elif self.type == 'updateTopology':
            required_options = Options.updateTopologyRequired
        else:
            required_options = Options.installRequired

        for required_option in required_options:
            if required_option not in user_options:
                raise OptionsError('"%s" not specified' % required_option)
            setattr(self, required_option, user_options[required_option])

    def __str__(self):
        attributes = filter( lambda a: not (a.startswith('__') or a == 'defaults'), dir(self))
        return str({ attr: getattr(self, attr) for attr in attributes })


class OptionsError(Exception):
    ''' Input errors related to invalid or missing configuration options
        passed on the command line or in a configuration file '''
    pass


class ExistingInstallationError(Exception):
    ''' There is an existing installation of Tableau Server '''
    pass

class ExitCodeError(Exception):
    ''' An external command exited with a non-success exit code '''

    def __init__(self, binary, exit_code):
        super(ExitCodeError, self).__init__('%s execution exited with code: %d' % (str(binary), exit_code))
        self.exit_code = exit_code

def print_error(*args, **kwargs):
    '''  Prints an error string '''

    print(*args, file=sys.stderr, **kwargs)

def read_json_file(file_path):
    ''' Reads a json file '''

    try:
        with open(file_path) as json_file:
            return json.loads(json_file.read())
    except IOError as ex:
        raise OptionsError('Could not open json file "%s"' % file_path)
    except ValueError as ex:
        raise OptionsError('The json file "%s" contains malformed json' % file_path)

def make_cmd_line_parser():
    ''' Creates a parser for the arguments passed on this script's command line '''

    parser = argparse.ArgumentParser(
        description='Tableau Server silent installation script',
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    optional_flags = parser.add_argument_group('optional flags')
    optional_flags.add_argument('-h', '--help', action='help', help='display this message and exit')
    optional_flags.add_argument('--bootstrapFile', help='A json file containing all options listed here. When using this option, no other options can be specified on the command line.')

    # Required arguments
    subparsers = parser.add_subparsers(help='Install Server, Install Worker or Update Topology')

    ### INSTALL ARGS
    install_parser = subparsers.add_parser('install')
    install_parser.set_defaults(type='install')

    # Optional flags (have reasonable defaults)
    optional_flags = install_parser.add_argument_group('optional flags')
    optional_flags.add_argument('--installDir', help='Installation directory', default=Options.defaults['installDir'])
    optional_flags.add_argument('--dataDir', help='Data directory', default=Options.defaults['dataDir'])
    optional_flags.add_argument('--controllerPort', help='TSM conroller port', default=Options.defaults['controllerPort'])
    optional_flags.add_argument('--coordinationserviceClientPort', help='ZooKeeper client port', default=Options.defaults['coordinationserviceClientPort'])
    optional_flags.add_argument('--coordinationservicePeerPort', help='ZooKeeper peer port', default=Options.defaults['coordinationservicePeerPort'])
    optional_flags.add_argument('--coordinationserviceLeaderPort', help='ZooKeeper leader port', default=Options.defaults['coordinationserviceLeaderPort'])
    optional_flags.add_argument('--licenseserviceVendorDaemonPort', help='License Service vendor daemon port', default=Options.defaults['licenseserviceVendorDaemonPort'])
    optional_flags.add_argument('--agentFileTransferPort', help='Tabadmin Agent file transfer port', default=Options.defaults['agentFileTransferPort'])
    optional_flags.add_argument('--portRangeMin', help='Port range min', default=Options.defaults['portRangeMin'])
    optional_flags.add_argument('--portRangeMax', help='Port range max', default=Options.defaults['portRangeMax'])
    optional_flags.add_argument('--portRemappingEnabled', help='Whether port remapping is enabled', default=Options.defaults['portRemappingEnabled'])
    optional_flags.add_argument('--start', help='Should Tableau Server start at the end of the installation?', choices=['yes', 'no'], default=Options.defaults['start'])
    optional_flags.add_argument('--saveNodeConfiguration', help='Should Tableau Server save the node configuration file for worker installation?', choices=['yes', 'no'], default=Options.defaults['saveNodeConfiguration'])
    optional_flags.add_argument('--nodeConfigurationDirectory', help='Directory to save the node setup file for worker installation if you choose YES for --saveNodeConfigurationFile option', default=Options.defaults['nodeConfigurationDirectory'])

    # Required flags (no reasonable defaults)
    required_flags = install_parser.add_argument_group('required flags')
    required_flags.add_argument('--secretsFile', required=True, help='User credentials json file')
    required_flags.add_argument('--configFile', help='Configuration and topology json file')
    required_flags.add_argument('--registrationFile', help='User registration file')
    required_flags.add_argument('installer', help='Installer path, e.g: Tableau-Server-64bit-9-3-1.exe')

    ### INSTALL WORKER ARGS
    install_worker_parser = subparsers.add_parser('installWorker')
    install_worker_parser.set_defaults(type='installWorker')

    # Optional flags (no reasonable defaults)
    optional_flags = install_worker_parser.add_argument_group('optional flags')
    optional_flags.add_argument('--installDir', help='Installation directory', default=Options.defaults['installDir'])
    optional_flags.add_argument('--dataDir', help='Data directory', default=Options.defaults['dataDir'])

    # Required flags (no reasonable defaults)
    required_flags = install_worker_parser.add_argument_group('required flags')
    required_flags.add_argument('--nodeConfigurationFile', help='Node configuration json file')
    required_flags.add_argument('--secretsFile', required=True, help='User credentials json file')
    required_flags.add_argument('installer', help='Worker Installer path, e.g: Tableau-Worker-64bit-9-3-1.exe')

    ### UPDATE Topology ARGS
    update_topology_parser = subparsers.add_parser('updateTopology')
    update_topology_parser.set_defaults(type='updateTopology')

    # Optional flags (have reasonable defaults)
    optional_flags = update_topology_parser.add_argument_group('optional flags')
    optional_flags.add_argument('--installDir', help='Installation directory', default=Options.defaults['installDir'])
    optional_flags.add_argument('--controllerPort', help='TSM conroller port', default=Options.defaults['controllerPort'])

    # Required flags (no reasonable defaults)
    required_flags = update_topology_parser.add_argument_group('required flags')
    required_flags.add_argument('--secretsFile', required=True, help='User credentials json file')
    required_flags.add_argument('--configFile', help='Topology json file')

    return parser


def make_bootstrap_cmd_line_parser():
    parser = argparse.ArgumentParser(description='Tableau Server silent installation script')
    required_flags = parser.add_argument_group('required flags')
    required_flags.add_argument('--bootstrapFile', help='a json file containing all options listed here. When using this option, no other options can be specified on the command line.', required=True)
    # parser.print_usage = lambda x: print_error('When using the --bootstrapFile flag, no other flags are allowed')
    return parser


def run_command(binary_path, arguments, environment={}, show_args=False, return_result=False):
    ''' Run an external command in a subprocess and wait for it to finish '''

    result = None
    if not os.path.isfile(binary_path):
        raise OptionsError('The executable file %s does not exist' %binary_path)

    print("Running: " + str(binary_path) + str(arguments if show_args else ''))
    if return_result:
        if environment:
            proc = subprocess.Popen([binary_path] + arguments, env=environment, universal_newlines=True, stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen([binary_path] + arguments, universal_newlines=True, stdout=subprocess.PIPE)
    else:
        if environment:
            proc = subprocess.Popen([binary_path] + arguments, env=environment)
        else:
            proc = subprocess.Popen([binary_path] + arguments)
    result = proc.communicate()[0]
    exit_code = proc.returncode
    if exit_code != 0:
        raise ExitCodeError(binary_path, exit_code)
    return result

def run_installer(binary_path, arguments, environment={}, show_args=False, return_result=False):
    ''' Run an external command in a subprocess and wait for it to finish '''

    result = None
    if not os.path.isfile(binary_path):
        raise OptionsError('The executable file %s does not exist' %binary_path)

    print("Running: " + str(binary_path) + str(arguments if show_args else ''))
    if return_result:
        if environment:
            proc = subprocess.Popen(binary_path + arguments, env=environment, universal_newlines=True, stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen(binary_path + arguments, universal_newlines=True, stdout=subprocess.PIPE)
    else:
        if environment:
            proc = subprocess.Popen(binary_path + arguments, env=environment)
        else:
            proc = subprocess.Popen(binary_path + arguments)
    result = proc.communicate()[0]
    exit_code = proc.returncode
    if exit_code != 0:
        raise ExitCodeError(binary_path, exit_code)
    return result


def run_wix_installer(options):
    ''' Runs the installer.exe, and checks for the exit code. Return the installer version. '''

    wix_log_file = tempfile.NamedTemporaryFile(prefix='TableauServerInstaller_', suffix='.log', delete=True);
    wix_log_file_full_path = wix_log_file.name
    wix_log_file.close()

    wix_installer_args = ' /INSTALL /SILENT ACCEPTEULA=1'
    wix_installer_args += ' /LOG "' + wix_log_file_full_path + '"'
    wix_installer_args += ' INSTALLDIR="' + options.installDir + '"'
    wix_installer_args += ' DATADIR="' + options.dataDir + '"'
    wix_installer_args += ' CONTROLLERPORT=' + options.controllerPort

    if options.coordinationserviceClientPort is not None:
        wix_installer_args += ' COORDINATIONSERVICECLIENTPORT=' + options.coordinationserviceClientPort

    if options.coordinationservicePeerPort is not None:
        wix_installer_args += ' COORDINATIONSERVICEPEERPORT=' + options.coordinationservicePeerPort

    if options.coordinationserviceLeaderPort is not None:
        wix_installer_args += ' COORDINATIONSERVICELEADERPORT=' + options.coordinationserviceLeaderPort

    if options.licenseserviceVendorDaemonPort is not None:
        wix_installer_args += ' LICENSESERVICEVENDORDAEMONPORT=' + options.licenseserviceVendorDaemonPort

    if options.agentFileTransferPort is not None:
        wix_installer_args += ' AGENTFILETRANSFERPORT=' + options.licenseserviceVendorDaemonPort

    if options.portRangeMin is not None:
        wix_installer_args += ' PORTRANGEMIN=' + options.portRangeMin
 
    if options.portRangeMax is not None:
        wix_installer_args += ' PORTRANGEMAX=' + options.portRangeMax

    if options.portRemappingEnabled is not None:
        wix_installer_args += ' PORTREMAPPINGENABLED=' + options.portRemappingEnabled

    try:
        run_installer(options.installer, wix_installer_args, show_args=True)

        # The installer will setup two environment variables: TABLEAU_SERVER_DATA_DIR and TABLEAU_SERVER_INSTALL_DIR.
        # However, this shell session will not be able to pick them up unless the shell is restarted.
        # Here we update the current shell with those environment variables.
        os.environ["TABLEAU_SERVER_DATA_DIR"] = options.dataDir if isinstance(options.dataDir, str) else options.dataDir.encode('utf-8')
        os.environ["TABLEAU_SERVER_INSTALL_DIR"] = options.installDir if isinstance(options.installDir, str) else options.installDir.encode('utf-8')

        # read the version of the installer we just run
        hKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\CurrentControlSet\Control\Session Manager\Environment")                  
        result = winreg.QueryValueEx(hKey, "TABLEAU_SERVER_DATA_DIR_VERSION")
        winreg.CloseKey(hKey)
        # Return the read result
        return result[0]

    except ExitCodeError as ex:
        print_error('Error exit code from the Setup installer: %d' % ex.exit_code)

        # print the last 100 lines from the Setup log
        print_error_lines(wix_log_file_full_path)

    except OSError:
	    # the registry read most likely failed, so return none
        return str('none')

def run_worker_installer(options, secrets):
    ''' Runs the worker installer.exe, and checks for the exit code. Return the installer version. '''

    worker_log_file = tempfile.NamedTemporaryFile(prefix='TableauWorkerInstaller_', suffix='.log', delete=True);
    worker_log_file_full_path = worker_log_file.name
    worker_log_file.close()

    worker_installer_args = ' /INSTALL /SILENT ACCEPTEULA=1'
    worker_installer_args += ' /LOG "' + worker_log_file_full_path + '"'
    worker_installer_args += ' INSTALLDIR="' + options.installDir + '"'
    worker_installer_args += ' DATADIR="' + options.dataDir + '"'
    worker_installer_args += ' BOOTSTRAPFILE="' + options.nodeConfigurationFile + '"'

    my_env = os.environ.copy()
    my_env['TableauAdminUser'] = secrets['local_admin_user'] if isinstance(secrets['local_admin_user'], str) else secrets['local_admin_user'].encode('utf-8')
    my_env['TableauAdminPassword'] = secrets['local_admin_pass'] if isinstance(secrets['local_admin_pass'], str) else secrets['local_admin_pass'].encode('utf-8')

    try:
        run_installer(options.installer, worker_installer_args, environment=my_env, show_args=True)

    except ExitCodeError as ex:
        print_error('Error exit code from the Worker Setup installer: %d' % ex.exit_code)

        # print the last 100 lines from the worker Setup log
        print_error_lines(worker_log_file_full_path)


def print_error_lines(log_file_full_path):
    # print the last 100 lines from the log file
    print_error('For more details see log file %s' % log_file_full_path)
    with open(log_file_full_path) as log_file:
        content = log_file.readlines()
        for line in content[-100:]:
            print_error(line)
    raise


def run_tsm_command(tsm_path, secrets, args, port=8850, return_tsm_result=False):
    ''' Runs the tsm command to perform setup actions '''
    if port != 8850:
        args.extend(['--server', str.format('https://{}:{}',socket.gethostname(),port)])
    user_and_pass = ['-u', secrets['local_admin_user'], '-p', secrets['local_admin_pass']]
    try:
        return run_command(tsm_path, args + user_and_pass, return_result=return_tsm_result)
    except ExitCodeError as ex:
        print_error('Tabadmin exited with code %d' % ex.exit_code)
        raise ex

def run_tabcmd_command(tabcmd_path, args):
    ''' Runs a tabcmd command to perform setup actions '''
    try:
        run_command(tabcmd_path, args)
    except ExitCodeError as ex:
        print_error('Tabadmin exited with code %d' % ex.exit_code)
        raise ex

def getGatewayPort(configFile):
    ''' Retrieves the gateway port from the config file'''
    config = read_json_file(configFile)

    # from entity
    result = config.get('configEntities', {}).get('gatewaySettings',{}).get('port', None)

    # from key. will overwrite entity port if found.
    if 'configKeys' in config:
        if 'gateway.port' in config['configKeys']:
            key = config['configKeys']['gateway.port']
            if result != None:
                print('Warning: gateway.port key specified twice in the configuration template, using value of ' + key)
            result = key

    elif result == None:
        result = 80
        print('Warning: No gateway port specified, defaulting to port 80.')

    return result

def run_setup(options, secrets, package_version):
    ''' Runs a sequence of tsm commands to perform setup '''

    tsm_path = os.path.join(options.installDir, 'packages', 'bin.' + str(package_version), 'tsm.cmd')
    tabcmd_path = os.path.join(options.installDir, 'packages', 'bin.' + str(package_version), 'tabcmd.exe')

    port = options.controllerPort

    # activate a trial and/or any license keys specified in the secrets file
    product_keys = secrets.get('product_keys')
    if (isinstance(product_keys, list)):
        if ('trial' in product_keys):
            run_tsm_command(tsm_path, secrets, ['licenses','activate', '--trial'], port)
            print('Activated trial')
        for productKey in product_keys:
            if (len(productKey) > 0 and productKey != 'trial'):
                run_tsm_command(tsm_path, secrets, ['licenses','activate', '--license-key', productKey], port)
                print('Activated license key: ' + productKey)

    run_tsm_command(tsm_path, secrets, ['register', '--file', options.registrationFile], port)
    if options.saveNodeConfiguration == 'yes':
        run_tsm_command(tsm_path, secrets, ['topology', 'nodes', 'get-bootstrap-file', '--file', options.nodeConfigurationDirectory], port)
        print('Node configuration file saved.')
    run_tsm_command(tsm_path, secrets, ['settings', 'import', '--config-only', '-f', options.configFile], port)
    print('Configuration settings imported')
    run_tsm_command(tsm_path, secrets, ['pending-changes', 'apply', '--ignore-prompt', '--ignore-warnings'], port)
    print('Configuration applied')
    run_tsm_command(tsm_path, secrets, ['initialize', '--request-timeout', '7200'], port)
    print('Initialization completed')
    get_nodes_and_apply_topology(options.configFile, tsm_path, secrets, port)
    run_tsm_command(tsm_path, secrets, ['pending-changes', 'apply', '--ignore-prompt', '--ignore-warnings'], port)
    print('Topology applied')
    if options.start == 'yes':
        run_tsm_command(tsm_path, secrets, ['start', '--request-timeout', '1800'], port)
        print('Server is installed and running')
        run_tabcmd_command(tabcmd_path, ['initialuser', '--server', 'localhost:'+str(getGatewayPort(options.configFile)), '--username', secrets['content_admin_user'], '--password', secrets['content_admin_pass']])
        print('Initial admin created')
    print('Installation complete')

def get_options():
    ''' Parses the command line arguments and configuration files specified by the user '''

    if any([arg.startswith('--bootstrapFile') for arg in sys.argv]):
        # read the options from the bootstrap file
        cmd_parser = make_bootstrap_cmd_line_parser()
        bootstrap_file = cmd_parser.parse_args().bootstrapFile
        bootstrap_options = read_json_file(bootstrap_file)
        options = Options(bootstrap_options)
    else:
        # read the options from the command line
        cmd_parser = make_cmd_line_parser()
        cmd_line_args = cmd_parser.parse_args()
        options = Options(vars(cmd_line_args))

    return options

def get_secrets(options):
    ''' Retrieves the secrets from the user specified file '''

    return read_json_file(options.secretsFile)

def is_server_installed():
    ''' Checks if there is an existing installation of Tableau Server '''

    out = subprocess.check_output(['sc', 'query', 'type=', 'service', 'state=', 'all'])
    return ('Tableau Server' in str(out))

def assert_no_existing_installation():
    ''' Raises an error if there is an existing installation of Tableau Server '''

    if is_server_installed():
        raise ExistingInstallationError('An existing installation of Tableau Server has been found. '
            'Please uninstall it before updating to the new version. '
            'Data currently in Tableau server will be preserved during this process.')


def get_nodes_and_apply_topology(config_file, tsm_path, secrets, port, apply_and_restart=False):
    ''' Retrieves the nodes from the config file and apply topology update if all nodes are ready '''

    config = read_json_file(config_file)
    expected_nodes = set()
    if 'nodes' in config['topologyVersion']:
        # See if nodes are in entities, if yes get them
        nodes = config['topologyVersion']['nodes']
        for nodeId in nodes:
            expected_nodes.add(nodeId)
        nodes_output_list = run_tsm_command(tsm_path, secrets, ['topology', 'list-nodes'], port, return_tsm_result=True)
        actual_nodes = set(nodes_output_list.splitlines())
        if not expected_nodes.issubset(actual_nodes):
            # topology not ready with all expected nodes, return with no-op
            print('Not all nodes in desired topology are ready. Please make sure all worker nodes are installed properly then rerun SilentInstaller with updateTopology option.')
            print('Expected nodes: ' + ', '.join(expected_nodes))
            print('Actual nodes: ' + ', '.join(actual_nodes))
            return
        run_tsm_command(tsm_path, secrets, ['settings', 'import', '--topology-only', '-f', config_file], port)
        print('Topology applied')
        if apply_and_restart:
            run_tsm_command(tsm_path, secrets, ['pending-changes', 'apply', '--ignore-prompt', '--ignore-warnings'], port)
            print('Topology change has been applied.')
            for node in actual_nodes - expected_nodes:
                # nodes not listed in topology will be removed for consistency
                print('Removing extra node: ' + node)
                run_tsm_command(tsm_path, secrets, ['topology', 'remove-nodes', '-n', node], port)
                print('Node ' + node + 'has been removed. Please uninstall Tableau server from the node for complete clean up.')
            print('Restarting server...')
            run_tsm_command(tsm_path, secrets, ['restart'], port)
            print('Server is running after restart.')


def main():
    try:
        options = get_options()
        secrets = get_secrets(options)
        if options.type == 'updateTopology':
            package_path = os.path.join(options.installDir, "packages")
            lst = os.listdir(package_path)
            lst.sort(reverse=True)
            for subdir in lst:
                if "bin." in subdir:
                    tsm_path = os.path.join(package_path, subdir, "tsm.cmd")
                    found_tsm = False
                    if os.path.isfile(tsm_path):
                        get_nodes_and_apply_topology(options.configFile, tsm_path, secrets, options.controllerPort, apply_and_restart=True)
                        found_tsm = True
                        break
                    if not found_tsm:
                        raise OptionsError('Could not find tsm under directory %s. Please provide correct value in the installDir option' % options.installDir)
        else:
            assert_no_existing_installation()
            if options.type == 'installWorker':
                # install worker node
                run_worker_installer(options, secrets)
            else:
                # install and set up first node
                package_version = run_wix_installer(options)
                # only configure if we can determine the version that was installed.
                if package_version != 'none':
                    run_setup(options, secrets, package_version)
        return 0

    # by default exceptions exit with 1
    except ExistingInstallationError as ex:
        print_error(str(ex))
        return 2
    except OptionsError as ex:
        print_error(str(ex))
        return 3
    except ExitCodeError as ex:
        return 4


if __name__ == '__main__':
    sys.exit(main())
