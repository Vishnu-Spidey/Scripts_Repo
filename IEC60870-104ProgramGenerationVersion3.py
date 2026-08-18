# -*- coding: utf-8 -*-
"""
CODESYS Scripting Engine -- IEC 60870-5-104 Server Configuration Generator
===========================================================================
Run inside CODESYS via: Tools > Scripting > Execute Script File

Compatible with: Python 2 (CODESYS / DIADesigner-AX scripting engine)
"""

import os
import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import (
    Form, Label, TextBox, Button, GroupBox,
    DialogResult, FormBorderStyle, FormStartPosition,
    MessageBox, MessageBoxButtons, MessageBoxIcon,
    FolderBrowserDialog, DataGridView, DataGridViewColumn,
    DataGridViewTextBoxColumn, DataGridViewSelectionMode,
    DataGridViewAutoSizeColumnsMode, ScrollBars,
    DataGridViewColumnHeadersHeightSizeMode,
    BorderStyle, Panel
)
from System.Drawing import Size, Point, Font, FontStyle, Color


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def make_label(text, x, y, w=170, h=22, bold=False):
    lbl          = Label()
    lbl.Text     = text
    lbl.Location = Point(x, y)
    lbl.Size     = Size(w, h)
    lbl.Font     = Font("Segoe UI", 9, FontStyle.Bold if bold else FontStyle.Regular)
    return lbl


def make_textbox(default, x, y, w=95):
    txt          = TextBox()
    txt.Text     = str(default)
    txt.Location = Point(x, y)
    txt.Size     = Size(w, 22)
    txt.Font     = Font("Segoe UI", 9)
    return txt


def on_numeric_keypress(sender, e):
    """Allow only digits and control keys (backspace, delete)."""
    if e.KeyChar not in "0123456789" and ord(e.KeyChar) not in (8, 127):
        e.Handled = True


def make_numeric_textbox(default, x, y, w=95):
    txt = make_textbox(default, x, y, w)
    txt.KeyPress += on_numeric_keypress
    return txt


def make_separator(parent, x, y, w):
    sep           = Label()
    sep.Text      = ""
    sep.Location  = Point(x, y)
    sep.Size      = Size(w, 1)
    sep.BackColor = Color.LightGray
    parent.Controls.Add(sep)


def make_plus_button(x, y):
    btn          = Button()
    btn.Text     = "+"
    btn.Location = Point(x, y)
    btn.Size     = Size(26, 22)
    btn.Font     = Font("Segoe UI", 9, FontStyle.Bold)
    return btn


# ---------------------------------------------------------------------------
# ASDU TABLE DIALOG
# ---------------------------------------------------------------------------

