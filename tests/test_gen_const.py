# SPDX-FileCopyrightText: CZ.NIC z.s.p.o.
#
# SPDX-License-Identifier: LGPL-3.0-or-later


import pytest
import cbor2

import yang_library.constrained as constrained
from yang_library.generate import GenerateConstrainedLibrary

from yang_sid_base import SID

from yang_library.datastore import DatastoreType, UnifiedDatastore


def test_const_one_ds():
    mod_a = constrained.ImplementModule(identifier=SID(1200), revision=None)
    mod_b = constrained.ImplementModule(identifier=SID(1300), revision=None)

    mod_import_c = constrained.ImportOnlyModule(identifier=SID(1500), revision=None)

    mod_set = constrained.ModuleSet(index=0, module=[mod_a,  mod_b],
                                    import_only_module=[mod_import_c])

    schema = constrained.Schema(0, [mod_set])
    datastore = constrained.Datastore(UnifiedDatastore(), schema)

    library = constrained.YangLibrary(module_set=[mod_set],
                                      schema=[schema],
                                      datastore=[datastore],
                                      checksum=b"\x00")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 0, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1200, # SID(70022) identifier
                            },
                            {
                                3: 1300, # SID(70022) identifier
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 1500, # SID(70010) identifier
                                4: "", # SID(70013) revision
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 0, # SID(70030) index
                        2: [0], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 0, # SID(70007) schema
                    },
                ],
                3: b"\x00", # SID(70004) checksum
                },
            }


def test_const_rev():
    mod_a = constrained.ImplementModule(identifier=SID(1200), revision=None)
    mod_b = constrained.ImplementModule(identifier=SID(1300), revision=b"\x20\x25\x05\x14")

    rev1=b"\x20\x25\x04\x10"
    rev2=b"\x20\x25\x04\x20"
    mod_rev1 = constrained.ImportOnlyModule(identifier=SID(1500), revision=rev1)
    mod_rev2 = constrained.ImportOnlyModule(identifier=SID(1500), revision=rev2)

    mod_set = constrained.ModuleSet(index=0, module=[mod_a, mod_b],
                                    import_only_module=[mod_rev1, mod_rev2])

    schema = constrained.Schema(0, [mod_set])
    datastore = constrained.Datastore(DatastoreType.get(("unified", "ietf-coreconf")), schema)

    library = constrained.YangLibrary(module_set=[mod_set],
                                      schema=[schema],
                                      datastore=[datastore],
                                      checksum=b"\x01")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 0, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1200, # SID(70022) identifier
                            },
                            {
                                3: 1300, # SID(70022) identifier
                                6: b"\x20\x25\x05\x14", # SID(70025) revision
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 1500, # SID(70010) identifier
                                4: rev1, # SID(70013) revision
                            },
                            {
                                1: 1500, # SID(70010) identifier
                                4: rev2, # SID(70013) revision
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 0, # SID(70030) index
                        2: [0], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 0, # SID(70007) schema
                    },
                ],
                3: b"\x01", # SID(70004) checksum
                },
            }
def test_const_namespace():
    rev=b"\x45\x67\x01\x23"
    mod_a = constrained.ImplementModule(identifier=SID(1500), revision=rev, namespace="urn:ietf:params:xml:ns:yang:ietf-interfaces")
    import_mod_b = constrained.ImportOnlyModule(identifier=SID(60000), revision=None, namespace="http://example.com/ns/mod")

    mod_set = constrained.ModuleSet(index=1, module=[mod_a], import_only_module=[import_mod_b])
    schema = constrained.Schema(index=2, module_set=[mod_set])
    datastore = constrained.Datastore(DatastoreType.get_from_sid(SID(1023)), schema)
    library = constrained.YangLibrary(module_set=[mod_set], schema=[schema], datastore=[datastore], checksum=b"\x02")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library, add_namespace=True)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 1, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1500, # SID(70022) identifier
                                6: rev, # SID(70025) revision
                                5: "urn:ietf:params:xml:ns:yang:ietf-interfaces", # SID(70024) namespace
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 60000, # SID(70010) identifier
                                4: "", # SID(70013) revision
                                3: "http://example.com/ns/mod", # SID(70012) namespace
                            }
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 2, # SID(70030) index
                        2: [1], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 2, # SID(70007) schema
                    },
                ],
                3: b"\x02", # SID(70004) checksum
                },
            }

