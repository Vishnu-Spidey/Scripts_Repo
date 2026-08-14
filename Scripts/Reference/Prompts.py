
# encoding:utf-8
from __future__ import print_function

"""Performs some tests on the messagestore and UI."""

print("Some Error, Warning and Information popups:")
system.ui.error("Fatal error: Everything is OK. :-)")
system.ui.warning("Your bank account is surprisingly low")
system.ui.info("Just for your information: 42")

print("Now, we ask the user something.")
res = system.ui.prompt("Do you like this?", PromptChoice.YesNo, PromptResult.Yes);
print("The user selected '%s'" % res)

print("Now, the user can choose between custom options:")
res = system.ui.choose("Please choose:", ("First", 2, 7.5, "Something else"))
print("The user selected option '%s'" % str(res)) # res is a tuple

print("Now, the user can choose several options:")
res = system.ui.select_many("Please select one or more options", PromptChoice.OKCancel, PromptResult.OK, ("La Premiere", "The Second", "Das Dritte"))
print("The returned result is: '%s'" % str(res)) # res is a tuple

print("Now, the user can select files and directories")
res = system.ui.open_file_dialog("Choose multiple files:", filter="Text files (*.txt)|*.txt|Image Files(*.BMP;*.JPG;*.GIF)|*.BMP;*.JPG;*.GIF|All files (*.*)|*.*", filter_index = 0, multiselect=True)
print("The user did choose: '%s'" % str(res)) # res is a tuple as multiselect is true.

res = system.ui.save_file_dialog("Choose a file to save:", filter="Text files (*.txt)|*.txt|Image Files(*.BMP;*.JPG;*.GIF)|*.BMP;*.JPG;*.GIF|All files (*.*)|*.*", filter_index = 0)
print("The user did choose: '%s'" % res)

res = system.ui.browse_directory_dialog("Choose a directory", path="C:\\")
print("The user did choose: '%s'" % res)

print("Now we query a single line string")
res = system.ui.query_string("What's your name?")
print("Nice to meet you, dear %s." % res)

print("Now we query a multi line string")
res = system.ui.query_string("Please tell me a nice story about your life!", multi_line=True)
if (res):
        print("Huh, that has been a long text, at least %s characters!" % len(res))
else:
        print("Hey, don't be lazy!")