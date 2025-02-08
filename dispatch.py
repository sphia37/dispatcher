import inspect
import functools
from typing import Any

def get_arg_index(arg_name: str, func):
    return list(func.__code__.co_varnames).index(arg_name)

def get_arg_value(arg_name: str, args, kwargs, func):
    arg_value = kwargs.get(arg_name, None)
    
    return args[get_arg_index(arg_name, func)] if arg_value is None else arg_value

class Dispatch:
    arg: int | str
    def get_overloads(self) -> list:
        return self.dispatchs[self.func.__name__]
    def __init__(self, func, arg: int | str, dispatchs = {}):
        self.dispatchs = dispatchs
        self.func = func
        if func.__name__ not in dispatchs:
            dispatchs[func.__name__] = []
        dispatchs[func.__name__].append(self)
        self.overloads = self.get_overloads()
        self.arg = self.overloads[-2].arg if len(self.overloads) > 1 else arg
        self.types = [Any if x == inspect._empty else x for x in [(x[self.arg].annotation if isinstance(self.arg, str) else list(x.values())[self.arg].annotation) 
                for x in 
                [inspect.signature(vis.func).parameters for vis in self.overloads]]]
    def get_signature(self): 
        return inspect.signature(self.func).replace(parameters=
                                 [(x.replace(annotation=functools.reduce(lambda x, y: x | y, self.types)) 
                                            if i == (self.arg if isinstance(self.arg, int) else get_arg_index(self.arg, self.func)) else x)
                                    for i, x in
                                    enumerate(inspect.signature(self.func).parameters.values())])
    def __call__(self, *args, **kwargs):
        t = type(args[self.arg] if isinstance(self.arg, int) else get_arg_value(self.arg, args, kwargs, self.func))
        f = lambda x: self.overloads[self.types.index(x)].func(*args, **kwargs)
        if t in self.types:
            return f(t)
        elif Any in self.types:
            return f(Any)
        else:
            raise ValueError(f"Invalid type for overloaded function {self.func.__name__}")


def dispatch(value):
    if isinstance(value, int | str):
        def _(func):
            data = Dispatch(func, value);
            response = functools.wraps(func)(data)
            response.__signature__ = data.get_signature()
            return response
        return _
    return dispatch(0)(value)
