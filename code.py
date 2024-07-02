#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 21:39:18 2023

@author: aravind
"""

import psutil
from datetime import datetime
from prettytable import PrettyTable

class Process:
    def __init__(self, pid, name, burst_time, cpu_usage, memory_info, priority):
        self.pid = pid
        self.name = name
        self.burst_time = burst_time
        self.waiting_time = 0
        self.turnaround_time = 0
        self.cpu_usage = cpu_usage
        self.memory_info = memory_info
        self.priority = priority

def calculate_waiting_turnaround_times(processes):
    waiting_time = 0
    for process in processes:
        process.waiting_time = waiting_time
        waiting_time += process.burst_time
        process.turnaround_time = process.waiting_time + process.burst_time

def get_system_processes():
    processes = []
    for process in psutil.process_iter(['pid', 'name', 'create_time', 'cpu_percent', 'memory_info']):
        create_time = datetime.fromtimestamp(process.info['create_time'])
        runtime = datetime.now() - create_time
        priority = psutil.Process(process.info['pid']).nice() if 'pid' in process.info else 0
        processes.append(Process(process.info['pid'], process.info['name'], runtime.total_seconds(), process.info['cpu_percent'], process.info['memory_info'], priority))

    return processes

def display_processes(processes):
    table = PrettyTable()
    table.field_names = ["S.No", "PID", "Name", "Burst Time", "CPU Usage", "Memory Info", "Priority"]

    for i, process in enumerate(processes, start=1):
        table.add_row([i, process.pid, process.name, process.burst_time, process.cpu_usage, process.memory_info, process.priority])

    print("Processes:")
    print(table)

def get_processes_by_sno(processes, selected_snos):
    selected_processes = [processes[sno - 1] for sno in selected_snos]
    return selected_processes

def fcfs_scheduling(processes):
    calculate_waiting_turnaround_times(processes)

def sjf_scheduling(processes):
    processes.sort(key=lambda x: (x.burst_time, x.priority))
    calculate_waiting_turnaround_times(processes)

def ljf_scheduling(processes):
    processes.sort(key=lambda x: (x.burst_time, x.priority), reverse=True)
    calculate_waiting_turnaround_times(processes)

def priority_queue_scheduling(processes):
    for process in processes:
        process.priority = int(input(f"Enter priority for process {process.name}: "))

    processes.sort(key=lambda x: (x.priority, x.burst_time))
    calculate_waiting_turnaround_times(processes)

def round_robin_scheduling(processes, time_quantum):
    remaining_burst_time = [process.burst_time for process in processes]
    current_time = 0
    queue_rr = processes.copy()  # Use a copy of the original processes

    while any(remaining_burst_time):
        process = queue_rr.pop(0)  # Pop the first process from the queue
        index = processes.index(process)

        if remaining_burst_time[index] <= time_quantum:
            current_time += remaining_burst_time[index]
            process.turnaround_time = current_time
            process.waiting_time = process.turnaround_time - process.burst_time
            remaining_burst_time[index] = 0
        else:
            current_time += time_quantum
            remaining_burst_time[index] -= time_quantum
            queue_rr.append(process)

    for i in range(len(processes)):
        if remaining_burst_time[i] > 0:
            processes[i].waiting_time = current_time
            current_time += remaining_burst_time[i]
            processes[i].turnaround_time = current_time

def display_results(processes):
    table = PrettyTable()
    table.field_names = ["Process", "Burst Time", "Waiting Time", "Turnaround Time", "CPU Usage", "Memory Info", "Priority"]

    for process in processes:
        table.add_row([process.name, process.burst_time, process.waiting_time, process.turnaround_time, process.cpu_usage, process.memory_info, process.priority])

    print(table)

def rank_algorithms(algorithms, processes):
    rank = {}
    for algorithm in algorithms:
        # Define a composite metric based on various CPU parameters
        composite_metric = sum(
            process.turnaround_time + process.waiting_time + process.cpu_usage + process.memory_info.rss
            for process in processes
        ) / len(processes)
        
        rank[algorithm.__name__] = composite_metric

    return sorted(rank.items(), key=lambda x: x[1])



if __name__ == "__main__":
    system_processes = get_system_processes()
    display_processes(system_processes)

    num_processes = int(input("\nEnter the number of processes to analyze: "))
    selected_snos = [int(input(f"Enter the S.No of process {i + 1}: ")) for i in range(num_processes)]

    processes = get_processes_by_sno(system_processes, selected_snos)

    # Proceed with scheduling and displaying results as before
    fcfs_scheduling(processes)
    print("\nFCFS Scheduling:")
    display_results(processes)

    sjf_scheduling(processes)
    print("\nSJF Scheduling:")
    display_results(processes)

    ljf_scheduling(processes)
    print("\nLJF Scheduling:")
    display_results(processes)

    priority_queue_scheduling(processes)
    print("\nPriority Queue Scheduling:")
    display_results(processes)

    time_quantum = int(input("Enter time quantum for Round Robin: "))
    round_robin_scheduling(processes, time_quantum)
    print("\nRound Robin Scheduling:")
    display_results(processes)

    # Rank algorithms and display the result
    algorithms = [fcfs_scheduling, sjf_scheduling, ljf_scheduling, priority_queue_scheduling, round_robin_scheduling]
    ranking = rank_algorithms(algorithms, processes)
    print("\nAlgorithm Ranking (Lower Average Turnaround Time is better):")
    for i, (algorithm, avg_turnaround_time) in enumerate(ranking, start=1):
        print(f"{i}. {algorithm}: {avg_turnaround_time}")
