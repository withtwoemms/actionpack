# actionpack

> a lib for describing Actions and how they should be performed

[![tests](https://github.com/withtwoemms/actionpack/workflows/tests/badge.svg)](https://github.com/withtwoemms/actionpack/actions?query=workflow%3Atests)
[![codecov](https://codecov.io/gh/withtwoemms/actionpack/branch/main/graph/badge.svg?token=27Z4W0COFH)](https://codecov.io/gh/withtwoemms/actionpack)
[![publish](https://github.com/withtwoemms/actionpack/workflows/publish/badge.svg)](https://github.com/withtwoemms/actionpack/actions?query=workflow%3Apublish)

# Overview

Side effects are annoying.
Verification of intended outcome is often difficult and can depend on the system's state at runtime.
Questions like _"Is the file going to be present when data is written?"_ or _"Will that service be available?"_ come to mind.
Keeping track of external system state is just impractical, but declaring intent and encapsulating its disposition is doable.

# Usage

Intent can be declared using `Action` objects:

```python
>>> action = ReadBytes('path/to/some/file')
```

An `Action` collection can be used to describe a procedure:

```python
>>> actions = [action,
...            ReadBytes('path/to/some/other/file'),
...            ReadInput('>>> how goes? <<<\n  > '),
...            MakeRequest('GET', 'http://google.com'),
...            RetryPolicy(MakeRequest('GET', 'http://bad-connectivity.com'),
...                        max_retries=2,
...                        delay_between_attempts=2)
...            WriteBytes('path/to/yet/another/file', b'sup')]
...
>>> procedure = Procedure(*actions)
```

And a `Procedure` can be executed synchronously or otherwise:

```python
>>> results = procedure.execute()  # synchronously by default
>>> _results = procedure.execute(synchronously=False)  # async; not thread safe
>>> result = next(results)
>>> print(result.value)
```

A `KeyedProcedure` is just a `Procedure` comprised of named `Action`s.
The `Action` names are used as keys for convenient result lookup.

```python
>>> prompt = '>>> sure, I'll save it for ya.. <<<\n  > '
>>> saveme = ReadInput(prompt).set(name='saveme')
>>> writeme = WriteBytes('path/to/yet/another/file', b'sup').set(name='writeme')
>>> actions = [saveme, writeme]
>>> keyed_procedure = KeyedProcedure(*actions)
>>> results = keyed_procedure.execute()
>>> keyed_results = dict(results)
>>> first, second = keyed_results.get('saveme'), keyed_results.get('writeme')
```

One can also create an `Action` from some arbitrary function

```python
>>> Call(closure=Closure(some_function, arg, kwarg=kwarg))
```

# Development

Build scripting is managed via [`Makefile`](https://www.gnu.org/software/make/manual/html_node/Introduction.html).
Execute `make commands` to see the available commands.
To get started, simply run `make`.
Doing so will create a virtualenv loaded with the relevant dependencies.
All tests can be run with `make tests` and a single test can be run with something like the following:

```
make test TESTCASE=<tests-subdir>.<test-module>.<class-name>.<method-name>
```

Making new `actionpack.actions` is straightforward.
After defining a class that inherits `Action`, ensure it has an `.instruction` method.
If any attribute validation is desired, a `.validate` method can be added.

There is no need to add `Action` dependencies to `setup.py`.
Dependencies required for developing an `Action` go in :::drum roll::: `requirements.txt`.
When declaring your `Action` class, a `requires` parameter can be passed a tuple.

```python
class MakeRequest(Action, requires=('requests',)):
    ...
```

This will check if the dependencies are installed and, if so, will register each of them as class attributes.

```python
mr = MakeRequest('GET', 'http://localhost')
mr.requests  #=> <module 'requests' from '~/actionpack/actionpack-venv/lib/python3/site-packages/requests/__init__.py'>
```

