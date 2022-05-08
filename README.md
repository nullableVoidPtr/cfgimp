# CfgImp
Oh dear cosmos why the hell are you using this??
Please look at `importlib.resources` instead...

Features include:
 * Not production safe

```py
>>> # package
>>> # |-- __init__.py
>>> # |-- data.json
>>> # |-- same.csv
>>> # +-- same.json
>>> from cfgimp import CfgImp
>>> CfgImp.install(CfgImp("package"))
>>> from package import data
>>> import package.same.csv
>>> import package.same.json
>>> data
<module 'package.data' from 'package/data.json'>
>>> data['test']
1
>>> dict(data)
{'test': 1}
>>> package.same.csv
<module 'package.same.csv' from 'package/same.csv'>
>>> package.same.csv[0]
['seq', 'name/first', 'name/last', 'age', 'street', 'city', 'state', 'zip', 'dollar', 'pick', 'date']
```
