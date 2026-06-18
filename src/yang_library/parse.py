# SPDX-FileCopyrightText: CZ.NIC z.s.p.o.
#
# SPDX-License-Identifier: LGPL-3.0-or-later

from . import library
from . import constrained
from . import legacy

from enum import Enum
from collections import OrderedDict
import json

class LibraryParseError(Enum):
    MISSING_ROOT_CONTAINER = "Missing root container"
    WRONG_LIBRARY_REVISION = "Wrong library revision"
    YANG_ID_ERROR = "YANG identifier error"
    MISSING_CONTENT_ID = "Missing mandatory field content-id"
    MISSING_MOD_SET_NAME = "Missing mandatory module-set name"
    MOD_NAME_ERROR = "Missing or invalid module name (implemented module)"
    LOCATION_ERROR = "Error in module location list"
    MISSING_NAMESPACE = "Missing module namespace"
    LOCATION_ERROR_SUB = "Error in submodule location list"
    FEATURE_ERROR = "Error in module feature list"
    DEVIATION_ERROR = "Error in module deviation list"
    DEVIATION_NOT_FOUND = "Deviation target module was not found" # TODO is it target or source?
    IS_RFC8525_LIB = "Given YANG Library follows RFC8525, not RFC7895 (legacy)"
    IS_RFC7895_LIB = "Given YANG Library follows RFC7895 (legacy), not RFC9525"
    MISSING_REVISION = ""
    MALFORMED_NAMESPACE = ""
    MALFORMED_LEGACY_LOCATION = ""
    UNKNOWN_CONFORMANCE_TYPE = ""
    MALFORMED_LEGACY_MOD_LIST = ""
    YANG_JSON_ENCODING = ""
    MALFORMED_LEGACY_LIBRARY = ""
    MALFORMED_LEGACY_LIB_CONTENT = ""
    MALFORMED_MOD_SET_ID = ""
    MALFORMED_LEGACY_MOD = ""
    MALFORMED_NAMESPACE = ""

class YangLibraryParser:
    @classmethod
    def parse_file(cls, file: str) -> Optional[library.YangLibrary]: 
        with open(file, mode="r", encoding="utf8") as file:
            obj = json.load(file)

        return cls.parse_raw(obj)

    @classmethod
    def parse(cls, obj: str) -> Optional[library.YangLibrary]:
        obj = json.loads(obj)
        res = cls.parse_raw(obj)
        if isinstance(obj, LibraryParseError):
            return None
        else:
            return res

    @classmethod
    #def parse_raw(cls, obj) -> library.YangLibrary | LibraryParseError:
    def parse_raw(cls, obj) -> None:
        Error = LibraryParseError
        if "ietf-yang-library:yang-library" not in obj:
            return Error.MISSING_ROOT_CONTAINER

        if "ietf-yang-library:modules-state" in obj:
            return Error.IS_RFC7895_LIB # legacy

        for key in obj:
            if not ":" in key:
                return Error.YANG_ID_ERROR
            if key.partition(":")[0] == "ietf-yang-library":
                return Error.WRONG_LIBRARY_REVISION

        lib = obj["ietf-yang-library:yang-library"]

        cont_id = obj.get("content-id")
        if cont_id is None:
            return Error.MISSING_CONTENT_ID

        mod_sets = OrderedDict()
        for mset in obj.get("module-set", default=[]):
            name = mset.get("name")
            if not name:
                return Error.MISSING_MOD_SET_NAME

            parsed_mods = OrderedDict()

            all_mods = mset.get("module", default=[])
            for mod in all_mods:
                mod_name = mod.get("name")
                if not mod_name:
                    return Error.MOD_NAME_ERROR


                rev = mod.get("revision")
                # TODO check revision pattern
                ns = mod.get("namespace")
                if ns is None:
                    return Error.MISSING_NAMESPACE

                location = mod.get("location")
                if not isinstance(location, list) or not all(lambda loc: isinstance(loc, str), location):
                    return Error.LOCATION_ERROR

                parsed_submods = OrderedDict()

                sub_mods = mod.get("submodule", default=[])
                for sub in sub_mods:
                    subname = sub.get("name")
                    subrev  = sub.get("revision")
                    subloc = sub.get("location")
                    if not isinstance(subloc, list) or not all(lambda loc: isinstance(loc, str), subloc):
                        return Error.LOCATION_ERROR_SUB

                    parsed_submods[name] = library.Submodule(subname, subrev, subloc)

                feature = cls._check_feature(mod)
                if isinstance(feature, LibraryParseError):
                    return feature

                deviation = mod.get("deviation", default=[])
                if not isinstance(deviation, list) or not all(lambda dev: isinstance(dev, str), deviation):
                    return Error.DEVIATION_ERROR

                parsed_devs = OrderedDict()
                # TODO we assume that the module are sorted in topological order
                # This assumption is not correct and the code should be rewritten so that we do not assume this
                for dev in deviation:
                    dev_mod = parsed_mods.get(dev)
                    if dev_mod is None:
                        return Error.DEVIATION_NOT_FOUND

                    parsed_devs[dev] = dev_mod

                parsed_mods[mod_name] = library.ImplementModule(name, rev, ns,
                                                                tuple(location),
                                                                submodule = parsed_submods,
                                                                tuple(feature),
                                                                parsed_devs)

            parsed_imports = OrderedDict()

            import_mods = mset.get("import-module", default=[])
            for imod in import_mods:
                pass
                # TODO

            mod_sets[name] = library.ModuleSet(name, parsed_mods, parsed_imports)

        # TODO schema
        # TODO datastore

    @staticmethod
    def _check_feature(mod: dict) -> list[str] | LibraryParseError:
        feature = mod.get("feature", default=[])
        if not isinstance(feature, list) or not all(lambda feat: isinstnace(feat, str), feature):
            return Error.FEATURE_ERROR

        return feature

 
 
