import cProfile
import pyinstrument
import yappi
import line_profiler
import memory_profiler


class ProfileDecorators:
    def __init__(self):
        pass

    def cprofile_decorator(function):
        def profiler_wrapper(*args, **kwargs):
            print("Start profiling (CProfile)")
            pr = cProfile.Profile()
            pr.enable()
            function(*args, **kwargs)
            pr.disable()
            pr.print_stats()
            print("End profiling  (CProfile)")

        return profiler_wrapper

    def pyinstrument_decorator(function):
        def profiler_wrapper(*args,**kwargs):
            print("Start profiling (pyinstrument)")
            pr = pyinstrument.Profiler()
            pr.start()
            function(*args, **kwargs)
            pr.stop()
            pr.print()
            print("End profiling  (pyinstrument)")

        return profiler_wrapper

    # TODO: Add clock type as a parameter
    def yappi_decorator(function):
        def profiler_wrapper(*args, **kwargs):
            print("Start profiling (yappi)")
            yappi.set_clock_type("cpu")
            yappi.start()
            function(*args, **kwargs)
            yappi.get_func_stats().print_all()
            yappi.get_thread_stats().print_all()
            print("End profiling  (yappi)")

        return profiler_wrapper

    def line_profiler_decorator(function):
        def profiler_wrapper(*args, **kwargs):
            print("Start profiling (line_profiler)")
            lp = line_profiler.LineProfiler()
            lp_wrapper = lp(function)
            lp_wrapper(*args, **kwargs)
            lp.print_stats()
            print("End profiling  (line_profiler)")

        return profiler_wrapper

    def memory_profiler_decorator(function):
        def profiler_wrapper(*args, **kwargs):
            print("Start profiling (memory_profiler)")
            lp = memory_profiler.profile()
            lp_wrapper = lp(function)
            lp_wrapper(*args, **kwargs)
            print("End profiling  (memory_profiler)")

        return profiler_wrapper
