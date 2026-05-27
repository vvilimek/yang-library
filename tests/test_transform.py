# SPDX-FileCopyrightText: CZ.NIC z.s.p.o.
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import pytest
import json

from typing import Any

from yang_sid_base import SID

import yang_sid
import yang_sid.schemadata
from yang_sid.schemadata import ModuleData
from yang_sid.sid_file import SidRepository, SidFile, SidFileStatus, ItemNamespace, ItemAssignment

import yang_library.constrained as constrained
import yang_library.library as library

from yang_library.translator import Translator
from yang_library.datastore import DatastoreType, UnifiedDatastore

class SchemaDataMock(yang_sid.schemadata.SchemaData):
    def __init__(self) -> None:
        super().__init__(dict(), tuple())

    def _from_yang_library(self, yang_lib: dict) -> None:
        pass

class SchemaDataMockFactory:
    def create_schema_data(self, yang_lib: dict[str, Any], mod_path: list[str]) -> "SchemaDataMock":
        return SchemaDataMock()

YANGSON_YLIB = json.dumps({
    "ietf-yang-library:modules-state": {
        "module": [],
        "module-set-id": "0",
        }
    })

def item(ns: ItemNamespace, id: str, sid: SID) -> ItemAssignment:
    return ItemAssignment(namespace=ns, identifier=id, sid=sid)

MODULE = ItemNamespace.MODULE

def test_simple():
    mod_a = library.ImplementModule("mod-a", revision=None, namespace="http://example.com/a")
    import_mod_c = library.ImportOnlyModule("import-mod-c", revision=None, namespace="http://example.com/c")

    mod_set = library.ModuleSet("oper-mod-set", module=[mod_a], import_only_module=[import_mod_c])
    schema = library.Schema("oper-schema", [mod_set])
    datastore = library.Datastore(DatastoreType.get(("operational", "ietf-datastores")), schema)

    lib = library.YangLibrary(module_set=[mod_set],
                                  schema=[schema],
                                  datastore=[datastore],
                                  content_id="0")

    model = yang_sid.DataModel(YANGSON_YLIB, mod_path=tuple(), data_factory=SchemaDataMockFactory())
    mod_a_sid_file = SidFile("mod-a", revision=None,
                             version=0, status=SidFileStatus.PUBLISHED,
                             item={1200: item(MODULE, "mod-a", SID(1200))},
                             # Not used
                             assignment_range=[], dependency_revision=[])
    y_mod_a = yang_sid.schemadata.ModuleData(("mod-a", ""), ("mod-a", ""))
    model.schema_data.modules[y_mod_a.main_module] = y_mod_a
    model.schema_data.modules_by_name["mod-a"] = y_mod_a
    model.schema_data.implement["mod-a"] = ""
    model.schema_data.apply_sid_file(mod_a_sid_file)
    import_mod_c_sid_file = SidFile("import-mod-c", revision=None,
                                    version=0, status=SidFileStatus.PUBLISHED,
                                    item={1300: item(MODULE, "import-mod-c", SID(1300))},
                                    assignment_range=[], dependency_revision={})
    y_import_mod_c = yang_sid.schemadata.ModuleData(("import-mod-c", ""), ("import-mod-c", ""))
    model.schema_data.modules[y_import_mod_c.main_module] = y_import_mod_c
    model.schema_data.modules_by_name["import-mod-c"] = y_import_mod_c
    model.schema_data.implement["import-mod-c"] = ""
    model.schema_data.apply_sid_file(import_mod_c_sid_file)
    const = Translator.create_constrained_library(lib, model)
    assert len(const.module_set) == 1
    c_mod_a = constrained.ImplementModule(identifier=SID(1200), revision=None)
    c_import_mod_c = constrained.ImportOnlyModule(identifier=SID(1300), revision=None)
    assert const.module_set[0] == constrained.ModuleSet(index=0,
                                                        module=[c_mod_a],
                                                        import_only_module=[c_import_mod_c])
    assert len(const.schema) == 1
    assert const.schema[0] == constrained.Schema(index=0,
                                                 module_set=[const.module_set[0]])
    assert len(const.datastore) == 1
    operational_ds = DatastoreType.get(("operational", "ietf-datastores"))
    assert const.datastore[operational_ds] == constrained.Datastore(
            datastore=operational_ds,
            schema=const.schema[0])

    assert const.checksum == b"0"
      
@pytest.mark.skip(reason="TODO, not done")
def test_rev():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_namespace():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_submodule():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_location():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_feature():
    pass

@pytest.mark.skip(reason="Not MVP feature")
def test_deviation():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_multi_ds():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_multi_schema_set():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_mod_set_no_import():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_mod_set_no_impl():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_no_ds():
    pass

@pytest.mark.skip(reason="TODO, not done")
def test_no_schema():
    pass

def test_no_mod_set():
    lib = library.YangLibrary(module_set=[], schema=[], datastore=[], content_id="0123")
    model = yang_sid.DataModel(YANGSON_YLIB, mod_path=tuple(), data_factory=SchemaDataMockFactory())
    con_lib = Translator.create_constrained_library(lib, model)
    assert len(con_lib.module_set) == 0
    assert len(con_lib.schema) == 0
    assert len(con_lib.datastore) == 0
    assert con_lib.checksum == b"0123"

@pytest.mark.skip(reason="need fs interactions, too much work (for now)")
def test_full():
    pass
