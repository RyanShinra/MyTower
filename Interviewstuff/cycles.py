# # I'll rewrite the code with proper Python 3 type annotations. Type annotations are a great feature to learn when getting started with Python as they make the code more self-documenting and help catch errors earlier.


# from dataclasses import dataclass
# import networkx as nx
# import datetime
# from typing import List, Dict, Tuple, Any, Optional, Set, Iterator, cast

# from typing import NamedTuple, Dict, Any, List

# # Define a type-annotated named tuple for edges
# class EdgeTuple(NamedTuple):
#     source: str
#     target: str
#     data: Dict[str, Any]

# @dataclass
# class TransactionWindow:
#     """Represents a window of transactions that might be suspicious."""
#     start_time: datetime.datetime
#     end_time: datetime.datetime
#     edges: List[EdgeTuple]
    
#     @property
#     def edge_count(self) -> int: 
#         return len(self.edges)
    
#     @property
#     def total_amount(self) -> float:
#         """Calculate the total amount of all transactions in this window."""
#         return sum(edge.data['amount'] for edge in self.edges)
    
#     @property
#     def time_span_hours(self) -> float:
#         delta_t = self.end_time - self.start_time
#         return delta_t.total_seconds() / 3600
    
# @dataclass
# class FanPattern:
#     """Represents a potential fan pattern with incoming and outgoing transaction windows."""
#     hub_account: str
#     in_window: TransactionWindow
#     out_window: TransactionWindow
#     suspicion_score: float
    
# class TransactionGraphAnalyzer:
#     def __init__(self) -> None:
#         # Initialize an empty directed graph
#         self.graph: nx.DiGraph = nx.DiGraph()
        
#     def build_graph_from_transactions(self, transactions: List[Dict[str, Any]]) -> None:
#         """Build a directed graph from transaction data"""
#         # Add all accounts as nodes
#         accounts: Set[str] = set()
#         for tx in transactions:
#             accounts.add(tx['source_account'])
#             accounts.add(tx['target_account'])
        
#         # Add nodes with properties
#         for account in accounts:
#             self.graph.add_node(account, type='account')
            
#         # Add transactions as edges
#         for tx in transactions:
#             # Add a directed edge from source to target
#             self.graph.add_edge(
#                 tx['source_account'], 
#                 tx['target_account'],
#                 transaction_id=tx['transaction_id'],
#                 amount=tx['amount'],
#                 timestamp=tx['timestamp']
#             )
        
#         print(f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
#     def detect_circular_transactions(self, max_cycle_length: int = 5) -> List[Dict[str, Any]]:
#         """Detect cycles in the transaction graph"""
#         suspicious_cycles: List[Dict[str, Any]] = []
        
#         # Find all simple cycles in the graph, up to max_cycle_length
#         # A simple cycle is one that doesn't repeat nodes
#         try:
#             cycles: List[List[str]] = list(nx.simple_cycles(self.graph))
#             # Filter cycles to only include those of reasonable length
#             cycles = [c for c in cycles if 2 <= len(c) <= max_cycle_length]
#         except nx.NetworkXNoCycle:
#             print("No cycles detected in the graph")
#             return []
        
#         for cycle in cycles:
#             if len(cycle) >= 2:  # At least 2 nodes needed for a meaningful cycle
#                 cycle_data: Dict[str, Any] = self._analyze_cycle(cycle)
#                 suspicious_cycles.append(cycle_data)
                
#         # Sort by suspicion score (highest first)
#         suspicious_cycles.sort(key=lambda x: x['suspicion_score'], reverse=True)
#         return suspicious_cycles
    
#     def _analyze_cycle(self, cycle: List[str]) -> Dict[str, Any]:
#         """Analyze a detected cycle and assign it a suspicion score"""
#         # Close the cycle for edge analysis
#         cycle_edges: List[Dict[str, Any]] = []
#         cycle_amounts: List[float] = []
#         cycle_times: List[datetime.datetime] = []
        