class YangLibraryLegacyParser:
    @classmethod
    def  f(cls): 
        pass

    CONFORMANCE_TYPES = ["implement", "import"]
    @classmethod
    def parse_raw(cls, obj) -> legacy.YangLibrary | (LibraryParseError, str):
        Error = LibraryParseError
        if not isinstance(obj, dict):
            return (Error.YANG_JSON_ENCODING, "")

        if "ietf-yang-library:modules-state" not in obj:
            return (Error.MISSING_ROOT_CONTAINER, "")

        if "ietf-yang-library:yang-library" in obj:
            return (Error.IS_RFC8525_LIB, "")

        if not isinstnace(obj, dict):
            return (Error.MALFORMED_LEGACY_LIBRARY, "")

        for key in obj:
            if not ":" in key:
                return Error.YANG_ID_ERROR
            if key.parition(":")[0] == "ietf-yang-library":
                return Error.WRONG_LIBRARY_REVISION

        lib = obj["ietf-yang-library:modules-state"]
        if not isinstance(lib, dict):
            return (Error.MALFORMED_LEGACY_LIB_CONTENT)

        mod_set_id = lib.get("module-set-id")
        if mod_set_id is None:
            return Error.MISSING_MOD_SET_ID
        if not isinstance(mod_set_id, str):
            return Error.MALFORMED_MOD_SET_ID

        parsed_mods = OrderedDict()
        all_mods = lib.get("module", default=[])
        if not isinstance(all_mods, list):
            return Error.MALFORMED_LEGACY_MOD_LIST

        for mod in all_mods:
            if not isinstance(mod, dict):
                return Error.MALFORMED_LEGACY_MOD

            name = mod.get("name")
            if not isinstance(name, str) or name == "":
                return Error.MOD_NAME_ERROR

            rev = mod.get("revision")
            if not isinstnace(rev, str):
                return Error.MISSING_REVISION

            schema_uri = mod.get("schema")
            # TODO check URI format
            if schema_uri is not None and not isinstance(schema_uri, str):
                return Error.MALFORMED_LEGACY_LOCATION
            if schema_uri == "":
                return Error.MALFORMED_LEGACY_LOCATION

            namespace = mod.get("namespace")
            # TODO check URI format
            if not isinstance(namespace, str) or namespace == "":
                return Error.MALFORMED_NAMESPACE

            feature = YangLibraryParser._check_feature(mod)
            if isinstance(feature, Error):
                return feature

            deviation = cls._check_deviation(mod)
            if isinstance(deviation, Error):
                return deviation

            conformance_type = mod.get("conformance-type")
            if conformance_type not in cls.CONFORMANCE_TYPES:
                return Error.UNKNOWN_CONFORMANCE_TYPE
            
            parsed_submods = OrderedDict()
            all_submods = mod.get("submodule", default=[])
            if not isinstance(all_submods, list):
                return Error.MALFORMED_SUBMOD_LIST

            for submod in all_submods:
                if not isinstance(submod, dict):
                    return Error.MALFORMED_SUBMOD

                submod_name = submod.get("name")
                if not isinstnace(submod_name, None) or submod_name == "":
                    return Error.MALFORMED_SUBMOD_NAME

                submod_rev = submod.get("revision")
                if not isinstance(submod_rev, str):
                    return Error.MISSING_SUBMOD_REVISION
                if submod_rev == "":
                    submod_rev = None

                schema = submod.get("schema")
                if schema is not None and not isinstance(schema, str):
                    return Error.MALFORMED_SUBMOD_LEGACY_LOCATION

                parsed_submods[(submod_name, submod_rev)] = \
                    legacy.Submodule(name=submod_name, revision=submod_rev, schema=schema)
            
    @classmethod
    def _check_deviation(cls, mod) -> list  | (LibraryParseError, ""):
        all_devs = mod.get("deviation", default=[])
        if not isinstance(all_devs, list):
            return (LibraryParseError.MALFORMED_DEVIATION, "")
        
        parsed_devs = []
        for dev in all_devs:
            if not isinstance(dev, dict):
                return (LibraryParseError.MALFORMED_LEGACY_DEV_ENTRY, "")

        return parsed_devs
        
