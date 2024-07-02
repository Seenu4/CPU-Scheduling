import psutil
import datetime
from prettytable import PrettyTable

class Process:
    def init(self, name, runtime, priority, create_time, cpu_usage, memory_info):
        self.name = name
        self.runtime = runtime
        self.priority = priority
        self.create_time = create_time
        self.arrival_time = datetime.datetime.now() - create_time
        self.waiting_time = 0
        self.turnaround_time = 0
        self.cpu_usage = cpu_usage
        self.memory_info = memory_info

def calculate_waiting_turnaround_times(processes):
    waiting_time = 0
    for process in processes:
        process.waiting_time = waiting_time
        waiting_time += process.runtime.total_seconds()
        process.turnaround_time = process.waiting_time + process.runtime.total_seconds()

def round_robin_scheduling(processes, time_quantum):
    remaining_runtime = [process.runtime for process in processes]
    current_time = datetime.timedelta()
    queue = processes.copy()

    while any(remaining_runtime):
        process = queue.pop(0)
        index = processes.index(process)

        if remaining_runtime[index] <= datetime.timedelta(seconds=time_quantum):
            current_time += remaining_runtime[index]
            process.turnaround_time = current_time
            process.waiting_time = process.turnaround_time - process.runtime
            remaining_runtime[index] = datetime.timedelta()
        else:
            current_time += datetime.timedelta(seconds=time_quantum)
            remaining_runtime[index] -= datetime.timedelta(seconds=time_quantum)
            queue.append(process)

    for i in range(len(processes)):
        if remaining_runtime[i] > datetime.timedelta():
            processes[i].waiting_time = current_time.total_seconds()
            current_time += remaining_runtime[i]
            processes[i].turnaround_time = current_time.total_seconds()

def largest_job_first_scheduling(processes):
    processes.sort(key=lambda x: (x.priority, x.runtime.total_seconds()), reverse=True)
    calculate_waiting_turnaround_times(processes)

def shortest_job_first_scheduling(processes):
    processes.sort(key=lambda x: (x.priority, x.runtime.total_seconds()))
    calculate_waiting_turnaround_times(processes)

def first_come_first_serve_scheduling(processes):
    calculate_waiting_turnaround_times(processes)

def multilevel_queue_scheduling(processes, time_quantum_low, time_quantum_high):
    low_priority_queue = [process for process in processes if process.priority < 3]
    high_priority_queue = [process for process in processes if process.priority >= 3]

    round_robin_scheduling(low_priority_queue, time_quantum_low)
    round_robin_scheduling(high_priority_queue, time_quantum_high)

    processes = low_priority_queue + high_priority_queue
    calculate_waiting_turnaround_times(processes)

def get_system_processes():
    processes = []
    for process in psutil.process_iter(['name', 'create_time', 'memory_info', 'cpu_percent']):
        create_time = datetime.datetime.fromtimestamp(process.info['create_time'])
        runtime = datetime.datetime.now() - create_time
        priority = psutil.Process(process.info['pid']).nice() if 'pid' in process.info else 0
        cpu_usage = process.info['cpu_percent']
        memory_info = process.info['memory_info']
        processes.append(Process(process.info['name'], runtime, priority, create_time, cpu_usage, memory_info))
    return processes

def display_results(processes):
    table = PrettyTable()
    table.field_names = ["Process", "Runtime", "Priority", "Waiting Time", "Turnaround Time", "Arrival Time", "CPU Usage", "Memory Info"]

    for process in processes:
        table.add_row([process.name, process.runtime, process.priority, process.waiting_time, process.turnaround_time,
                       process.arrival_time.total_seconds(), process.cpu_usage, process.memory_info])

    print(table)

def suggest_algorithm(process):
    suggestions = []
    
    if process.runtime.total_seconds() <= 5:
        suggestions.append("Shortest Job First - Process has a short runtime.")
    elif process.runtime.total_seconds() > 15:
        if process.arrival_time.total_seconds() < 60:
            suggestions.append("First Come First Serve - Process arrived recently.")
        suggestions.append("Largest Job First - Process has a long runtime.")
    elif process.arrival_time.total_seconds() < 60:
        suggestions.append("First Come First Serve - Process arrived recently.")
    else:
        suggestions.append("Round Robin - Process has a moderate runtime.")
    
    return suggestions

def compare_suggestions(suggestions):
    # Prioritize algorithms based on a simple order
    priorities = {
        "Shortest Job First": 4,
        "Largest Job First": 3,
        "First Come First Serve": 2,
        "Round Robin": 1
    }

    # Find the suggestion with the highest priority
    best_suggestion = max(suggestions, key=lambda x: priorities.get(x.split('-')[0].strip(), 0))

    return best_suggestion

def display_suggestion(algorithm_name, process_name, suggestion):
    print(f"\nSuggestion for {process_name} using {algorithm_name} Scheduling:")
    print(f"Best Suggestion: {suggestion}\n")

if name == "main":
    system_processes = get_system_processes()

    for process in system_processes:
        algorithm_suggestions = suggest_algorithm(process)
        best_suggestion = compare_suggestions(algorithm_suggestions)

        if best_suggestion.startswith("Shortest Job First"):
            processes_sjf = [process]
            shortest_job_first_scheduling(processes_sjf)
            display_suggestion("Shortest Job First", process.name, best_suggestion)
            display_results(processes_sjf)
        elif best_suggestion.startswith("Largest Job First"):
            processes_ljf = [process]
            largest_job_first_scheduling(processes_ljf)
            display_suggestion("Largest Job First", process.name, best_suggestion)
            display_results(processes_ljf)
        elif best_suggestion.startswith("First Come First Serve"):
            processes_fcfs = [process]
            first_come_first_serve_scheduling(processes_fcfs)
            display_suggestion("First Come First Serve", process.name, best_suggestion)
            display_results(processes_fcfs)
        elif best_suggestion.startswith("Round Robin"):
            processes_rr = [process]
            round_robin_scheduling(processes_rr, time_quantum=2)
            display_suggestion("Round Robin", process.name, best_suggestion)
            display_results(processes_rr)
        elif best_suggestion.startswith("Multilevel Queue"):
            processes_mlq = [process]
            multilevel_queue_scheduling(processes_mlq, time_quantum_low=2, time_quantum_high=5)
            display_suggestion("Multilevel Queue", process.name, best_suggestion)
            display_results(processes_mlq)