def show_asdu_table_dialog(asdu_name, existing_rows=None):
    """
    Opens the table dialog for a given ASDU type.
    Shows a DataGridView with columns: #, IOA, IValue, Description
    Supports inline editing and Ctrl+Click multiselect.
    Generate button prints data to console. Cancel closes.
    """

    DIALOG_W = 580
    DIALOG_H = 480

    dlg                 = Form()
    dlg.Text            = asdu_name
    dlg.Size            = Size(DIALOG_W, DIALOG_H)
    dlg.FormBorderStyle = FormBorderStyle.FixedDialog
    dlg.StartPosition   = FormStartPosition.CenterScreen
    dlg.MaximizeBox     = False
    dlg.MinimizeBox     = False

    GRP_W = DIALOG_W - 28

    # ------------------------------------------------------------------
    # Toolbar -- Add Row / Delete Selected
    # ------------------------------------------------------------------
    btn_add_row             = Button()
    btn_add_row.Text        = "Add Row"
    btn_add_row.Location    = Point(14, 12)
    btn_add_row.Size        = Size(80, 26)
    btn_add_row.Font        = Font("Segoe UI", 9)
    dlg.Controls.Add(btn_add_row)

    btn_del_row             = Button()
    btn_del_row.Text        = "Delete Selected"
    btn_del_row.Location    = Point(102, 12)
    btn_del_row.Size        = Size(110, 26)
    btn_del_row.Font        = Font("Segoe UI", 9)
    dlg.Controls.Add(btn_del_row)

    # ------------------------------------------------------------------
    # DataGridView
    # ------------------------------------------------------------------
    grid                        = DataGridView()
    grid.Location               = Point(8, 46)
    grid.Size                   = Size(DIALOG_W - 18, DIALOG_H - 140)
    grid.Font                   = Font("Segoe UI", 9)
    grid.SelectionMode          = DataGridViewSelectionMode.CellSelect
    grid.MultiSelect            = True
    grid.AllowUserToAddRows     = False
    grid.AllowUserToDeleteRows  = False
    grid.RowHeadersVisible      = False
    grid.AutoSizeColumnsMode    = DataGridViewAutoSizeColumnsMode.Fill
    grid.ScrollBars             = ScrollBars.Vertical
    grid.BorderStyle            = BorderStyle.FixedSingle
    grid.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.DisableResizing
    grid.ColumnHeadersHeight    = 30
    grid.BackgroundColor        = Color.White
    grid.GridColor              = Color.LightGray

    # Header style -- dark grey
    grid.ColumnHeadersDefaultCellStyle.BackColor  = Color.FromArgb(64, 64, 64)
    grid.ColumnHeadersDefaultCellStyle.ForeColor  = Color.White
    grid.ColumnHeadersDefaultCellStyle.Font       = Font("Segoe UI", 9, FontStyle.Bold)
    grid.ColumnHeadersDefaultCellStyle.Alignment  = getattr(
        __import__("System.Windows.Forms", fromlist=["DataGridViewContentAlignment"]),
        "DataGridViewContentAlignment").MiddleCenter
    grid.EnableHeadersVisualStyles = False

    # Alternating row colour for readability
    grid.AlternatingRowsDefaultCellStyle.BackColor = Color.FromArgb(245, 245, 245)

    # Columns: #, IOA, IValue, Description
    col_no              = DataGridViewTextBoxColumn()
    col_no.HeaderText   = "#"
    col_no.Name         = "No"
    col_no.ReadOnly     = True
    col_no.FillWeight   = 20
    col_no.DefaultCellStyle.Alignment = getattr(
        __import__("System.Windows.Forms", fromlist=["DataGridViewContentAlignment"]),
        "DataGridViewContentAlignment").MiddleCenter
    grid.Columns.Add(col_no)

    col_ioa             = DataGridViewTextBoxColumn()
    col_ioa.HeaderText  = "IOA"
    col_ioa.Name        = "IOA"
    col_ioa.FillWeight  = 60
    grid.Columns.Add(col_ioa)

    col_ival            = DataGridViewTextBoxColumn()
    col_ival.HeaderText = "IValue"
    col_ival.Name       = "IValue"
    col_ival.FillWeight = 60
    grid.Columns.Add(col_ival)

    col_desc              = DataGridViewTextBoxColumn()
    col_desc.HeaderText   = "Description"
    col_desc.Name         = "Description"
    col_desc.FillWeight   = 260
    col_desc.MinimumWidth = 160
    grid.Columns.Add(col_desc)

    dlg.Controls.Add(grid)

    # ------------------------------------------------------------------
    # Same-column multi-cell edit logic
    # When user finishes editing a cell, if multiple cells in the SAME
    # column are selected, apply the new value to all of them.
    # If selection spans multiple columns, block and warn.
    # ------------------------------------------------------------------

    def on_cell_validated(sender, e):
        """After a cell is edited, propagate value to all selected cells in same column."""
        edited_col = grid.CurrentCell.ColumnIndex if grid.CurrentCell else -1
        if edited_col <= 0:   # skip # column (index 0)
            return

        selected = list(grid.SelectedCells)
        if len(selected) <= 1:
            return

        # Check if all selected cells are in the same column
        col_indices = set()
        for cell in selected:
            col_indices.add(cell.ColumnIndex)

        if len(col_indices) > 1:
            # Mixed columns selected -- deselect and warn
            grid.ClearSelection()
            grid.CurrentCell.Selected = True
            MessageBox.Show(
                "Multi-edit only works within the same column.\nPlease select cells from one column only.",
                "Selection Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning
            )
            return

        # All same column -- apply current cell value to all selected
        new_value = grid.CurrentCell.Value
        for cell in selected:
            if cell.RowIndex != grid.CurrentCell.RowIndex:
                if not cell.ReadOnly and cell.ColumnIndex != 0:
                    cell.Value = new_value

    def on_selection_changed(sender, e):
        """Block cross-column selection visually by deselecting mismatched cells."""
        selected = list(grid.SelectedCells)
        if len(selected) <= 1:
            return

        # Find the anchor column (the current cell's column)
        anchor_col = grid.CurrentCell.ColumnIndex if grid.CurrentCell else -1
        if anchor_col < 0:
            return

        # Deselect any cell not in the anchor column
        for cell in selected:
            if cell.ColumnIndex != anchor_col:
                cell.Selected = False

    grid.CellValidated      += on_cell_validated
    grid.SelectionChanged   += on_selection_changed

    # ------------------------------------------------------------------
    # Populate rows -- restore saved data or start with 5 empty rows
    # ------------------------------------------------------------------
    def renumber_rows():
        for i in range(grid.Rows.Count):
            grid.Rows[i].Cells["No"].Value = str(i + 1)

    if existing_rows and len(existing_rows) > 0:
        for r in existing_rows:
            grid.Rows.Add(r["No"], r["IOA"], r["IValue"], r["Description"])
    else:
        for i in range(5):
            grid.Rows.Add(str(i + 1), "", "", "")

    # ------------------------------------------------------------------
    # Button events
    # ------------------------------------------------------------------
    def on_add_row(sender, e):
        # Find the lowest selected row index
        selected = list(grid.SelectedCells)
        if selected:
            insert_after = max([cell.RowIndex for cell in selected])
            insert_at    = insert_after + 1
        else:
            insert_at    = grid.Rows.Count

        grid.Rows.Insert(insert_at, "", "", "", "")
        renumber_rows()

    def on_delete_selected(sender, e):
        # Collect unique row indices from selected cells
        selected_indices = list(set([cell.RowIndex for cell in grid.SelectedCells]))
        selected_indices.sort(reverse=True)
        for idx in selected_indices:
            grid.Rows.RemoveAt(idx)
        renumber_rows()

    btn_add_row.Click  += on_add_row
    btn_del_row.Click  += on_delete_selected

    # ------------------------------------------------------------------
    # Click outside cells to clear selection
    # ------------------------------------------------------------------
    def on_grid_click(sender, e):
        hit = grid.HitTest(e.X, e.Y)
        from System.Windows.Forms import DataGridViewHitTestType
        if hit.Type == DataGridViewHitTestType.None:
            grid.ClearSelection()
            grid.CurrentCell = None

    def on_dialog_click(sender, e):
        grid.ClearSelection()
        try:
            grid.CurrentCell = None
        except Exception:
            pass

    grid.Click  += on_grid_click
    dlg.Click   += on_dialog_click

    # ------------------------------------------------------------------
    # Bottom buttons: Generate / Cancel
    # ------------------------------------------------------------------
    sep_y = dlg.Size.Height - 90
    make_separator(dlg, 14, sep_y, DIALOG_W - 28)

    btn_generate              = Button()
    btn_generate.Text         = "Generate"
    btn_generate.Location     = Point(DIALOG_W - 210, sep_y + 12)
    btn_generate.Size         = Size(90, 30)
    btn_generate.Font         = Font("Segoe UI", 9, FontStyle.Bold)
    btn_generate.DialogResult = DialogResult.OK
    dlg.AcceptButton          = btn_generate
    dlg.Controls.Add(btn_generate)

    btn_cancel              = Button()
    btn_cancel.Text         = "Cancel"
    btn_cancel.Location     = Point(DIALOG_W - 110, sep_y + 12)
    btn_cancel.Size         = Size(78, 30)
    btn_cancel.DialogResult = DialogResult.Cancel
    dlg.CancelButton        = btn_cancel
    dlg.Controls.Add(btn_cancel)

    result = dlg.ShowDialog()

    if result != DialogResult.OK:
        return None

    # Collect rows into a list of dicts
    rows = []
    for i in range(grid.Rows.Count):
        row = grid.Rows[i]
        rows.append({
            "No"          : str(i + 1),
            "IOA"         : str(row.Cells["IOA"].Value or ""),
            "IValue"      : str(row.Cells["IValue"].Value or ""),
            "Description" : str(row.Cells["Description"].Value or ""),
        })
    return rows


