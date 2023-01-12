import os
import subprocess
import ast
import astunparse
import json

from io_manager import IOManager

PACKAGE_NAME = 'decoProf'
PACKAGE_VERSION = '0.0.1'


class Core:
    def __init__(self):
        """
        :_profiler_types: Dictionary of profiler types and corresponding decorator names
        :_profiler_module_name: Name of the module that should be added to the "import"
                                statement at the header of the script
        :_profiler_class_name: Name of the class from the "module_name"
        :_io_man: Object of the IO manager
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

    def generate_call_tree(self, args):
        """
        Generate a call tree using PyCG package (see https://github.com/vitsalis/PyCG).
        PyCG is called using a subprocess and generates a JSON file as a result of its execution
        :param args: List of CLI arguments passed to this script
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
        subprocess.run(['pycg', '--package', str(args.p),
                        os.path.join(str(args.p), str(args.f)),
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

    def dump_decorated_src(self, src_tree, working_copy_filename):
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
        :return: None
        """
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef):
                if child.name == function_name:
                    self._io_man.print_dbg_info('Function_name: ' + child.name)
                    self._io_man.print_dbg_info('Original decorator_list: ')
                    self._io_man.print_dbg_info(child.decorator_list)

                    child.decorator_list.append(ast.Name(id=decorator_name, ctx=ast.Load()))

                    self._io_man.print_dbg_info('Modified decorator_list: ')
                    self._io_man.print_dbg_info(child.decorator_list)

    def inject_decorator(self, src_tree, function_name, decorator_name):
        """
        Inject decorator to the AST
        :param src_tree: AST
        :param function_name: Function name to which the decorator should be added to
        :param decorator_name: Name of the decorator that should be injected
        :return: None
        """
        pattern_names = str(function_name).split('.')

        is_class = False
        if len(pattern_names) > 1:
            is_class = True
            self._io_man.print_dbg_info('Function "' + function_name + '" is a member of a class or an inner function')
        else:
            self._io_man.print_dbg_info('Function "' + function_name + '" is not a member of a class')

        # print_dbg_info(ast.dump(src_tree))
        file_name = function_name + '_ast.json'
        self._io_man.write_to_file(file_name, ast.dump(src_tree))
        self._io_man.print_dbg_info('AST is written to the file: ' + file_name)

        for node in ast.walk(src_tree):
            if is_class:
                if isinstance(node, ast.ClassDef) and node.name == pattern_names[0] \
                        or isinstance(node, ast.FunctionDef) and node.name == pattern_names[0]:
                    self.append_decorator_to_tree(node, pattern_names[1], decorator_name)
                    break
            else:
                self.append_decorator_to_tree(node, pattern_names[0], decorator_name)
                break

        # print_dbg_info(ast.dump(src_tree))
        #
        # print_dbg_info('Modified code:')
        # print_dbg_info(astunparse.unparse(src_tree))

    def inject_import(self, src_tree, module_name, class_name):
        """
        Inject "import" statement at the beginning of the source file
        :param src_tree: AST
        :param module_name: Module to be imported
        :param class_name: Class name from the 'module_name'
        :return: None
        """
        full_module_name = PACKAGE_NAME + '.' + module_name
        import_node = ast.ImportFrom(module=full_module_name,
                                     names=[ast.alias(name=class_name, asname='gp')],
                                     level=0)
        src_tree.body.insert(0, import_node)

    def parse_src_file(self, filename):
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

    def run(self):
        """
        1) Analyze CLI arguments
        2) Generate a call tree
        :return: None
        """
        # Parse CLI arguments
        args = self._io_man.parse_cli(self._profiler_types)

        # Detect the profiler type
        profiler_decorator_name = self.detect_prof_type(args)

        self._io_man.print_msg_with_header('', '--------------------')
        self._io_man.print_msg_with_header('', 'Starting the decorator injector...')

        # Create a temporary directory
        self._io_man.create_working_dir(args.p)

        # Make a working copy of the scripts we are going to work with
        self._io_man.make_working_copy_of_project(args.p)

        # Run call tree generator
        call_tree_filename = self.generate_call_tree(args)
        # call_tree = self.read_call_tree(call_tree_filename)

        # Run AST
        working_copy_filename = os.path.join(self._io_man.get_working_dir_name(), args.f)
        self._io_man.print_dbg_info("Working copy filename: " + working_copy_filename)
        src_tree = self.parse_src_file(working_copy_filename)

        # Inject decorator into the source code
        self.inject_decorator(src_tree, args.n, profiler_decorator_name)

        # Inject "import" statement into the source code
        self.inject_import(src_tree, self._profiler_module_name, self._profiler_class_name)

        self._io_man.print_dbg_info('Modified code:')
        self._io_man.print_dbg_info(astunparse.unparse(src_tree))

        # Write modified tree back into the file
        self.dump_decorated_src(src_tree, working_copy_filename)

        self._io_man.print_msg_with_header('', '--------------------')
        self._io_man.print_msg_with_header('', 'Finished...')
        self._io_man.print_msg_with_header('', 'See %s for the modified copy of the original code'
                                           % working_copy_filename)
