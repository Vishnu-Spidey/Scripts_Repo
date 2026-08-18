# -*- coding: utf-8 -*-
"""
CODESYS Scripting Engine -- IEC 60870-5-104 Server Configuration Generator
===========================================================================
Run inside CODESYS via: Tools > Scripting > Execute Script File

Behaviour:
  - Shows a dialog with all IEC 104 server configuration fields
  - Generates IEC104_ServerConfig.ini in a folder you choose
  - Prints the full config to the CODESYS scripting console

Compatible with: Python 2 (CODESYS / DIADesigner-AX scripting engine)
"""

import os
import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import (
    Form, Label, TextBox, Button, CheckBox, GroupBox,
    DialogResult, FormBorderStyle, FormStartPosition,
    MessageBox, MessageBoxButtons, MessageBoxIcon,
    FolderBrowserDialog, Panel, ScrollBars
)
from System.Drawing import Size, Point, Font, FontStyle, Color


# ---------------------------------------------------------------------------
# 1.  CONFIG DIALOG
# ---------------------------------------------------------------------------

def make_label(text, x, y, w=160, h=22, bold=False):
    lbl          = Label()
    lbl.Text     = text
    lbl.Location = Point(x, y)
    lbl.Size     = Size(w, h)
    style        = FontStyle.Bold if bold else FontStyle.Regular
    lbl.Font     = Font("Segoe UI", 9, style)
    return lbl


def make_textbox(default, x, y, w=80):
    txt          = TextBox()
    txt.Text     = str(default)
    txt.Location = Point(x, y)
    txt.Size     = Size(w, 22)
    txt.Font     = Font("Segoe UI", 9)
    return txt


def show_config_dialog():
    """
    Show the IEC 104 configuration dialog.
    Returns a dict of all values, or None if cancelled.
    """

    form             = Form()
    form.Text        = "IEC-104 Configurator"
    form.Size        = Size(540, 620)
    form.FormBorderStyle = FormBorderStyle.FixedDialog
    form.StartPosition   = FormStartPosition.CenterScreen
    form.MaximizeBox     = False
    form.MinimizeBox     = False

    y = 12  # running vertical position

    # ------------------------------------------------------------------
    # GROUP: Server Configuration
    # ------------------------------------------------------------------
    grp_server          = GroupBox()
    grp_server.Text     = "Server Configuration"
    grp_server.Font     = Font("Segoe UI", 9, FontStyle.Bold)
    grp_server.Location = Point(12, y)
    grp_server.Size     = Size(498, 210)
    form.Controls.Add(grp_server)

    col_lbl = 12
    col_val = 180
    col_lbl2 = 280
    col_val2 = 420
    gy = 24  # y inside group

    # Row 1 -- K and W
    grp_server.Controls.Add(make_label("K  (max unacknowledged):", col_lbl,  gy))
    txt_k = make_textbox("12", col_val, gy)
    grp_server.Controls.Add(txt_k)

    grp_server.Controls.Add(make_label("W  (latest ACK after W):", col_lbl2, gy))
    txt_w = make_textbox("8", col_val2, gy)
    grp_server.Controls.Add(txt_w)
    gy += 34

    # Row 2 -- T0 and T1
    grp_server.Controls.Add(make_label("T0  (connection timeout s):", col_lbl,  gy))
    txt_t0 = make_textbox("10", col_val, gy)
    grp_server.Controls.Add(txt_t0)

    grp_server.Controls.Add(make_label("T1  (APDU send timeout s):", col_lbl2, gy))
    txt_t1 = make_textbox("15", col_val2, gy)
    grp_server.Controls.Add(txt_t1)
    gy += 34

    # Row 3 -- T2 and T3
    grp_server.Controls.Add(make_label("T2  (ACK timeout s):", col_lbl,  gy))
    txt_t2 = make_textbox("10", col_val, gy)
    grp_server.Controls.Add(txt_t2)

    grp_server.Controls.Add(make_label("T3  (idle timeout s):", col_lbl2, gy))
    txt_t3 = make_textbox("20", col_val2, gy)
    grp_server.Controls.Add(txt_t3)
    gy += 34

    # Row 4 -- Source IP and Port
    grp_server.Controls.Add(make_label("Source IP:", col_lbl,  gy))
    txt_ip = make_textbox("0.0.0.0", col_val, gy, w=120)
    grp_server.Controls.Add(txt_ip)

    grp_server.Controls.Add(make_label("Port:", col_lbl2, gy))
    txt_port = make_textbox("2404", col_val2, gy)
    grp_server.Controls.Add(txt_port)
    gy += 34

    # Row 5 -- groupbox height adjustment done
    grp_server.Size = Size(498, gy + 16)

    y += gy + 28

    # ------------------------------------------------------------------
    # GROUP: ASDU Types
    # ------------------------------------------------------------------
    grp_asdu          = GroupBox()
    grp_asdu.Text     = "ASDU Types"
    grp_asdu.Font     = Font("Segoe UI", 9, FontStyle.Bold)
    grp_asdu.Location = Point(12, y)
    grp_asdu.Size     = Size(498, 190)
    form.Controls.Add(grp_asdu)

    ay = 24  # y inside ASDU group

    # CP56Time2a checkbox (applies to all types)
    chk_time          = CheckBox()
    chk_time.Text     = "Time included (CP56Time2a)"
    chk_time.Location = Point(12, ay)
    chk_time.Size     = Size(300, 22)
    chk_time.Font     = Font("Segoe UI", 9)
    chk_time.Checked  = False
    grp_asdu.Controls.Add(chk_time)
    ay += 32

    # Header row
    grp_asdu.Controls.Add(make_label("ASDU Type",         12,  ay, w=220))
    grp_asdu.Controls.Add(make_label("Count of Objects",  340, ay, w=140))
    ay += 22

    # Divider line via label
    div          = Label()
    div.Text     = ""
    div.Location = Point(12, ay)
    div.Size     = Size(470, 1)
    div.BorderStyle = getattr(__import__("System.Windows.Forms", fromlist=["BorderStyle"]), "BorderStyle").FixedSingle
    grp_asdu.Controls.Add(div)
    ay += 6

    # Single-point Information
    grp_asdu.Controls.Add(make_label("Single-point Information", 12, ay, w=300))
    txt_sp = make_textbox("0", 340, ay)
    grp_asdu.Controls.Add(txt_sp)
    ay += 32

    # Double-point Information
    grp_asdu.Controls.Add(make_label("Double-point Information", 12, ay, w=300))
    txt_dp = make_textbox("0", 340, ay)
    grp_asdu.Controls.Add(txt_dp)
    ay += 32

    # Measured Value
    grp_asdu.Controls.Add(make_label("Measured Value",           12, ay, w=300))
    txt_mv = make_textbox("0", 340, ay)
    grp_asdu.Controls.Add(txt_mv)
    ay += 16

    grp_asdu.Size = Size(498, ay + 16)
    y += ay + 28

    # ------------------------------------------------------------------
    # Buttons
    # ------------------------------------------------------------------
    btn_ok          = Button()
    btn_ok.Text     = "Generate Config"
    btn_ok.Location = Point(300, y)
    btn_ok.Size     = Size(120, 32)
    btn_ok.DialogResult = DialogResult.OK
    btn_ok.Font     = Font("Segoe UI", 9, FontStyle.Bold)
    form.AcceptButton = btn_ok
    form.Controls.Add(btn_ok)

    btn_cancel          = Button()
    btn_cancel.Text     = "Cancel"
    btn_cancel.Location = Point(430, y)
    btn_cancel.Size     = Size(74, 32)
    btn_cancel.DialogResult = DialogResult.Cancel
    form.CancelButton   = btn_cancel
    form.Controls.Add(btn_cancel)

    # Resize form to fit content
    form.Size = Size(540, y + 80)

    result = form.ShowDialog()

    if result != DialogResult.OK:
        return None

    return {
        "K"                        : txt_k.Text.strip(),
        "W"                        : txt_w.Text.strip(),
        "T0"                       : txt_t0.Text.strip(),
        "T1"                       : txt_t1.Text.strip(),
        "T2"                       : txt_t2.Text.strip(),
        "T3"                       : txt_t3.Text.strip(),
        "SourceIP"                 : txt_ip.Text.strip(),
        "Port"                     : txt_port.Text.strip(),
        "CP56Time2a"               : str(chk_time.Checked),
        "SinglePointInformation"   : txt_sp.Text.strip(),
        "DoublePointInformation"   : txt_dp.Text.strip(),
        "MeasuredValue"            : txt_mv.Text.strip(),
    }


