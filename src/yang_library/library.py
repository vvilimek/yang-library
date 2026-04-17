# SPDX-FileCopyrightText: CZ.NIC z.s.p.o.
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import re

from dataclasses import dataclass
from abc import abstractmethod
from collections import OrderedDict
from urllib.parse import urlparse
from typing import TypeAlias, Optional

from .datastore import DatastoreType
from ._types import QualName

__all__ = (
    "YangLibrary", "Datastore", "Schema", "ModuleSet", "Module", "ImportOnlyModule", "ImplementModule",
    "Submodule"
)

@dataclass
class YangLibrary:
    # even through the module set is a set we want to preserve the yang-library order
    # (to prevent user confusino)
    module_set: OrderedDict[str, "ModuleSet"]
    schema: OrderedDict[str, "Schema"]
    datastore: OrderedDict[QualName, "Datastore"]
    content_id: str

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

@dataclass
class Datastore:
    __type: "DatastoreType"
    schema: "Schema"

    @property
    def name(self) -> str:
        return self.__type.QUAL_NAME[0]

    @property
    def qual_name(self) -> QualName:
        return self.__type.QUAL_NAME

    def __init__(self, name: QualName, schema: "Schema") -> None:
        # TODO find the definition of ietf-datastores identity @name
        self.__type = DatastoreType.get(name)
        self.schema = schema

    def __hash__(self) -> int:
        return hash(self.qual_name)

    def type(self) -> "DatastoreType":
        return self.__type

@dataclass
class Schema:
    name: str
    module_set: OrderedDict[str, "ModuleSet"]

    def __hash__(self) -> int:
        return hash(self.name)

@dataclass
class ModuleSet:
    name: str
    module: OrderedDict[str, "ImplementModule"]
    import_only_module: OrderedDict[str, "ImportOnlyModule"]

    def __hash__(self) -> int:
        return hash(self.name)

# TODO NewType URL
URL: TypeAlias = str
Revision: TypeAlias = str

RFC8525_REVISION_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RFC7895_REVISION_REGEX = re.compile(r"^(|\d{4}-\d{2}-\d{2})$")

@dataclass
class Module:
    # TODO use the factories
    name: str
    revision: Optional[str]
    namespace: str
    location: tuple[URL]
    submodule: OrderedDict[str, "Submodule"]

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
        return hash((self.name, self.revision))

# TODO is this useful?
@dataclass(unsafe_hash=True)
class ImportOnlyModule(Module):
    # fields inherited from Module
    ...

@dataclass
class ImplementModule(Module):
    # fields inherited from Module
    feature: tuple[str]
    deviation: OrderedDict[str, "ImplementModule"] # TODO use Module instead

    def __hash__(self) -> int:
        return hash((self.name, self.revision, 'implement'))

@dataclass
class Submodule:
    name: str
    revision: Optional[str]
    location: tuple[str]
