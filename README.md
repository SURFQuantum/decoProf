# HowTo
## Install 3rd-party packages
```python
pip install -r requirements.txt
```

## Inject profiler decorators
Example:
```python
python3 main.py -f factorial.py -p examples -n taylor_exp -t cpu
```
This call will perform the following steps:
1. create a working copy of the package `example`
2. add a decorator that corresponds to the `cpu` profiler to function 
`taylor_exp` in file `factorial.py` 

After the call, go to the directory with a working copy and execute your scripts 
as usual.  

Note that the working copy has a unique based name based on the time stamp and 
is not deleted after the call.