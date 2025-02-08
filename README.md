# Dispatcher(@singledispatch analogue)
## Examples
```py
@dispatch(1)
def foo(b, a: int):
    print(f"Int: {a}")


@dispatch
def foo(b, a: str):
    print(f"String: {a}")


@dispatch("a")
def bar(b, a: int):
    print(f"Int: {a}")

@dispatch
def bar(b, a: str):
    print(f"String: {a}")

@dispatch
def bar(b, a):
    print(f"Unknown: {a}")

if __name__ == "__main__":
    print(f"Signature: {inspect.signature(foo)}") # Signature: (b, a: int | str)
    foo(0, 42)
    foo(0, "Hello world")
    bar(0, 42)
    bar(0, "Hello world")
    bar(0, 3.1415)
    try:
        foo(0, 3.1415)
    except Exception as e:
        print(f"Error: {e}")

```