def test_const_submod():
    # test submod + submod revision
    submod_a = constrained.Submodule(identifier=1260)
    mod_a = constrained.ImplementModule(identifier=SID(1200), revision=None, submodule=[submod_a])
    submod_b1 = constrained.Submodule(identifier=1320)
    submod_b2 = constrained.Submodule(identifier=1340, revision=b"\x20\x25\x05\x10")
    mod_b = constrained.ImplementModule(identifier=SID(1300), revision=b"\x20\x25\x05\x14",
                                        submodule=[submod_b1, submod_b2])

    rev1=b"\x20\x25\x04\x10"
    rev2=b"\x20\x25\x04\x20"
    mod_rev1 = constrained.ImportOnlyModule(identifier=SID(1500), revision=rev1)
    mod_rev2_sub = constrained.Submodule(identifier=1560, revision=b"\x20\x25\x04\x20")
    mod_rev2 = constrained.ImportOnlyModule(identifier=SID(1500), revision=rev2,
                                            submodule=[mod_rev2_sub])

    mod_set = constrained.ModuleSet(index=0, module=[mod_a, mod_b],
                                    import_only_module=[mod_rev1, mod_rev2])
    schema = constrained.Schema(0, [mod_set])
    datastore = constrained.Datastore(DatastoreType.get(("unified", "ietf-coreconf")), schema)

    library = constrained.YangLibrary(module_set=[mod_set],
                                      schema=[schema],
                                      datastore=[datastore],
                                      checksum=b"\x01")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 0, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1200, # SID(70022) identifier
                                7: [ # SID(70026) submodule
                                    {
                                        1: 1260, # SID(70027) identifier
                                    },
                                ],
                            },
                            {
                                3: 1300, # SID(70022) identifier
                                6: b"\x20\x25\x05\x14", # SID(70025) revision
                                7: [ # SID(70026) submodule
                                    {
                                        1: 1320, # SID(70027) identifier
                                    },
                                    {
                                        1: 1340, # SID(70027) identifier
                                        3: b"\x20\x25\x05\x10", # SID(70029) revision
                                    },
                                ],
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 1500, # SID(70010) identifier
                                4: rev1, # SID(70013) revision
                            },
                            {
                                1: 1500, # SID(70010) identifier
                                4: rev2, # SID(70013) revision
                                5: [ # SID(70014) submodule
                                    {
                                        1: 1560, # SID(70015) identifier
                                        3: b"\x20\x25\x04\x20", # SID(70017) revision
                                    },
                                ],
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 0, # SID(70030) index
                        2: [0], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 0, # SID(70007) schema
                    },
                ],
                3: b"\x01", # SID(70004) checksum
                },
            }

