# encoding:utf-8
from __future__ import print_function

proj = projects.primary
apl = proj.active_application
# Find the POU
new_PRGname='pou_IEC104'

pou_list = apl.find(new_PRGname, recursive=True)

if not pou_list:
    raise Exception("POU not found!")

pou = pou_list[0]

# Get existing implementation code
existing_code = pou.textual_implementation.text

# Append new line
new_code = existing_code + "\niCounter := iCounter + 1;"


# Get existing declaration
existing_decl = pou.textual_declaration.text

# Add new variable before END_VAR
new_decl = existing_decl.replace(
    "END_VAR",
    "    iNewVar : INT := 0;\nEND_VAR"
)

# Write back
pou.textual_declaration.replace(new_decl)

# Write back
pou.textual_implementation.replace(new_code)



print("Variable appended to:", new_decl)
print("Code appended to:", new_PRGname)
