# SPDX-FileCopyrightText: CZ.NIC z.s.p.o.
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import threading
from typing import ClassVar

from yang_sid_base import SID

from .constant import (DATASTORE_IDENTITY_SID, CONVENTIONAL_DATASTORE,
                       STARTUP_DATASTORE, CANDIDATE_DATASTORE, RUNNING_DATASTORE,
                       INTENDED_DATASTORE, DYNAMIC_DATASTORE, OPERATIONAL_DATASTORE,
                       CORECONF_UNIFIED_DS)
from ._types import QualName


class _Singleton(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        l_args = tuple(args)
        l_kwargs = tuple(sorted(kwargs.items()))
        if (cls, l_args, l_kwargs) not in cls._instances:
            with cls._lock:
                if (cls, l_args, l_kwargs) not in cls._instances:
                    cls._instances[(cls, l_args, l_kwargs)] = super().__call__(*args, **kwargs)

        return cls._instances[(cls, l_args, l_kwargs)]

class DatastoreType(metaclass=_Singleton):
    QUAL_NAME = ("datastore", "ietf-datastores")
    SID: ClassVar = SID(DATASTORE_IDENTITY_SID)

    # more advanced version of qual_name
    __known_types: dict[QualName, type["DatastoreType"]] = {}
    __types_by_sid: dict[SID, type["DatastoreType"]] = {}

    # TODO make me singleton
    # TODO make auto generation of DatatypeTypes from identities in the Data Model

    def __init_subclass__(cls) -> None:
        if cls.QUAL_NAME in DatastoreType.__known_types:
            raise ValueError(f"Duplicate registration of datastore \"{cls.QUAL_NAME[1]}:{cls.QUAL_NAME[0]}\"")

        if cls.SID in DatastoreType.__types_by_sid:
            raise ValueError(f"Duplicate registration of datastore SID {cls.SID}")

        DatastoreType.__known_types[cls.QUAL_NAME] = cls
        DatastoreType.__types_by_sid[cls.SID] = cls

    @staticmethod
    def get(name: QualName) -> "DatastoreType":
        type = DatastoreType.__known_types.get(name)
        if type is not None:
            return type()

        raise ValueError(f"Unknown datastore \"{name[1]}:{name[0]}\"") # TODO format qual name

    @staticmethod
    def get_from_sid(sid: SID) -> "DatastoreType":
        type = DatastoreType.__types_by_sid.get(sid)
        if type is not None:
            return type()

        raise ValueError(f"Unknonw datastore SID {sid}")

    def __hash__(self) -> int:
        return hash(self.QUAL_NAME)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DatastoreType):
            return self.QUAL_NAME == other.QUAL_NAME
        elif isinstance(other, tuple) and len(other) == 2:
            return self.QUAL_NAME == other
        else:
            return False

    def __str__(self):
        return str(self.QUAL_NAME)

# TODO deal with ALL_EXT, STRUCTURE and YANG_DATA content types
class ConventionalDatastore(DatastoreType):
    QUAL_NAME: ClassVar = ("conventional", "ietf-datastores")
    SID: ClassVar = SID(CONVENTIONAL_DATASTORE)

class RunningDatastore(ConventionalDatastore):
    QUAL_NAME: ClassVar = ("running", "ietf-datastores")
    SID: ClassVar = SID(RUNNING_DATASTORE)

class CandidateDatastore(ConventionalDatastore):
    QUAL_NAME: ClassVar = ("candidate", "ietf-datastores")
    SID: ClassVar = SID(CANDIDATE_DATASTORE)

class StartupDatastore(ConventionalDatastore):
    QUAL_NAME: ClassVar = ("startup", "ietf-datastores")
    SID: ClassVar = SID(STARTUP_DATASTORE)

class IntendedDatastore(ConventionalDatastore):
    QUAL_NAME: ClassVar = ("intended", "ietf-datastores")
    SID: ClassVar = SID(INTENDED_DATASTORE)

class DynamicDatastore(DatastoreType):
    QUAL_NAME: ClassVar = ("dynamic", "ietf-datastores")
    SID: ClassVar = SID(DYNAMIC_DATASTORE)

class OperationalDatastore(DatastoreType):
    QUAL_NAME: ClassVar = ("operational", "ietf-datastores")
    SID: ClassVar = SID(OPERATIONAL_DATASTORE)

class UnifiedDatastore(DatastoreType):
    QUAL_NAME: ClassVar = ("unified", "ietf-coreconf")
    SID: ClassVar = SID(CORECONF_UNIFIED_DS)

