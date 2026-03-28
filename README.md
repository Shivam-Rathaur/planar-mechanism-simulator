# Planar Mechanism Simulator

**Course:** ME2220 - Kinematics and Dynamics of Mechanisms  
**Institute:** Indian Institute of Technology Hyderabad  
**Semester:** January - April 2026  

A single-file Python desktop application that simulates, animates, and analyses two fundamental planar mechanisms - the **Four-Bar Linkage** and the **Slider-Crank Mechanism** - covering all five course project tasks inside one tabbed GUI.

---

## Demonstration

### Four-Bar Mechanism

**Task 1: Live Animation with Grashof Classification**  
![Task 1 - Four-Bar Animation](docs/task1_fourbar_animation.png)
> Crank-Rocker configuration (Link 4 grounded, L1=2, L2=5, L3=4, L4=5). The status bar and plot title show the automatically detected Grashof type. Animation bounces smoothly at toggle positions for rocking mechanisms.

---

**Task 2: Velocity & Acceleration Polygon Diagrams**  
![Task 2 - Velocity and Acceleration Polygons](docs/task2_velocity_acceleration_polygons.png)
> At θ₂ = 60°, ω₂ = 10 rad/s, α₂ = 0. Left: position diagram with ground pins. Middle: velocity polygon (Vₐ, V_b, V_ba). Right: acceleration polygon (Aₐ, A_b, A_ba). All vectors drawn to scale with magnitudes labelled.

---

**Task 3: Coupler Curve Path + |Vp| and |Ap| vs θ₂**  
![Task 3 - Coupler Curve](docs/task3_coupler_curve.png)
> Coupler point P traced with Rp = 3.0, δ = 30°, sweeping all 360 valid crank positions. Left: the coupler curve path (figure-eight shape). Middle: |Vp| vs θ₂. Right: |Ap| vs θ₂. NaN gaps are inserted near toggle positions instead of unphysical spikes.

---

### Slider-Crank Mechanism

**Task 4: Animated Slider-Crank (Standard Inversion)**  
![Task 4 - Slider-Crank Animation](docs/task4_slidercrank_animation.png)
> Inversion 1 (Standard — frame fixed, piston engine layout). Crank radius a = 2.0, connecting rod b = 6.0. The slider block moves horizontally along the sliding axis as the crank rotates.

---

**Task 5: Slider-Crank Velocity & Acceleration Polygons**  
![Task 5 - Slider Vel Acc Polygons](docs/task5_slider_vel_acc_polygons.png)
> At θ₂ = 60°, ω₂ = 10 rad/s, α₂ = 0. Status bar reports θ₃ = −16.78°, ω₃ = −1.741 rad/s, V_slider = −20.336 units/s, A_slider = −66.767 units/s². Left: mechanism position. Middle: velocity polygon. Right: acceleration polygon.

---

## 🗂️ Project Structure

```
planar-mechanism-simulator/
│
├── mechanism_simulator.py                  # main application (run this)
├── requirements.txt                        # python dependencies
├── README.md                               # this file
└── docs/
    ├── task1_fourbar_animation.png
    ├── task2_velocity_acceleration_polygons.png
    ├── task3_coupler_curve.png
    ├── task4_slidercrank_animation.png
    └── task5_slider_vel_acc_polygons.png
```

---

## ✨ Features

### Four-Bar Linkage (Tasks 1 – 3)

| Task | Description |
|------|-------------|
| **Task 1** | Live animation of the four-bar linkage. Automatically detects the **Grashof condition**, classifies the mechanism type (Double Crank, Crank-Rocker, Double Rocker, Non-Grashof), and animates either full rotation or smooth rocking — with no abrupt jumps at toggle positions. |
| **Task 2** | Static **velocity and acceleration polygon** diagrams at a user-specified crank angle θ₂, angular velocity ω₂, and angular acceleration α₂. Drawn as proper vector arrows with magnitudes. |
| **Task 3** | **Coupler curve** path traced by a point P rigidly attached to the coupler, defined by distance Rp and offset angle δ. Also plots \|Vp\| and \|Ap\| vs θ₂ across the full valid range, with NaN gaps at toggle positions instead of unphysical spikes. |

