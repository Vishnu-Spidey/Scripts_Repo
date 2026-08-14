# encoding:utf-8
from __future__ import print_function

STRUCT_CONTENT = """\
    a : BOOL;
    b : BIT;
    c : BIT;
"""

UNION_WHOLE = """\
TYPE MyUnion :
UNION
    Zahl : INT;
    Prozent : MyAlias;
    Bits : MyStruct;
END_UNION
END_TYPE
"""

proj = projects.primary

folder = proj.find('DataTypes', recursive = True)[0]

# Create a struct DUT and insert the list of variables just into the right
# place in line two, row 0 (line numbering starts with line 0)
struktur = folder.create_dut('MyStruct') # DutType.Structure is the default
struktur.textual_declaration.insert(2, 0, STRUCT_CONTENT)

# Alias types get their "content" via the base type, which will just end up
# as one line in the declaration part:
# TYPE MyAlias : INT (0..100); END_TYPE
bereich = folder.create_dut('MyAlias', DutType.Alias, "INT (0..100)")

# Instead of injecting the variables into the existing declaration,
# one can also just replace the complete declaration part, including the
# boilerplate code.
union = folder.create_dut('MyUnion', DutType.Union)
union.textual_declaration.replace(UNION_WHOLE)