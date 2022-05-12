# CfgImp
Oh dear cosmos why the hell are you using this??
Please look at `importlib.resources` instead...

Features include:
 * Not production safe

```py
>>> # pkg
>>> # ├── data.json
>>> # ├── __init__.py
>>> # ├── same.csv
>>> # └── same.json
>>> from cfgimp import CfgImp
>>> CfgImp("pkg").install()
>>> from pkg import data
>>> data
<table module 'pkg.data.json' from 'pkg/data.json'>
>>> data.json
<table module 'pkg.data.json' from 'pkg/data.json'>
>>> dict(data)
{'test': 1}
>>> data['test'] = 0
>>> data == data.json
True
>>> from pkg import same
>>> same
<unresolved module 'pkg.same' (either 'pkg/same.csv' or 'pkg/same.json')>
>>> import pkg.same.csv
>>> pkg.same.csv
<array module 'pkg.same.csv' from 'pkg/same.csv'>
>>> pkg.same.csv[0]
['seq', 'name/first', 'name/last', 'age', 'street', 'city', 'state', 'zip', 'dollar', 'pick', 'date']
>>> # I am certain there are good reasons not to do this.
```
