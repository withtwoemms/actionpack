<img src="https://user-images.githubusercontent.com/7152453/158044431-7a6515f1-3eef-4d8e-a549-69453d61088a.png" align="left" width="450" />

<!-- # actionpack -->
[![tests](https://github.com/withtwoemms/actionpack/workflows/tests/badge.svg)](https://github.com/withtwoemms/actionpack/actions?query=workflow%3Atests) [![codecov](https://codecov.io/gh/withtwoemms/actionpack/branch/main/graph/badge.svg?token=27Z4W0COFH)](https://codecov.io/gh/withtwoemms/actionpack) [![publish](https://github.com/withtwoemms/actionpack/workflows/publish/badge.svg)](https://github.com/withtwoemms/actionpack/actions?query=workflow%3Apublish) [![PyPI version](https://badge.fury.io/py/actionpack.svg)](https://badge.fury.io/py/actionpack)

> a lib for describing Actions and how they should be performed

# Overview

Side effects are annoying.
Verification of intended outcome is often difficult and can depend on the system's state at runtime.
Questions like _"Is the file going to be present when data is written?"_ or _"Will that service be available?"_ come to mind.
Keeping track of external system state is just impractical, but declaring intent and encapsulating its disposition is doable.

# Usage

### _What are Actions for?_

`Action` objects are used to declare intent:

```python
>>> action = Read('path/to/some/file')
```

The `action`, above, represents the intent to `Read` the contents from the file at some path.
An `Action` can be "performed" and the result is captured by a `Result` object:

```python
>>> result = action.perform()  # produces a Result object
```

The `result` holds disposition information about the outcome of the `action`.
That includes information like _whether or not it was `.successful`_ or that it was _`.produced_at` some unix timestamp_ (microseconds by default).
To gain access to the value of the `result`, check the `.value` attribute.
If unsuccessful, there will be an `Exception`, otherwise there will be an instance of some non-`Exception` type.

### _Can Actions be connected?_

A `Result` can be produced by performing an `Action` and that value can be percolated through a collection of `ActionTypes` using the `Pipeline` abstraction:

```python
>>> pipeline = Pipeline(ReadInput('Which file? '), Read)
```

The above, is not the most helpful incantation, but toss the following in a `while` loop and witness some REPL-like behavior (bonus points for feeding it _actual_ filenames/filepaths).

```python
result = Pipeline(ReadInput('Which file? '), Read).perform()
print(result.value)
```

Sometimes `ActionType`s in a `Pipeline` don't "fit" together.
That's where the `Pipeline.Fitting` comes in:

```python
listen = ReadInput('What should I record? ')
record = Pipeline.Fitting(
    action=Write,
    **{
        'prefix': f'[{datetime.now()}] ',
        'append': True,
        'filename': filename,
        'to_write': Pipeline.Receiver
    },
)
Pipeline(listen, record).perform()
```

> ⚠️ **_NOTE:_**  Writing to stdout is also possible using the `Write.STDOUT` object as a filename. How that works is an exercise left for the user.

### _Handling multiple Actions at a time_

An `Action` collection can be used to describe a procedure:

```python
actions = [action,
           Read('path/to/some/other/file'),
           ReadInput('>>> how goes? <<<\n  > '),
           MakeRequest('GET', 'http://google.com'),
           RetryPolicy(MakeRequest('GET', 'http://bad-connectivity.com'),
                       max_retries=2,
                       delay_between_attempts=2)
           Write('path/to/yet/another/file', 'sup')]

procedure = Procedure(actions)
```

And a `Procedure` can be executed synchronously or otherwise:

```python
results = procedure.execute()  # synchronously by default
_results = procedure.execute(synchronously=False)  # async; not thread safe
result = next(results)
print(result.value)
```

A `KeyedProcedure` is just a `Procedure` comprised of named `Action`s.
The `Action` names are used as keys for convenient result lookup.

```python
prompt = '>>> sure, I'll save it for ya.. <<<\n  > '
saveme = ReadInput(prompt).set(name='saveme')
writeme = Write('path/to/yet/another/file', 'sup').set(name='writeme')
actions = [saveme, writeme]
keyed_procedure = KeyedProcedure(actions)
results = keyed_procedure.execute()
keyed_results = dict(results)
first, second = keyed_results.get('saveme'), keyed_results.get('writeme')
```

> ⚠️ **_NOTE:_**  `Procedure` elements are evaluated _independently_ unlike with a `Pipeline` in which the result of performing an `Action` is passed to the next `ActionType`.

### _For the honeybadgers_

One can also create an `Action` from some arbitrary function

```python
>>> Call(closure=Closure(some_function, arg, kwarg=kwarg))
```

# Development

### Setup

Build scripting is managed via [`noxfile`](https://nox.thea.codes/en/stable/config.html).
Execute `nox -l` to see the available commands (set the `USEVENV` environment variable to view virtualenv-oriented commands).
To get started, simply run `nox`.
Doing so will install `actionpack` on your PYTHONPATH.
Using the `USEVENV` environment variable, a virtualenv can be created in the local ".nox/" directory with something like:

```
USEVENV=virtualenv nox -s actionpack-venv-install-3.10
```

All tests can be run with `nox -s test` and a single test can be run with something like the following:

```
TESTNAME=<tests-subdir>.<test-module>.<class-name>.<method-name> nox -s test
```

Coverage reports are optional and can be disabled using the `COVERAGE` environment variable set to a falsy value like "no".

### Homebrewed Actions

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
