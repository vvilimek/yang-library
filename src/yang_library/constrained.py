# SPDX-FileCopyrightText: CZ.NIC z.s.p.o.
#
# SPDX-License-Identifier: LGPL-3.0-or-later

# based on draft I-D.ietf-core-yang-library (rev 3)

from __future__ import annotations

import re

from dataclasses import dataclass, field
from collections import OrderedDict
from collections.abc import Iterable
from urllib.parse import urlparse
from typing import TypeAlias, Optional, Union, TYPE_CHECKING, NewType

from yang_sid_base import SID

from .datastore import DatastoreType
from ._types import QualName


if TYPE_CHECKING:
    from . import constrained
    import yang_sid

__all__ = (
    "YangLibrary", "Datastore", "Schema", "ModuleSet", "Module", "ImportOnlyModule", "ImplementModule",
    "Submodule"
)

RevisionId = NewType("RevisionId", bytes)

@dataclass
class YangLibrary:
    # even through the module set is a set we want to preserve the yang-library order
    # (to prevent user confusino)
    module_set: OrderedDict[int, "ModuleSet"]
    schema: OrderedDict[int, "Schema"]
    datastore: OrderedDict[SID, "Datastore"]
    checksum: bytes

    def __init__(self,
             module_set: Union[OrderedDict[int, "ModuleSet"], Iterable["ModuleSet"]],
             schema: Union[OrderedDict[int, "Schema"], Iterable["Schema"]],
             datastore: Union[OrderedDict[SID, "Datastore"], Iterable["Datastore"]],
             checksum: bytes) -> None:

        if not isinstance(module_set, OrderedDict):
            module_set = OrderedDict((mod_set.index, mod_set) for mod_set in module_set)
        self.module_set = module_set
        if not isinstance(schema, OrderedDict):
            schema = OrderedDict((sch.index, sch) for sch in schema)
        self.schema = schema
        if not isinstance(datastore, OrderedDict):
            datastore = OrderedDict((ds.identifier, ds) for ds in datastore)
        self.datastore = datastore
        self.checksum = checksum

    def validate(self) -> None:
        # TODO
        raise NotImplementedError()

@dataclass
class Datastore:
    __type: "DatastoreType"
    schema: "Schema"

    @property
    def identifier(self) -> SID:
        return self.__type.SID

    @property
    def name(self) -> str:
        return self.__type.QUAL_NAME[0]

    @property
    def qual_name(self) -> QualName:
        return self.__type.QUAL_NAME

    @property
    def datastore(self) -> DatastoreType:
        return self.__type


    def __init__(self, datastore: DatastoreType, schema: "Schema") -> None:
        # TODO find the definition of ietf-datastores identity @name
        self.__type = datastore
        self.schema = schema

    @classmethod
    def from_sid(cls, sid: SID, schema: "Schema") -> None:
        return cls(DatastoreType.get_from_sid(sid), schema)


    def __hash__(self) -> int:
        return hash(self.qual_name)

    def type(self) -> "DatastoreType":
        return self.__type

@dataclass
class Schema:
    index: int
    module_set: OrderedDict[int, "ModuleSet"]

    def __init__(self,
             index: int,
             module_set: Union[OrdredDict[int, "ModuleSet"], Iterable["ModuleSet"]]) -> None:
        self.index = index
        if not isinstance(module_set, OrderedDict):
            module_set = OrderedDict((mod_set.index, mod_set) for mod_set in module_set)
        self.module_set = module_set

    def __hash__(self) -> int:
        return hash(self.index)

