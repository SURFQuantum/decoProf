from decoProf.io_manager import IOManager
from decoProf.core import Core

def main():
    """
    User should specify a function name including the class name the function belongs 
    to, e.g.:
        class Vector:
            def __init__():
                ...
            def add():
                ...
    User input: -f vector.py -n Vector.add 
    """
    io_man = IOManager()
    core = Core()

    io_man.print_msg_with_header('', '')
    core.run()


if __name__ == '__main__':
    main()


# TODO:
# - test code on more complex examples
# - Redirect the DBG messages to files
#
# - add profiler:
# 	https://pypi.org/project/scalene/
# 	https://github.com/plasma-umass/scalene
