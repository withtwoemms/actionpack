# actionpack

> a lib for describing Actions and how they should be performed

[![tests](https://github.com/withtwoemms/actionpack/workflows/tests/badge.svg)](https://github.com/withtwoemms/actionpack/actions?query=workflow%3Atests)
[![publish](https://github.com/withtwoemms/actionpack/workflows/publish/badge.svg)](https://github.com/withtwoemms/actionpack/actions?query=workflow%3Apublish)

# Overview

Side effects are annoying.
Verification of intended outcome is often difficult and can depend on the system's state at runtime.
Questions like _"Is the file going to be present when data is written?"_ or _"Will that service be available?"_ come to mind.
Keeping track of external system state is just impractical, but declaring intent and encapsulating its disposition is doable.

# Usage

```python
>>> action = ReadBytes('path/to/some/file')
...
>>> actions = [action,
...            ReadBytes('path/to/some/other/file'),
...            ReadInput('>>> how goes? <<<\n  > '),
...            MakeRequest('GET', 'http://google.com'),
...            RetryPolicy(MakeRequest('GET', 'http://bad-connectivity.com'),
...                        max_retries=2,
...                        delay_between_attempts=2)
...            WriteBytes('path/to/yet/another/file', b'sup')]
...
>>> procedure = Procedure(*actions, sync=False)
>>> procedure.execute()
```

