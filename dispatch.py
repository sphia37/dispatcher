import inspect
import functools
from typing import Any

def get_arg_index(arg_name: str, func):
    return list(func.__code__.co_varnames).index(arg_name)

def get_arg_value(arg_name: str, args, kwargs, func):
    arg_value = kwargs.get(arg_name, None)
    
    return args[get_arg_index(arg_name, func)] if arg_value is None else arg_value

def is_compatible(arg_type, param_type):
    return param_type is Any or issubclass(arg_type, param_type)

def overloads_match(args, overload):
    return all(is_compatible(type(arg), param) for arg, param in zip(args, overload))

def find_best_overload(overloads, args):
    matching_overloads = {}
    for overload in overloads:
        if overloads_match(args, overload):
            i = sum(1 for param in overload if param is not Any)
            if i not in matching_overloads:
                matching_overloads[i] = []
            matching_overloads[i].append(overload)
    
    max_idx = max(matching_overloads.keys())
    
    if len(matching_overloads[max_idx]) > 1:
        raise ValueError("Ambiguous overload")

    return matching_overloads[max_idx][0]

class Dispatch:
    args: list[int | str]

    def update(self):
        self.types = [[
                Any
                if y == inspect._empty
                else y
                    for y in [(x[arg].annotation if isinstance(arg, str) else list(x.values())[arg].annotation) 
                        for x in [inspect.signature(vis).parameters for vis in self.overloads]]]
                            for arg in self.args]
        self.__signature__ = self.get_signature()
    def __init__(self, func, *args: int | str):
        self.func = func
        self.overloads = []
        self.overloads.append(self.func)
        self.args = list(args)
        self.update()
    def get_signature(self): 
        index_to_types = {
            i: functools.reduce(lambda x, y: x | y, types) for i, types in 
                zip({get_arg_index(arg, self.func) if not isinstance(arg, int) else arg for arg in self.args},
                    self.types)}
        return inspect.signature(self.func).replace(
            parameters=[
                param.replace(annotation=index_to_types[i]) 
                if i in index_to_types else param 
                for i, param in enumerate(inspect.signature(self.func).parameters.values())
            ])
    def __call__(self, *args, **kwargs):
        cargs = [args[arg] if isinstance(arg, int) else get_arg_value(arg, args, kwargs, self.func) for arg in self.args]
        types = [list(item) for item in zip(*self.types)]
        overload = find_best_overload( types
                                      ,cargs)
        return self.overloads[types.index(overload)](*args, **kwargs)
    def register(self, func):
        self.overloads.append(func)
        self.update()
        return func



def dispatch(*value):
    if isinstance(value[0], int | str):
        def _(func):
            data = Dispatch(func, *value);
            response = functools.wraps(func)(data)
            return response
        return _
    return dispatch(0)(value)
