# encoding:utf-8
from __future__ import print_function

proj = projects.primary
apl = proj.active_application
new_PRGname='pou_IEC104'
# Get POU
pou_list = apl.find(new_PRGname, recursive=True)
pou = pou_list[0]

if not pou_list:
    raise Exception("POU not found!")


# Read existing code
code = pou.textual_implementation.text

# Define markers
start_tag = "//CodeStart"
end_tag = "//Codeend"

# Remove block
if start_tag in code and end_tag in code:
    start_index = code.find(start_tag)
    end_index = code.find(end_tag) + len(end_tag)

    new_code = code[:start_index] + code[end_index:]

    pou.textual_implementation.replace(new_code)
    print("Block removed successfully")
else:
    print("Tags not found")