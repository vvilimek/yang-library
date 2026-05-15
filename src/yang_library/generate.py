# SPDX-FileCopyrightText: CZ.NIC z.s.p.o.
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import json
import cbor2
from typing import NamedTuple
from collections import OrderedDict

from yang_sid_base import RelativeSID

from . import library
from . import constrained

from .constant import *

class GenerateLibrary:
    pass

class GenerateConstrainedLibrary:
    @classmethod
    def to_cbor(cls, lib: constrained.YangLibrary, add_namespace: bool = False, location_filter = lambda x: None) -> bytes:
        mod_set = cls._mod_set(lib.module_set, add_namespace, location_filter)
        schema = cls._schema(lib.schema)
        datastore = cls._datastore(lib.datastore)

        cyl = CONSTRAINED_YANG_LIBRARY
        yang_lib = OrderedDict()
        if len(mod_set) > 0:
            yang_lib[MODULE_SET - cyl] = mod_set
        if len(schema) > 0:
            yang_lib[SCHEMA - cyl] = schema
        if len(datastore):
            yang_lib[DATASTORE - cyl] = datastore
        yang_lib[CHECKSUM - cyl] = lib.checksum
        return cbor2.dumps(
                {
                    CONSTRAINED_YANG_LIBRARY: yang_lib,
                })


    @classmethod
    def _mod_set(cls, mod_set: OrderedDict[int, constrained.ModuleSet], add_namespace: bool, location_filter):
        data = []
        index = MODULE_SET_INDEX - MODULE_SET
        module =  MODULE - MODULE_SET
        import_only_module = IMPORT_ONLY_MODULE - MODULE_SET
        for mset in mod_set.values():
            ms = OrderedDict()
            ms[index] = mset.index
            if len(mset.module) > 0:
                ms[module] = cls._mods(mset.module, add_namespace, location_filter)
            if len(mset.import_only_module) > 0:
                ms[import_only_module] = cls._import_mods(mset.import_only_module, add_namespace, location_filter)
            data.append(ms)
        return data

    @classmethod
    def _mods(cls, mods: OrderedDict[SID, constrained.ImplementModule], add_namespace: bool, location_filter):
        data = []
        identifier = MOD_IDENTIFIER - MODULE
        revision = MOD_REVISION - MODULE
        namespace = MOD_NAMESPACE - MODULE
        location = MOD_LOCATION - MODULE
        submodule = MOD_SUBMODULE - MODULE
        feature = MOD_FEATURE - MODULE
        deviation = MOD_DEVIATION - MODULE
        for m in mods.values():
            one = OrderedDict()
            one[identifier] = m.identifier
            if m.revision:
                one[revision] = m.revision
            if add_namespace:
                one[namespace] = m.namespace
            filtered = location_filter(m.location)
            if filtered is not None and len(filtered) > 0:
                one[location] = filtered
            if len(m.submodule) > 0:
                one[submodule] = cls._mods_submods(m.submodule, location_filter)
            if len(m.feature) > 0:
                one[feature] = m.feature
            if len(m.deviation) > 0:
                one[deviation] = tuple(m.deviation.keys())
            data.append(one)

        return data

    @classmethod
    def _import_mods(cls, io_mods: OrderedDict[SID, constrained.ImportOnlyModule], add_namespace: bool, location_filter):
        data = []
        identifier = IMPORT_IDENTIFIER - IMPORT_ONLY_MODULE
        revision = IMPORT_REVISION - IMPORT_ONLY_MODULE
        namespace = IMPORT_NAMESPACE - IMPORT_ONLY_MODULE
        location = IMPORT_LOCATION - IMPORT_ONLY_MODULE
        submodule = IMPORT_SUBMODULE - IMPORT_ONLY_MODULE
        for m in io_mods.values():
            one = OrderedDict()
            one[identifier] = m.identifier
            if m.revision:
                one[revision] = m.revision
            else:
                one[revision] = str()
            if add_namespace:
                one[namespace] = m.namespace
            filtered = location_filter(m.location)
            if filtered is not None and len(filtered) > 0:
                one[location] = filtered
            if len(m.submodule) > 0:
                one[submodule] = cls._import_mods_submods(m.submodule, location_filter)
            data.append(one)

        return data

    @classmethod
    def _mods_submods(cls, submods: OrderedDict[SID, constrained.Submodule], location_filter):
        data = []
        identifier = SUBMOD_IDENTIFIER - MOD_SUBMODULE
        revision = SUBMOD_REVISION - MOD_SUBMODULE
        location = SUBMOD_LOCATION - MOD_SUBMODULE
        for sm in submods.values():
            one = OrderedDict()
            one[identifier] = sm.identifier
            if sm.revision:
                one[revision] = sm.revision
            filtered = location_filter(sm.location)
            if filtered is not None and len(filtered) > 0:
                one[location] = filtered
            data.append(one)

        return data

    @classmethod
    def _import_mods_submods(cls, submods: OrderedDict[SID, constrained.Submodule], location_filter):
        data = []
        identifier = IMPORT_SUBMOD_IDENTIFIER - IMPORT_SUBMODULE
        revision = IMPORT_SUBMOD_REVISION - IMPORT_SUBMODULE
        location = IMPORT_SUBMOD_LOCATION - IMPORT_SUBMODULE
        for sm in submods.values():
            one = OrderedDict()
            one[identifier] = sm.identifier
            if sm.revision:
                one[revision] = sm.revision
            filtered = location_filter(sm.location)
            if filtered is not None and len(filtered) > 0:
                one[location] = filtered
            data.append(one)

        return data

    @classmethod
    def _schema(cls, schema: OrderedDict[int, constrained.Schema]):
        data = []

        index = SCHEMA_INDEX - SCHEMA
        mod_set = SCHEMA_MOD_SET - SCHEMA
        for sch in schema.values():
            one = OrderedDict()
            one[index] = sch.index
            if len(sch.module_set) > 0:
                one[mod_set] = tuple(sch.module_set.keys())
            data.append(one)
        return data

    @classmethod
    def _datastore(cls, datastore: OrderedDict[SID, constrained.Datastore]):
        data = []
        identifier  = DATASTORE_IDENTIFIER - DATASTORE
        schema = DATASTORE_SCHEMA - DATASTORE
        for ds in datastore.values():
            data.append(OrderedDict((
                    (identifier, ds.identifier),
                    (schema, ds.schema.index),
                )))
        return data

