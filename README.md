# yang-library

Python 3 library for hodling representation of YANG Library (as of RFC7895)

[[RFC7895]()]: YANG Module Library

# Installation

### pip
```
pip install git+https://github.com/vvilimek/yang-library
```

### uv
```
uv add git+https://github.com/vvilimek/yang-library
```

### poetry
```
poetry add git+https://github.com/vvilimek/yang-library
```

# Quick start

```python3
from yang_library import *
```

Note that while the package name is `yang-library`, it is not valid python identifier so you must use `yang_library` to import the package in python.
