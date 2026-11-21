# 🚦 Intelligent Traffic Signal Optimization Using Fuzzy Logic and Hill Climbing

An Artificial Intelligence course project combining **Reasoning Under Uncertainty (Mamdani Fuzzy Logic)** and **Informed Heuristic Search (Hill Climbing Optimization)** for adaptive traffic intersection signal control.

---

## 📌 Project Highlights
* **Rubric Weightage:** 10 Points
* **Core Syllabus Alignment:**
  * **Unit 2 (Informed Search Techniques):** Hill Climbing parameter optimizer with multi-objective fitness formulation.
  * **Unit 4 (Reasoning Under Uncertainty):** Mamdani Fuzzy Inference System (Fuzzification $\to$ 9 Linguistic Rules $\to$ Centroid Defuzzification).
* **Key Result:** Achieves **24.1% reduction in average vehicle waiting time** during rush-hour traffic and reduces maximum delay by 23 seconds compared to conventional fixed-time baseline signals.

---

## 📂 Project Directory Structure

```text
traffic_signal_ai/
│
├── src/
│   ├── simulation.py          # 4-way intersection microscopic simulator (Poisson arrivals, queues, signals)
│   ├── fuzzy_controller.py   # Mamdani Fuzzy Logic Controller (membership sets, 9 rules, centroid defuzzifier)
│   ├── hill_climbing.py       # Heuristic search optimizer for controller calibration
│   └── benchmark.py           # Automated evaluation suite across 3 traffic scenarios
│
├── results/                   # Generated evaluation artifacts
│   ├── benchmark_summary.csv  # Full tabular comparison metrics
│   ├── delay_comparison.png   # High-resolution bar chart comparing average delays
│   ├── queue_timeseries.png   # Vehicle queue evolution over 600 seconds
│   └── hill_climbing_convergence.png # Optimization fitness improvement curve
│
├── docs/
│   ├── PROJECT_REPORT.md      # Formal 4-5 page academic project report matching all rubric points
│   ├── PRESENTATION_SLIDES.md # 10-slide deck text with full speaker notes for oral defense
│   └── DEMO_SCRIPT.md         # 2-3 minute video demonstration walkthrough script
│
├── app.py                     # Interactive Streamlit Web Dashboard
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation & quickstart guide
```

---

## ⚡ Quickstart Guide

### 1. Installation
Ensure Python 3.10+ is installed. Open PowerShell / Command Prompt and install dependencies:
```bash
cd traffic_signal_ai
pip install -r requirements.txt
```

### 2. Run the Benchmark Suite
Executes the Hill Climbing optimization and benchmarks all 3 controllers across Balanced, Rush-Hour, and High-Congestion scenarios:
```bash
python -m src.benchmark
```
*Outputs are saved directly to `results/`.*

### 3. Launch the Interactive Web Dashboard
Launches the real-time simulation and comparison interface in your browser:
```bash
streamlit run app.py
```
Open `http://localhost:8501` to test custom traffic arrival rates, inspect queue dynamics, and view the fuzzy rule base.

---

## 📋 Evaluation Rubric Mapping (10 Points)

| Rubric Item | Weight | Project Deliverable / File |
| :--- | :---: | :--- |
| **Project Idea** | 1.5 Pts | Detailed in `docs/PROJECT_REPORT.md` (Section 1) & `docs/PRESENTATION_SLIDES.md` (Slide 2). |
| **Research Background** | 1.5 Pts | Historical review & literature survey in `docs/PROJECT_REPORT.md` (Section 2) citing Zadeh (1965), Webster (1958), and MDPI (2026). |
| **Algorithm Selection & Rationale** | 3.0 Pts | Mathematical rationale for Fuzzy Logic & Hill Climbing in `docs/PROJECT_REPORT.md` (Section 3). |
| **Implementation Work** | 3.0 Pts | Complete modular Python codebase (`src/simulation.py`, `src/fuzzy_controller.py`, `src/hill_climbing.py`, `app.py`). |
| **Teamwork** | 1.0 Pt | 4-member contribution matrix in `docs/PROJECT_REPORT.md` (Section 6). |
| **References** | Mandatory | 5 formal IEEE/ACM citations in Section 8 of the report. |

---

## 📅 Submission Guidelines (Deadlines 1 & 2)

* **Deadline 1 (60% Work):**
  * Submit the initial 3-page report draft covering Sections 1 to 4.
  * Code submission: `src/simulation.py` and `src/fuzzy_controller.py` demonstrating baseline vs. unoptimized fuzzy control.
* **Deadline 2 (40% Work):**
  * Submit the finalized 5-page report (`docs/PROJECT_REPORT.md`) or PPT (`docs/PRESENTATION_SLIDES.md`).
  * Final code with Hill Climbing optimizer (`src/hill_climbing.py`) and Streamlit App (`app.py`).
  * *(Optional)* 2-3 minute screen recording following `docs/DEMO_SCRIPT.md`.
