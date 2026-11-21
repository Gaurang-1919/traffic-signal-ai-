"""
Comprehensive Benchmarking Suite.
Compares:
1. Conventional Fixed-Time Baseline (30s)
2. Unoptimized Fuzzy Logic Controller
3. Hill-Climbing Optimized Fuzzy Controller
Generates performance metrics, summary tables, and academic publication-ready plots.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from src.simulation import TrafficIntersectionSim
from src.fuzzy_controller import FuzzyTrafficController
from src.hill_climbing import HillClimbingOptimizer

def run_benchmarks(output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 60)
    print("STEP 1: Calibrating Fuzzy Controller with Hill Climbing...")
    print("=" * 60)
    
    optimizer = HillClimbingOptimizer(max_iterations=25, step_size=2.0, seed=42)
    best_theta, best_fitness, opt_history = optimizer.optimize(verbose=True)

    # Instantiate controllers
    default_fuzzy = FuzzyTrafficController()
    optimized_fuzzy = FuzzyTrafficController(best_theta)

    # Scenarios
    scenarios = {
        "Balanced Moderate": {'N': 0.16, 'S': 0.16, 'E': 0.16, 'W': 0.16},
        "Asymmetric Rush Hour": {'N': 0.26, 'S': 0.26, 'E': 0.08, 'W': 0.08},
        "High Congestion": {'N': 0.28, 'S': 0.28, 'E': 0.22, 'W': 0.22}
    }

    records = []
    timeseries_data = None

    print("\n" + "=" * 60)
    print("STEP 2: Evaluating All Controllers Across Scenarios...")
    print("=" * 60)

    for sc_name, rates in scenarios.items():
        # Fixed Time Baseline
        sim_fixed = TrafficIntersectionSim(arrival_rates=rates, seed=100)
        res_fixed = sim_fixed.run(controller_type="fixed", fixed_duration=30, total_time=600)

        # Default Fuzzy
        sim_fuzzy = TrafficIntersectionSim(arrival_rates=rates, seed=100)
        res_fuzzy = sim_fuzzy.run(controller_type="fuzzy", controller=default_fuzzy, total_time=600)

        # Optimized Fuzzy
        sim_opt = TrafficIntersectionSim(arrival_rates=rates, seed=100)
        res_opt = sim_opt.run(controller_type="fuzzy", controller=optimized_fuzzy, total_time=600)

        if sc_name == "Asymmetric Rush Hour":
            timeseries_data = {
                'fixed': res_fixed['history'],
                'fuzzy': res_fuzzy['history'],
                'opt': res_opt['history']
            }

        fixed_wait = res_fixed['avg_wait_time']
        fuzzy_red = ((fixed_wait - res_fuzzy['avg_wait_time']) / fixed_wait) * 100.0
        opt_red = ((fixed_wait - res_opt['avg_wait_time']) / fixed_wait) * 100.0

        records.append({
            'Scenario': sc_name,
            'Controller': 'Fixed-Time Baseline',
            'Avg Wait (s)': res_fixed['avg_wait_time'],
            'Max Wait (s)': res_fixed['max_wait_time'],
            'Avg Queue': res_fixed['avg_queue_length'],
            'Throughput (veh)': res_fixed['total_completed'],
            'Delay Reduction (%)': '0.0%'
        })
        records.append({
            'Scenario': sc_name,
            'Controller': 'Default Fuzzy',
            'Avg Wait (s)': res_fuzzy['avg_wait_time'],
            'Max Wait (s)': res_fuzzy['max_wait_time'],
            'Avg Queue': res_fuzzy['avg_queue_length'],
            'Throughput (veh)': res_fuzzy['total_completed'],
            'Delay Reduction (%)': f"{fuzzy_red:.1f}%"
        })
        records.append({
            'Scenario': sc_name,
            'Controller': 'Optimized Fuzzy (HC)',
            'Avg Wait (s)': res_opt['avg_wait_time'],
            'Max Wait (s)': res_opt['max_wait_time'],
            'Avg Queue': res_opt['avg_queue_length'],
            'Throughput (veh)': res_opt['total_completed'],
            'Delay Reduction (%)': f"{opt_red:.1f}%"
        })

    df = pd.DataFrame(records)
    csv_path = os.path.join(output_dir, "benchmark_summary.csv")
    df.to_csv(csv_path, index=False)
    print("\nBenchmark Results Summary Table:")
    print(df.to_string(index=False))
    print(f"\nSaved CSV summary to: {csv_path}")

    # Plot 1: Bar chart comparing average waiting times
    plt.figure(figsize=(10, 5))
    sc_list = list(scenarios.keys())
    x = np.arange(len(sc_list))
    width = 0.25

    fixed_waits = [df[(df['Scenario'] == s) & (df['Controller'] == 'Fixed-Time Baseline')]['Avg Wait (s)'].values[0] for s in sc_list]
    fuzzy_waits = [df[(df['Scenario'] == s) & (df['Controller'] == 'Default Fuzzy')]['Avg Wait (s)'].values[0] for s in sc_list]
    opt_waits = [df[(df['Scenario'] == s) & (df['Controller'] == 'Optimized Fuzzy (HC)')]['Avg Wait (s)'].values[0] for s in sc_list]

    plt.bar(x - width, fixed_waits, width, label='Fixed-Time Baseline', color='#d9534f')
    plt.bar(x, fuzzy_waits, width, label='Default Fuzzy Logic', color='#f0ad4e')
    plt.bar(x + width, opt_waits, width, label='Optimized Fuzzy (HC)', color='#5cb85c')

    plt.ylabel('Average Waiting Time (seconds)', fontsize=11, fontweight='bold')
    plt.title('Performance Comparison: Average Waiting Time Across Scenarios', fontsize=12, fontweight='bold')
    plt.xticks(x, sc_list, fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(frameon=True)
    plt.tight_layout()
    chart1_path = os.path.join(output_dir, "delay_comparison.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()

    # Plot 2: Queue evolution over time (Asymmetric Rush Hour)
    if timeseries_data:
        plt.figure(figsize=(11, 5))
        t = timeseries_data['fixed']['time'][:350]
        q_fixed = (np.array(timeseries_data['fixed']['ns_queue']) + np.array(timeseries_data['fixed']['ew_queue']))[:350]
        q_fuzzy = (np.array(timeseries_data['fuzzy']['ns_queue']) + np.array(timeseries_data['fuzzy']['ew_queue']))[:350]
        q_opt = (np.array(timeseries_data['opt']['ns_queue']) + np.array(timeseries_data['opt']['ew_queue']))[:350]

        plt.plot(t, q_fixed, label='Fixed-Time Baseline', color='#d9534f', alpha=0.85, linewidth=1.8)
        plt.plot(t, q_fuzzy, label='Default Fuzzy', color='#f0ad4e', alpha=0.85, linewidth=1.8)
        plt.plot(t, q_opt, label='Optimized Fuzzy (HC)', color='#5cb85c', linewidth=2.2)

        plt.xlabel('Simulation Time (seconds)', fontsize=11, fontweight='bold')
        plt.ylabel('Total Queue Length (vehicles)', fontsize=11, fontweight='bold')
        plt.title('Queue Accumulation Dynamics under Asymmetric Rush Hour', fontsize=12, fontweight='bold')
        plt.legend(loc='upper left', frameon=True)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        chart2_path = os.path.join(output_dir, "queue_timeseries.png")
        plt.savefig(chart2_path, dpi=300)
        plt.close()

    # Plot 3: Hill Climbing Convergence Curve
    plt.figure(figsize=(8, 4.5))
    iters = [h['iteration'] for h in opt_history]
    fits = [h['fitness'] for h in opt_history]
    plt.plot(iters, fits, marker='o', color='#0275d8', linewidth=2, markersize=5)
    plt.xlabel('Search Iterations', fontsize=11, fontweight='bold')
    plt.ylabel('Objective Fitness Score', fontsize=11, fontweight='bold')
    plt.title('Hill Climbing Search Convergence on Membership Parameters', fontsize=12, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    chart3_path = os.path.join(output_dir, "hill_climbing_convergence.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()

    print(f"Generated and saved 3 high-res charts to: {output_dir}/")
    return df, best_theta


if __name__ == "__main__":
    run_benchmarks()