# ---------------------------------------------------------------------------
# 2.  FOLDER BROWSER
# ---------------------------------------------------------------------------

def ask_save_folder():
    """Ask the user where to save the .ini file. Returns folder path or None."""
    dlg             = FolderBrowserDialog()
    dlg.Description = "Select folder to save IEC104_ServerConfig.ini"

    # Try to default to project folder
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
# 3.  GENERATE INI FILE
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
    lines.append("CP56Time2a             = " + cfg["CP56Time2a"])
    lines.append("")
    lines.append("SinglePointInformation = " + cfg["SinglePointInformation"])
    lines.append("DoublePointInformation = " + cfg["DoublePointInformation"])
    lines.append("MeasuredValue          = " + cfg["MeasuredValue"])
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4.  MAIN
# ---------------------------------------------------------------------------

def main():
    # --- Show config dialog ---
    cfg = show_config_dialog()
    if cfg is None:
        print("Configuration cancelled by user.")
        return

    # --- Ask where to save ---
    save_folder = ask_save_folder()
    if save_folder is None:
        print("Save location not selected. Cancelled.")
        return

    # --- Generate ini content ---
    ini_content = generate_ini(cfg)

    # --- Save to file ---
    file_path = os.path.join(save_folder, "IEC104_ServerConfig.ini")
    with open(file_path, "w") as f:
        f.write(ini_content)

    # --- Print to CODESYS console ---
    print("=" * 60)
    print("IEC 60870-5-104 Server Configuration")
    print("=" * 60)
    print(ini_content)
    print("=" * 60)
    print("Saved to: " + file_path)
    print("=" * 60)

    # --- Summary dialog ---
    MessageBox.Show(
        "Configuration saved successfully!\n\n" + file_path,
        "IEC104 Config Generator",
        MessageBoxButtons.OK,
        MessageBoxIcon.Information
    )


main()