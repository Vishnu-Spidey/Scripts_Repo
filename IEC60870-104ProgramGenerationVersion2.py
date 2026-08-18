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
    FolderBrowserDialog
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
    """Allow only digits and control keys (backspace, delete, arrows)."""
    allowed = "0123456789"
    if e.KeyChar not in allowed and ord(e.KeyChar) not in (8, 127):
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


# ---------------------------------------------------------------------------
# CONFIG DIALOG
# ---------------------------------------------------------------------------

def show_config_dialog():

    FORM_W = 660

    form                 = Form()
    form.Text            = "IEC-104 Configurator"
    form.Size            = Size(FORM_W, 300)
    form.FormBorderStyle = FormBorderStyle.FixedDialog
    form.StartPosition   = FormStartPosition.CenterScreen
    form.MaximizeBox     = False
    form.MinimizeBox     = False

    GRP_W  = FORM_W - 34

    # Left column
    LBL1_X = 14
    VAL1_X = 185
    TXT_W  = 95

    # Right column
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
    grp_asdu.Text     = "ASDU Configuration"
    grp_asdu.Font     = Font("Segoe UI", 9, FontStyle.Bold)
    grp_asdu.Location = Point(12, asdu_y)
    grp_asdu.Size     = Size(GRP_W, 100)   # resized below
    form.Controls.Add(grp_asdu)

    COL_TYPE  = 14
    COL_CNT   = 480
    ASDU_TW   = 95
    ay        = 26

    # Column headers
    grp_asdu.Controls.Add(make_label("ASDU Type",        COL_TYPE, ay, w=440, bold=True))
    grp_asdu.Controls.Add(make_label("Count of Objects", COL_CNT,  ay, w=130, bold=True))
    ay += 24

    # Header separator
    make_separator(grp_asdu, 14, ay, GRP_W - 28)
    ay += 8

    # --- Single-point Information ---
    grp_asdu.Controls.Add(make_label("Single-point Information",            COL_TYPE, ay, w=440))
    txt_sp = make_numeric_textbox("0", COL_CNT, ay, ASDU_TW)
    grp_asdu.Controls.Add(txt_sp)
    ay += ROW_H

    grp_asdu.Controls.Add(make_label("Single-point Information (CP56Time2a)", COL_TYPE, ay, w=440))
    txt_sp_cp = make_numeric_textbox("0", COL_CNT, ay, ASDU_TW)
    grp_asdu.Controls.Add(txt_sp_cp)
    ay += ROW_H

    # Separator between types
    make_separator(grp_asdu, 14, ay, GRP_W - 28)
    ay += 8

    # --- Double-point Information ---
    grp_asdu.Controls.Add(make_label("Double-point Information",            COL_TYPE, ay, w=440))
    txt_dp = make_numeric_textbox("0", COL_CNT, ay, ASDU_TW)
    grp_asdu.Controls.Add(txt_dp)
    ay += ROW_H

    grp_asdu.Controls.Add(make_label("Double-point Information (CP56Time2a)", COL_TYPE, ay, w=440))
    txt_dp_cp = make_numeric_textbox("0", COL_CNT, ay, ASDU_TW)
    grp_asdu.Controls.Add(txt_dp_cp)
    ay += ROW_H

    # Separator between types
    make_separator(grp_asdu, 14, ay, GRP_W - 28)
    ay += 8

    # --- Measured Value ---
    grp_asdu.Controls.Add(make_label("Measured Value",            COL_TYPE, ay, w=440))
    txt_mv = make_numeric_textbox("0", COL_CNT, ay, ASDU_TW)
    grp_asdu.Controls.Add(txt_mv)
    ay += ROW_H

    grp_asdu.Controls.Add(make_label("Measured Value (CP56Time2a)", COL_TYPE, ay, w=440))
    txt_mv_cp = make_numeric_textbox("0", COL_CNT, ay, ASDU_TW)
    grp_asdu.Controls.Add(txt_mv_cp)
    ay += 16

    grp_asdu.Size = Size(GRP_W, ay + 14)

    # ------------------------------------------------------------------
    # Buttons
    # ------------------------------------------------------------------
    btn_y = grp_asdu.Location.Y + grp_asdu.Size.Height + 14

    btn_ok              = Button()
    btn_ok.Text         = "Generate Config"
    btn_ok.Location     = Point(FORM_W - 260, btn_y)
    btn_ok.Size         = Size(130, 32)
    btn_ok.Font         = Font("Segoe UI", 9, FontStyle.Bold)
    btn_ok.DialogResult = DialogResult.OK
    form.AcceptButton   = btn_ok
    form.Controls.Add(btn_ok)

    btn_cancel              = Button()
    btn_cancel.Text         = "Cancel"
    btn_cancel.Location     = Point(FORM_W - 120, btn_y)
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
    lines.append("Count          = " + cfg["SinglePointInformation"])
    lines.append("Count_CP56     = " + cfg["SinglePointInformation_CP56"])
    lines.append("")
    lines.append("[DoublePointInformation]")
    lines.append("Count          = " + cfg["DoublePointInformation"])
    lines.append("Count_CP56     = " + cfg["DoublePointInformation_CP56"])
    lines.append("")
    lines.append("[MeasuredValue]")
    lines.append("Count          = " + cfg["MeasuredValue"])
    lines.append("Count_CP56     = " + cfg["MeasuredValue_CP56"])
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