### Slider-Crank Mechanism (Tasks 4 – 5)

| Task | Description |
|------|-------------|
| **Task 4** | Animated simulation of all **four kinematic inversions**: Standard (piston engine), Rotary/Gnome Engine, Oscillating Cylinder, and Pendulum Pump. Each inversion is implemented as a rigid-body coordinate transform. |
| **Task 5** | Static **velocity and acceleration polygon** at a given θ₂, showing crank velocity VA, slider velocity VB, and the relative velocity/acceleration vectors. |

---

## 🔢 Mathematics

### Position Analysis — Freudenstein's Equation
The four-bar vector loop equation  
`a·e^(jθ₂) + b·e^(jθ₃) − c·e^(jθ₄) − d = 0`  
is reduced to a scalar quadratic in `t = tan(θ₄/2)` via the Weierstrass substitution:

```
A·t² + B·t + C = 0

where:
  K₁ = d/a,  K₂ = d/c,  K₃ = (a² − b² + c² + d²) / (2ac)
  A  = cos(θ₂) − K₁ − K₂·cos(θ₂) + K₃
  B  = −2·sin(θ₂)
  C  = K₁ − (K₂ + 1)·cos(θ₂) + K₃
```

The discriminant `disc = B² − 4AC` determines whether a real solution (valid assembly) exists.

### Velocity & Acceleration — 2×2 Jacobian Method
Differentiating the vector loop equation once (velocity) and twice (acceleration) yields the same 2×2 linear system:

```
[−b·sin(θ₃)   c·sin(θ₄)] [ω₃]   [RHS_vel]
[ b·cos(θ₃)  −c·cos(θ₄)] [ω₄] =

RHS_vel = [ a·ω₂·sin(θ₂),  −a·ω₂·cos(θ₂) ]
RHS_acc = [ a·α₂·sin(θ₂) + a·ω₂²·cos(θ₂) + b·ω₃²·cos(θ₃) − c·ω₄²·cos(θ₄),
           −a·α₂·cos(θ₂) + a·ω₂²·sin(θ₂) + b·ω₃²·sin(θ₃) − c·ω₄²·sin(θ₄) ]
```

Solved via `numpy.linalg.solve` at each configuration.

### Coupler Point Kinematics
```
P  = A + Rp·[cos(θ₃ + δ),  sin(θ₃ + δ)]
Vp = VA + Rp·ω₃·[−sin(θ₃ + δ),  cos(θ₃ + δ)]
Ap = AA + Rp·[−α₃·sin(θ₃+δ) − ω₃²·cos(θ₃+δ),
               α₃·cos(θ₃+δ) − ω₃²·sin(θ₃+δ)]
```

### Grashof Condition
```
s + l ≤ p + q   →   Grashof (at least one full rotation possible)
s + l  > p + q  →   Non-Grashof (both links rock)

where s = shortest link,  l = longest link,  p, q = the other two.
```

---

## 🖥️ Input Reference

