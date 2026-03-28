# Kinematics & Dynamics of Mechanisms — Simulator

> **Course:** ME2220: Kinematics and Dynamics of Mechanisms
> **Institution:** Indian Institute of Technology Hyderabad
> **Semester:** Jan – Apr 2026
> **Stage:** Project Stage I

---

## Overview

A fully self-contained, interactive Python desktop application that simulates the kinematics and dynamics of the two most fundamental planar mechanisms — the **Four-Bar Linkage** and the **Slider-Crank Mechanism**.

All five required tasks from the Stage I problem statement are bundled into a **single seamless GUI** (qualifying for the bonus point allocation). The user enters parameters, presses one button, and immediately sees a live animation or a multi-panel diagnostic plot — no command-line interaction or file editing is ever required.

---

## Tech Stack

| Library | Version | Role |
|---|---|---|
| Python | 3.9 + | Core language; all numerical and control logic |
| PyQt6 | ≥ 6.4 | Tabbed GUI, spin-boxes, combo-boxes, animation timer |
| NumPy | ≥ 1.23 | Matrix solves for velocity/acceleration; trig utilities |
| Matplotlib | ≥ 3.7 | Embedded animated canvas; vector-polygon diagrams; coupler curves |

---

## Features & Implemented Tasks

### Task 1 — Four-Bar Animation `[3 marks]`
- Takes four link lengths **L1–L4** and a **grounded link** selection
- Automatically checks the **Grashof condition** and identifies mechanism type (Crank-Rocker, Double-Crank, Double-Rocker, Change-Point)
- **Grashof:** animates continuous 360° rotation of the shortest link
- **Non-Grashof:** smoothly rocks back and forth between the two extreme positions
- Ground pins rendered with standard hatch triangle symbols

### Task 2 — Four-Bar Vector Diagrams `[2 marks]`
- Takes input angle **θ₂**, angular velocity **ω₂**, and angular acceleration **α₂**
- Solves the velocity and acceleration matrix equations
- Plots three panels: **Position diagram**, **Velocity polygon**, and **Acceleration polygon** — all with labelled magnitude arrows

### Task 3 — Coupler Curves `[1 mark]`
- Takes coupler point distance **Rp** and offset angle **δ**
- Sweeps the crank through all 360 valid degrees
- Plots **Coupler Curve path**, **|Vp| vs θ₂**, and **|Ap| vs θ₂** simultaneously

### Task 4 — Slider-Crank Inversions `[2 marks]`
- Takes crank radius **a** and connecting rod length **b** (zero offset)
- Animates all **four kinematic inversions** using rigid-body coordinate transformations:
  1. Frame / Sliding Axis — Standard slider-crank
  2. Crank Pin Fixed — Rotary / Gnome Engine
  3. Connecting Rod Fixed — Oscillating Cylinder
  4. Slider Block Fixed — Pendulum Pump

### Task 5 — Slider-Crank Vector Diagrams `[2 marks]`
- Takes **θ₂**, **ω₂**, **α₂** for the standard configuration
- Computes and displays **Position diagram**, **Velocity polygon**, and **Acceleration polygon**
- Includes a singularity guard at θ₃ = ±90° (dead-centre position)

### Bonus — Single Unified UI `[+1 / +2 marks]`
> All five tasks are bundled into one PyQt6 application with a tabbed interface, real-time speed slider, and Stop button. The user never needs to re-run the script between tasks.

---

## Prerequisites & Installation