#         # Analyze each edge in the cycle
#         for i in range(len(cycle)):
#             source: str = cycle[i]
#             target: str = cycle[(i + 1) % len(cycle)]
            
#             if self.graph.has_edge(source, target):
#                 edge_data: Dict[str, Any] = self.graph.get_edge_data(source, target)
#                 cycle_edges.append(edge_data)
#                 cycle_amounts.append(edge_data['amount'])
#                 cycle_times.append(edge_data['timestamp'])
        
#         # Calculate metrics for suspicion scoring
#         amount_variance: float = self._calculate_variance(cycle_amounts)
#         time_span: datetime.timedelta = max(cycle_times) - min(cycle_times)
#         time_span_hours: float = time_span.total_seconds() / 3600
        
#         # Factors that increase suspicion:
#         # 1. Low variance in transaction amounts (similar amounts moving around)
#         # 2. Short timespan for the complete cycle
#         # 3. Number of accounts involved (more is generally more suspicious)
        
#         # Simple scoring formula (can be refined with domain knowledge)
#         suspicion_score: float = (
#             (1.0 / (amount_variance + 0.01)) * 0.4 +  # Low variance is suspicious
#             (1.0 / (time_span_hours + 0.1)) * 0.4 +   # Short timespan is suspicious
#             len(cycle) * 0.2                          # More accounts involved is suspicious
#         )
        
#         return {
#             'cycle': cycle,
#             'transactions': cycle_edges,
#             'amount_variance': amount_variance,
#             'time_span_hours': time_span_hours,
#             'suspicion_score': suspicion_score
#         }
    
#     def _calculate_variance(self, values: List[float]) -> float:
#         """Calculate variance of a list of values"""
#         if not values:
#             return 0
#         mean: float = sum(values) / len(values)
#         return sum((x - mean) ** 2 for x in values) / len(values)
    
#     def detect_fan_patterns(self, time_window_hours: float = 24.0, 
#                             min_connections: int = 3,
#                             suspicion_threshold: float = 0.6) -> List[FanPattern]:
#         """
#         Detect suspicious fan-in/fan-out patterns in transaction graphs.
#         """
#         suspicious_fans: List[FanPattern] = []

#         # Create a properly typed list of nodes
#         nodes: List[str] = [cast(str, node) for node in self.graph.nodes() #type: ignore
#                     if self.graph.in_degree(node) >= min_connections and  #type: ignore
#                        self.graph.out_degree(node) >= min_connections] #type: ignore
    
#         for node in nodes:
#             # Convert to EdgeTuple objects
#             in_edges: List[EdgeTuple] = [
#                 EdgeTuple(source, target, data) 
#                 for source, target, data in self.graph.in_edges(node, data=True) #type: ignore
#             ]
        
#             out_edges: List[EdgeTuple] = [
#                 EdgeTuple(source, target, data) 
#                 for source, target, data in self.graph.out_edges(node, data=True) #type: ignore
#             ]
        
#             # Analyze both sides
#             in_windows = self._analyze_single_side(in_edges, time_window_hours, min_connections)
#             out_windows = self._analyze_single_side(out_edges, time_window_hours, min_connections)
        
#             # If both sides have suspicious windows, this might be a fan pattern
#             if in_windows and out_windows:
#                 # Calculate suspicion score and add to results
#                 for in_window in in_windows:
#                     for out_window in out_windows:
#                         suspicion_score = self._calculate_fan_suspicion(in_window, out_window)
                        
#                         if suspicion_score >= suspicion_threshold:
#                             fan_pattern = FanPattern(
#                                 hub_account=node,
#                                 in_window=in_window,
#                                 out_window=out_window,
#                                 suspicion_score=suspicion_score
#                             )
#                             suspicious_fans.append(fan_pattern)
#                 # Sort by suspicion score
#         suspicious_fans.sort(key=lambda x: x.suspicion_score, reverse=True)
#         return suspicious_fans  
    
