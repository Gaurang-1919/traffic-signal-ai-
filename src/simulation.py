"""
Microscopic Traffic Intersection Simulator for 4-Way Signalized Intersection.
Simulates vehicle arrivals, queuing dynamics, signal phase switching, and performance metrics.
"""

import numpy as np

class Vehicle:
    def __init__(self, arrival_time, is_emergency=False):
        self.arrival_time = arrival_time
        self.departure_time = None
        self.is_emergency = is_emergency

    @property
    def waiting_time(self):
        return self.departure_time - self.arrival_time if self.departure_time else 0.0


class Approach:
    def __init__(self, name, arrival_rate):
        self.name = name
        self.arrival_rate = arrival_rate  # avg vehicles per second (Poisson parameter lambda)
        self.queue = []                   # active waiting vehicles
        self.completed_vehicles = []      # vehicles that crossed

    def step_arrival(self, current_time, dt=1.0, emergency_prob=0.01):
        """Simulate stochastic Poisson arrival with optional Emergency Vehicle spawning."""
        k = np.random.poisson(self.arrival_rate * dt)
        for _ in range(k):
            is_ev = (np.random.uniform(0, 1) < emergency_prob)
            self.queue.append(Vehicle(arrival_time=current_time, is_emergency=is_ev))

    def has_emergency(self):
        """Check if any waiting vehicle in queue is an Emergency Vehicle."""
        return any(v.is_emergency for v in self.queue)

    def step_discharge(self, current_time, discharge_capacity):
        """Discharge up to discharge_capacity vehicles during green phase."""
        discharged = 0
        while self.queue and discharged < discharge_capacity:
            veh = self.queue.pop(0)
            veh.departure_time = current_time
            self.completed_vehicles.append(veh)
            discharged += 1
        return discharged

    def get_avg_wait(self, current_time):
        """Return average wait time of currently waiting vehicles."""
        if not self.queue:
            return 0.0
        waits = [current_time - v.arrival_time for v in self.queue]
        return float(np.mean(waits))

    def get_max_wait(self, current_time):
        """Return maximum wait time of the oldest vehicle currently waiting."""
        if not self.queue:
            return 0.0
        return float(current_time - self.queue[0].arrival_time)