| Field | Symbol | Units | Description |
|-------|--------|-------|-------------|
| L1 – L4 | d, a, b, c | length units | Ground, crank, coupler, rocker link lengths |
| Ground Link | — | — | Which of the four links is fixed to the frame |
| θ₂ | theta2 | degrees | Crank angle at the analysis instant (Tasks 2 & 3) |
| ω₂ | omega2 | rad/s | Crank angular velocity — the known input speed |
| α₂ | alpha2 | rad/s² | Crank angular acceleration (0 = constant speed) |
| Rp | Rp | length units | Distance from joint A to the traced coupler point P |
| δ | delta | degrees | Angle of Rp vector relative to coupler link direction |
| Crank Radius a | a | length units | Crank arm length for the slider-crank |
| Connecting Rod b | b | length units | Rod length for the slider-crank |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10 or newer**
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/planar-mechanism-simulator.git
cd planar-mechanism-simulator

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the simulator
python simulator.py
```

### requirements.txt

```
PyQt6>=6.4.0
numpy>=1.24.0
matplotlib>=3.7.0
```

---

## 🎮 How to Use

### Four-Bar Tab

1. Set **L1 – L4** to your desired link lengths.
2. Choose which link is the **Ground Link** from the drop-down.
3. Click **Task 1** to start the animation. The status bar shows the Grashof classification automatically.
4. For **Task 2**, set θ₂, ω₂, α₂ and click the button. Three panels appear: position diagram, velocity polygon, and acceleration polygon.
5. For **Task 3**, also set **Rp** and **δ**, then click the button. Three panels appear: coupler curve path, |Vp| vs θ₂, and |Ap| vs θ₂.
6. Use the **Speed** slider to slow down or speed up the animation.
7. Click **Stop** to freeze the mechanism at the current frame.

### Slider-Crank Tab

1. Set the **Crank Radius (a)** and **Connecting Rod (b)**.
2. Choose the **Inversion** from the drop-down (1 = standard piston engine).
3. Click **Task 4** to start the animation.
4. For **Task 5**, set θ₂, ω₂, α₂ and click the button.

---

## ⚠️ Edge Cases Handled

| Situation | How it is handled |
|-----------|-------------------|
| Non-Grashof / rocking mechanisms | Bounces within the first contiguous valid angular segment only — no jumps between open and crossed assembly modes |
| Near-toggle singularity (Task 3) | `disc < 0.30` → `NaN` inserted in Vp/Ap; Matplotlib renders a clean gap instead of a spike |
| Degenerate Freudenstein (`A ≈ 0`) | Falls back to linear solution `t = −C/B` |
| Singular velocity Jacobian | `abs(det(J)) < 1e-8` guard returns zeros gracefully |
| arcsin domain errors in slider-crank | `np.clip(−Ay/b, −1, 1)` before `arcsin` |
| `cos(θ₃) ≈ 0` in Task 5 | Explicit guard with user-friendly status-bar error message |
| Windows DPI scaling font warning | All font sizes use `pt` units instead of `px` |
| Mechanism cannot assemble | `calc_fourbar` returns `None`; animation frame is silently skipped |

---

## 📐 Scoring Breakdown

| Task | Marks | What is demonstrated |
|------|-------|----------------------|
| Task 1 — Four-Bar Animation | 3 | Grashof check, position analysis, live animation |
| Task 2 — Vel & Acc Polygons | 2 | Jacobian method, vector polygon diagrams |
| Task 3 — Coupler Curves | 1 | Coupler-point kinematics, path and kinematic plots |
| Task 4 — Slider-Crank Inversions | 2 | All four inversions, rigid-body transform |
| Task 5 — Slider Vel & Acc | 2 | Scalar slider-crank analysis, polygon diagrams |
| **Bonus — Unified GUI** | **1–2** | All tasks in one window, dark theme, speed control |
| **Total** | **10 + 2** | |

---

## 🛠️ Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| [PyQt6](https://pypi.org/project/PyQt6/) | ≥ 6.4 | GUI framework — window, widgets, animation timer |
| [NumPy](https://numpy.org/) | ≥ 1.24 | Array maths, trigonometry, `linalg.solve` |
| [Matplotlib](https://matplotlib.org/) | ≥ 3.7 | All plots, embedded inside the Qt window |

---

## 📚 References

- Norton, R. L. — *Design of Machinery*, 5th Edition (McGraw-Hill)
- Shigley, J. E. — *Theory of Machines and Mechanisms*
- ME2220 Course Notes — IIT Hyderabad, Jan–Apr 2026
- Freudenstein, F. (1955) — "Approximate Synthesis of Four-Bar Linkages", *ASME Transactions*

---

## 👤 Author

**[Your Name]**  
B.Tech, Department of Mechanical & Aerospace Engineering  
Indian Institute of Technology Hyderabad  
[your.email@iith.ac.in]

---

## 📄 License

This project was submitted as part of a university course assignment.  
You are welcome to study, reference, or build upon this code with attribution.
