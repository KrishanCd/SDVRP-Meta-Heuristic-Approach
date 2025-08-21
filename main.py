import numpy as np
from PASA8 import update_graph
from CVRP3 import solve_cvrp
import time
import tkinter as tk
from tkinter import filedialog

def parse_problem_file(filepath):
    """Parses a problem file in the specified format."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]

        # Initialize variables
        distance_matrix = []
        demand_list = []
        num_vehicles = None
        vehicle_capacity = None

        # Parse sections
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith("DISTANCE MATRIX"):
                i += 1
                while i < len(lines) and not lines[i].startswith("DEMAND LIST"):
                    row = list(map(int, lines[i].split()))
                    distance_matrix.append(row)
                    i += 1
                i -= 1  # Move back to DEMAND LIST for next section
            
            elif line.startswith("DEMAND LIST"):
                i += 1
                if i < len(lines):
                    demand_list = list(map(int, lines[i].split()))
            
            elif line.startswith("NUMBER OF VEHICLES"):
                num_vehicles = int(line.split(":")[1].strip())
            
            elif line.startswith("VEHICLE CAPACITY"):
                vehicle_capacity = int(line.split(":")[1].strip())
            
            i += 1

        # Validate inputs
        if not distance_matrix:
            raise ValueError("Distance matrix not found or empty.")
        n = len(distance_matrix)
        if any(len(row) != n for row in distance_matrix):
            raise ValueError("Distance matrix must be square.")
        if not demand_list:
            raise ValueError("Demand list not found or empty.")
        if len(demand_list) != n:
            raise ValueError("Demand list length must match distance matrix size.")
        if demand_list[0] != 0:
            raise ValueError("Depot demand must be 0.")
        if num_vehicles is None or vehicle_capacity is None:
            raise ValueError("Number of vehicles or vehicle capacity not found.")
        if num_vehicles <= 0 or vehicle_capacity <= 0:
            raise ValueError("Number of vehicles and vehicle capacity must be positive.")

        return np.array(distance_matrix), demand_list, num_vehicles, vehicle_capacity

    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        raise
    except ValueError as e:
        print(f"Error in file format: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error while parsing file: {str(e)}")
        raise

def browse_file():
    """Opens a file dialog to select the problem file and returns its path."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Problem File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    root.destroy()
    if not file_path:
        raise ValueError("No file selected.")
    return file_path

def main():
    """Runs PASA8 first, then feeds its output into CVRP3 with execution time measurement."""
    try:
        # Browse for the problem file
        print("Please select the problem file...")
        file_path = browse_file()
        print(f"Selected file: {file_path}")

        # Parse the file
        distance_matrix, demand_list, num_vehicles, vehicle_capacity = parse_problem_file(file_path)

        # Start timing
        start_time = time.time()

        # Run the splitting algorithm (PASA8)
        new_distance_matrix, new_demands, vehicle_capacities = update_graph(
            distance_matrix, demand_list, vehicle_capacity, num_vehicles
        )

        # Solve with OR-Tools (CVRP3)
        solution = solve_cvrp(new_distance_matrix, new_demands, vehicle_capacities)

        # End timing
        end_time = time.time()
        execution_time = end_time - start_time

        # Display results
        if isinstance(solution, str):
            print(f"\n{solution}")
        else:
            print("\nOptimal Routes and Distances:")
            for route in solution["routes"]:
                print(f"Vehicle {route['vehicle']}: Route {route['route']} | Distance: {route['distance']}")
            print(f"Total Distance: {solution['total_distance']}")
            print(f"Execution Time: {execution_time:.2f} seconds")

    except Exception as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    main()