class TrafficIntersectionSim:
    """
    Simulates a 4-way intersection (North, South, East, West) with 2 primary phases:
    - Phase 0: North-South Green (East-West Red)
    - Phase 1: East-West Green (North-South Red)
    Between green phases, a 3-second Yellow clearance phase is enforced.
    """
    def __init__(self, arrival_rates=None, yellow_time=3, discharge_rate=0.5, seed=42):
        """
        arrival_rates: dict with keys 'N', 'S', 'E', 'W' (vehicles per second).
        discharge_rate: vehicles discharged per second per approach during green light.
        """
        if seed is not None:
            np.random.seed(seed)
            
        default_rates = {'N': 0.18, 'S': 0.18, 'E': 0.12, 'W': 0.12}
        self.arrival_rates = arrival_rates if arrival_rates else default_rates
        self.yellow_time = yellow_time
        self.discharge_rate = discharge_rate
        
        self.approaches = {
            'N': Approach('North', self.arrival_rates['N']),
            'S': Approach('South', self.arrival_rates['S']),
            'E': Approach('East', self.arrival_rates['E']),
            'W': Approach('West', self.arrival_rates['W'])
        }

    def run(self, controller_type="fixed", controller=None, total_time=600, fixed_duration=30, enable_emergency_preemption=True):
        """
        Run simulation for total_time seconds.
        controller_type: "fixed" or "fuzzy"
        controller: instance of FuzzyTrafficController if controller_type=="fuzzy"
        enable_emergency_preemption: whether emergency vehicle priority preemption is active
        """
        current_time = 0
        current_phase = 0  # 0: NS Green, 1: EW Green
        phase_time_remaining = fixed_duration
        in_yellow = False
        min_green_enforced = 10
        green_elapsed = 0
        
        # History metrics for plotting/analysis
        history = {
            'time': [],
            'ns_queue': [],
            'ew_queue': [],
            'current_phase': [],
            'ns_wait': [],
            'ew_wait': [],
            'emergency_events': []
        }
        
        # Decide initial green duration
        if controller_type == "fuzzy" and controller is not None:
            q_ns = len(self.approaches['N'].queue) + len(self.approaches['S'].queue)
            w_ns = max(self.approaches['N'].get_avg_wait(0), self.approaches['S'].get_avg_wait(0))
            phase_time_remaining = controller.compute_green_duration(q_ns, w_ns)
        else:
            phase_time_remaining = fixed_duration

        while current_time < total_time:
            # 1. Vehicle arrivals on all approaches (with 1.5% emergency vehicle probability)
            for app in self.approaches.values():
                app.step_arrival(current_time, dt=1.0, emergency_prob=0.015)

            # Check for Emergency Vehicle Preemption
            ns_has_ev = self.approaches['N'].has_emergency() or self.approaches['S'].has_emergency()
            ew_has_ev = self.approaches['E'].has_emergency() or self.approaches['W'].has_emergency()

            # Preemption Logic (Deadline 2 feature)
            if enable_emergency_preemption and controller_type == "fuzzy":
                # If opposing phase has EV and current phase has run for at least min_green, preempt
                if current_phase == 0 and ew_has_ev and not in_yellow and green_elapsed >= min_green_enforced:
                    in_yellow = True
                    phase_time_remaining = self.yellow_time
                    history['emergency_events'].append({'time': current_time, 'phase': 'EW_Preempt'})
                elif current_phase == 1 and ns_has_ev and not in_yellow and green_elapsed >= min_green_enforced:
                    in_yellow = True
                    phase_time_remaining = self.yellow_time
                    history['emergency_events'].append({'time': current_time, 'phase': 'NS_Preempt'})

            # 2. Vehicle discharge on active approaches (if not in yellow clearance)
            if not in_yellow:
                active_keys = ['N', 'S'] if current_phase == 0 else ['E', 'W']
                discharge_capacity = int(np.floor(self.discharge_rate * 1.0 + np.random.uniform(0, 1)))
                for k in active_keys:
                    self.approaches[k].step_discharge(current_time, discharge_capacity)
                green_elapsed += 1
            else:
                green_elapsed = 0

            # 3. Log history
            ns_q = len(self.approaches['N'].queue) + len(self.approaches['S'].queue)
            ew_q = len(self.approaches['E'].queue) + len(self.approaches['W'].queue)
            ns_w = max(self.approaches['N'].get_avg_wait(current_time), self.approaches['S'].get_avg_wait(current_time))
            ew_w = max(self.approaches['E'].get_avg_wait(current_time), self.approaches['W'].get_avg_wait(current_time))

            history['time'].append(current_time)
            history['ns_queue'].append(ns_q)
            history['ew_queue'].append(ew_q)
            history['ns_wait'].append(ns_w)
            history['ew_wait'].append(ew_w)
            history['current_phase'].append(-1 if in_yellow else current_phase)

            # 4. Advance phase timer
            phase_time_remaining -= 1

            if phase_time_remaining <= 0:
                if not in_yellow:
                    # Transition to Yellow clearance phase
                    in_yellow = True
                    phase_time_remaining = self.yellow_time
                else:
                    # Switch green phase (0 -> 1 or 1 -> 0)
                    in_yellow = False
                    current_phase = 1 - current_phase
                    green_elapsed = 0
                    
                    if controller_type == "fuzzy" and controller is not None:
                        # Controller inspects queue and wait for the upcoming active phase
                        if current_phase == 0:
                            q_active = len(self.approaches['N'].queue) + len(self.approaches['S'].queue)
                            w_active = max(self.approaches['N'].get_avg_wait(current_time), 
                                           self.approaches['S'].get_avg_wait(current_time))
                            active_has_ev = ns_has_ev
                        else:
                            q_active = len(self.approaches['E'].queue) + len(self.approaches['W'].queue)
                            w_active = max(self.approaches['E'].get_avg_wait(current_time), 
                                           self.approaches['W'].get_avg_wait(current_time))
                            active_has_ev = ew_has_ev
                        
                        base_duration = controller.compute_green_duration(q_active, w_active)
                        # Emergency vehicle priority green bonus
                        if active_has_ev and enable_emergency_preemption:
                            phase_time_remaining = min(60, base_duration + 15)
                        else:
                            phase_time_remaining = base_duration
                    else:
                        phase_time_remaining = fixed_duration

            current_time += 1

        # 5. Calculate summary metrics
        all_completed = []
        emergency_completed = []
        for app in self.approaches.values():
            all_completed.extend(app.completed_vehicles)
            emergency_completed.extend([v for v in app.completed_vehicles if v.is_emergency])

        total_completed = len(all_completed)
        avg_wait = float(np.mean([v.waiting_time for v in all_completed])) if all_completed else 0.0
        avg_ev_wait = float(np.mean([v.waiting_time for v in emergency_completed])) if emergency_completed else 0.0
        
        # Include vehicles still waiting in queue at end of simulation
        all_remaining_waits = []
        for app in self.approaches.values():
            for v in app.queue:
                all_remaining_waits.append(total_time - v.arrival_time)
                
        all_waits = [v.waiting_time for v in all_completed] + all_remaining_waits
        global_avg_wait = float(np.mean(all_waits)) if all_waits else 0.0
        max_wait = float(np.max(all_waits)) if all_waits else 0.0
        avg_queue = float(np.mean(np.array(history['ns_queue']) + np.array(history['ew_queue'])))

        summary = {
            'total_completed': total_completed,
            'emergency_completed': len(emergency_completed),
            'avg_wait_time': round(global_avg_wait, 2),
            'avg_emergency_wait': round(avg_ev_wait, 2),
            'max_wait_time': round(max_wait, 2),
            'avg_queue_length': round(avg_queue, 2),
            'throughput_per_min': round((total_completed / (total_time / 60.0)), 2),
            'history': history
        }
        return summary
