# HowTo
## Installation
### Using `requirements.txt`
Use the list of packages from `requirements.txt` to prepare your environment:
```bash
pip install -r requirements.txt
```
After this, add the path to the `decoProf` folder to the `PYTHONPATH` environment variable.

### Using `setup.py`
Call for:
```bash
$ pip3 install .
```
This will install `decoProf` as a binary and as a site package along with other 
`site-packages` on your system.

## Print help
If you didn't install the package using `setup.py`, then call for the `decoProf.py` 
script from the `decoProf` folder without any arguments to print the help message:
```bash
$ python3 decoProf.py
```
If you installed the package using `setup.py`, then simply call for:
```bash
$ decoProf
```

## Inject profiler decorators
The code injects decorators in front of the functions that should be profiled.
Therefore, the user should specify the function name, the filename where the function 
is defined, and the name of the project to which the file belongs to. If the function 
of interest is a member function of a class or a nested function, then the user should
prepend the class or the upper function names to the function name using '.' (dot) as
a separator character, e.g. `-n <class_name>.<function.name>`. 

Here is an example call:
1. If `decoProf` is not installed using `setup.py`:
```bash
$ python3 decoProf.py -f factorial.py -p examples -n taylor_exp -t cpu
```
2. If `decoProf` is installed using `setup.py`:
```bash
$ decoProf -f factorial.py -p examples -n taylor_exp -t cpu
```

Execution of the lines above will perform the following steps:
1. create a working copy of the package `example`
2. add a decorator that corresponds to the `cpu` profiler to the `taylor_exp`
function in the `factorial.py` file

After the call, go to the directory with a working copy and execute your scripts 
as usual:
1. If `decoProf` is not installed using `setup.py` (Don't forget to modify `PYTHONPATH` 
to let `python` know that the directory with `decoProf` exists):
```bash
$ PYTHONPATH="<path_to_decoProf_folder>:$PYTHONPATH" python3 factorial.py
```
2. If `decoProf` is installed using `setup.py`:
```bash
$ python3 factorial.py
```

Note that the working copy has a unique name based on the time stamp and is not deleted after 
execution of `decoPrfo`.

## Profilers
At the moment, only five profilers are available. The types and the corresponding `-t` options are 
listed in the table below:

| Profiler         |     -t     |                             Notes                             |
|------------------|:----------:|:-------------------------------------------------------------:|
| cProfile         |    cpu     |       Default CPU profiler, a bit slow (deterministic)        |
| pyinstrument     | call_stack |     Report the call stack and elapsed times (statistical)     |
| yappi            |   thread   | Allows to profile multi-threaded applications (deterministic) |
| memory_profiler  |    mem     |            Monitors memory consumption of a process           |
| line_profiler    |    line    |   Profile the time individual lines of code take to execute   |


### What are "deterministic" and "statistical" profilers?

#### Deterministic
Deterministic profilers work by hooking into several function call/leave events and calculate all metrics according to these. 

#### Statistical
Statistical profilers do not track every function call the program makes but they record the call stack every 1ms or whatever defined in the interval. The statistical profilers can impose less overhead compared to the deterministic ones.
