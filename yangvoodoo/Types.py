RESERVED_PYTHON_KEYWORDS = ('import', 'class', 'in', 'and', 'as', 'not', 'from', 'or', 'global', 'pass',
                            'if', 'return', 'try', 'is', 'break')
DATA_ABSTRACTION_MAPPING = {
    # These values are now libyang types, instead of sysrepo
    # the node_types' for PRESENCE_CONTAINER and LIST are
    # artificially high to make it obvious these aren't real
    # libyang types.
    'UINT64': 19,
    'UINT32': 17,
    'UINT16': 15,
    'UINT8': 13,
    'INT64': 18,
    'INT32': 16,
    'INT16': 14,
    'INT8': 12,
    'STRING': 10,
    'DECIMAL64': 4,
    'BOOLEAN': 3,
    'ENUM': 6,
    'EMPTY': 5,
    # 'PRESENCE_CONTAINER': 100,
    # 'LIST': 101,
}

FORMAT = {
    'XML': 1,
    'JSON': 2
}

DATA_NODE_MAPPING = {
    'LIST': 16,
    'PRESENCE_CONTAINER': 100
}

INT_CONVERSION = {
    DATA_ABSTRACTION_MAPPING['INT32'],
    DATA_ABSTRACTION_MAPPING['INT16'],
    DATA_ABSTRACTION_MAPPING['INT8'],
    DATA_ABSTRACTION_MAPPING['UINT32'],
    DATA_ABSTRACTION_MAPPING['UINT16'],
    DATA_ABSTRACTION_MAPPING['UINT8'],
    DATA_ABSTRACTION_MAPPING['INT64'],
    DATA_ABSTRACTION_MAPPING['UINT64']
}

LIBYANG_MAPPING = {
    3: DATA_ABSTRACTION_MAPPING['BOOLEAN'],
    4: DATA_ABSTRACTION_MAPPING['DECIMAL64'],
    5: DATA_ABSTRACTION_MAPPING['EMPTY'],
    6: DATA_ABSTRACTION_MAPPING['ENUM'],
    10: DATA_ABSTRACTION_MAPPING['STRING'],
    12: DATA_ABSTRACTION_MAPPING['INT8'],
    13: DATA_ABSTRACTION_MAPPING['UINT8'],
    14: DATA_ABSTRACTION_MAPPING['INT16'],
    15: DATA_ABSTRACTION_MAPPING['UINT16'],
    16: DATA_ABSTRACTION_MAPPING['INT32'],
    17: DATA_ABSTRACTION_MAPPING['UINT32'],
    18: DATA_ABSTRACTION_MAPPING['INT64'],
    19: DATA_ABSTRACTION_MAPPING['UINT64']
}

LIBYANG_LEAF_TYPES = {
    3: "BOOLEAN",
    4: "DECIMAL64",
    5: "EMPTY",
    6: "ENUM",
    10: "STRING",
    11: "UNION",
    12: "INT8",
    13: "UINT8",
    14: "INT16",
    15: "UINT16",
    16: "INT32",
    17: "UINT32",
    18: "INT64",
    19: "UINT64",
    'BOOLEAN': 3,
    'DECIMAL64': 4,
    'EMPTY': 5,
    'ENUM': 6,
    'STRING': 10,
    'UNION': 11,
    'INT8': 12,
    'UINT8': 13,
    'INT16': 14,
    'UINT16': 15,
    'INT32': 16,
    'UINT32': 17,
    'INT64': 18,
    'UINT64': 19
}

LIBYANG_LEAFTYPE = {
    5: 'EMPTY',
    6: 'ENUM',
    'EMPTY': 5,
    'ENUM': 6
}

LIBYANG_LEAF_LIKE_NODES = {
    4: 'LEAF',
    8: 'LEAFLIST',
}

# To populate from lys_nodetype
LIBYANG_NODETYPE = {
    1: 'CONTAINER',
    2: 'CHOICE',
    4: 'LEAF',
    8: 'LEAFLIST',
    16: 'LIST',
    64: 'CASE',
    'CONTAINER': 1,
    'CHOICE': 2,
    'LEAF': 4,
    'LEAFLIST': 8,
    'LIST': 16,
    'CASE': 64
}
