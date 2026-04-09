from typing import Any

from ._types import QualName

class DatastoreType:
    QUAL_NAME = ("datastore", "ietf-datastores")

    # more advanced version of qual_name
    __known_types: dict[QualName, type["DatastoreType"]] = {}

    # TODO make me singleton
    # TODO make auto generation of DatatypeTypes from identities in the Data Model

    def __init_subclass__(cls) -> None:
        if cls.QUAL_NAME in DatastoreType.__known_types:
            raise ValueError(f"Duplicate registration of datastore \"{qual_name[1]}:{qual_name[0]}\"")

        DatastoreType.__known_types[cls.QUAL_NAME] = cls

    @staticmethod
    def get(name: QualName) -> "DatastoreType":
        if name in DatastoreType.__known_types:
            return DatastoreType.__known_types[name]()

        raise ValueError(f"Unknown datastore {None}") # TODO format qual name

    def __hash__(self) -> int:
        return hash(self.QUAL_NAME)
    
    def __eq__(self, other: Any) -> bool:
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
    QUAL_NAME = ("conventional", "ietf-datastores")

class RunningDatastore(ConventionalDatastore):
    QUAL_NAME = ("running", "ietf-datastores")

class CandidateDatastore(ConventionalDatastore):
    QUAL_NAME = ("candidate", "ietf-datastores")

class StartupDatastore(ConventionalDatastore):
    QUAL_NAME = ("startup", "ietf-datastores")

class IntendedDatastore(ConventionalDatastore):
    QUAL_NAME = ("intended", "ietf-datastores")

class DynamicDatastore(DatastoreType):
    QUAL_NAME = ("dynamic", "ietf-datastores")

class OperationalDatastore(DatastoreType):
    QUAL_NAME = ("operational", "ietf-datastores")

class UnifiedDatastores(DatastoreType):
    QUAL_NAME = ("unified", "ietf-coreconf")