#     def _analyze_single_side(self, 
#                              edges: List[EdgeTuple], 
#                              time_window_hours: float, 
#                              min_connections: int) -> List[TransactionWindow]:
#         # First check to see if there's enough
#         if (len(edges) < min_connections):
#             return []
        
#         # Now sort them
#         def edge_timestamp(edge: EdgeTuple) -> datetime.datetime:
#             """Extract the timestamp from an edge for sorting."""
#             return edge.data['timestamp']
        
        
#         sorted_edges: List[EdgeTuple] = sorted(edges, key=edge_timestamp)
        
#         i = 0
#         j = 0
#         suspicious_windows: List[Dict[str, Any]] = []
#         for i in range(len(sorted_edges)):
#             def edge_time_diff(i: int, j: int) -> float:
#                 time_delta: datetime.timedelta = edge_timestamp(sorted_edges[j]) - edge_timestamp(sorted_edges[i])
#                 return time_delta.total_seconds() / 3600  # Convert to hours
            
#             current_windows: List[EdgeTuple] = []
#             for j in range(i, len(sorted_edges)):
#                 if edge_time_diff(i, j) <= time_window_hours:
#                     current_windows.append(sorted_edges[j])
#                 else:
#                     break
    
#             if (len(current_windows) >= min_connections):
#                 suspicious_windows.append({
#                     'start_time': edge_timestamp(current_windows[0]),
#                     'end_time': edge_timestamp(current_windows[-1]),
#                     'edge_count': len(current_windows),
#                     'edges': current_windows,
#                     # Add more analysis here
#                 })
            
#         return suspicious_windows
    
#     def _calculate_fan_suspicion(self, 
#                            in_window: TransactionWindow,
#                            out_window: TransactionWindow) -> float:
#         """
#         Calculate a suspicion score for a fan pattern based on:
#         1. Time proximity between fan-in and fan-out
#         2. Similarity in total amounts
#         3. Number of connections
#         """
#                 # Time proximity (shorter is more suspicious)
#         if out_window.start_time <= in_window.end_time:
#             time_score = 1.0  # Maximum suspicion
#         else:
#             # Calculate hours between end of fan-in and start of fan-out
#             time_gap = (out_window.start_time - in_window.end_time).total_seconds() / 3600
#             time_score = 1.0 / (1.0 + time_gap)
        
#         # Amount similarity (closer is more suspicious)
#         in_total = in_window.total_amount
#         out_total = out_window.total_amount
#         amount_ratio = min(in_total, out_total) / max(in_total, out_total) if max(in_total, out_total) > 0 else 0
        
#         # Connection count (more is more suspicious)
#         connection_score = (in_window.edge_count + out_window.edge_count) / 20
        
#         # Weighted final score
#         suspicion_score = (
#             (time_score * 0.5) +
#             (amount_ratio * 0.3) +
#             (connection_score * 0.2)
#         )
        
#         return min(suspicion_score, 1.0)

    
#     def visualize_suspicious_cycle(self, cycle_data: Dict[str, Any]) -> None:
#         """Prepare data to visualize a suspicious cycle"""
#         # In a real implementation, this would create a visualization
#         # For this prototype, we'll just print the cycle details
#         print(f"Suspicious cycle with score {cycle_data['suspicion_score']:.2f}:")
#         print(f"Accounts involved: {' -> '.join(cycle_data['cycle'])} -> {cycle_data['cycle'][0]}")
#         print(f"Time span: {cycle_data['time_span_hours']:.2f} hours")
#         print(f"Amount variance: {cycle_data['amount_variance']:.2f}")
        
#         # In a real-world application, we would return data for visualization
#         # Perhaps using a library like matplotlib, plotly, or a specialized
#         # graph visualization tool


# def generate_sample_transactions() -> List[Dict[str, Any]]:
#     """Generate sample transaction data including some circular patterns"""
#     now: datetime.datetime = datetime.datetime.now()
    
