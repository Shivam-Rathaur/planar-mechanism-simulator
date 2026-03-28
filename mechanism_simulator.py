

import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QDoubleSpinBox, QComboBox, QPushButton, QFrame,
    QTabWidget, QSlider, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl

## Global Matplotlib dark theme
mpl.rcParams.update({
    'figure.facecolor':  '#0d1117',
    'axes.facecolor':    '#161b22',
    'axes.edgecolor':    '#30363d',
    'text.color':        '#e6edf3',
    'axes.labelcolor':   '#e6edf3',
    'xtick.color':       '#e6edf3',
    'ytick.color':       '#e6edf3',
    'grid.color':        '#21262d',
    'grid.alpha':        0.8,
    'legend.facecolor':  '#161b22',
    'legend.edgecolor':  '#30363d',
    'axes.titlecolor':   '#e6edf3',
    'figure.titlesize':  12,
})

## Colour palette 
BG  = "#0d1117"
PNL = "#161b22"
CRD = "#21262d"
BLU = "#58a6ff"
GRN = "#3fb950"
RED = "#f85149"
ORG = "#d29922"
PRP = "#bc8cff"
CYN = "#39d353"
TXT = "#e6edf3"
SBT = "#8b949e"

## Qt stylesheet 
STYLE = f"""
QMainWindow, QWidget       {{ background: {BG};  color: {TXT}; font-family: 'Segoe UI', Arial; }}
QTabWidget::pane           {{ border: 1px solid #30363d; background: {PNL}; border-radius: 6px; }}
QTabBar::tab               {{ background: {CRD}; color: {SBT}; padding: 9px 18px;
                              font-size: 13px; font-weight: 600; margin-right: 3px;
                              border-radius: 4px 4px 0 0; }}
QTabBar::tab:selected      {{ background: {BLU}; color: white; }}
QTabBar::tab:hover:!selected {{ background: #2d333b; color: {TXT}; }}
QPushButton                {{ padding: 7px 14px; border-radius: 5px; font-size: 12px;
                              font-weight: bold; border: none; color: white; min-height: 30px; }}
QPushButton:hover          {{ background-color: rgba(255,255,255,0.08); }}
QPushButton:disabled       {{ background: #3d444d !important; color: {SBT} !important; }}
QDoubleSpinBox, QComboBox  {{ background: {CRD}; color: {TXT}; border: 1px solid #30363d;
                              border-radius: 4px; padding: 3px 6px;
                              min-width: 65px; font-size: 12px; }}
QDoubleSpinBox:focus, QComboBox:focus {{ border: 1px solid {BLU}; }}
QComboBox QAbstractItemView {{ background: {CRD}; color: {TXT};
                               selection-background-color: {BLU}; }}
QLabel                     {{ color: {TXT}; font-size: 12px; }}
QGroupBox                  {{ border: 1px solid #30363d; border-radius: 6px;
                              margin-top: 8px; padding-top: 6px;
                              color: {BLU}; font-weight: bold; font-size: 12px; }}
QGroupBox::title           {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}
QFrame[frameShape="4"]     {{ color: #30363d; max-height: 1px; margin: 2px 0; }}
QSlider::groove:horizontal {{ height: 4px; background: #30363d; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {BLU}; width: 14px; height: 14px;
                              margin: -5px 0; border-radius: 7px; }}
QSlider::sub-page:horizontal {{ background: {BLU}; border-radius: 2px; }}
"""


##  Helper

def hline():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    return f



