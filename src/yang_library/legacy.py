# SPDX-FileCopyrightText: CZ.NIC z.s.p.o.
#
# SPDX-License-Identifier: LGPL-3.0-or-later

from __future__ import annotations

import re

from dataclasses import dataclass
from abc import abstractmethod
from enum import Enum
from collections import OrderedDict
from urllib.parse import urlparse
from typing import TypeAlias, Optional

from .datastore import DatastoreType
from ._types import QualName
from .translator import Translator

__all__ = (
    "YangLibrary", "Datastore", "Schema", "ModuleSet", "Module", "ImportOnlyModule", "ImplementModule",
    "Submodule"
)

RevisionId = Optional[str]

@dataclass
class YangLibrary:
    # even through the module set is a set we want to preserve the yang-library order
    # (to prevent user confusino)
    module: OrderedDict[(str, RevisionId), "Module"]
    module_set_id: str

    def __init__(self,
                 module_set: Union[OrderedDict[str, "ModuleSet", Iterable["ModuleSet"]]],
                 schema: Union[OrderedDict[str, "Schema"], Iterable["Schema"]],
                 datastore: Union[OrderedDict[QualName, "Datastore"], Iterable["Datastore"]],
                 content_id: str) -> None:
        if not isinstance(module_set, OrderedDict):
            module_set = OrderedDict((mod_set.name, mod_set) for mod_set in module_set)
        self.module_set = module_set
        if not isinstance(schema, OrderedDict):
            schema = OrderedDict((sch.name, sch) for sch in schema)
        self.schema = schema
        if not isinstance(datastore, OrderedDict):
            datastore = OrderedDict((ds.qual_name, ds) for ds in datastore)
        self.datastore = datastore
        self.content_id = content_id

    def is_rfc7895(self) -> bool:
        # TODO move to state where rfc7895 is represented as datastores[""] = Datastore("", Schema("", ModuleSet("", ...)))
        # schema[""] = datastore[""].schema
        # module_set[""] = schema[""].module_sets[""]
        return len(self.datastore) == 0 and len(self.schema) == 0 and \
            len(self.module_set) == 1 and \
            len(next(iter(self.module_set))) == 0

    def get_set(self) -> "ModuleSet":
        if self.is_rfc7895():
            return next(iter(self.module_set.items()))[1]
        else:
            raise ValueError("Usable only for RFC7895 data models")

    def validate(self) -> None:
        # TODO
        raise NotImplementedError()

# TODO NewType URL
URL: TypeAlias = str
Revision: TypeAlias = str

RFC8525_REVISION_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RFC7895_REVISION_REGEX = re.compile(r"^(|\d{4}-\d{2}-\d{2})$")

class ConformanceType(Enum):
    IMPLEMENT = "implement"
    IMPORT = "import"

@dataclass
class Module:
    # TODO use the factories
    name: str
    revision: RevisionId
    schema: Optional[URL]
    namespace: str
    feature: list[str]
    deviation: OrderedDict[(str, RevisionId), "Module"]
    submodule: OrderedDict[(str, RevisionId), "Submodule"]

# TODO is this useful?
@dataclass(unsafe_hash=True)
class ImportOnlyModule(Module):
    # fields inherited from Module
    ...

@dataclass
class ImplementModule(Module):
    # fields inherited from Module
    ...

@dataclass
class Submodule:
    name: str
    revision: Optional[str]
    schema: Optional[URL]