#     # Normal transactions
#     transactions: List[Dict[str, Any]] = [
#         {
#             'transaction_id': 'tx001',
#             'source_account': 'A001',
#             'target_account': 'B001',
#             'amount': 5000.00,
#             'timestamp': now - datetime.timedelta(hours=48)
#         },
#         {
#             'transaction_id': 'tx002',
#             'source_account': 'B001',
#             'target_account': 'C001',
#             'amount': 2500.00,
#             'timestamp': now - datetime.timedelta(hours=36)
#         },
#         {
#             'transaction_id': 'tx003',
#             'source_account': 'D001',
#             'target_account': 'E001',
#             'amount': 10000.00,
#             'timestamp': now - datetime.timedelta(hours=24)
#         }
#     ]
    
#     # Suspicious circular pattern (similar amounts, short timeframe)
#     suspicious_cycle: List[Dict[str, Any]] = [
#         {
#             'transaction_id': 'tx101',
#             'source_account': 'X001',
#             'target_account': 'Y001',
#             'amount': 9500.00,
#             'timestamp': now - datetime.timedelta(hours=5)
#         },
#         {
#             'transaction_id': 'tx102',
#             'source_account': 'Y001',
#             'target_account': 'Z001',
#             'amount': 9400.00,
#             'timestamp': now - datetime.timedelta(hours=4)
#         },
#         {
#             'transaction_id': 'tx103',
#             'source_account': 'Z001',
#             'target_account': 'X001',
#             'amount': 9450.00,
#             'timestamp': now - datetime.timedelta(hours=3)
#         }
#     ]
    
#     # Another cycle but less suspicious (varied amounts, longer timeframe)
#     less_suspicious_cycle: List[Dict[str, Any]] = [
#         {
#             'transaction_id': 'tx201',
#             'source_account': 'M001',
#             'target_account': 'N001',
#             'amount': 1500.00,
#             'timestamp': now - datetime.timedelta(hours=72)
#         },
#         {
#             'transaction_id': 'tx202',
#             'source_account': 'N001',
#             'target_account': 'P001',
#             'amount': 4500.00,
#             'timestamp': now - datetime.timedelta(hours=48)
#         },
#         {
#             'transaction_id': 'tx203',
#             'source_account': 'P001',
#             'target_account': 'M001',
#             'amount': 2000.00,
#             'timestamp': now - datetime.timedelta(hours=24)
#         }
#     ]
    
#     return transactions + suspicious_cycle + less_suspicious_cycle


# def main() -> None:
#     # Generate sample data
#     transactions: List[Dict[str, Any]] = generate_sample_transactions()
    
#     # Initialize the analyzer
#     analyzer: TransactionGraphAnalyzer = TransactionGraphAnalyzer()
    
#     # Build the graph
#     analyzer.build_graph_from_transactions(transactions)
    
#     # Detect circular transactions
#     suspicious_cycles: List[Dict[str, Any]] = analyzer.detect_circular_transactions()
    
#     # Display results
#     print(f"\nFound {len(suspicious_cycles)} suspicious circular patterns")
    
#     # Visualize top suspicious cycles
#     for i, cycle_data in enumerate(suspicious_cycles[:3]):
#         print(f"\nSuspicious Pattern #{i+1}")
#         analyzer.visualize_suspicious_cycle(cycle_data)


# if __name__ == "__main__":
#     main()
# '''


# Key type annotation improvements:

# 1. Function return types are now properly annotated (e.g., `-> None`, `-> List[Dict[str, Any]]`)
# 2. All variables have type annotations (e.g., `suspicious_cycles: List[Dict[str, Any]] = []`)
# 3. Complex data structures use appropriate generics (e.g., `Dict[str, Any]` for transaction records)
# 4. Class attributes are typed in the `__init__` method

# Type annotations are particularly valuable for:
# - Self-documenting code (making the expected data types clear)
# - IDE integration (better autocomplete and error detection)
# - Static type checking with tools like mypy
# - Making refactoring safer

# Would you like me to explain any particular aspect of the implementation or how the graph analysis works?
# ```
# '''