##  Main Window
class MechanismSimulator(QMainWindow):

    # Construction 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kinematics & Dynamics of Mechanisms — IIT Hyderabad")
        self.setGeometry(40, 30, 1340, 990)
        self.setStyleSheet(STYLE)

        # Animation state
        self.timer            = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.current_angle    = 0.0
        self.angle_step       = 1.0
        self.active_lengths   = []
        self.active_ground_idx = 0
        self.current_mechanism = None
        self.non_grashof_range = None   # (lo_deg, hi_deg) or None
        self._grashof_text     = "—"

        # Build UI
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(6)
        root.setContentsMargins(8, 8, 8, 8)

        self.tabs = QTabWidget()
        self.tab_fb = QWidget()
        self.tab_sc = QWidget()
        self.tabs.addTab(self.tab_fb, "⚙  Four-Bar Mechanism  (Tasks 1 – 3)")
        self.tabs.addTab(self.tab_sc, "🔩  Slider-Crank Mechanism  (Tasks 4 – 5)")
        root.addWidget(self.tabs)

        self.setup_fourbar_ui()
        self.setup_slider_ui()

        # Status bar
        self.status = QLabel("✅  Ready — configure inputs and press a Task button.")
        self._set_status_style(GRN)
        root.addWidget(self.status)

        # Shared Matplotlib canvas
        self.figure = Figure(figsize=(13, 4.4), dpi=100)
        self.figure.patch.set_facecolor(BG)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(360)
        root.addWidget(self.canvas)

        self.setup_single_plot()

    ## Status helper 
    def _set_status_style(self, color=GRN):
        self.status.setStyleSheet(
            f"background:{PNL}; color:{color}; font-size:13px; font-weight:600;"
            f" padding:6px 10px; border-radius:4px; border:1px solid #30363d;"
        )

    def set_status(self, msg, color=GRN):
        self.status.setText(msg)
        self._set_status_style(color)

    ## Spin-box helper 
    def _spin(self, label, layout, lo, hi, default, step=0.5):
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color:{SBT}; font-size:9pt;")
        sb = QDoubleSpinBox()
        sb.setRange(lo, hi)
        sb.setValue(default)
        sb.setSingleStep(step)
        layout.addWidget(lbl)
        layout.addWidget(sb)
        return sb

    
    ##  UI: FOUR-BAR TAB
    def setup_fourbar_ui(self):
        lay = QVBoxLayout(self.tab_fb)
        lay.setSpacing(4)

        # Geometry group
        grp_geo = QGroupBox("  Link Lengths")
        geo_h = QHBoxLayout(grp_geo)
        self.links = []
        defaults = [2.0, 5.0, 4.0, 5.0]
        for i in range(4):
            sb = self._spin(f"L{i+1}:", geo_h, 0.1, 9999.0, defaults[i])
            self.links.append(sb)
        geo_h.addWidget(QLabel("  Ground Link:"))
        self.ground_combo = QComboBox()
        self.ground_combo.addItems(["Link 1 (d)", "Link 2 (a)", "Link 3 (b)", "Link 4 (c)"])
        geo_h.addWidget(self.ground_combo)
        geo_h.addStretch()
        lay.addWidget(grp_geo)

        # Dynamics group
        grp_dyn = QGroupBox("  Dynamics & Coupler Inputs  (Tasks 2 & 3)")
        dyn_h = QHBoxLayout(grp_dyn)
        self.theta2_input      = self._spin("θ₂ (°):",     dyn_h, -360, 360,   60.0, 5.0)
        self.omega2_input      = self._spin("ω₂ (rad/s):", dyn_h, -1000, 1000, 10.0, 1.0)
        self.alpha2_input      = self._spin("α₂ (rad/s²):",dyn_h, -1000, 1000,  0.0, 1.0)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.VLine); sep.setStyleSheet("color:#30363d;")
        dyn_h.addWidget(sep)
        self.coupler_dist_input = self._spin("Rp:", dyn_h, 0.0, 9999, 3.0)
        self.coupler_ang_input  = self._spin("δ (°):", dyn_h, -360, 360, 30.0, 5.0)
        dyn_h.addStretch()
        lay.addWidget(grp_dyn)

        # Buttons + controls
        ctrl = QHBoxLayout()

        self.btn_task1 = QPushButton("▶  Task 1 — Animate Four-Bar")
        self.btn_task1.setStyleSheet(f"background:{BLU};")
        self.btn_task1.clicked.connect(self.start_task1_animation)
        ctrl.addWidget(self.btn_task1)

        self.btn_task2 = QPushButton("📐  Task 2 — Vel & Acc Diagrams")
        self.btn_task2.setStyleSheet(f"background:{GRN}; color:#000;")
        self.btn_task2.clicked.connect(self.start_task2_diagrams)
        ctrl.addWidget(self.btn_task2)

        self.btn_task3 = QPushButton("〰  Task 3 — Coupler Curves")
        self.btn_task3.setStyleSheet(f"background:{PRP};")
        self.btn_task3.clicked.connect(self.start_task3_coupler)
        ctrl.addWidget(self.btn_task3)

        ctrl.addStretch()

        self.btn_stop_fb = QPushButton("⏹  Stop")
        self.btn_stop_fb.setStyleSheet(f"background:{RED};")
        self.btn_stop_fb.clicked.connect(self.stop_animation)
        ctrl.addWidget(self.btn_stop_fb)

        ctrl.addWidget(QLabel("  Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.valueChanged.connect(self.on_speed_change)
        ctrl.addWidget(self.speed_slider)

        lay.addLayout(ctrl)
        lay.addStretch()


    ##  UI: SLIDER-CRANK TAB
    
    def setup_slider_ui(self):
        lay = QVBoxLayout(self.tab_sc)
        lay.setSpacing(4)

        grp_geo = QGroupBox("  Slider-Crank Geometry  (zero offset)")
        geo_h = QHBoxLayout(grp_geo)
        self.slider_crank_input = self._spin("Crank Radius (a):", geo_h, 0.1, 9999, 2.0)
        self.slider_rod_input   = self._spin("Connecting Rod (b):", geo_h, 0.1, 9999, 6.0)
        geo_h.addWidget(QLabel("  Inversion:"))
        self.slider_ground_combo = QComboBox()
        self.slider_ground_combo.setMinimumWidth(280)
        self.slider_ground_combo.addItems([
            "1 — Frame / Sliding Axis  (Standard)",
            "2 — Crank Pin Fixed  (Rotary / Gnome Engine)",
            "3 — Connecting Rod Fixed  (Oscillating Cylinder)",
            "4 — Slider Block Fixed  (Pendulum Pump)",
        ])
        geo_h.addWidget(self.slider_ground_combo)
        geo_h.addStretch()
        lay.addWidget(grp_geo)

        grp_dyn = QGroupBox("  Dynamics Inputs  (Task 5)")
        dyn_h = QHBoxLayout(grp_dyn)
        self.slider_theta2_input = self._spin("θ₂ (°):",     dyn_h, -360, 360,   60.0, 5.0)
        self.slider_omega2_input = self._spin("ω₂ (rad/s):", dyn_h, -1000, 1000, 10.0, 1.0)
        self.slider_alpha2_input = self._spin("α₂ (rad/s²):",dyn_h, -1000, 1000,  0.0, 1.0)
        dyn_h.addStretch()
        lay.addWidget(grp_dyn)

        ctrl = QHBoxLayout()

        self.btn_task4 = QPushButton("▶  Task 4 — Animate Slider-Crank Inversions")
        self.btn_task4.setStyleSheet(f"background:{ORG};")
        self.btn_task4.clicked.connect(self.start_task4_animation)
        ctrl.addWidget(self.btn_task4)

        self.btn_task5 = QPushButton("📐  Task 5 — Slider Vel & Acc Diagrams")
        self.btn_task5.setStyleSheet(f"background:{RED};")
        self.btn_task5.clicked.connect(self.start_task5_diagrams)
        ctrl.addWidget(self.btn_task5)

        ctrl.addStretch()

        self.btn_stop_sc = QPushButton("⏹  Stop")
        self.btn_stop_sc.setStyleSheet(f"background:{RED};")
        self.btn_stop_sc.clicked.connect(self.stop_animation)
        ctrl.addWidget(self.btn_stop_sc)

        ctrl.addWidget(QLabel("  Speed:"))
        self.speed_slider2 = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider2.setRange(1, 10)
        self.speed_slider2.setValue(5)
        self.speed_slider2.setFixedWidth(120)
        self.speed_slider2.valueChanged.connect(self.on_speed_change)
        ctrl.addWidget(self.speed_slider2)

        lay.addLayout(ctrl)
        lay.addStretch()

    ##  Speed / Stop

    def on_speed_change(self, v):
        sign = 1 if self.angle_step >= 0 else -1
        self.angle_step = sign * max(0.5, v * 0.5)
        # Sync both sliders without recursion
        for attr in ('speed_slider', 'speed_slider2'):
            sl = getattr(self, attr, None)
            if sl:
                sl.blockSignals(True)
                sl.setValue(v)
                sl.blockSignals(False)

    def stop_animation(self):
        self.timer.stop()
        self.set_status("⏹  Animation stopped.", ORG)

    ##  Canvas helpers
    
    def setup_single_plot(self, title="Mechanism Animation Area"):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(title, fontsize=12, pad=8)
        self.ax.grid(True, alpha=0.4)
        self.ax.set_aspect('equal')
        self.figure.tight_layout(rect=[0, 0, 1, 0.97])
        self.canvas.draw_idle()

    def setup_triple_plot(self, titles=("Position", "Velocity", "Acceleration")):
        self.figure.clear()
        self.ax_pos = self.figure.add_subplot(131)
        self.ax_vel = self.figure.add_subplot(132)
        self.ax_acc = self.figure.add_subplot(133)
        for ax, t in zip([self.ax_pos, self.ax_vel, self.ax_acc], titles):
            ax.set_title(t, fontsize=11, pad=6)
            ax.grid(True, alpha=0.4)
        self.figure.tight_layout(rect=[0, 0, 1, 0.97], w_pad=3.0)

    def _draw_ground_pin(self, ax, x, y, sz=0.3):
        """Equilateral triangle hatching to denote a ground pin."""
        tri_x = [x - sz, x + sz, x,      x - sz]
        tri_y = [y - sz, y - sz, y + sz * 0.6, y - sz]
        ax.fill(tri_x, tri_y, color=SBT, zorder=5, alpha=0.75)
        ax.plot([x - sz * 1.6, x + sz * 1.6], [y - sz, y - sz],
                color=SBT, lw=2, zorder=5)

    def add_vector(self, ax, start, end, color, label):
        """Draw an arrow and annotate with magnitude."""
        sx, sy = start
        ex, ey = end
        mag = float(np.hypot(ex - sx, ey - sy))
        ax.plot([], [], color=color, lw=2, label=f"{label}  |{mag:.2f}|")
        ax.annotate('', xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                   lw=2.0, mutation_scale=16))
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        ax.text(mx, my, f"{mag:.2f}", fontsize=8, color=color,
                ha='center', va='bottom', zorder=10)

    def _auto_lim(self, ax, pts, margin=1.5):
        """Set equal-span limits around a set of points."""
        xs, ys = pts[:, 0], pts[:, 1]
        xc = (xs.min() + xs.max()) / 2
        yc = (ys.min() + ys.max()) / 2
        span = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2 + margin
        ax.set_xlim(xc - span, xc + span)
        ax.set_ylim(yc - span, yc + span)

    
    ##  Grashof Analysis

    def grashof_analysis(self, lengths, ground_idx):
        """Returns (is_grashof: bool, type_name: str)."""
        srt   = sorted(lengths)
        s, l  = srt[0], srt[3]
        p, q  = srt[1], srt[2]
        diff  = (s + l) - (p + q)
        grashof = diff <= 0

        if not grashof:
            return False, "Non-Grashof — Double Rocker (oscillates)"

        if abs(diff) < 1e-9:
            return True, "Grashof Special (s + l = p + q) — Parallelogram / Change-point"

        d = lengths[ground_idx]
        a = lengths[(ground_idx + 1) % 4]
        b = lengths[(ground_idx + 2) % 4]
        c = lengths[(ground_idx + 3) % 4]

        if   d == s: return True, "Grashof — Double Crank (Drag-Link): input & output rotate fully"
        elif b == s: return True, "Grashof — Double Rocker (coupler rotates): both links oscillate"
        elif a == s: return True, "Grashof — Crank-Rocker: input (a) is crank, output (c) rocks"
        else:        return True, "Grashof — Crank-Rocker: input (a) rocks, output (c) is crank"

    def _find_valid_range(self, lengths, ground_idx):
        """
        Return (lo, hi) of the FIRST contiguous valid angular segment in degrees.

        Why this matters
        ----------------
        For rocking mechanisms (Grashof Double-Rocker, Crank-Rocker with rocking
        input, or Non-Grashof) the discriminant in Freudenstein's equation is ≥ 0
        only over two SEPARATE angular bands, e.g. [37°–101°] and [259°–323°].
        These are two distinct assembly modes (open vs crossed).  The old code
        returned (first_valid_overall, last_valid_overall) = (37, 323), which
        spans BOTH segments and the dead gap between them.  The animation then
        advanced silently through the gap and landed in the wrong assembly mode —
        producing the abrupt positional jump seen by the user.

        This version finds the first angle where disc ≥ 0, then walks forward
        until disc first goes negative again.  That contiguous band is the correct
        bounce range for one physical assembly of the linkage.
        """
        # ── Step 1: find the first valid angle ────────────────────────────
        lo = None
        for i in range(361):
            if self.calc_fourbar(lengths, ground_idx, np.radians(i)) is not None:
                lo = i
                break
        if lo is None:
            return None          # mechanism cannot assemble at all

        # ── Step 2: walk forward from lo until the segment ends ───────────
        hi = lo
        for i in range(lo, lo + 362):
            angle = i % 361
            if self.calc_fourbar(lengths, ground_idx, np.radians(angle)) is not None:
                hi = i           # keep extending while still valid
            else:
                break            # first invalid angle → segment has ended

        return float(lo), float(hi)

    
    ##  Four-Bar Kinematics
    
    def calc_fourbar(self, lengths, ground_idx, th2):
        """Freudenstein half-angle solve.  Returns (O2,A,B,O4,th3,th4) or None."""
        try:
            d = lengths[ground_idx]
            a = lengths[(ground_idx + 1) % 4]
            b = lengths[(ground_idx + 2) % 4]
            c = lengths[(ground_idx + 3) % 4]

            K1 = d / a
            K2 = d / c
            K3 = (a**2 - b**2 + c**2 + d**2) / (2.0 * a * c)

            A = np.cos(th2) - K1 - K2 * np.cos(th2) + K3
            B = -2.0 * np.sin(th2)
            C = K1 - (K2 + 1.0) * np.cos(th2) + K3

            disc = B**2 - 4.0 * A * C
            if disc < -1e-9:        # truly no solution
                return None
            disc = max(0.0, disc)   # clamp floating-point noise

            # Handle A ≈ 0 (degenerate)
            if abs(A) < 1e-9:
                if abs(B) < 1e-9:
                    return None
                t4 = -C / B
            else:
                t4 = (-B - np.sqrt(disc)) / (2.0 * A)

            th4 = 2.0 * np.arctan(t4)
            O2  = np.array([0.0, 0.0])
            Aj  = np.array([a * np.cos(th2),  a * np.sin(th2)])
            O4  = np.array([d,  0.0])
            Bj  = np.array([d + c * np.cos(th4), c * np.sin(th4)])
            th3 = np.arctan2(Bj[1] - Aj[1], Bj[0] - Aj[0])
            return O2, Aj, Bj, O4, th3, th4
        except Exception:
            return None

    def dyn_fourbar(self, a, b, c, th2, th3, th4, w2, alp2):
        """Velocity & acceleration analysis. Returns (w3,w4,alp3,alp4)."""
        try:
            mat = np.array([
                [-b * np.sin(th3),  c * np.sin(th4)],
                [ b * np.cos(th3), -c * np.cos(th4)],
            ])
            if abs(np.linalg.det(mat)) < 1e-8:
                return 0.0, 0.0, 0.0, 0.0

            rhs_v = np.array([
                 a * w2 * np.sin(th2),
                -a * w2 * np.cos(th2),
            ])
            w3, w4 = np.linalg.solve(mat, rhs_v)

            rhs_a = np.array([
                a * alp2 * np.sin(th2) + a * w2**2 * np.cos(th2)
                + b * w3**2 * np.cos(th3) - c * w4**2 * np.cos(th4),
                -a * alp2 * np.cos(th2) + a * w2**2 * np.sin(th2)
                + b * w3**2 * np.sin(th3) - c * w4**2 * np.sin(th4),
            ])
            alp3, alp4 = np.linalg.solve(mat, rhs_a)
            return w3, w4, alp3, alp4
        except Exception:
            return 0.0, 0.0, 0.0, 0.0

    
    ##  Draw helpers
    
    def draw_fourbar(self, coords):
        ax = self.ax
        ax.clear()
        ax.grid(True, alpha=0.4)
        ax.set_aspect('equal')
        O2, A, B, O4, th3, th4 = coords

        lim = sum(self.active_lengths) * 0.6
        cx  = (O2[0] + O4[0]) / 2
        ax.set_xlim(cx - lim, cx + lim)
        ax.set_ylim(-lim * 0.75, lim * 0.75)

        sz = lim * 0.04
        self._draw_ground_pin(ax, O2[0], O2[1] - sz, sz)
        self._draw_ground_pin(ax, O4[0], O4[1] - sz, sz)

        ax.plot([O2[0], A[0]],  [O2[1], A[1]],  '-o', color=BLU, lw=3.5, ms=9, zorder=4, label="Crank (a)")
        ax.plot([A[0],  B[0]],  [A[1],  B[1]],  '-o', color=GRN, lw=3.5, ms=9, zorder=4, label="Coupler (b)")
        ax.plot([B[0],  O4[0]], [B[1],  O4[1]], '-o', color=ORG, lw=3.5, ms=9, zorder=4, label="Rocker (c)")
        ax.plot([O2[0], O4[0]], [O2[1], O4[1]], '--', color=SBT, lw=2.5, ms=10, zorder=2, label="Ground (d)")

        off = lim * 0.06
        for pt, nm in [(O2, "O₂"), (A, "A"), (B, "B"), (O4, "O₄")]:
            ax.text(pt[0], pt[1] + off, nm, fontsize=10, ha='center',
                    color=TXT, fontweight='bold', zorder=6)

        ax.set_xlabel("x (units)")
        ax.set_ylabel("y (units)")
        ax.legend(loc='upper right', fontsize=9, framealpha=0.6)
        ax.set_title(
            f"Four-Bar  |  θ₂ = {self.current_angle % 360:.1f}°  |  {self._grashof_text}",
            fontsize=10, pad=6
        )
        self.canvas.draw_idle()

    
    ##  TASK 1 — Four-Bar Animation

    def start_task1_animation(self):
        self.timer.stop()
        self.setup_single_plot()
        self.current_mechanism = 'fourbar'

        lengths    = [b.value() for b in self.links]
        ground_idx = self.ground_combo.currentIndex()

        # Validate
        if any(l <= 0 for l in lengths):
            self.set_status("❌  All link lengths must be positive.", RED)
            return

        is_g, gtype = self.grashof_analysis(lengths, ground_idx)
        self._grashof_text = gtype
        icon = "✅" if is_g else "⚠️"
        self.set_status(f"{icon}  Task 1 — {gtype}", GRN if is_g else ORG)

        self.active_lengths    = lengths
        self.active_ground_idx = ground_idx

        vrange = self._find_valid_range(lengths, ground_idx)
        if vrange is None:
            self.set_status("❌  Mechanism cannot assemble — check link lengths (Grübler's criterion).", RED)
            return

        lo, hi = vrange
        # If the contiguous valid segment spans a full revolution → continuous spin.
        # Otherwise (rocking / oscillating, any Grashof type) → bounce within [lo, hi].
        is_full_rotation = (hi - lo) >= 358.0
        self.non_grashof_range = None if is_full_rotation else vrange
        self.current_angle     = lo
        self.angle_step        = abs(self.speed_slider.value() * 0.5)
        self.timer.start(20)

    
    ##  Global animation tick

    def update_animation(self):
        step = self.angle_step

        if self.current_mechanism == 'fourbar':
            if self.non_grashof_range:
                lo, hi = self.non_grashof_range
                nxt = self.current_angle + step
                if nxt >= hi:
                    nxt = hi
                    self.angle_step = -abs(self.angle_step)
                elif nxt <= lo:
                    nxt = lo
                    self.angle_step =  abs(self.angle_step)
                self.current_angle = nxt
            else:
                self.current_angle += step

            coords = self.calc_fourbar(
                self.active_lengths, self.active_ground_idx,
                np.radians(self.current_angle)
            )
            if coords is not None:
                self.draw_fourbar(coords)

        elif self.current_mechanism == 'slidercrank':
            self.current_angle += step
            coords = self.calc_slidercrank(
                self.active_lengths[0], self.active_lengths[1],
                self.active_ground_idx, np.radians(self.current_angle)
            )
            if coords is not None:
                self.draw_slidercrank(coords)

    
    #  TASK 2 — Four-Bar Velocity & Acceleration Polygons

    def start_task2_diagrams(self):
        self.timer.stop()
        self.setup_triple_plot(("Position Diagram", "Velocity Polygon", "Acceleration Polygon"))

        lengths    = [b.value() for b in self.links]
        ground_idx = self.ground_combo.currentIndex()
        th2        = np.radians(self.theta2_input.value() % 360)
        w2         = self.omega2_input.value()
        alp2       = self.alpha2_input.value()

        coords = self.calc_fourbar(lengths, ground_idx, th2)
        if coords is None:
            self.set_status("❌  Task 2: Mechanism cannot assemble at the given θ₂.", RED)
            self.canvas.draw_idle()
            return

        O2, A, B, O4, th3, th4 = coords
        a   = lengths[(ground_idx + 1) % 4]
        b_l = lengths[(ground_idx + 2) % 4]
        c   = lengths[(ground_idx + 3) % 4]

        w3, w4, alp3, alp4 = self.dyn_fourbar(a, b_l, c, th2, th3, th4, w2, alp2)
        self.set_status(
            f"✅  Task 2 Complete  |  ω₃={w3:.3f}, ω₄={w4:.3f} rad/s  |"
            f"  α₃={alp3:.3f}, α₄={alp4:.3f} rad/s²"
        )

        ## Position diagram 
        ax = self.ax_pos
        ax.set_aspect('equal')
        sz = sum(lengths) * 0.025
        self._draw_ground_pin(ax, O2[0], O2[1] - sz, sz)
        self._draw_ground_pin(ax, O4[0], O4[1] - sz, sz)
        ax.plot([O2[0], A[0]],  [O2[1], A[1]],  '-o', color=BLU, lw=3, ms=7)
        ax.plot([A[0],  B[0]],  [A[1],  B[1]],  '-o', color=GRN, lw=3, ms=7)
        ax.plot([B[0],  O4[0]], [B[1],  O4[1]], '-o', color=ORG, lw=3, ms=7)
        ax.plot([O2[0], O4[0]], [O2[1], O4[1]], '--', color=SBT, lw=2)
        off = sz * 2.5
        for pt, nm in [(O2, "O₂"), (A, "A"), (B, "B"), (O4, "O₄")]:
            ax.text(pt[0], pt[1] + off, nm, fontsize=9, ha='center', color=TXT)
        ax.set_xlabel("x (units)")
        ax.set_ylabel("y (units)")

        ## Velocity polygon 
        ax = self.ax_vel
        ax.set_aspect('equal')
        VA  = np.array([-a * w2 * np.sin(th2),  a * w2 * np.cos(th2)])
        VB  = np.array([-c * w4 * np.sin(th4),  c * w4 * np.cos(th4)])
        self.add_vector(ax, (0, 0), VA, RED,  "Vₐ")
        self.add_vector(ax, (0, 0), VB, GRN,  "V_b")
        self.add_vector(ax, tuple(VA), tuple(VB), PRP, "V_ba")
        ax.plot(0, 0, 'w+', ms=8, zorder=10)
        ax.set_xlabel("Vx (units/s)")
        ax.set_ylabel("Vy (units/s)")
        ax.legend(fontsize=8, loc='best', framealpha=0.55)
        self._auto_lim(ax, np.array([[0, 0], VA, VB]))

        ## Acceleration polygon 
        ax = self.ax_acc
        ax.set_aspect('equal')
        AA  = np.array([-a * alp2 * np.sin(th2) - a * w2**2 * np.cos(th2),
                         a * alp2 * np.cos(th2) - a * w2**2 * np.sin(th2)])
        AB  = np.array([-c * alp4 * np.sin(th4) - c * w4**2 * np.cos(th4),
                         c * alp4 * np.cos(th4) - c * w4**2 * np.sin(th4)])
        self.add_vector(ax, (0, 0), AA, RED,  "Aₐ")
        self.add_vector(ax, (0, 0), AB, GRN,  "A_b")
        self.add_vector(ax, tuple(AA), tuple(AB), PRP, "A_ba")
        ax.plot(0, 0, 'w+', ms=8, zorder=10)
        ax.set_xlabel("Ax (units/s²)")
        ax.set_ylabel("Ay (units/s²)")
        ax.legend(fontsize=8, loc='best', framealpha=0.55)
        self._auto_lim(ax, np.array([[0, 0], AA, AB]), margin=3)

        self.figure.tight_layout(rect=[0, 0, 1, 0.97], w_pad=3)
        self.canvas.draw_idle()

    
    ##  TASK 3 — Coupler Curve, Vel vs θ₂, Acc vs θ₂
    
    def start_task3_coupler(self):
        self.timer.stop()
        self.setup_triple_plot((
            "Coupler Curve Path",
            "Coupler |V| vs θ₂  (°)",
            "Coupler |A| vs θ₂  (°)"
        ))
        self.ax_pos.set_aspect('equal')

        lengths    = [b.value() for b in self.links]
        ground_idx = self.ground_combo.currentIndex()
        w2         = self.omega2_input.value()
        alp2       = self.alpha2_input.value()
        Rp         = self.coupler_dist_input.value()
        phi        = np.radians(self.coupler_ang_input.value())

        a   = lengths[(ground_idx + 1) % 4]
        b_l = lengths[(ground_idx + 2) % 4]
        c   = lengths[(ground_idx + 3) % 4]

        # ── Determine the valid sweep range ───────────────────────────────
        # For rocking mechanisms there are two disconnected valid segments
        # (open and crossed assembly modes).  We sweep only the first
        # contiguous segment so the coupler curve stays in one assembly mode.
        vrange = self._find_valid_range(lengths, ground_idx)
        if vrange is None:
            self.set_status("❌  Task 3: No valid positions found for this mechanism.", RED)
            self.canvas.draw_idle()
            return
        lo_deg, hi_deg = vrange
        is_full = (hi_deg - lo_deg) >= 358.0
        sweep_angles = range(360) if is_full else range(int(lo_deg), int(hi_deg) + 1)

        # Pre-compute Freudenstein coefficients for near-toggle discriminant check
        d_fr  = lengths[ground_idx]
        a_fr  = lengths[(ground_idx + 1) % 4]
        b_fr  = lengths[(ground_idx + 2) % 4]
        c_fr  = lengths[(ground_idx + 3) % 4]
        K1_fr = d_fr / a_fr
        K2_fr = d_fr / c_fr
        K3_fr = (a_fr**2 - b_fr**2 + c_fr**2 + d_fr**2) / (2.0 * a_fr * c_fr)
        # Velocities blow up as disc → 0 (toggle position).  Insert NaN for any
        # angle within ~3° of a toggle so the plot shows a gap, not a spike.
        # disc=0.034 → |Ap|~700,000 ; disc=0.30 → |Ap|~30,000 ; disc=0.56+ → reasonable.
        # Threshold 0.3 removes the 2 worst points at each toggle edge.
        NEAR_TOGGLE = 0.30

        ang_list, Px_l, Py_l, Vp_l, Ap_l = [], [], [], [], []
        ref_coords, ref_Px, ref_Py = None, None, None
        ref_angle = int(self.theta2_input.value() % 360)

        for t in sweep_angles:
            th2    = np.radians(t)
            coords = self.calc_fourbar(lengths, ground_idx, th2)
            if coords is None:
                continue

            O2, A, B, O4, th3, th4 = coords

            # Coupler point position — always valid geometrically
            Px = A[0] + Rp * np.cos(th3 + phi)
            Py = A[1] + Rp * np.sin(th3 + phi)
            ang_list.append(t)
            Px_l.append(Px); Py_l.append(Py)

            # Update reference position (must happen before any continue)
            if ref_coords is None or t == ref_angle:
                ref_coords, ref_Px, ref_Py = coords, Px, Py

            # Near-toggle check: disc ≈ 0 → velocities singular → insert NaN
            A_f   = np.cos(th2) - K1_fr - K2_fr*np.cos(th2) + K3_fr
            B_f   = -2.0 * np.sin(th2)
            C_f   = K1_fr - (K2_fr + 1.0)*np.cos(th2) + K3_fr
            disc_val = B_f**2 - 4.0*A_f*C_f
            if disc_val < NEAR_TOGGLE:
                Vp_l.append(np.nan)
                Ap_l.append(np.nan)
                continue

            # Dynamics (only away from toggle)
            w3, w4, alp3, alp4 = self.dyn_fourbar(a, b_l, c, th2, th3, th4, w2, alp2)

            Vax  = -a  * w2   * np.sin(th2)
            Vay  =  a  * w2   * np.cos(th2)
            Vpax = -Rp * w3   * np.sin(th3 + phi)
            Vpay =  Rp * w3   * np.cos(th3 + phi)
            Vp   = np.hypot(Vax + Vpax, Vay + Vpay)

            Aax  = -a  * alp2 * np.sin(th2)         - a  * w2**2 * np.cos(th2)
            Aay  =  a  * alp2 * np.cos(th2)         - a  * w2**2 * np.sin(th2)
            Apax = -Rp * alp3 * np.sin(th3 + phi)  - Rp * w3**2 * np.cos(th3 + phi)
            Apay =  Rp * alp3 * np.cos(th3 + phi)  - Rp * w3**2 * np.sin(th3 + phi)
            Ap   = np.hypot(Aax + Apax, Aay + Apay)

            Vp_l.append(Vp); Ap_l.append(Ap)

        if not ang_list:
            self.set_status("❌  Task 3: No valid positions found for this mechanism.", RED)
            self.canvas.draw_idle()
            return

        O2, A, B, O4, th3, th4 = ref_coords

        # Coupler curve
        ax = self.ax_pos
        ax.plot(Px_l, Py_l, '-', color=PRP, lw=2, label="Coupler Curve")
        ax.plot([O2[0], A[0], B[0], O4[0]],
                [O2[1], A[1], B[1], O4[1]], 'o-', color=BLU, alpha=0.55, lw=2)
        ax.plot([O2[0], O4[0]], [O2[1], O4[1]], '--', color=SBT, lw=2)
        ax.plot([A[0], ref_Px], [A[1], ref_Py], '-', color=RED, lw=2,
                label=f"Rp = {Rp:.2f}")
        ax.plot(ref_Px, ref_Py, 'o', color=RED, ms=10, zorder=6)
        ax.set_xlabel("x (units)")
        ax.set_ylabel("y (units)")
        ax.legend(fontsize=9, framealpha=0.6, loc='best')

        # Velocity vs angle
        ax = self.ax_vel
        ax.plot(ang_list, Vp_l, '-', color=GRN, lw=2)
        ax.fill_between(ang_list, Vp_l, alpha=0.12, color=GRN)
        ax.set_xlabel("θ₂  (degrees)")
        ax.set_ylabel("|Vp|  (units / s)")

        # Acceleration vs angle
        ax = self.ax_acc
        ax.plot(ang_list, Ap_l, '-', color=RED, lw=2)
        ax.fill_between(ang_list, Ap_l, alpha=0.12, color=RED)
        ax.set_xlabel("θ₂  (degrees)")
        ax.set_ylabel("|Ap|  (units / s²)")

        self.set_status(
            f"✅  Task 3 Complete  |  Rp={Rp},  δ={np.degrees(phi):.1f}°"
            f"  |  {len(ang_list)} valid crank positions plotted"
        )
        self.figure.tight_layout(rect=[0, 0, 1, 0.97], w_pad=3)
        self.canvas.draw_idle()

    
    ##  Slider-Crank Kinematics
    
    def calc_slidercrank(self, a, b, ground_idx, th2):
        """Returns transformed point list or None."""
        try:
            Ax, Ay = a * np.cos(th2), a * np.sin(th2)
            disc   = b**2 - Ay**2
            if disc < 0:
                return None
            Bx = Ax + np.sqrt(max(0.0, disc))
            O2 = np.array([0.0,  0.0])
            A  = np.array([Ax,   Ay])
            B  = np.array([Bx,   0.0])
            th3 = np.arctan2(B[1] - A[1], B[0] - A[0])

            axis_len = a + b + 3.0
            F1 = np.array([-axis_len, 0.0])
            F2 = np.array([ axis_len, 0.0])
            bw, bh = a * 0.55, a * 0.45
            box = np.array([
                [Bx - bw/2,  bh/2],
                [Bx + bw/2,  bh/2],
                [Bx + bw/2, -bh/2],
                [Bx - bw/2, -bh/2],
                [Bx - bw/2,  bh/2],   # close
            ])

            all_pts = [O2, A, B, F1, F2] + [row for row in box]

            # Inversion transform
            if   ground_idx == 0: tx, ty, rot = 0.0, 0.0,  0.0
            elif ground_idx == 1: tx, ty, rot = 0.0, 0.0, -th2
            elif ground_idx == 2: tx, ty, rot = Ax,  Ay,  -th3
            elif ground_idx == 3: tx, ty, rot = Bx,  0.0,  0.0
            else:                 tx, ty, rot = 0.0, 0.0,  0.0

            cs, sn = np.cos(rot), np.sin(rot)
            t_pts = []
            for p in all_pts:
                xt, yt = p[0] - tx, p[1] - ty
                t_pts.append(np.array([xt * cs - yt * sn, xt * sn + yt * cs]))
            return t_pts
        except Exception:
            return None

    def draw_slidercrank(self, t_pts):
        ax = self.ax
        ax.clear()
        ax.grid(True, alpha=0.4)
        ax.set_aspect('equal')

        O2, A, B = t_pts[0], t_pts[1], t_pts[2]
        F1, F2   = t_pts[3], t_pts[4]
        box_pts  = np.array(t_pts[5:])

        a, b   = self.active_lengths
        lim    = a + b + 3.5

        ax.plot([F1[0], F2[0]], [F1[1], F2[1]], '--', color=SBT, lw=2,
                label="Sliding Axis", zorder=1)
        ax.fill(box_pts[:, 0], box_pts[:, 1], color=GRN, alpha=0.25, zorder=2)
        ax.plot(box_pts[:, 0], box_pts[:, 1], '-', color=GRN, lw=2.5,
                label="Slider Block", zorder=3)
        ax.plot([O2[0], A[0]], [O2[1], A[1]], '-o', color=BLU, lw=3.5, ms=9,
                label=f"Crank (a={a})", zorder=4)
        ax.plot([A[0],  B[0]], [A[1],  B[1]], '-o', color=ORG, lw=3.5, ms=9,
                label=f"Rod (b={b})", zorder=4)

        sz = lim * 0.035
        self._draw_ground_pin(ax, O2[0], O2[1] - sz, sz)

        off = lim * 0.07
        for pt, nm in [(O2, "O"), (A, "A"), (B, "B")]:
            ax.text(pt[0], pt[1] + off, nm, fontsize=10, ha='center',
                    color=TXT, fontweight='bold', zorder=6)

        inv_names = ["Standard", "Rotary / Gnome Engine",
                     "Oscillating Cylinder", "Pendulum Pump"]
        name = inv_names[self.active_ground_idx]
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim * 0.85, lim * 0.85)
        ax.set_xlabel("x (units)")
        ax.set_ylabel("y (units)")
        ax.set_title(
            f"Slider-Crank — Inversion {self.active_ground_idx + 1}: {name}"
            f"  |  θ₂ = {self.current_angle % 360:.1f}°",
            fontsize=10, pad=6
        )
        ax.legend(loc='upper right', fontsize=9, framealpha=0.6)
        self.canvas.draw_idle()

    
    ##  TASK 4 — Slider-Crank Animation
    
    def start_task4_animation(self):
        self.timer.stop()
        self.setup_single_plot()
        self.current_mechanism = 'slidercrank'

        a          = self.slider_crank_input.value()
        b          = self.slider_rod_input.value()
        ground_idx = self.slider_ground_combo.currentIndex()

        if a <= 0 or b <= 0:
            self.set_status("❌  Crank and rod lengths must be positive.", RED)
            return
        if b < a:
            self.set_status(
                "⚠️  Rod b < Crank a — slider may not complete full rotation.", ORG
            )

        inv_names = ["Standard", "Rotary / Gnome Engine",
                     "Oscillating Cylinder", "Pendulum Pump"]
        self.active_lengths    = [a, b]
        self.active_ground_idx = ground_idx
        self.current_angle     = 0.0
        self.angle_step        = abs(self.speed_slider2.value() * 0.5)
        self.non_grashof_range = None

        self.set_status(
            f"▶  Task 4 — Inversion {ground_idx + 1}: {inv_names[ground_idx]}"
        )
        self.timer.start(20)


    ##  TASK 5 — Slider-Crank Velocity & Acceleration Polygons
    
    def start_task5_diagrams(self):
        self.timer.stop()
        self.setup_triple_plot((
            "Slider-Crank Position",
            "Velocity Polygon",
            "Acceleration Polygon"
        ))

        a  = self.slider_crank_input.value()
        b  = self.slider_rod_input.value()

        th2_deg = self.slider_theta2_input.value() % 360
        th2     = np.radians(th2_deg)
        w2      = self.slider_omega2_input.value()
        alp2    = self.slider_alpha2_input.value()

        Ax, Ay = a * np.cos(th2), a * np.sin(th2)
        disc   = b**2 - Ay**2
        if disc < 0:
            self.set_status(
                "❌  Task 5: Mechanism cannot assemble (b < |a·sin θ₂|). "
                "Choose a larger rod or different angle.", RED
            )
            self.canvas.draw_idle()
            return

        Bx = Ax + np.sqrt(max(0.0, disc))
        O2 = np.array([0.0, 0.0])
        A  = np.array([Ax, Ay])
        B  = np.array([Bx, 0.0])

        # Guard against arcsin domain error
        sin3 = np.clip(-Ay / b, -1.0, 1.0)
        th3  = np.arcsin(sin3)
        cos3 = np.cos(th3)

        if abs(cos3) < 1e-9:
            self.set_status(
                "❌  Task 5: Singular configuration (θ₃ ≈ ±90°). "
                "Choose a different input angle.", RED
            )
            self.canvas.draw_idle()
            return

        # Velocity analysis
        w3     = (-a * w2 * np.cos(th2)) / (b * cos3)
        Vb_mag = -a * w2 * np.sin(th2) - b * w3 * np.sin(th3)

        # Acceleration analysis
        alp3   = (-a * alp2 * np.cos(th2) + a * w2**2 * np.sin(th2)
                  + b * w3**2 * np.sin(th3)) / (b * cos3)
        Ab_mag = (-a * alp2 * np.sin(th2) - a * w2**2 * np.cos(th2)
                  - b * alp3 * np.sin(th3) - b * w3**2 * np.cos(th3))

        VA  = np.array([-a * w2  * np.sin(th2), a * w2  * np.cos(th2)])
        VB  = np.array([Vb_mag, 0.0])

        AA  = np.array([
            -a * alp2 * np.sin(th2) - a * w2**2 * np.cos(th2),
             a * alp2 * np.cos(th2) - a * w2**2 * np.sin(th2),
        ])
        AB  = np.array([Ab_mag, 0.0])

        self.set_status(
            f"✅  Task 5 Complete  |  θ₃={np.degrees(th3):.2f}°,  ω₃={w3:.3f} rad/s"
            f"  |  V_slider={Vb_mag:.3f},  A_slider={Ab_mag:.3f}  (units/s, units/s²)"
        )

        ## Position 
        ax = self.ax_pos
        ax.set_aspect('equal')
        lim = a + b + 2
        ax.plot([-lim, lim], [0, 0], '--', color=SBT, lw=2, label="Sliding Axis")
        ax.plot([O2[0], A[0]], [O2[1], A[1]], '-o', color=BLU, lw=3.5, ms=9,
                label=f"Crank a={a}")
        ax.plot([A[0],  B[0]], [A[1],  B[1]], '-o', color=ORG, lw=3.5, ms=9,
                label=f"Rod b={b}")
        ax.plot(B[0], B[1], 's', color=GRN, ms=14, label="Slider", zorder=5)
        sz = lim * 0.03
        self._draw_ground_pin(ax, O2[0], O2[1] - sz, sz)
        off = lim * 0.07
        for pt, nm in [(O2, "O"), (A, "A"), (B, "B")]:
            ax.text(pt[0], pt[1] + off, nm, fontsize=10, ha='center',
                    color=TXT, fontweight='bold')
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim * 0.7, lim * 0.7)
        ax.set_xlabel("x (units)")
        ax.set_ylabel("y (units)")
        ax.legend(fontsize=8, framealpha=0.6)

        ## Velocity polygon 
        ax = self.ax_vel
        ax.set_aspect('equal')
        self.add_vector(ax, (0, 0), VA, RED,  "Vₐ")
        self.add_vector(ax, (0, 0), VB, GRN,  "V_slider")
        self.add_vector(ax, tuple(VA), tuple(VB), PRP, "V_ba")
        ax.plot(0, 0, 'w+', ms=8, zorder=10)
        ax.set_xlabel("Vx (units/s)")
        ax.set_ylabel("Vy (units/s)")
        ax.legend(fontsize=8, framealpha=0.55)
        self._auto_lim(ax, np.array([[0, 0], VA, VB]))

        ## Acceleration polygon 
        ax = self.ax_acc
        ax.set_aspect('equal')
        self.add_vector(ax, (0, 0), AA, RED,  "Aₐ")
        self.add_vector(ax, (0, 0), AB, GRN,  "A_slider")
        self.add_vector(ax, tuple(AA), tuple(AB), PRP, "A_ba")
        ax.plot(0, 0, 'w+', ms=8, zorder=10)
        ax.set_xlabel("Ax (units/s²)")
        ax.set_ylabel("Ay (units/s²)")
        ax.legend(fontsize=8, framealpha=0.55)
        self._auto_lim(ax, np.array([[0, 0], AA, AB]), margin=3)

        self.figure.tight_layout(rect=[0, 0, 1, 0.97], w_pad=3)
        self.canvas.draw_idle()


## run 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MechanismSimulator()
    window.show()
    sys.exit(app.exec())