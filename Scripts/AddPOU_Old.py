# encoding:utf-8
from __future__ import print_function

proj = projects.primary
apl = proj.active_application

base_PRGname = "pou_IEC104"
base_GVLname = "gvl_IEC104"

# Get all existing object names in the application
existing_names = [obj.get_name() for obj in apl.get_children(recursive=True)]

# Find a unique name
new_PRGname = base_PRGname
new_GVLname = base_GVLname
i = 1
j = 1

prg_renamed = False
gvl_renamed = False

while new_PRGname in existing_names:
    new_PRGname = "{}_{}".format(base_PRGname, i)
    i += 1
    prg_renamed = True

while new_GVLname in existing_names:
    new_GVLname = "{}_{}".format(base_GVLname, j)
    j += 1
    gvl_renamed = True

# Print only once
if prg_renamed:
    print(base_PRGname, "already exists, creating:", new_PRGname)

if gvl_renamed:
    print(base_GVLname, "already exists, creating:", new_GVLname)


# Create POU with unique name
apl.create_pou(new_PRGname, PouType.Program)

# Create GVL (simple, no rename logic here)
apl.create_gvl(new_GVLname)

print("Created POU:", new_PRGname)
print("Created POU:", new_GVLname)