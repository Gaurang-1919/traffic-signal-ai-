"""
Fuzzy Logic Controller for Traffic Signal Timing Optimization.
Unit 4 Alignment: Reasoning under Uncertainty.
Implements a Mamdani Fuzzy Inference System (Fuzzification -> Min-Max Inference -> Centroid Defuzzification).
"""

import numpy as np

class FuzzyTrafficController:
    """
    Fuzzy Logic Controller that determines the optimal green light phase duration
    based on current queue length and waiting time of approaching vehicles.
    
    Parameters:
    - theta: List/Array of 6 calibration parameters [q1, q2, w1, w2, g1, g2]
      which define the membership function transition points.
    """
    def __init__(self, theta=None):
        # Default membership cutoff parameters:
        # Queue: Low <= q1, Med around (q1+q2)/2, High >= q2
        # Wait: Short <= w1, Med around (w1+w2)/2, Long >= w2
        # Green: Short <= g1, Med around (g1+g2)/2, Long >= g2
        if theta is None:
            # Default hand-tuned parameters
            self.theta = [10.0, 25.0, 20.0, 50.0, 15.0, 40.0]
        else:
            self.theta = list(theta)
            
        self._unpack_params()

    def _unpack_params(self):
        self.q1, self.q2 = self.theta[0], self.theta[1]
        self.w1, self.w2 = self.theta[2], self.theta[3]
        self.g1, self.g2 = self.theta[4], self.theta[5]
        
        # Enforce bounds
        self.q1 = max(2.0, min(self.q1, self.q2 - 2.0))
        self.w1 = max(5.0, min(self.w1, self.w2 - 5.0))
        self.g1 = max(10.0, min(self.g1, self.g2 - 5.0))
        self.g2 = min(60.0, max(self.g2, self.g1 + 5.0))

    def update_params(self, new_theta):
        """Update controller parameters (used by Hill Climbing optimizer)."""
        self.theta = list(new_theta)
        self._unpack_params()

    # --- Membership Functions (Fuzzification) ---
    @staticmethod
    def _trap_left(x, a, b):
        """Left-trapezoidal membership function (Low / Short)."""
        if x <= a:
            return 1.0
        elif x >= b:
            return 0.0
        else:
            return (b - x) / (b - a)

    @staticmethod
    def _triangular(x, a, b, c):
        """Triangular membership function (Medium)."""
        if x <= a or x >= c:
            return 0.0
        elif x == b:
            return 1.0
        elif a < x < b:
            return (x - a) / (b - a)
        else:
            return (c - x) / (c - b)

    @staticmethod
    def _trap_right(x, a, b):
        """Right-trapezoidal membership function (High / Long)."""
        if x <= a:
            return 0.0
        elif x >= b:
            return 1.0
        else:
            return (x - a) / (b - a)

    def fuzzify_queue(self, q):
        """Calculate membership degrees for Queue Length."""
        q_mid = (self.q1 + self.q2) / 2.0
        low = self._trap_left(q, self.q1 * 0.5, self.q1)
        med = self._triangular(q, self.q1 * 0.7, q_mid, self.q2 * 1.2)
        high = self._trap_right(q, self.q2 * 0.8, self.q2 * 1.3)
        return {'LOW': low, 'MEDIUM': med, 'HIGH': high}

    def fuzzify_wait(self, w):
        """Calculate membership degrees for Waiting Time."""
        w_mid = (self.w1 + self.w2) / 2.0
        short = self._trap_left(w, self.w1 * 0.5, self.w1)
        med = self._triangular(w, self.w1 * 0.7, w_mid, self.w2 * 1.2)
        long_val = self._trap_right(w, self.w2 * 0.8, self.w2 * 1.3)
        return {'SHORT': short, 'MEDIUM': med, 'LONG': long_val}

    def infer_and_defuzzify(self, queue_len, avg_wait_time):
        """
        Evaluate Mamdani Fuzzy Rules and calculate defuzzified green duration.
        Rules:
        R1: IF queue is LOW and wait is SHORT -> green is SHORT
        R2: IF queue is LOW and wait is MEDIUM -> green is SHORT
        R3: IF queue is LOW and wait is LONG -> green is MEDIUM
        R4: IF queue is MEDIUM and wait is SHORT -> green is SHORT
        R5: IF queue is MEDIUM and wait is MEDIUM -> green is MEDIUM
        R6: IF queue is MEDIUM and wait is LONG -> green is LONG
        R7: IF queue is HIGH and wait is SHORT -> green is MEDIUM
        R8: IF queue is HIGH and wait is MEDIUM -> green is LONG
        R9: IF queue is HIGH and wait is LONG -> green is LONG
        """
        q_mem = self.fuzzify_queue(queue_len)
        w_mem = self.fuzzify_wait(avg_wait_time)

        # Rule evaluation (Mamdani Min operator for AND)
        act_short = max(
            min(q_mem['LOW'], w_mem['SHORT']),
            min(q_mem['LOW'], w_mem['MEDIUM']),
            min(q_mem['MEDIUM'], w_mem['SHORT'])
        )
        
        act_med = max(
            min(q_mem['LOW'], w_mem['LONG']),
            min(q_mem['MEDIUM'], w_mem['MEDIUM']),
            min(q_mem['HIGH'], w_mem['SHORT'])
        )
        
        act_long = max(
            min(q_mem['MEDIUM'], w_mem['LONG']),
            min(q_mem['HIGH'], w_mem['MEDIUM']),
            min(q_mem['HIGH'], w_mem['LONG'])
        )

        # Centroid Defuzzification over domain [10s, 60s]
        x_vals = np.linspace(10.0, 60.0, 101)
        g_mid = (self.g1 + self.g2) / 2.0

        # Aggregated output fuzzy set (Clipping using Mamdani Min-Max)
        y_short = np.array([min(act_short, self._trap_left(x, 10.0, self.g1)) for x in x_vals])
        y_med   = np.array([min(act_med, self._triangular(x, self.g1 * 0.8, g_mid, self.g2 * 1.2)) for x in x_vals])
        y_long  = np.array([min(act_long, self._trap_right(x, self.g2 * 0.8, 60.0)) for x in x_vals])

        aggregated = np.maximum(y_short, np.maximum(y_med, y_long))
        
        total_area = np.sum(aggregated)
        if total_area == 0:
            # Fallback to midpoint green duration
            return 30.0

        # Centroid formula: Sum(x * mu(x)) / Sum(mu(x))
        centroid = np.sum(x_vals * aggregated) / total_area
        return float(np.clip(centroid, 10.0, 60.0))

    def compute_green_duration(self, queue_len, avg_wait_time):
        """Public API returning rounded green light duration in seconds."""
        duration = self.infer_and_defuzzify(queue_len, avg_wait_time)
        return int(round(duration))


if __name__ == "__main__":
    controller = FuzzyTrafficController()
    test_cases = [
        (5, 10, "Low traffic, low wait"),
        (20, 30, "Medium traffic, medium wait"),
        (45, 65, "Heavy traffic, high wait"),
        (5, 80, "Low queue, high starvation wait")
    ]
    print("--- Fuzzy Controller Test Cases ---")
    for q, w, desc in test_cases:
        dur = controller.compute_green_duration(q, w)
        print(f"[{desc}] Queue: {q}, Wait: {w}s -> Green Duration: {dur}s")