@pytest.fixture
def location_library():
    rev=b"\x45\x67\x01\x23"
    mod_a = constrained.ImplementModule(identifier=SID(1500), revision=rev, namespace="urn:ietf:params:xml:ns:yang:ietf-interfaces",
                                        location=["http://example.com/ns/mod_a", "https://example.com/archive/ns/yang/mod_a"])
    _submod_b1 = constrained.Submodule(identifier=1550, revision=None, location=["http://example.com/loc/sub/b"])
    _submod_b2 = constrained.Submodule(1600, b"\x20\x22\x12\x20", location=["http://example.com/loc/sub/b2_1", "http://example.com/alt-loc/sub/b2_2"])

    mod_b = constrained.ImplementModule(identifier=SID(2000), namespace="urn:example:totally-not-interfaces",
                                        location=["http://example.com/ns/not-ifs", "https://example.com/archive/ns/yang/not-ifs"],
                                        submodule=[_submod_b1, _submod_b2])
    import_mod_b = constrained.ImportOnlyModule(identifier=SID(60000), revision=None,
                                                location=["ftp://example.com/ns/mod_b", "http://example.com/ns/mod_b"])
    import_mod_c = constrained.ImportOnlyModule(identifier=SID(60100), revision=b"\x20\x21\x01\x02",
                                                location=["http://example.com/ns/mod_c"])
    import_mod_d = constrained.ImportOnlyModule(identifier=SID(60200), revision=b"\x20\x21\x01\x03",
                                                location=["http://example.com/ns/mod_d"])

    _submod_e1 = constrained.Submodule(identifier=60360)
    _submod_e2 = constrained.Submodule(identifier=60380, location=["http://example.com/mod_e/submod/e2"])

    # no location
    import_mod_e = constrained.ImportOnlyModule(identifier=SID(60300), revision=b"\x20\x21\x01\x03",
                                            submodule=[_submod_e1, _submod_e2])

    mod_set = constrained.ModuleSet(index=1, module=[mod_a, mod_b],
                                    import_only_module=[import_mod_b, import_mod_c, import_mod_d, import_mod_e])
    schema = constrained.Schema(index=2, module_set=[mod_set])
    datastore = constrained.Datastore(DatastoreType.get_from_sid(SID(1023)), schema)
    library = constrained.YangLibrary(module_set=[mod_set], schema=[schema], datastore=[datastore], checksum=b"\x02")

    return library

def test_const_location_none(location_library):
    rev=b"\x45\x67\x01\x23"
    cbor_bytes = GenerateConstrainedLibrary.to_cbor(location_library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 1, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1500, # SID(70022) identifier
                                6: rev, # SID(70025) revision
                            },
                            {
                                3: 2000, # SID(70022) identifier
                                7: [ # SID(70026) submodule
                                    {
                                        1: 1550, # SID(70027) identifier
                                    },
                                    {
                                        1: 1600, # SID(70027) identifier
                                        3: b"\x20\x22\x12\x20", # SID(70029) revision
                                    },
                                ],
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 60000, # SID(70010) identifier
                                4: "", # SID(70013) revision
                            },
                            {
                                1: 60100, # SID(70010) identifier
                                4: b"\x20\x21\x01\x02", # SID(70013) revision
                            },
                            {
                                1: 60200, # SID(70010) identifier
                                4: b"\x20\x21\x01\x03", # SID(70013) revision
                            },
                            {
                                1: 60300, # SID(70010) identifier
                                4: b"\x20\x21\x01\x03", # SID(70013) revision
                                5: [ # SID(70014) submodule
                                    {
                                        1: 60360, # SID(70015) identifier
                                    },
                                    {
                                        1: 60380, # SID(70015) identifier
                                    },
                                ],
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 2, # SID(70030) index
                        2: [1], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 2, # SID(70007) schema
                    },
                ],
                3: b"\x02", # SID(70004) checksum
                },
            }

