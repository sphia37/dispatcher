# Simple Multiply Dispatcher
## Examples
```py
@dispatch("a", "b")
def some(a: Any, b: Any):
    return 1
assert(isinstance(some, Dispatch))


@some.register
def _(a: Any, b: int):
    return 2


@some.register
def _(a: int, b: int):
    return 3


if __name__ == "__main__":
    print(inspect.signature(some))
    assert(some("", "") == 1)
    assert(some("", 1) == 2)
    assert(some(1, 1) == 3)
```
