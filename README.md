# HowTo
## Install 3rd-party packages
Use the list of packages from `requirements.txt` to prepare your environment:
```python
pip install -r requirements.txt
```

## Print help
to priont help message just call for the main script without any arguments:
```python
python3 main.py
```

## Inject profiler decorators
The code injects decorators in front of the functions that should be profiled.
Therefore, the user should specify the function (and class) name, the file that
defines the function, and the name of the project to which the file belongs to.
Here is an example call:
```python
python3 main.py -f factorial.py -p examples -n taylor_exp -t cpu
```
This call will perform the following steps:
1. create a working copy of the package `example`
2. add a decorator that corresponds to the `cpu` profiler to function 
`taylor_exp` in file `factorial.py` 

After the call, go to the directory with a working copy and execute your scripts 
as usual. Don't forget to change the `PYTHONPATH`, so that python will be aware of
existence of the working directory:
```python
PYTHONPATH="${PWD}/..:$PYTHONPATH" python3 factorial.py
```

If the function of interest is a member function of a class, then the class name 
should be prependet to the function name and separated by dot as follows: `className.functionName` 

Note that the working copy has a unique based name based on the time stamp and 
is not deleted after the call.

## Profilers
At the moment, only four profilers are available. The types and the corresponding `-t` options are 
listed in the table below:

| Profiler         |     -t     |                     Notes                                     |
|------------------|:----------:|:-------------------------------------------------------------:|
| cProfile         |    cpu     |       Default CPU profiler, a bit slow (deterministic)        |
| pyinstrument     | call_stack |    Report the call stack and elapsed times (statistical)      |
| yappi            |   thread   | Allows to profile multi-threaded applications (deterministic) |
| memory_profiler  |    mem     |                Memory profiler                                |

### What are "deterministic" and "statistical" profilers?
#### Deterministic
Deterministic profilers work by hooking into several function call/leave events and calculate all metrics according to these. 
#### Statistical
Statistical profilers do not track every function call the program makes but they record the call stack every 1ms or whatever defined in the interval. The statistical profilers can impose less overhead compared to the deterministic ones.