def test_const_location_all(location_library):
    rev=b"\x45\x67\x01\x23"
    cbor_bytes = GenerateConstrainedLibrary.to_cbor(location_library, location_filter=lambda x: x)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 1, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1500, # SID(70022) identifier
                                6: rev, # SID(70025) revision
                                4: ["http://example.com/ns/mod_a", "https://example.com/archive/ns/yang/mod_a"], # SID(70023) location
                            },
                            {
                                3: 2000, # SID(70022) identifier
                                4: ["http://example.com/ns/not-ifs", "https://example.com/archive/ns/yang/not-ifs"], # SID(70023) location
                                7: [ # SID(70026) submodule
                                    {
                                        1: 1550, # SID(70027) identifier
                                        2: ["http://example.com/loc/sub/b"], # SID(70028) location
                                    },
                                    {
                                        1: 1600, # SID(70027) identifier
                                        3: b"\x20\x22\x12\x20", # SID(70029) revision
                                        2: ["http://example.com/loc/sub/b2_1", "http://example.com/alt-loc/sub/b2_2"], # SID(70028) location
                                    },
                                ],
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 60000, # SID(70010) identifier
                                4: "", # SID(70013) revision
                                2: ["ftp://example.com/ns/mod_b", "http://example.com/ns/mod_b"], # SID(70011) location
                            },
                            {
                                1: 60100, # SID(70010) identifier
                                4: b"\x20\x21\x01\x02", # SID(70013) revision
                                2: ["http://example.com/ns/mod_c"], # SID(70011) location
                            },
                            {
                                1: 60200, # SID(70010) identifier
                                4: b"\x20\x21\x01\x03", # SID(70013) revision
                                2: ["http://example.com/ns/mod_d"], # SID(70011) location
                            },
                            {
                                1: 60300, # SID(70010) identifier
                                4: b"\x20\x21\x01\x03", # SID(70013) revision
                                5: [ # SID(70014) submodule
                                    {
                                        1: 60360, # SID(70015) identifier
                                    },
                                    {
                                        1: 60380, # SID(70015) identifier
                                        2: ["http://example.com/mod_e/submod/e2"], # SID(70016) location
                                    },
                                ],
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 2, # SID(70030) index
                        2: [ # SID(70031) module-set
                            1,
                        ],
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 2, # SID(70007) schema
                    },
                ],
                3: b"\x02", # SID(70004) checksum
                },
            }

def test_const_location_first(location_library):
    rev=b"\x45\x67\x01\x23"
    cbor_bytes = GenerateConstrainedLibrary.to_cbor(location_library, location_filter=
                                                    lambda x: [x[0]] if x and len(x) else tuple())
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 1, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1500, # SID(70022) identifier
                                6: rev, # SID(70025) revision
                                4: ["http://example.com/ns/mod_a"], # SID(70023) location
                            },
                            {
                                3: 2000, # SID(70022) identifier
                                4: ["http://example.com/ns/not-ifs"], # SID(70023) location
                                7: [ # SID(70026) submodule
                                    {
                                        1: 1550, # SID(70027) identifier
                                        2: ["http://example.com/loc/sub/b"], # SID(70028) location
                                    },
                                    {
                                        1: 1600, # SID(70027) identifier
                                        3: b"\x20\x22\x12\x20", # SID(70029) revision
                                        2: ["http://example.com/loc/sub/b2_1"], # SID(70028) location
                                    },
                                ],
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 60000, # SID(70010) identifier
                                4: "", # SID(70013) revision
                                2: ["ftp://example.com/ns/mod_b"], # SID(70011) location
                            },
                            {
                                1: 60100, # SID(70010) identifier
                                4: b"\x20\x21\x01\x02", # SID(70013) revision
                                2: ["http://example.com/ns/mod_c"], # SID(70011) location
                            },
                            {
                                1: 60200, # SID(70010) identifier
                                4: b"\x20\x21\x01\x03", # SID(70013) revision
                                2: ["http://example.com/ns/mod_d"], # SID(70011) location
                            },
                            {
                                1: 60300, # SID(70010) identifier
                                4: b"\x20\x21\x01\x03", # SID(70013) revision
                                5: [ # SID(70014) submodule
                                    {
                                        1: 60360, # SID(70015) identifier
                                    },
                                    {
                                        1: 60380, # SID(70015) identifier
                                        2: ["http://example.com/mod_e/submod/e2"], # SID(70016) location
                                    },
                                ],
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 2, # SID(70030) index
                        2: [1], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 2, # SID(70007) schema
                    },
                ],
                3: b"\x02", # SID(70004) checksum
                },
            }