@dataclass
class ModuleSet:
    index: int
    module: OrderedDict[SID, "ImplementModule"]
    import_only_module: OrderedDict[(SID, RevisionId), "ImportOnlyModule"]

    def __init__(self,
             index: int,
             module: Union[OrderedDict[SID, "ImplementModule"], Iterable["ImplementModule"]],
             import_only_module: Union[OrderedDict[(SID, RevisionId), "ImportOnlyModule"], Iterable["ImportOnlyModule"]]) -> None:
        self.index = index
        if not isinstance(module, OrderedDict):
            module = OrderedDict((mod.identifier, mod) for mod in module)
        self.module = module
        if not isinstance(import_only_module, OrderedDict):
            import_only_module = OrderedDict(((imod.identifier, imod.revision), imod) for imod in import_only_module)
        self.import_only_module = import_only_module

    def __hash__(self) -> int:
        return hash(self.index)

# TODO NewType URL
URL: TypeAlias = str
URI: TypeAlias = str

CONSTRAINED_REVISION_REGEX = re.compile(r"^(.{2})(.{1})(.{1})$")

@dataclass
class Module:
    # TODO use the factories
    identifier: SID
    revision: Optional[RevisionId]
    namespace: Optional[URI] = None
    location: tuple[URL] = field(default_factory=tuple)
    submodule: OrderedDict[SID, "Submodule"] = field(default_factory=OrderedDict)

    def __init__(self,
             identifier: SID,
             revision: Optional[RevisionId],
             namespace: Optional[URI] = None,
             location: Optional[tuple[URL]] = None,
             submodule: Union[OrdredDcit[SID, "Submodule"], Iterable["Submodule"], None] = None) -> None:
        self.identifier = identifier
        self.revision = revision
        self.namespace = namespace
        if location is not None:
            self.location = location
        else:
            self.location = tuple()
        if submodule is None:
            submodule = OrderedDict()
        elif not isinstance(submodule, OrderedDict):
            submodule = OrderedDict((submod.identifier, submod) for submod in submodule)
        self.submodule = submodule

    @staticmethod
    def url_factory(url: str) -> URL:
        # basic check of URL, if malformed raises ValueError
        _parsed = urlparse(url)
        return url

    @staticmethod
    def revision_factory(rev: str, regex: re.Pattern) -> Optional[Revision]:
        # TODO check that revision is valid date
        if not regex.match(rev):
            raise ValueError()

        if rev == "":
            return None
        else:
            return rev

    def __hash__(self) -> int:
        return hash((self.identifier, self.revision))

# TODO is this useful?
@dataclass(unsafe_hash=True)
class ImportOnlyModule(Module):
    # fields inherited from Module

    def __init__(self,
             identifier: SID,
             revision: Optional[RevisionId],
             namespace: Optional[URI] = None,
             location: Optional[tuple[URL]] = None,
             submodule: Union[OrdredDict[SID, "Submodule"], Iterable["Submodule"], None] = None) -> None:
        super().__init__(identifier, revision, namespace, location, submodule)


@dataclass
class ImplementModule(Module):
    # fields inherited from Module
    feature: tuple[SID] = field(default_factory=tuple)
    deviation: OrderedDict[SID, "ImplementModule"] = field(default_factory=OrderedDict)

    def __init__(self,
             identifier: SID,
             revision: Optional[RevisionId] = None,
             namespace: Optional[URI] = None,
             location: Optional[tuple[URL]] = None,
             submodule: Union[OrdredDcit[SID, "Submodule"], Iterable["Submodule"], None] = None,
             feature: Optional[tuple[SID]] = None,
             deviation: Union[OrderedDict[SID, "ImplementModule"], Iterable["ImplementModule"], None] = None) -> None:

        super().__init__(identifier, revision, namespace, location, submodule)
        if feature is None:
            feature = tuple()
        self.feature = feature
        if deviation is None:
            deviation = OrderedDict()
        elif not isinstance(deviation, OrderedDict):
            deviation = OrderedDict((dev.identifier, dev) for dev in deviation)
        self.deviation = deviation

    def __hash__(self) -> int:
        return hash((self.identifier, self.revision, 'implement'))

@dataclass
class Submodule:
    identifier: SID
    revision: Optional[RevisionId] = None
    location: tuple[URL] = field(default_factory=tuple)

