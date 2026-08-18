# -*- coding: utf-8 -*-
"""
CODESYS Scripting Engine -- POU/FB/Function/Structure/GVL Exporter
===================================================================
Run inside CODESYS via: Tools > Scripting > Execute Script File

Behaviour:
  - Scans the full project tree on startup
  - Shows a checklist tree dialog (Controllers, folders, POUs)
  - Checking a parent auto-checks all children
  - Non-exportable items shown greyed out (not selectable)
  - Mirrors folder structure on disk per Controller
  - Each object saved as its own <Name>.st file

Compatible with: Python 2 (CODESYS / DIADesigner-AX scripting engine)
"""

import os
import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import (
    Form, Button, DialogResult, FormBorderStyle, FormStartPosition,
    MessageBox, MessageBoxButtons, MessageBoxIcon,
    TreeView, TreeNode, CheckState, TreeViewAction,
    DockStyle, Panel, Label, ScrollBars
)
from System.Drawing import Size, Point, Font, Color, FontStyle


# ---------------------------------------------------------------------------
# 1.  HELPERS
# ---------------------------------------------------------------------------

def get_name_safe(obj):
    try:
        return obj.get_name()
    except Exception:
        return "(unnamed)"

def is_exportable(obj):
    try:
        return obj.has_textual_declaration
    except Exception:
        return False

def is_skippable(name):
    """Return True for hardware/system nodes that clutter the tree."""
    skip = [
        "Library Manager", "Task Configuration", "TaskConfig",
        "Hardware Configuration", "Network Configuration",
        "EtherCAT Topology", "EtherCAT_1", "BuiltIn", "BuiltIn_DIO",
        "BuiltIn_Pulse_Encoder", "SoftMotion General Axis Pool",
        "Telecontrol_Configurator_1", "Project Settings",
        "Project Information", "GlobalTextList", "ArchiveObject",
        "__VisualizationStyle",
    ]
    return name in skip