# ---------------------------------------------------------------------------
# MAIN CONFIG DIALOG
# ---------------------------------------------------------------------------

def show_config_dialog():

    FORM_W = 720

    form                 = Form()
    form.Text            = "IEC-104 Configurator"
    form.Size            = Size(FORM_W, 300)
    form.FormBorderStyle = FormBorderStyle.FixedDialog
    form.StartPosition   = FormStartPosition.CenterScreen
    form.MaximizeBox     = False
    form.MinimizeBox     = False

    GRP_W  = FORM_W - 34

    LBL1_X = 14
    VAL1_X = 185
    TXT_W  = 95
    LBL2_X = 322
    VAL2_X = 502
    ROW_H  = 34

    # ------------------------------------------------------------------
    # GROUP: Server Configuration
    # ------------------------------------------------------------------
    grp_srv           = GroupBox()
    grp_srv.Text      = "Server Configuration"
    grp_srv.Font      = Font("Segoe UI", 9, FontStyle.Bold)
    grp_srv.Location  = Point(12, 10)
    grp_srv.Size      = Size(GRP_W, 220)
    form.Controls.Add(grp_srv)

    gy = 26

    # Row 1: K | W
    grp_srv.Controls.Add(make_label("K  (max unacknowledged):", LBL1_X, gy, w=168))
    txt_k = make_numeric_textbox("12", VAL1_X, gy, TXT_W)
    grp_srv.Controls.Add(txt_k)
    grp_srv.Controls.Add(make_label("W  (latest ACK after W):", LBL2_X, gy, w=168))
    txt_w = make_numeric_textbox("8", VAL2_X, gy, TXT_W)
    grp_srv.Controls.Add(txt_w)
    gy += ROW_H

    # Row 2: T0 | T1
    grp_srv.Controls.Add(make_label("T0  (connection timeout s):", LBL1_X, gy, w=168))
    txt_t0 = make_numeric_textbox("10", VAL1_X, gy, TXT_W)
    grp_srv.Controls.Add(txt_t0)
    grp_srv.Controls.Add(make_label("T1  (APDU send timeout s):", LBL2_X, gy, w=168))
    txt_t1 = make_numeric_textbox("15", VAL2_X, gy, TXT_W)
    grp_srv.Controls.Add(txt_t1)
    gy += ROW_H

    # Row 3: T2 | T3
    grp_srv.Controls.Add(make_label("T2  (ACK timeout s):", LBL1_X, gy, w=168))
    txt_t2 = make_numeric_textbox("10", VAL1_X, gy, TXT_W)
    grp_srv.Controls.Add(txt_t2)
    grp_srv.Controls.Add(make_label("T3  (idle timeout s):", LBL2_X, gy, w=168))
    txt_t3 = make_numeric_textbox("20", VAL2_X, gy, TXT_W)
    grp_srv.Controls.Add(txt_t3)
    gy += ROW_H

    # Row 4: Source IP | Port
    grp_srv.Controls.Add(make_label("Source IP:", LBL1_X, gy, w=168))
    txt_ip = make_textbox("0.0.0.0", VAL1_X, gy, TXT_W)
    grp_srv.Controls.Add(txt_ip)
    grp_srv.Controls.Add(make_label("Port:", LBL2_X, gy, w=168))
    txt_port = make_numeric_textbox("2404", VAL2_X, gy, TXT_W)
    grp_srv.Controls.Add(txt_port)
    gy += ROW_H

    grp_srv.Size = Size(GRP_W, gy + 14)

    # ------------------------------------------------------------------
    # GROUP: ASDU Types
    # ------------------------------------------------------------------
    asdu_y            = grp_srv.Location.Y + grp_srv.Size.Height + 12
    grp_asdu          = GroupBox()
    grp_asdu.Text     = "ASDU Types"
    grp_asdu.Font     = Font("Segoe UI", 9, FontStyle.Bold)
    grp_asdu.Location = Point(12, asdu_y)
    grp_asdu.Size     = Size(GRP_W, 100)
    form.Controls.Add(grp_asdu)

    # Column positions inside ASDU group
    COL_TYPE  = 14
    COL_PLUS  = 490   # [+] button
    COL_CNT   = 524   # count textbox
    ASDU_TW   = 95
    ay        = 26

    # Column headers
    grp_asdu.Controls.Add(make_label("ASDU Type",        COL_TYPE, ay, w=470, bold=True))
    grp_asdu.Controls.Add(make_label("Count of Objects", COL_CNT,  ay, w=130, bold=True))
    ay += 24

    make_separator(grp_asdu, 14, ay, GRP_W - 28)
    ay += 8

    # Storage for table data keyed by ASDU name
    table_data = {}

    def make_asdu_row(name, ay_pos):
        """Create one ASDU row with label, [+] button and count textbox."""
        grp_asdu.Controls.Add(make_label(name, COL_TYPE, ay_pos, w=470))

        btn_plus = make_plus_button(COL_PLUS, ay_pos)
        grp_asdu.Controls.Add(btn_plus)

        txt_cnt = make_numeric_textbox("0", COL_CNT, ay_pos, ASDU_TW)
        grp_asdu.Controls.Add(txt_cnt)

        # Closure to capture name
        asdu_name_ref = [name]
        def on_plus_click(sender, e, n=asdu_name_ref):
            existing = table_data.get(n[0], None)
            rows = show_asdu_table_dialog(n[0], existing_rows=existing)
            if rows is not None:
                table_data[n[0]] = rows
                # Print summary to console
                print("")
                print("=== " + n[0] + " ===")
                print("{:<6} {:<12} {:<12} {}".format("#", "IOA", "IValue", "Description"))
                print("-" * 50)
                for r in rows:
                    print("{:<6} {:<12} {:<12} {}".format(
                        r["No"], r["IOA"], r["IValue"], r["Description"]
                    ))

        btn_plus.Click += on_plus_click
        return txt_cnt

    # --- Single-point Information ---
    txt_sp    = make_asdu_row("Single-point Information",            ay)
    ay += ROW_H
    txt_sp_cp = make_asdu_row("Single-point Information (CP56Time2a)", ay)
    ay += ROW_H

    make_separator(grp_asdu, 14, ay, GRP_W - 28)
    ay += 8

    # --- Double-point Information ---
    txt_dp    = make_asdu_row("Double-point Information",            ay)
    ay += ROW_H
    txt_dp_cp = make_asdu_row("Double-point Information (CP56Time2a)", ay)
    ay += ROW_H

    make_separator(grp_asdu, 14, ay, GRP_W - 28)
    ay += 8

    # --- Measured Value ---
    txt_mv    = make_asdu_row("Measured Value",            ay)
    ay += ROW_H
    txt_mv_cp = make_asdu_row("Measured Value (CP56Time2a)", ay)
    ay += 16

    grp_asdu.Size = Size(GRP_W, ay + 14)

    # ------------------------------------------------------------------
    # Bottom buttons
    # ------------------------------------------------------------------
    btn_y = grp_asdu.Location.Y + grp_asdu.Size.Height + 14

    btn_ok              = Button()
    btn_ok.Text         = "Generate Config"
    btn_ok.Location     = Point(FORM_W - 230, btn_y)
    btn_ok.Size         = Size(130, 32)
    btn_ok.Font         = Font("Segoe UI", 9, FontStyle.Bold)
    btn_ok.DialogResult = DialogResult.OK
    form.AcceptButton   = btn_ok
    form.Controls.Add(btn_ok)

    btn_cancel              = Button()
    btn_cancel.Text         = "Cancel"
    btn_cancel.Location     = Point(FORM_W - 90, btn_y)
    btn_cancel.Size         = Size(78, 32)
    btn_cancel.DialogResult = DialogResult.Cancel
    form.CancelButton       = btn_cancel
    form.Controls.Add(btn_cancel)

    form.Size = Size(FORM_W, btn_y + 80)

    result = form.ShowDialog()
    if result != DialogResult.OK:
        return None

    return {
        "K"                               : txt_k.Text.strip(),
        "W"                               : txt_w.Text.strip(),
        "T0"                              : txt_t0.Text.strip(),
        "T1"                              : txt_t1.Text.strip(),
        "T2"                              : txt_t2.Text.strip(),
        "T3"                              : txt_t3.Text.strip(),
        "SourceIP"                        : txt_ip.Text.strip(),
        "Port"                            : txt_port.Text.strip(),
        "SinglePointInformation"          : txt_sp.Text.strip(),
        "SinglePointInformation_CP56"     : txt_sp_cp.Text.strip(),
        "DoublePointInformation"          : txt_dp.Text.strip(),
        "DoublePointInformation_CP56"     : txt_dp_cp.Text.strip(),
        "MeasuredValue"                   : txt_mv.Text.strip(),
        "MeasuredValue_CP56"              : txt_mv_cp.Text.strip(),
        "TableData"                       : table_data,
    }


