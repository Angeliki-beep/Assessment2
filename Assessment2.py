import pandas as pd # type: ignore
import random
from collections import deque
import heapq

# Graph and Station Data Classes
# -------------------------------
class Station:
    def __init__(self, name, line):
        self.name = name
        self.line = line

    def id(self):
        return f"{self.name} ({self.line})"

class Graph:
    def __init__(self):
        self.nodes = {} 
        self.edges = {}  

    def add_station(self, station):
        self.nodes[station.id()] = station
        self.edges[station.id()] = []

    def add_connection(self, from_id, to_id, time):
        self.edges[from_id].append((to_id, time))
        self.edges[to_id].append((from_id, time))


# Load Data and Build Graph




def build_graph(csv_path):
    df = pd.read_csv(csv_path)
    graph = Graph()

    for _, row in df.iterrows():
        station = Station(row["Station"], row["Line"])
        graph.add_station(station)

    # Connect stations on the same line in order of appearance
    for line, group in df.groupby("Line"):
        stations = group.sort_values("Station").reset_index()
        for i in range(len(stations) - 1):
            a = Station(stations.loc[i, "Station"], line).id()
            b = Station(stations.loc[i+1, "Station"], line).id()
            time = random.randint(2, 8)
            graph.add_connection(a, b, time)

    # Add 5-minute transfers at interchange stations
    for station_name, group in df.groupby("Station"):
        lines = list(group["Line"])
        for i in range(len(lines)):
            for j in range(i+1, len(lines)):
                a = f"{station_name} ({lines[i]})"
                b = f"{station_name} ({lines[j]})"
                graph.add_connection(a, b, 5)

    return graph


# Algorithms

def find_shortest_path(graph, start_name, end_name):
    start_ids = [sid for sid in graph.nodes if sid.startswith(start_name)]
    end_ids = [sid for sid in graph.nodes if sid.startswith(end_name)]

    visited = set()
    parent = {}
    queue = deque()

    for sid in start_ids:
        queue.append(sid)
        visited.add(sid)
        parent[sid] = None

    while queue:
        current = queue.popleft()
        if current in end_ids:
            path = []
            while current:
                path.append(current)
                current = parent[current]
            return path[::-1]

        for neighbor, _ in graph.edges[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return None

def find_fastest_path(graph, start_name, end_name):
    start_ids = [sid for sid in graph.nodes if sid.startswith(start_name)]
    end_ids = [sid for sid in graph.nodes if sid.startswith(end_name)]

    distances = {sid: float('inf') for sid in graph.nodes}
    previous = {}
    queue = []

    for sid in start_ids:
        distances[sid] = 0
        heapq.heappush(queue, (0, sid))

    while queue:
        current_dist, current = heapq.heappop(queue)
        if current in end_ids:
            path = []
            while current:
                path.append(current)
                current = previous.get(current)
            return path[::-1], current_dist

        for neighbor, time in graph.edges[current]:
            new_dist = current_dist + time
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current
                heapq.heappush(queue, (new_dist, neighbor))

    return None, float('inf')




# Main 

def main():
    print(" Singapore Metro Route Finder")
    
    graph = build_graph("stations.csv")

    start = input("Enter start station: ").strip()
    end = input("Enter destination station: ").strip()

    print("\n Shortest Path (by number of stops) ")
    path = find_shortest_path(graph, start, end)
    if path:
        print(" -> ".join(path))
        print(f"Stops: {len(path) - 1}")
    else:
        print("No route found.")

    print("\n Fastest Path (by travel time) ")
    path, total_time = find_fastest_path(graph, start, end)
    if path:
        print(" -> ".join(path))
        print(f"Time: {total_time} minutes")
    else:
        print("No route found.")

if __name__ == "__main__":
    main()


