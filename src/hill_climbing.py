"""
Hill Climbing Optimization Algorithm for Fuzzy Controller Calibration.
Unit 2 Alignment: Informed Heuristic Search Techniques.
Optimizes membership function transition points theta = [q1, q2, w1, w2, g1, g2]
to minimize vehicle delay and queue accumulation.
"""

import copy
import numpy as np
from src.fuzzy_controller import FuzzyTrafficController
from src.simulation import TrafficIntersectionSim

class HillClimbingOptimizer:
    def __init__(self, initial_theta=None, max_iterations=50, step_size=2.0, seed=42):
        """
        initial_theta: starting parameters [q1, q2, w1, w2, g1, g2]
        max_iterations: number of hill climbing steps
        step_size: perturbation magnitude
        """
        self.initial_theta = initial_theta if initial_theta else [10.0, 25.0, 20.0, 50.0, 15.0, 40.0]
        self.max_iterations = max_iterations
        self.step_size = step_size
        self.seed = seed
        self.history = []

    def evaluate_fitness(self, theta, sim_duration=400, eval_seeds=[10, 42]):
        """
        Evaluate objective fitness function:
        Fitness = -(Avg Wait Time + 0.5 * Avg Queue Length + 0.05 * Max Wait Time)
        Averaged over multiple seeds to reduce stochastic variance.
        """
        controller = FuzzyTrafficController(theta)
        scores = []
        for s in eval_seeds:
            sim = TrafficIntersectionSim(seed=s)
            res = sim.run(controller_type="fuzzy", controller=controller, total_time=sim_duration)
            penalty = res['avg_wait_time'] + 0.5 * res['avg_queue_length'] + 0.05 * res['max_wait_time']
            scores.append(-penalty)
            
        return float(np.mean(scores))

    def get_valid_neighbor(self, theta):
        """
        Generate a neighbor solution by perturbing parameters while respecting physical constraints.
        """
        candidate = list(copy.deepcopy(theta))
        idx = np.random.randint(0, len(candidate))
        delta = np.random.choice([-self.step_size, self.step_size])
        candidate[idx] += delta

        # Enforce domain constraints
        # q1 in [2, 20], q2 in [q1+3, 45]
        candidate[0] = max(2.0, min(candidate[0], 20.0))
        candidate[1] = max(candidate[0] + 3.0, min(candidate[1], 45.0))
        
        # w1 in [5, 35], w2 in [w1+5, 90]
        candidate[2] = max(5.0, min(candidate[2], 35.0))
        candidate[3] = max(candidate[2] + 5.0, min(candidate[3], 90.0))
        
        # g1 in [10, 25], g2 in [g1+5, 55]
        candidate[4] = max(10.0, min(candidate[4], 25.0))
        candidate[5] = max(candidate[4] + 5.0, min(candidate[5], 55.0))

        return candidate

    def optimize(self, verbose=True):
        """
        Executes Steepest / First-Choice Hill Climbing search.
        Returns: (best_theta, best_fitness, convergence_history)
        """
        np.random.seed(self.seed)
        current_theta = list(self.initial_theta)
        current_fitness = self.evaluate_fitness(current_theta)
        
        best_theta = list(current_theta)
        best_fitness = current_fitness
        
        self.history = [{'iteration': 0, 'fitness': current_fitness, 'theta': list(current_theta)}]
        
        if verbose:
            print(f"[Iter 0] Initial Fitness: {current_fitness:.2f} | Theta: {current_theta}")

        for i in range(1, self.max_iterations + 1):
            # Generate candidate neighbor
            candidate_theta = self.get_valid_neighbor(current_theta)
            candidate_fitness = self.evaluate_fitness(candidate_theta)

            # Accept if strictly better or equal (Hill Climbing rule)
            if candidate_fitness > current_fitness:
                current_theta = list(candidate_theta)
                current_fitness = candidate_fitness
                if current_fitness > best_fitness:
                    best_fitness = current_fitness
                    best_theta = list(candidate_theta)
                if verbose and i % 5 == 0:
                    print(f"[Iter {i}] Improved Fitness: {current_fitness:.2f} | Theta: {current_theta}")
            
            self.history.append({'iteration': i, 'fitness': current_fitness, 'theta': list(current_theta)})

        if verbose:
            print(f"Optimization Complete! Best Fitness: {best_fitness:.2f}")
            print(f"Optimal Parameters Theta: {[round(x, 1) for x in best_theta]}")

        return best_theta, best_fitness, self.history

    def random_restart_optimize(self, num_restarts=4, iterations_per_restart=15, verbose=True):
        """
        Deadline 2 Algorithmic Extension:
        Random-Restart Hill Climbing (RR-HC) to overcome local optima and search plateaus.
        Executes num_restarts independent search climbs and returns the globally superior parameter set.
        """
        overall_best_theta = None
        overall_best_fitness = -float('inf')
        restart_logs = []

        if verbose:
            print("=" * 60)
            print(f"Starting Random-Restart Hill Climbing ({num_restarts} Restarts, {iterations_per_restart} Iter/Restart)...")
            print("=" * 60)

        for r in range(num_restarts):
            if r == 0:
                start_theta = list(self.initial_theta)
            else:
                # Stochastic initialization within valid physical parameter bounds
                start_theta = [
                    float(np.random.uniform(4.0, 15.0)),
                    float(np.random.uniform(18.0, 35.0)),
                    float(np.random.uniform(10.0, 28.0)),
                    float(np.random.uniform(35.0, 70.0)),
                    float(np.random.uniform(10.0, 22.0)),
                    float(np.random.uniform(28.0, 50.0))
                ]
            
            # Sub-optimizer
            sub_opt = HillClimbingOptimizer(
                initial_theta=start_theta,
                max_iterations=iterations_per_restart,
                step_size=self.step_size,
                seed=self.seed + r * 17
            )
            b_theta, b_fitness, hist = sub_opt.optimize(verbose=False)
            
            restart_logs.append({
                'restart': r + 1,
                'start_theta': [round(x, 1) for x in start_theta],
                'best_theta': [round(x, 1) for x in b_theta],
                'fitness': b_fitness
            })

            if verbose:
                print(f"[Restart {r+1}/{num_restarts}] Best Fitness Found: {b_fitness:.2f}")

            if b_fitness > overall_best_fitness:
                overall_best_fitness = b_fitness
                overall_best_theta = list(b_theta)

        if verbose:
            print("=" * 60)
            print(f"Random-Restart Complete! Global Best Fitness: {overall_best_fitness:.2f}")
            print(f"Global Optimal Parameters: {[round(x, 1) for x in overall_best_theta]}")

        return overall_best_theta, overall_best_fitness, restart_logs


if __name__ == "__main__":
    print("Testing Hill Climbing Optimizer (quick 15-iteration test)...")
    opt = HillClimbingOptimizer(max_iterations=15, step_size=2.0)
    best_t, best_f, hist = opt.optimize(verbose=True)