def test_const_feature():
    mod_a = constrained.ImplementModule(identifier=SID(1200), revision=None, feature=(1201,))
    mod_b = constrained.ImplementModule(SID(1300), b"\x20\x25\x05\x14", feature=(1310, 1311, 1316))

    rev1=b"\x20\x25\x04\x10"
    rev2=b"\x20\x25\x04\x20"
    mod_rev1 = constrained.ImportOnlyModule(SID(1500), revision=rev1)
    mod_rev2 = constrained.ImportOnlyModule(SID(1500), revision=rev2)

    mod_set = constrained.ModuleSet(0, [mod_a, mod_b],
                                    [mod_rev1, mod_rev2])

    schema = constrained.Schema(index=0, module_set=[mod_set])
    datastore = constrained.Datastore(DatastoreType.get(("unified", "ietf-coreconf")), schema)

    library = constrained.YangLibrary(module_set=[mod_set],
                                      schema=[schema],
                                      datastore=[datastore],
                                      checksum=b"\x01")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 0, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1200, # SID(70022) identifier
                                2: [1201], # SID(70021) feature
                            },
                            {
                                3: 1300, # SID(70022) identifier
                                6: b"\x20\x25\x05\x14", # SID(70025) revision
                                2: [1310, 1311, 1316], # SID(70021) feature
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 1500, # SID(70010) identifier
                                4: rev1, # SID(70013) revision
                            },
                            {
                                1: 1500, # SID(70010) identifier
                                4: rev2, # SID(70013) revision
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 0, # SID(70030) index
                        2: [0], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 0, # SID(70007) schema
                    },
                ],
                3: b"\x01", # SID(70004) checksum
                },
            }

@pytest.mark.skip(reason="Not MVP feature, TODO")
def test_const_deviation():
    pass

def test_const_multi_ds():
    mod_a_rev = b"\x20\x26\x02\x12"
    mod_a = constrained.ImplementModule(identifier=SID(2000), revision=mod_a_rev)
    import_rev = b"\x20\x25\x06\x06"
    import_mod_b = constrained.ImportOnlyModule(identifier=SID(1000), revision=import_rev)
    mod_set = constrained.ModuleSet(index=12, module=[mod_a], import_only_module=[import_mod_b])
    schema = constrained.Schema(index=10, module_set=[mod_set])
    running = constrained.Datastore(DatastoreType.get(("running", "ietf-datastores")), schema)
    operational = constrained.Datastore(DatastoreType.get(("operational", "ietf-datastores")), schema)
    library = constrained.YangLibrary(module_set=[mod_set], schema=[schema],
                                     datastore=[running, operational],
                                     checksum=b"\x00\x00\x00\x00\x12\x34\x56\x78")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 12, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 2000, # SID(70022) identifier
                                6: mod_a_rev, # SID(70025) revision
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 1000, # SID(70010) identifier
                                4: import_rev, # SID(70013) revision
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 10, # SID(70030) index
                        2: [12], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 71007, # SID(70006) identifier, SID(71007) == "ietf-datastores:running"
                        2: 10, # SID(70007) schema
                    },
                    {
                        1: 71006, # SID(70006) identifier, SID(71006) == "ietf-datastores:operational"
                        2: 10, # SID(70007) schema
                    },
                ],
                3: b"\x00\x00\x00\x00\x12\x34\x56\x78", # SID(70004) checksum
                },
            }