### Requirements
- Python 3.9 or newer — [python.org/downloads](https://python.org/downloads)
- `pip` package manager (ships with Python 3.4+)
- A display / screen (required for the GUI window)

### Step 1 — Install dependencies

```bash
# Standard install
pip install PyQt6 numpy matplotlib

# If pip is not found
python -m pip install PyQt6 numpy matplotlib

# Using a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
pip install PyQt6 numpy matplotlib
```

### Step 2 — Run the application

```bash
# Navigate to the project directory
cd path/to/project

# Launch the simulator
python main.py

# On some systems
python3 main.py
```

> **Note:** No additional configuration files, datasets, or compiled extensions are required. The entire simulation runs from a single Python script.

---

## How to Use

| Step | Action | Expected Output |
|---|---|---|
| 1 | Select the **Four-Bar** tab | Link-length inputs and ground-link selector appear |
| 2 | Enter link lengths L1–L4 | Defaults (2, 5, 4, 5) preloaded as a valid Grashof example |
| 3 | Click **Task 1 — Animate** | Live animation starts; status bar shows Grashof type |
| 4 | Enter θ₂, ω₂, α₂ → click **Task 2** | Position + Velocity + Acceleration polygon view |
| 5 | Enter Rp, δ → click **Task 3** | Coupler curve path, \|Vp\| and \|Ap\| vs crank angle |
| 6 | Switch to **Slider-Crank** tab | Crank radius, rod length, and inversion selector appear |
| 7 | Click **Task 4 — Animate** | Selected inversion animates with rigid-body transformation |
| 8 | Enter dynamics inputs → click **Task 5** | Slider-crank vector diagram (3 panels) |
| 9 | Use **Speed slider / Stop button** | Adjust animation speed (1–10×) or halt at any frame |

---

## Mathematical Approach

### Freudenstein's Equation — Four-Bar Position Analysis

The output link angle is found by solving **Freudenstein's equation**, which reduces the vector loop closure to a single transcendental equation in the unknown angle θ₄:

```
K₁·cos(θ₄) − K₂·cos(θ₂) + K₃ = cos(θ₂ − θ₄)
```

where:

```
K₁ = d/a,   K₂ = d/c,   K₃ = (a² − b² + c² + d²) / (2ac)
```

This is cast in the half-angle tangent substitution form, yielding a quadratic in `tan(θ₄/2)`. The coupler angle θ₃ is recovered from the triangle O₂–A–B.

### Velocity & Acceleration — Matrix Method

Differentiating the vector loop equation twice gives two 2×2 linear systems of the form **[J]{dθ/dt} = {RHS}**, solved with `numpy.linalg.solve`. A singularity guard (`|det J| < 1e-8`) prevents division by zero at toggle positions. The same formulation handles the slider-crank by treating the slider as a prismatic joint.

### Coupler Point Kinematics

The coupler point **P** is defined by:

```
P = A + Rp · [cos(θ₃ + δ),  sin(θ₃ + δ)]
```

Its absolute velocity and acceleration are obtained by differentiating this expression and adding the crank-pin (A) contributions. The magnitudes |Vp| and |Ap| are swept over 360° and plotted versus input angle.

### Slider-Crank Inversions — Rigid-Body Transformations

All four inversions reuse the standard zero-offset slider-crank solution. Each inversion is rendered by applying a **rigid-body transformation** (translation to the new ground pivot + rotation by the negative of that link's current angle) to every point in the mechanism.

### Grashof Condition

For link lengths s (shortest), l (longest), p and q (intermediate):

```
Grashof condition:  s + l ≤ p + q
```

| Grounded Link | Mechanism Type | Behaviour |
|---|---|---|
| Shortest link (s) | Double Crank (Drag-Link) | Both input & output rotate 360° |
| Adjacent to s (a) | Crank-Rocker | Input rotates; output rocks |
| Opposite to s (b) | Double Rocker | Both links rock; coupler rotates |
| Adjacent to s (c) | Crank-Rocker (mirror) | Input rocks; output rotates |
| Any (s + l > p + q) | Non-Grashof — Double Rocker | Both links oscillate between limits |

---

## Edge Cases & Robustness

| Issue | How it is handled |
|---|---|
| Floating-point discriminant noise | Discriminant clamped to `max(0, disc)` so values of −1e-15 don't abort valid configs |
| Freudenstein degenerate case (A ≈ 0) | Detected; switches to linear solve `t₄ = −C/B` instead of dividing by A |
| Non-Grashof range detection | Valid angular range [lo°, hi°] pre-scanned; animation bounces cleanly within it |
| Slider-crank arcsin domain | `sin(θ₃)` clipped to [−1, 1] before `arcsin` to prevent NaN from float noise |
| Dead-centre singularity (cos θ₃ ≈ 0) | Toggle position detected; descriptive error shown instead of crash |
| Velocity/acceleration matrix singular | `|det J| < 1e-8` guard returns (0,0,0,0) at singular configurations |
| Rod shorter than crank (b < a) | Warning displayed in status bar; animation proceeds for valid range |

---

## Project Structure

```
project/
├── main.py          # Complete application — single entry point
├── README.md        # This file
└── README.pdf       # Formatted PDF version
```

---

## Scoring Alignment

| Task | Description | Marks |
|---|---|:---:|
| 1 | Four-Bar Animation (Grashof check + inversion selection) | 3 |
| 2 | Four-Bar Velocity & Acceleration Polygons | 2 |
| 3 | Coupler Curve, Velocity vs Angle, Acceleration vs Angle | 1 |
| 4 | Slider-Crank Inversions (animation of all 4) | 2 |
| 5 | Slider-Crank Velocity & Acceleration Polygons | 2 |
| **Bonus** | All tasks bundled in one seamless GUI interface | +1/+2 |
| | **Total (excluding bonus)** | **10** |

---

*ME2220 Kinematics and Dynamics of Mechanisms — IIT Hyderabad — Jan–Apr 2026*
*Simulator built with Python 3, PyQt6, NumPy, and Matplotlib*