# ---------------------------------------------------------------------------
# FOLDER BROWSER
# ---------------------------------------------------------------------------

def ask_save_folder():
    dlg             = FolderBrowserDialog()
    dlg.Description = "Select folder to save IEC104_ServerConfig.ini"
    try:
        proj = projects.primary
        dlg.SelectedPath = os.path.dirname(proj.path)
    except Exception:
        pass
    from System.Windows.Forms import DialogResult as DR
    if dlg.ShowDialog() == DR.OK:
        return dlg.SelectedPath
    return None


# ---------------------------------------------------------------------------
# GENERATE INI
# ---------------------------------------------------------------------------

def generate_ini(cfg):
    lines = []
    lines.append("; IEC 60870-5-104 Server Configuration")
    lines.append("; Generated by CODESYS IEC104 Config Script")
    lines.append("")
    lines.append("[ServerConfiguration]")
    lines.append("K  = " + cfg["K"])
    lines.append("W  = " + cfg["W"])
    lines.append("T0 = " + cfg["T0"])
    lines.append("T1 = " + cfg["T1"])
    lines.append("T2 = " + cfg["T2"])
    lines.append("T3 = " + cfg["T3"])
    lines.append("")
    lines.append("[NetworkConfiguration]")
    lines.append("SourceIP = " + cfg["SourceIP"])
    lines.append("Port     = " + cfg["Port"])
    lines.append("")
    lines.append("[ASDUTypes]")
    lines.append("")
    lines.append("[SinglePointInformation]")
    lines.append("Count      = " + cfg["SinglePointInformation"])
    lines.append("Count_CP56 = " + cfg["SinglePointInformation_CP56"])
    lines.append("")
    lines.append("[DoublePointInformation]")
    lines.append("Count      = " + cfg["DoublePointInformation"])
    lines.append("Count_CP56 = " + cfg["DoublePointInformation_CP56"])
    lines.append("")
    lines.append("[MeasuredValue]")
    lines.append("Count      = " + cfg["MeasuredValue"])
    lines.append("Count_CP56 = " + cfg["MeasuredValue_CP56"])
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    cfg = show_config_dialog()
    if cfg is None:
        print("Configuration cancelled by user.")
        return

    save_folder = ask_save_folder()
    if save_folder is None:
        print("Save location not selected. Cancelled.")
        return

    ini_content = generate_ini(cfg)

    file_path = os.path.join(save_folder, "IEC104_ServerConfig.ini")
    with open(file_path, "w") as f:
        f.write(ini_content)

    print("=" * 60)
    print("IEC 60870-5-104 Server Configuration")
    print("=" * 60)
    print(ini_content)
    print("=" * 60)
    print("Saved to: " + file_path)
    print("=" * 60)

    MessageBox.Show(
        "Configuration saved successfully!\n\n" + file_path,
        "IEC104 Config Generator",
        MessageBoxButtons.OK,
        MessageBoxIcon.Information
    )


main()