def test_const_multi_schema_set():
    mod_a_rev = b"\x20\x26\x02\x12"
    mod_a = constrained.ImplementModule(identifier=SID(2000), revision=mod_a_rev)
    import_rev = b"\x20\x25\x06\x06"
    import_mod_b = constrained.ImportOnlyModule(identifier=SID(1000), revision=import_rev)
    mod_c = constrained.ImplementModule(identifier=SID(3000))
    mod_set1 = constrained.ModuleSet(index=12, module=[mod_a], import_only_module=[import_mod_b])
    mod_set2 = constrained.ModuleSet(index=30, module=[mod_c], import_only_module=[])
    schema1 = constrained.Schema(index=10, module_set=[mod_set1])
    schema2 = constrained.Schema(index=240, module_set=[mod_set1, mod_set2])
    running = constrained.Datastore(DatastoreType.get(("running", "ietf-datastores")), schema1)
    operational = constrained.Datastore(DatastoreType.get(("operational", "ietf-datastores")), schema2)
    library = constrained.YangLibrary(module_set=[mod_set1, mod_set2], schema=[schema1, schema2],
                                     datastore=[running, operational],
                                     checksum=b"\xab\xcd\xef\x00\x00\xab\xcd\xef")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 12, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 2000, # SID(70022) identifier
                                6: mod_a_rev, # SID(70025) revision
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 1000, # SID(70010) identifier
                                4: import_rev, # SID(70013) revision
                            },
                        ],
                    },
                    {
                        10: 30, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 3000, # SID(70022) identifier
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 10, # SID(70030) index
                        2: [12], # SID(70031) module-set
                    },
                    {
                        1: 240, # SID(70030) index
                        2: [12, 30], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 71007, # SID(70006) identifier, SID(71007) == "ietf-datastores:running"
                        2: 10, # SID(70007) schema
                    },
                    {
                        1: 71006, # SID(70006) identifier, SID(71006) == "ietf-datastores:operational"
                        2: 240, # SID(70007) schema
                    },
                ],
                3: b"\xab\xcd\xef\x00\x00\xab\xcd\xef", # SID(70004) checksum
                },
            }

def test_mod_set_no_import():
    mod_a = constrained.ImplementModule(identifier=SID(1000))
    mod_b = constrained.ImplementModule(identifier=SID(2000))
    mod_c = constrained.ImplementModule(identifier=SID(3000), revision=b"\x20\x24\x01\x02")
    mod_d = constrained.ImplementModule(identifier=SID(4000), revision=b"\x20\x25\x04\x20")

    mod_set = constrained.ModuleSet(index=1, module=[mod_a, mod_b, mod_c, mod_d], import_only_module=[])
    schema = constrained.Schema(index=2, module_set=[mod_set])
    datastore = constrained.Datastore(DatastoreType.get_from_sid(SID(1023)), schema=schema)
    library = constrained.YangLibrary(module_set=[mod_set], schema=[schema], datastore=[datastore],
                                      checksum=b"\x12\x34")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 1, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1000, # SID(70022) identifier
                            },
                            {
                                3: 2000, # SID(70022) identifier
                            },
                            {
                                3: 3000, # SID(70022) identifier
                                6: b"\x20\x24\x01\x02", # SID(70025) revision
                            },
                            {
                                3: 4000, # SID(70022) identifier
                                6: b"\x20\x25\x04\x20", # SID(70025) revision
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 2, # SID(70030) index
                        2: [1], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 2, # SID(70007) schema
                    },
                ],
                3: b"\x12\x34", # SID(70004) checksum
                },
            }

