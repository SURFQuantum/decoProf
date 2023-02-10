import os
import subprocess
import ast
import astunparse
import json

from decoProf.io_manager import IOManager
from decoProf.info import PACKAGE_NAME


class Core:
    def __init__(self):
        """
        :_profiler_types: Dictionary of profiler types and corresponding decorator names
        :_profiler_module_name: Name of the module that should be added to the "import"
                                statement at the header of the script
        :_profiler_class_name: Name of the class from the "module_name"
        :_io_man: Object of the IO manager
        :function_name: Function name to which the decorator should be added to
        :decorator_name: Name of the decorator that should be injected
        """
        self._profiler_module_name = 'genericProfiler'
        self._profiler_class_name = 'ProfileDecorators'
        self._profiler_types = {'cpu': 'gp.cprofile_decorator',
                                'mem': 'gp.memory_profiler_decorator',
                                'call_stack': 'gp.pyinstrument_decorator',
                                'thread': 'gp.yappi_decorator',
                                'line': 'gp.line_profiler_decorator',
                                }
        self._io_man = IOManager()

        self.file_name = ''
        self.project_name = ''
        self.function_name = []
        self.decorator_name = ''

    def generate_call_tree(self):
        """
        Generate a call tree using PyCG package (see https://github.com/vitsalis/PyCG).
        PyCG is called using a subprocess and generates a JSON file as a result of its execution
        :return: Output filename
        """
        # working_dir_name - name of the working directory where the
        # JSON file will be stored. It's also used as a basename
        # for the JSON file
        working_dir_name = self._io_man.get_working_dir_name()

        # Assemble unique output filename
        output_filename = os.path.join(working_dir_name, working_dir_name + '.json')
        self._io_man.print_dbg_info('Call tree is written to the file: \t' + output_filename)

        # Execute PyCG
        subprocess.run(['pycg', '--package', self.project_name,
                        os.path.join(self.project_name, self.file_name),
                        '-o', output_filename])

        return output_filename

    def read_call_tree(self, filename):
        """
        Read the call tree from a file
        :param filename: Filename
        :return: Dictionary of a call tree
        """
        call_tree = None
        with open(filename) as json_file:
            call_tree = json.load(json_file)
        return call_tree

    def write_modified_src(self, src_tree, working_copy_filename):
        """
        Write AST to the file
        :param src_tree: AST object
        :param working_copy_filename: Filename AST should be written into
        :return: None
        """
        self._io_man.write_to_file(working_copy_filename, astunparse.unparse(src_tree))

    def append_decorator_to_tree(self, node, function_name, decorator_name):
        """
        Append decorator to the AST's structure
        :param node: Node which should contain the function
        :param function_name: Function name to which we should add decorator to
        :param decorator_name: Name of the decorator
        :return: Tuple of the function name and boolean. True, if function was found,
                 False otherwise
        """
        function_found = ('', False)

        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef):
                if child.name == function_name:
                    self._io_man.print_dbg_info('Function_name: ' + child.name)
                    self._io_man.print_dbg_info('Original decorator_list: ')
                    self._io_man.print_dbg_info(child.decorator_list)

                    child.decorator_list.append(ast.Name(id=decorator_name, ctx=ast.Load()))

                    self._io_man.print_dbg_info('Modified decorator_list: ')
                    self._io_man.print_dbg_info(child.decorator_list)
                    function_found = (function_name, True)

        return function_found

    def inject_decorator(self, src_tree):
        """
        Inject decorator to the AST
        :param src_tree: AST
        :return: None
        """
        pattern_names = [elt.split('.') for elt in self.function_name]
        function_found = ('', False)

        for pattern_name in pattern_names:
            is_class = False
            if len(pattern_name) > 1:
                is_class = True
                self._io_man.print_dbg_info('Function "' + pattern_name[1] + '" is a member of a class or an inner '
                                                                             'function')
            else:
                self._io_man.print_dbg_info('Function "' + pattern_name[0] + '" is a static function')

            # print_dbg_info(ast.dump(src_tree))
            file_name = os.path.join(self._io_man.get_working_dir_name(), self.file_name + '_ast.json')
            self._io_man.write_to_file(file_name, ast.dump(src_tree))
            self._io_man.print_dbg_info('AST is written to the file: ' + file_name)

            for node in ast.walk(src_tree):
                if is_class:
                    if isinstance(node, ast.ClassDef) and node.name == pattern_name[0] \
                            or isinstance(node, ast.FunctionDef) and node.name == pattern_name[0]:
                        function_found = self.append_decorator_to_tree(node, pattern_name[1], self.decorator_name)
                        break
                else:
                    function_found = self.append_decorator_to_tree(node, pattern_name[0], self.decorator_name)
                    break

        if not function_found[1]:
            self._io_man.print_err_info('Function "' + pattern_name[0]
                                        + '" was not found in the file ' + self.file_name)

        # print_dbg_info(ast.dump(src_tree))
        #
        # print_dbg_info('Modified code:')
        # print_dbg_info(astunparse.unparse(src_tree))

    def inject_import(self, src_tree):
        """
        Inject "import" statement at the beginning of the source file
        :param src_tree: AST
        :return: None
        """
        full_module_name = PACKAGE_NAME + '.' + self._profiler_module_name
        import_node = ast.ImportFrom(module=full_module_name,
                                     names=[ast.alias(name=self._profiler_class_name, asname='gp')],
                                     level=0)
        src_tree.body.insert(0, import_node)

    def generate_ast(self, filename):
        """
        Parse source file to build AST
        :param filename: Filename
        :return: AST object
        """
        file = open(filename, 'r')
        code = file.read()
        file.close()

        src_tree = ast.parse(code)

        return src_tree

    def detect_prof_type(self, args):
        """
        Detect type of the profiler
        :param args: List of CLI arguments
        :return: Decorator name
        """
        return self._profiler_types[args.t]

    def configure(self):
        """
        Perform initial configuration of the script
        :return: None
        """
        # Parse CLI arguments
        args = self._io_man.parse_cli(self._profiler_types)
        self.file_name = args.f
        self.project_name = args.p
        self.function_name = str(args.n).split(',')

        # Detect the profiler type
        self.decorator_name = self.detect_prof_type(args)

    def prepare_fs(self):
        """
        Prepare file system by creating a working directory and copying the original
        sources in it
        :return: None
        """
        # Create a temporary directory
        self._io_man.create_working_dir(self.project_name)

        # Make a working copy of the scripts we are going to work with
        self._io_man.make_working_copy_of_project(self.project_name)

    def assemble_wrk_copy_filename(self):
        """
        Assemble the filename for the working copy
        :return: Assembled name
        """
        working_copy_filename = os.path.join(self._io_man.get_working_dir_name(), self.file_name)
        self._io_man.print_dbg_info("Working copy filename: " + working_copy_filename)
        return working_copy_filename

    def modify_src(self, as_tree):
        """
        Modify source code by injecting a decorator and import statements
        :param as_tree: AST
        :return: None
        """
        # Inject decorator into the source code
        self.inject_decorator(as_tree)

        # Inject "import" statement into the source code
        self.inject_import(as_tree)

        self._io_man.print_dbg_info('Modified code:')
        self._io_man.print_dbg_info(astunparse.unparse(as_tree))

    def run(self):
        """
        1) Analyze CLI arguments
        2) Generate a call tree
        3) Generate an AST
        4) Modify the source file
        :return: None
        """
        # self._io_man.print_msg_with_header('', '--------------------')
        # self._io_man.print_msg_with_header('', 'Starting the decorator injector...')

        # Configure the script
        self.configure()

        # Prepare file system
        self.prepare_fs()

        # Run call tree generator
        call_tree_filename = self.generate_call_tree()
        # call_tree = self.read_call_tree(call_tree_filename)

        # Run AST
        working_copy_filename = self.assemble_wrk_copy_filename()
        as_tree = self.generate_ast(working_copy_filename)

        # Modify original source code
        self.modify_src(as_tree)

        # Write modified AS tree back into the file
        self.write_modified_src(as_tree, working_copy_filename)

        self._io_man.print_msg_with_header('', '--------------------')
        self._io_man.print_msg_with_header('', 'Finished...')
        self._io_man.print_msg_with_header('', 'See %s for the modified copy of the original code'
                                           % working_copy_filename)
