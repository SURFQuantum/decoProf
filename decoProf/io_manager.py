import time
import os
import argparse
import sys
import shutil
import errno


from decoProf.info import PACKAGE_NAME, PACKAGE_VERSION


class IOManager:
    def __init__(self):
        self._working_dir_name = ''

    def get_working_dir_name(self):
        if not self._working_dir_name:
            self.print_err_info('Empty name of the working directory.')
            exit(errno.EFAULT)
        else:
            return self._working_dir_name

    def set_working_dir_name(self, name):
        self._working_dir_name = name

    def print_msg_with_header(self, msg_header, msg):
        """
        Print a message with a header to terminal
        :param msg_header: Header of the message
        :param msg: Message body
        :return: None
        """
        print(msg_header, end=' ')
        print(msg)

    def print_dbg_info(self, msg):
        """
        Print a debug message to terminal
        :param msg: Message body
        :return: None
        """
        msg_header = "== DEBUG =="
        if __debug__:
            self.print_msg_with_header(msg_header, msg)

    def print_err_info(self, msg):
        """
        Print an error message to terminal
        :param msg: Message body
        :return: None
        """
        msg_header = "== ERROR =="
        self.print_msg_with_header(msg_header, msg)

    def write_to_file(self, file_name, body):
        """
        Write "body" into a file "file_name"
        :param file_name: Filename
        :param body: File bofy
        :return: None
        """
        file = open(file_name, 'w')
        file.write(body)
        file.close()

    def check_if_project_exists(self, project_name):
        """
        Check if project folder exists
        :param project_name: Name of the project folder
        :return: True if project folder exists, False otherwise
        """
        return os.path.exists(project_name)

    def create_working_dir(self, project_name):
        """
        Create temporary directory with a unique name using a timestamp
        :param project_name: Name of the project folder
        :return: None
        """
        # Before creating the working copy - check if the project actually exists
        if not self.check_if_project_exists(project_name):
            self.print_err_info('Can\'t find the project folder: ' + project_name)
            exit(errno.EFAULT)

        timestamp = str(time.time()).replace('.', '')
        self.set_working_dir_name(os.path.basename(project_name) + "_" + timestamp)

        self.print_dbg_info('Creating temporary directory: ' + self.get_working_dir_name())

        try:
            os.mkdir(self.get_working_dir_name())
        except OSError as err:
            self.print_err_info('Can\'t create a working directory: ' + err)
            exit(errno.EFAULT)

    def check_arg_existence(self, arg, arg_name, parser):
        """
        Check existence of a mandatory argument. Throw an error and exit if argument
        is not specified
        :param arg: Argument to be checked
        :param arg_name: Argument's meta name
        :param parser: Parser object
        :return: None
        """
        if arg is None:
            self.print_err_info(arg_name + ' is not specified.')
            parser.print_help()
            exit(errno.EFAULT)

    def parse_cli(self, known_profiler_types):
        """
        Parse CLI arguments passed to this script and check for their correctness.
        :return: Object of parsed arguments.
        """
        # Instantiate the parser
        args = None
        profiler_keys = known_profiler_types.keys()
        parser = argparse.ArgumentParser(prog=PACKAGE_NAME, usage='%(prog)s [options]',
                                         description='Create call tree.')
        parser.add_argument('-v', '--version', action='version',
                            version=str(PACKAGE_VERSION),
                            help='Print version of the package.')
        parser.add_argument('-f', metavar='<filename>', type=str,
                            help='Specify the file name.')
        parser.add_argument('-p', metavar='<project name>', type=str,
                            help='Specify the project name.')
        parser.add_argument('-n', metavar='<function name>', type=str,
                            help='Function name to be analyzed. If the function is an inner '
                                 'function or a class member, the name of the corresponding '
                                 'outer function or class should be prepended to the function '
                                 'name and separated by the dot, e.g. "-n foo.bar".')
        parser.add_argument('-t', metavar='<profiler type>', type=str,
                            help='Type of the profiler to be used '
                                 '(available options: '
                                 + ', '.join(profiler_keys) + ').')

        # Check if we have enough arguments, otherwise print an error and the help message
        if len(sys.argv) > 1:
            args = parser.parse_args()

            # All CLI arguments are mandatory
            self.check_arg_existence(args.f, 'Filename', parser)
            self.check_arg_existence(args.p, 'Project name', parser)
            self.check_arg_existence(args.n, 'Function name', parser)
            # check_arg_existence(args.t, 'Profiler type', parser)
            # Set default profiler type if it was not specified
            if args.t is None:
                args.t = "cpu"

            # Print some debug info
            self.print_dbg_info('Filename: \t' + str(args.f))
            self.print_dbg_info('Project name: \t' + str(args.p))
            self.print_dbg_info('Function name: \t' + str(args.n))
            self.print_dbg_info('Profiler type: \t' + str(args.t))

            # Check that the profiler type is knowns
            if args.t not in profiler_keys:
                self.print_err_info('Unknown profiler type. Available options: '
                                    + ', '.join(profiler_keys))
                exit(errno.EFAULT)
        else:
            self.print_err_info('No CLI arguments passed.')
            parser.print_help()
            exit(errno.EFAULT)

        return args

    def make_working_copy_of_project(self, src_dir_name):
        """
        Copy source files to the working directory
        :param src_dir_name: Path to the directory with source files
        :return: None
        """
        self.print_dbg_info('Copying sources to the temporary directory: ' + src_dir_name
                            + ' --> ' + self.get_working_dir_name())
        shutil.copytree(src_dir_name, self.get_working_dir_name(), dirs_exist_ok=True)
