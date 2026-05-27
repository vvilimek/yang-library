# SPDX-FileCopyrightText: CZ.NIC z.s.p.o.
#
# SPDX-License-Identifier: LGPL-3.0-or-later

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING

from . import library
from . import constrained
from .datastore import DatastoreType

if TYPE_CHECKING:
    import yang_sid

class Translator:
    @classmethod
    def create_constrained_library(cls, library: library.YangLibrary, model: yang_sid.DataModel, checksum = lambda lib: bytes(lib.content_id, encoding="utf8")) -> constrained.YangLibrary:
        # TODO add namespace lambda, location lambda filtering
        schema_data = model.schema_data
        c_mod_set = OrderedDict()
        translator = {}
        for (i, mod_set) in enumerate(library.module_set.values()):
            cms = cls._create_c_mod_set(mod_set, i, schema_data)
            c_mod_set[i] = cms
            translator[mod_set] = cms

        translator2 = {}
        c_sch = OrderedDict()
        for (j, schema) in enumerate(library.schema.values()):
            cs = constrained.Schema(index=j, module_set=(translator[mod_set] for mod_set in schema.module_set.values()))
            c_sch[j] = cs
            translator2[schema] = cs

        c_ds = OrderedDict()
        for datastore in library.datastore.values():
            ds_sid = DatastoreType.get(datastore.qual_name)
            if not ds_sid:
                raise ValueError(f"Unknown SID for datastore identity {datastore.qual_name}")
            c_ds[ds_sid] = constrained.Datastore(datastore.datastore, translator2[datastore.schema])

        c_yl = constrained.YangLibrary(module_set=c_mod_set, schema=c_sch,
                                       datastore=c_ds,
                                       checksum=checksum(library))
        cls.bind_libraries(c_yl, library, model, no_check=True)
        return c_yl

    @classmethod
    def create_library(cls, constrained: constrained.YangLibrary, model: yang_sid.DataModel) -> library.YangLibrary:
        pass

    @classmethod
    def bind_libraries(cls, constrained: constrained.YangLibrary, library: library.YangLibrary, model: yang_sid.DataModel, no_check: bool = False) -> None:
        library.__constrained_library = constrained
        constrained.__library = library

    @classmethod
    def _create_c_mod_set(cls, mod_set: library.ModuleSet, i: int, data: yang_sid.schemadata.SchemaData) -> constrained.ModuleSet:
        c_m = OrderedDict()
        for mod in mod_set.module.values():
            m = ImplementModuleTransformer.to_constrained(mod, data, c_m)
            c_m[m.identifier] = m

        c_io_m = OrderedDict()
        for impo_mod in mod_set.import_only_module.values():
            iom = ImportOnlyModuleTransformer.to_constrained(impo_mod, data)
            c_io_m[(iom.identifier, iom.revision)] = iom

        return constrained.ModuleSet(index=i, module=c_m, import_only_module=c_io_m)

    #@datastore
    @staticmethod
    def _create_mod_set(mod_set: constrained.ModuleSet) -> library.ModuleSet:
        pass

    #@datastore
    @staticmethod
    def _create_schema(schema: constrained.Schema) -> library.Schema:
        pass

    #@datastore
    @staticmethod
    def _create_ds(ds: constrained.Datastore) -> library.Datastore:
        pass

class Transformer:
    @classmethod
    def revision_to_constrained(cls, rev: Optional[str]) -> Optinal[RevisionId]:
        if rev is None:
            return None
        return bytes((
            # Note that ord('0') is 48
            ((ord(rev[0]) - ord('0')) << 4) | ord(rev[1]) - 48,
            ((ord(rev[2]) - 48) << 4) | ord(rev[3]) - 48,
            ord(rev[5]) - 48 << 4 | ord(rev[6]) - 48,
            ord(rev[8]) - 48 << 4 | ord(rev[9]) - 48
            ))

    @classmethod
    def submodule_to_constrained(cls, submods: Iterable[library.Submodule], data: yang_sid.schemadata.SchemaData) -> OrderedDict[SID, constrained.Submodule]:
        result = OrderedDict()
        for sm in submods:
            csm = SubmoduleTransformer.to_constrained(sm, data)
            result[csm.sid] = csm
        return result


class ImportOnlyModuleTransformer:
    @classmethod
    def to_constrained(cls, module: library.ImportOnlyModule, data: yang_sid.schemadata.SchemaData) -> constrained.ImportOnlyModule:
        sid = data.modules[(module.name, module.revision if module.revision else "")].sid
        assert sid is not None
        return constrained.ImportOnlyModule(
                identifier=sid,
                revision=Transformer.revision_to_constrained(module.revision),
                # TODO location
                location=tuple(),
                submodule=Transformer.submodule_to_constrained(module.submodule, data),
                )


class ImplementModuleTransformer:
    @classmethod
    def to_constrained(cls, module: library.ImplementModule, data: yang_sid.schemadata.SchemaData, modules: OrderedDict[SID, constrained.ImplementModule]) -> constrained.ImplementModule:
        
        mod = data.modules.get((module.name, module.revision if module.revision else ""))
        if mod is None:
            raise ValueError(f"Missing module data for module \"{module.name}\" revision {module.revision}")

        if mod.sid is None:
            raise ValueError(f"Missing SID for module \"{module.name}\" revision {module.revision}")
        return constrained.ImplementModule(
                identifier=mod.sid,
                revision=Transformer.revision_to_constrained(module.revision),
                # TODO location
                location=tuple(),
                submodule=Transformer.submodule_to_constrained(module.submodule, data),
                feature=tuple(map(lambda n: data.sid_features[n], module.feature)),
                deviation=cls._deviation_to_constrained(module.deviation, data, modules)
                )

    @classmethod
    def _deviation_to_constrained(cls, deviations: OrderedDict[str, library.ImplementModule], data: yang_sid.schemadata.SchemaData, modules: OrderedDict[SID, constrained.ImplementModule]) -> OrderedDict[SID, constrained.ImplementModule]:
        result = OrderedDict()
        for dev in deviations:
            sid = data.modules[(dev.name, dev.revision)]
            # TODO find a correct topological order and use it instead
            assert sid in modules
            result[sid] = modules[sid]

        return result


class SubmoduleTransformer:
    @classmethod
    def to_constrained(cls, submod: library.Submodule, data: yang_sid.schemadata.SchemaData) -> constrained.Submodule:
        sid = data.modules[submod.yang_id].sid
        rev = Transformer.revision_to_constrained(submod.revision)
        # TODO copy location
        return constrained.Submodule(sid, rev, ())

