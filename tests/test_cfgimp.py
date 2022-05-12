import json
import sys

import pytest

from cfgimp import CfgImp
from cfgimp.modules import ArrayModule, TableModule, UnresolvedModule


@pytest.fixture
def package(tmp_path):
    pkg = tmp_path / "pkg"
    pkg.mkdir()

    open(pkg / "__init__.py", "w", encoding="utf-8").close()

    pkg.resolve()

    cfg = CfgImp("pkg")
    cfg.install()
    sys.path.append(str(tmp_path))
    yield pkg

    cfg.uninstall()
    sys.path.remove(str(tmp_path))
    for module in [name for name in sys.modules.keys() if name.startswith("pkg")]:
        sys.modules.pop(module)


def test_json_import(package):
    test_data = {
        "bool": False,
        "string": "string",
        "number": 12.34,
        "object": {"inner": 0},
        "array": [9, 8, 7],
        "null": None,
    }
    with open(package / "data.json", "w", encoding="utf-8") as json_file:
        json.dump(test_data, json_file)

    import pkg.data

    assert pkg.data.__package__ == "pkg"
    assert pkg.data.__name__ == "pkg.data.json"
    assert test_data == dict(pkg.data)
    assert pkg.data == pkg.data.json


def test_unresolved(package):
    with open(package / "data.json", "w", encoding="utf-8") as json_file:
        json_file.write('{"a": 1}')
    with open(package / "data.csv", "w", encoding="utf-8") as csv_file:
        csv_file.write("a,b")

    import pkg.data

    assert isinstance(pkg.data, UnresolvedModule)

    import pkg.data.json

    assert isinstance(pkg.data.json, TableModule)
    assert dict(pkg.data.json) == {"a": 1}

    import pkg.data.csv

    assert isinstance(pkg.data.csv, ArrayModule)
    assert list(pkg.data.csv) == [["a", "b"]]