def makedirs_safe(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

def get_declaration(obj):
    try:
        t = obj.textual_declaration.text
        return t if t else ""
    except Exception:
        return ""

def get_implementation(obj):
    try:
        t = obj.textual_implementation.text
        return t if t else ""
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# 2.  BUILD TREE DATA  (pure Python, no UI yet)
# ---------------------------------------------------------------------------

class NodeData(object):
    """Holds a reference to a CODESYS object and its metadata."""
    def __init__(self, obj, name, exportable, children=None):
        self.obj        = obj
        self.name       = name
        self.exportable = exportable          # True = has code to export
        self.children   = children or []     # list of NodeData


def build_tree(obj, depth=0):
    """
    Recursively build a NodeData tree from a CODESYS object.
    Skippable system nodes are included but marked non-exportable.
    """
    name       = get_name_safe(obj)
    exportable = is_exportable(obj)
    children   = []

    try:
        raw_children = obj.get_children(False)
    except Exception:
        raw_children = []

    for child in raw_children:
        child_node = build_tree(child, depth + 1)
        children.append(child_node)

    return NodeData(obj, name, exportable, children)


def build_controller_nodes(proj):
    """Return a list of NodeData for each Controller found in the project."""
    result = []
    try:
        top = proj.get_children(False)
    except Exception:
        return result

    for child in top:
        name = get_name_safe(child)
        if "Controller" in name:
            result.append(build_tree(child))

    return result


# ---------------------------------------------------------------------------
# 3.  CHECKLIST TREE DIALOG
# ---------------------------------------------------------------------------

# We use a standard TreeView with checkboxes.
# Each TreeNode's Tag holds the corresponding NodeData.

_suppress_check = [False]   # mutable flag to prevent recursive check events


def populate_tree_node(tree_node, node_data):
    """
    Recursively populate a WinForms TreeNode from a NodeData.
    Non-exportable, non-folder nodes are greyed out and unchecked.
    """
    has_exportable_descendant = node_data.exportable or any(
        child_has_exportable(c) for c in node_data.children
    )

    for child_data in node_data.children:
        child_node       = TreeNode(child_data.name)
        child_node.Tag   = child_data

        skippable = is_skippable(child_data.name)
        child_exportable = child_data.exportable
        child_has_desc   = child_has_exportable(child_data)

        if skippable or (not child_exportable and not child_has_desc):
            # Grey out -- not selectable
            child_node.ForeColor    = Color.Gray
            child_node.NodeFont     = Font("Segoe UI", 9, FontStyle.Italic)
            child_node.Checked      = False
            child_node.Tag          = None   # Tag=None means skip on export
        else:
            child_node.ForeColor = Color.Black

        tree_node.Nodes.Add(child_node)
        populate_tree_node(child_node, child_data)


def child_has_exportable(node_data):
    """Return True if node_data or any descendant is exportable."""
    if node_data.exportable:
        return True
    for child in node_data.children:
        if child_has_exportable(child):
            return True
    return False


def set_children_checked(tree_node, state):
    """Recursively set all children checkboxes to state (True/False)."""
    for i in range(tree_node.Nodes.Count):
        child = tree_node.Nodes[i]
        if child.Tag is not None:        # only selectable nodes
            child.Checked = state
        set_children_checked(child, state)


def on_after_check(sender, e):
    """Auto-check/uncheck children when a parent is toggled."""
    if _suppress_check[0]:
        return
    if e.Action == TreeViewAction.Unknown:
        return

    _suppress_check[0] = True
    try:
        set_children_checked(e.Node, e.Node.Checked)
    finally:
        _suppress_check[0] = False


def show_checklist_dialog(controller_nodes):
    """
    Build and show the checklist tree dialog.
    Returns list of selected NodeData objects, or None if cancelled.
    """
    form             = Form()
    form.Text        = "CODESYS Exporter -- Select items to export"
    form.Size        = Size(520, 580)
    form.FormBorderStyle = FormBorderStyle.FixedDialog
    form.StartPosition   = FormStartPosition.CenterScreen
    form.MaximizeBox     = False
    form.MinimizeBox     = False

    lbl          = Label()
    lbl.Text     = "Check items to export. Checking a folder selects all contents."
    lbl.Location = Point(12, 12)
    lbl.Size     = Size(490, 20)
    lbl.Font     = Font("Segoe UI", 9)
    form.Controls.Add(lbl)

    tv                  = TreeView()
    tv.Location         = Point(12, 38)
    tv.Size             = Size(480, 440)
    tv.CheckBoxes       = True
    tv.Font             = Font("Segoe UI", 9)
    tv.Scrollable       = True
    tv.AfterCheck      += on_after_check
    form.Controls.Add(tv)

    # Populate tree
    for ctrl_data in controller_nodes:
        ctrl_node          = TreeNode(ctrl_data.name)
        ctrl_node.Tag      = ctrl_data
        ctrl_node.NodeFont = Font("Segoe UI", 9, FontStyle.Bold)
        tv.Nodes.Add(ctrl_node)
        populate_tree_node(ctrl_node, ctrl_data)
        ctrl_node.Expand()

    btn_export          = Button()
    btn_export.Text     = "Export Selected"
    btn_export.Location = Point(300, 494)
    btn_export.Size     = Size(110, 30)
    btn_export.DialogResult = DialogResult.OK
    form.AcceptButton   = btn_export
    form.Controls.Add(btn_export)

    btn_cancel          = Button()
    btn_cancel.Text     = "Cancel"
    btn_cancel.Location = Point(420, 494)
    btn_cancel.Size     = Size(74, 30)
    btn_cancel.DialogResult = DialogResult.Cancel
    form.CancelButton   = btn_cancel
    form.Controls.Add(btn_cancel)

    result = form.ShowDialog()

    if result != DialogResult.OK:
        return None

    # Collect all checked selectable nodes
    selected = []
    collect_checked(tv.Nodes, selected)
    return selected


def collect_checked(nodes, selected):
    """Walk all TreeNodes and collect checked ones with valid Tag."""
    for i in range(nodes.Count):
        node = nodes[i]
        if node.Checked and node.Tag is not None:
            selected.append(node.Tag)
        collect_checked(node.Nodes, selected)


# ---------------------------------------------------------------------------
# 4.  EXPORT LOGIC
# ---------------------------------------------------------------------------

def export_object(obj, name, export_root):
    """Write declaration + implementation to <export_root>/<name>.st"""
    declaration    = get_declaration(obj).rstrip()
    implementation = get_implementation(obj).rstrip()

    parts = []
    if declaration:
        parts.append(declaration)
    if implementation:
        parts.append(implementation)

    if not parts:
        print("[skip] No content: " + name)
        return False

    makedirs_safe(export_root)

    file_path    = os.path.join(export_root, name + ".st")
    file_content = "\n\n".join(parts) + "\n"

    with open(file_path, "w") as f:
        if isinstance(file_content, unicode):
            f.write(file_content.encode("utf-8"))
        else:
            f.write(file_content)

    print("  Exported: " + file_path)
    return True


def get_controller_name(node_data):
    """
    Walk up the NodeData tree is not possible (no parent ref),
    so we derive the controller from the export root path instead.
    This is pre-set by the caller.
    """
    return node_data.name


def find_controller_of(node_data, controller_nodes):
    """Find which controller a given node_data belongs to."""
    for ctrl in controller_nodes:
        if node_contains(ctrl, node_data):
            return ctrl.name
    return "Unknown"


def node_contains(parent, target):
    if parent is target:
        return True
    for child in parent.children:
        if node_contains(child, target):
            return True
    return False


def build_path_to(node_data, controller_nodes, project_dir):
    """
    Build the export directory path for a node by tracing its ancestry
    through the controller_nodes tree.
    Returns (export_root, controller_name) tuple.
    """
    # Find the path from controller root down to node_data
    for ctrl in controller_nodes:
        path = find_path(ctrl, node_data, [])
        if path is not None:
            ctrl_name  = ctrl.name
            # path includes ctrl itself; skip it and system containers
            # (Plc Logic, Application, Application_1) that add no value
            skip_names = [ctrl_name, "Plc Logic", "Application", "Application_1"]
            folder_parts = [n.name for n in path if n.name not in skip_names]
            export_root  = os.path.join(project_dir, "Exports", ctrl_name, *folder_parts)
            return export_root, ctrl_name
    return os.path.join(project_dir, "Exports"), "Unknown"


def find_path(current, target, path):
    """Return list of NodeData from current to target, or None."""
    new_path = path + [current]
    if current is target:
        return new_path
    for child in current.children:
        result = find_path(child, target, new_path)
        if result is not None:
            return result
    return None


def run_export(selected_nodes, controller_nodes, project_dir):
    """Export all selected nodes."""
    exported = 0
    skipped  = 0

    # De-duplicate: if a parent folder AND its children are both checked,
    # we only need to export the leaf exportable objects once.
    # Since collect_checked walks all nodes, we may get both folder and
    # its children. We export only objects that have has_textual_declaration.

    exported_paths = set()

    for node_data in selected_nodes:
        if not node_data.exportable:
            # It is a folder/container -- its children are also in selected list
            continue

        export_root, ctrl_name = build_path_to(node_data, controller_nodes, project_dir)

        # Avoid exporting same object twice if parent + child both checked
        key = export_root + "|" + node_data.name
        if key in exported_paths:
            continue
        exported_paths.add(key)

        ok = export_object(node_data.obj, node_data.name, export_root)
        if ok:
            exported += 1
        else:
            skipped += 1

    return exported, skipped


# ---------------------------------------------------------------------------
# 5.  MAIN
# ---------------------------------------------------------------------------

def main():
    # --- Get open project ---
    try:
        proj         = projects.primary
        project_path = proj.path
        project_dir  = os.path.dirname(project_path)
    except Exception as e:
        MessageBox.Show(
            "No project is currently open.\n\n" + str(e),
            "CODESYS Exporter",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error
        )
        return

    print("=" * 60)
    print("CODESYS Exporter")
    print("Project: " + project_path)
    print("Scanning project tree...")

    # --- Scan project tree ---
    controller_nodes = build_controller_nodes(proj)

    if not controller_nodes:
        MessageBox.Show(
            "No Controllers found in the project.\nMake sure the project is fully loaded.",
            "CODESYS Exporter",
            MessageBoxButtons.OK,
            MessageBoxIcon.Warning
        )
        return

    print("Found " + str(len(controller_nodes)) + " controller(s).")

    # --- Show checklist dialog ---
    selected = show_checklist_dialog(controller_nodes)

    if selected is None:
        print("Export cancelled by user.")
        return

    if not selected:
        MessageBox.Show(
            "No items were selected.\nPlease check at least one item to export.",
            "CODESYS Exporter",
            MessageBoxButtons.OK,
            MessageBoxIcon.Warning
        )
        return

    print("Selected " + str(len(selected)) + " item(s) for export.")

    # --- Run export ---
    exported, skipped = run_export(selected, controller_nodes, project_dir)

    # --- Summary ---
    export_path = os.path.join(project_dir, "Exports")
    lines = []
    lines.append("Export complete!")
    lines.append("")
    lines.append("Files exported : " + str(exported))
    if skipped:
        lines.append("Skipped (empty): " + str(skipped))
    lines.append("")
    lines.append("Saved to:")
    lines.append(export_path)

    print("")
    print("\n".join(lines))

    MessageBox.Show(
        "\n".join(lines),
        "CODESYS Exporter",
        MessageBoxButtons.OK,
        MessageBoxIcon.Information
    )


main()