def test_mod_set_no_impl():
    import_mod_a = constrained.ImplementModule(identifier=SID(1000))
    import_mod_b = constrained.ImplementModule(identifier=SID(2000))
    import_mod_c = constrained.ImplementModule(identifier=SID(3000), revision=b"\x20\x24\x01\x02")
    import_mod_d = constrained.ImplementModule(identifier=SID(4000), revision=b"\x20\x25\x04\x20")

    mod_set = constrained.ModuleSet(index=1, module=[], import_only_module=[import_mod_a, import_mod_b, import_mod_c, import_mod_d])
    schema = constrained.Schema(index=2, module_set=[mod_set])
    datastore = constrained.Datastore(DatastoreType.get_from_sid(SID(1023)), schema=schema)
    library = constrained.YangLibrary(module_set=[mod_set], schema=[schema], datastore=[datastore],
                                      checksum=b"\x12\x34")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 1, # SID(70018) index
                        1: [ # SID(70009) import-only-module
                            {
                                1: 1000, # SID(70010) identifier
                                4: "", # SID(70013) revision
                            },
                            {
                                1: 2000, # SID(70010) identifier
                                4: "", # SID(70013) revision
                            },
                            {
                                1: 3000, # SID(70010) identifier
                                4: b"\x20\x24\x01\x02", # SID(70013) revision
                            },
                            {
                                1: 4000, # SID(70010) identifier
                                4: b"\x20\x25\x04\x20", # SID(70013) revision
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 2, # SID(70030) index
                        2: [1], # SID(70031) module-set
                    },
                ],
                4: [ # SID(70005) datastore
                    {
                        1: 1023, # SID(70006) identifier, SID(1023) == "ietf-coreconf:unified"
                        2: 2, # SID(70007) schema
                    },
                ],
                3: b"\x12\x34", # SID(70004) checksum
                },
            }

def test_no_ds():
    mod_a = constrained.ImplementModule(identifier=SID(1200), revision=None)
    mod_b = constrained.ImplementModule(identifier=SID(1300), revision=None)

    mod_import_c = constrained.ImportOnlyModule(identifier=SID(1500), revision=None)

    mod_set = constrained.ModuleSet(index=0, module=[mod_a,  mod_b],
                                    import_only_module=[mod_import_c])

    schema = constrained.Schema(0, [mod_set])

    library = constrained.YangLibrary(module_set=[mod_set],
                                      schema=[schema],
                                      datastore=[],
                                      checksum=b"\x00")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 0, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1200, # SID(70022) identifier
                            },
                            {
                                3: 1300, # SID(70022) identifier
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 1500, # SID(70010) identifier
                                4: "", # SID(70013) revision
                            },
                        ],
                    },
                ],
                29: [# SID(70030) schema
                    {
                        1: 0, # SID(70030) index
                        2: [0], # SID(70031) module-set
                    },
                ],
                3: b"\x00", # SID(70004) checksum
                },
            }



def test_no_schema():
    mod_a = constrained.ImplementModule(identifier=SID(1200), revision=None)
    mod_b = constrained.ImplementModule(identifier=SID(1300), revision=None)

    mod_import_c = constrained.ImportOnlyModule(identifier=SID(1500), revision=None)

    mod_set = constrained.ModuleSet(index=0, module=[mod_a,  mod_b],
                                    import_only_module=[mod_import_c])

    library = constrained.YangLibrary(module_set=[mod_set],
                                      schema=[],
                                      datastore=[],
                                      checksum=b"\x00")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                7: [ # SID(70008) module-set
                    {
                        10: 0, # SID(70018) index
                        11: [ # SID(70019) module
                            {
                                3: 1200, # SID(70022) identifier
                            },
                            {
                                3: 1300, # SID(70022) identifier
                            },
                        ],
                        1: [ # SID(70009) import-only-module
                            {
                                1: 1500, # SID(70010) identifier
                                4: "", # SID(70013) revision
                            },
                        ],
                    },
                ],
                3: b"\x00", # SID(70004) checksum
                },
            }


def test_no_mod_set():
    library = constrained.YangLibrary(module_set=[],
                                      schema=[],
                                      datastore=[],
                                      checksum=b"\x01\x02\x03\x04\x05\x06\x07\x80\x90\xa0\xb0\xc0\xd0\xe0\xf0")

    cbor_bytes = GenerateConstrainedLibrary.to_cbor(library)
    obj = cbor2.loads(cbor_bytes)
    assert obj == {
            70001: { # ietf-constrained-yang-library:yang-library
                3: b"\x01\x02\x03\x04\x05\x06\x07\x80\x90\xa0\xb0\xc0\xd0\xe0\xf0", # SID(70004) checksum
                },
            }
