# VIDEO DEMO SCRIPT (2 to 3 Minutes)

## Intelligent Traffic Signal Optimization Using Fuzzy Logic and Hill Climbing
**Deliverable:** Optional Video Demonstration for Deadlines 1 & 2

---

### Video Overview
* **Target Duration:** 2 minutes 30 seconds
* **Tools to Record:** OBS Studio, Windows Xbox Game Bar (`Win + G`), or Loom.
* **Recording Layout:** Fullscreen browser showing the Streamlit Dashboard (`http://localhost:8501`), with occasional switches to terminal/benchmark plots.

---

### Step-by-Step Script & Actions

#### [0:00 - 0:30] Introduction & Problem Setup
* **Screen:** Show Slide 1 or the top header of the Streamlit App (`app.py`).
* **Speaker:**
  > "Hello everyone. Today we are presenting our AI course project: **Intelligent Traffic Signal Optimization using Fuzzy Logic and Hill Climbing**.
  > Traditional traffic lights use static timers that cause significant delays, especially during rush hour when one road is packed and the crossroad is empty.
  > Our project solves this by combining two key AI techniques: **Fuzzy Logic** for real-time dynamic decision making, and **Hill Climbing** to automatically optimize the controller's parameters."

#### [0:30 - 1:15] Demonstrating the Simulation & Baseline vs. Fuzzy
* **Screen:** Streamlit Dashboard.
  1. Point to the sidebar: select the preset **"Asymmetric Rush Hour (Heavy NS)"**.
  2. Click the red **"🚀 Run Live Traffic Simulation"** button.
  3. Watch the progress bar complete and the KPI cards appear.
* **Speaker:**
  > "In our dashboard, we simulate a realistic 4-way intersection. Notice the preset we've chosen: Asymmetric Rush Hour, where North and South have heavy traffic, while East and West have light traffic.
  > Under the conventional Fixed-Time baseline, vehicles wait an average of **33.6 seconds**.
  > However, our Fuzzy Logic Controller automatically senses queue lengths and vehicle waiting times, extending the green light for the busy corridor and cutting the green light on empty lanes.
  > With Hill-Climbing optimization, the average waiting time drops to **25.5 seconds**—a **24.1% reduction in traffic delay**!"

#### [1:15 - 1:55] Inspecting Queue Dynamics & Rule Base
* **Screen:** 
  1. Click on **Tab 2: "📈 Queue Dynamics Over Time"**. Hover over the green line (Optimized Fuzzy) vs. the red line (Fixed-Time Baseline).
  2. Switch to **Tab 3: "🧠 Fuzzy Rule Base & Architecture"**.
* **Speaker:**
  > "Looking at the queue dynamics over time, the red line shows fixed-time signals accumulating massive queues of over 40 vehicles. The green line shows our optimized fuzzy controller keeping the accumulated queue consistently under 20 vehicles.
  > Under Tab 3, you can see our 9 Mamdani linguistic rules. The system evaluates queue density and waiting time, using centroid defuzzification to determine the precise green duration between 10 and 60 seconds."

#### [1:55 - 2:30] Hill Climbing Convergence & Conclusion
* **Screen:** Display `results/hill_climbing_convergence.png` and `results/delay_comparison.png` or the terminal benchmark table.
* **Speaker:**
  > "Finally, our Hill Climbing algorithm automatically tuned the controller boundaries across 25 iterations, improving the objective fitness score from -23.6 to -19.5.
  > In conclusion, our system proves that combining heuristic search with fuzzy reasoning achieves real-time, explainable, and significant traffic delay reductions without the overhead of deep neural networks.
  > Thank you!"

---

### Tips for High Marks
1. Speak clearly and maintain an enthusiastic pace.
2. Ensure the Streamlit dashboard is running in full screen (`streamlit run app.py`).
3. Keep the video under 3 minutes—professors grade faster when the video is concise and packed with metrics!
