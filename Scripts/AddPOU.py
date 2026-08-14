# encoding:utf-8
from __future__ import print_function

proj = projects.primary
apl = proj.active_application

base_PRGname = "pou_IEC104"
base_GVLname = "gvl_IEC104"

# Get all existing object names
existing_names = [obj.get_name() for obj in apl.get_children(recursive=True)]

# Find unique names
new_PRGname = base_PRGname
new_GVLname = base_GVLname

i = 1
j = 1

while new_PRGname in existing_names:
    new_PRGname = "{}_{}".format(base_PRGname, i)
    i += 1

while new_GVLname in existing_names:
    new_GVLname = "{}_{}".format(base_GVLname, j)
    j += 1

# -------------------------------
# Create POU and add code
# -------------------------------
pou = apl.create_pou(new_PRGname, PouType.Program)

# Add variable + declaration
pou.textual_declaration.replace("""\
PROGRAM {}
VAR
    iCounter : INT := 0;
END_VAR
""".format(new_PRGname))

# Add one line of code
pou.textual_implementation.replace("""\
iCounter := iCounter + 1;
""")

# -------------------------------
# Create GVL and add variable
# -------------------------------
gvl = apl.create_gvl(new_GVLname)

gvl.textual_declaration.replace("""\
VAR_GLOBAL
    xEnable : BOOL := FALSE;
END_VAR
""")

# -------------------------------
# Print result
# -------------------------------
print("Created POU:", new_PRGname)
print("Created GVL:", new_GVLname)