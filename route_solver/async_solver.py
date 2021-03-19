import pygraphviz as pgv

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def create_weight_callback(data: dict):
	"""
	Create a callback to return the weight between points.
	"""

	def weight_callback(from_node, to_node):
		"""
		Return the weight between the two points.
		"""
		return data['weights'][from_node][to_node]

	return weight_callback

def create_demand_callback(data: dict):
	"""
	Create a callback to get demands at each location.
	"""

	def demand_callback(from_node, _):
		"""
		Return the demand.
		"""
		return data['demands'][from_node]

	return demand_callback

def add_capacity_constraints(routing: pywrapcp.RoutingModel, data: dict,
							 demand_callback):
	"""
	Add capacity constraints.
	"""
	routing.AddDimensionWithVehicleCapacity(
		evaluator=demand_callback,
		slack_max=0,  # null slack
		# vehicle maximum capacities
		vehicle_capacities=data['vehicle_capacities'],
		fix_start_cumul_to_zero=True,  # start cumul to zero
		name='Capacity',
	)

def create_time_callback(data: dict):
	"""
	Create a callback to get total times between locations.
	"""

	def service_time(node: int) -> int:
		"""
		Get the service time to the specified location.
		"""
		return data['service_times'][node]

	def travel_time(from_node: int, to_node: int) -> int:
		"""
		Get the travel times between two locations.
		"""
		return data['weights'][from_node][to_node]

	def time_callback(from_node: int, to_node: int):
		"""
		Return the total time between the two nodes.
		"""
		serv_time = service_time(from_node)
		trav_time = travel_time(from_node, to_node)
		return serv_time + trav_time

	return time_callback


def add_time_window_constraints(routing: pywrapcp.RoutingModel, data: dict,
								time_callback):
	"""
	Add time window constraints.
	"""
	time = 'Time'
	horizon = 120
	routing.AddDimension(
		evaluator=time_callback,
		slack_max=horizon,  # allow waiting time
		capacity=horizon,  # maximum time per vehicle
		# Don't force start cumul to zero. This doesn't have any effect in this example,
		# since the depot has a start window of (0, 0).
		fix_start_cumul_to_zero=False,
		name=time,
	)
	time_dimension = routing.GetDimensionOrDie(time)
	for loc_node, (open_time, close_time) in enumerate(data['time_windows']):
		index = routing.NodeToIndex(loc_node)
		time_dimension.CumulVar(index).SetRange(open_time, close_time)

def node_properties(
		routing: pywrapcp.RoutingModel,
		assignment: pywrapcp.Assignment,
		capacity_dimension: pywrapcp.RoutingDimension,
		time_dimension: pywrapcp.RoutingDimension,
		index: int,
) -> tuple:
	"""
	Get a node's properties on the index.
	"""
	node_index = routing.IndexToNode(index)
	load = assignment.Value(capacity_dimension.CumulVar(index))
	time_var = time_dimension.CumulVar(index)
	time_min, time_max = assignment.Min(time_var), assignment.Max(time_var)
	return (node_index, load, time_min, time_max)


def print_solution(data: dict, routing: pywrapcp.RoutingModel,
				   assignment: pywrapcp.Assignment):
	"""
	Print routes on console.
	"""
	capacity_dimension = routing.GetDimensionOrDie('Capacity')
	time_dimension = routing.GetDimensionOrDie('Time')
	total_time = 0
	d = {}
	r = []

	for vehicle_id in range(data['num_vehicles']):
		index = routing.Start(vehicle_id)
		node_props = []

		while not routing.IsEnd(index):
			props = node_properties(routing, assignment, capacity_dimension,
									time_dimension, index)
			node_props.append(props)
			index = assignment.Value(routing.NextVar(index))

		props = node_properties(routing, assignment, capacity_dimension,
								time_dimension, index)
		node_props.append(props)
		route_time = assignment.Value(time_dimension.CumulVar(index))
		route = "\n  -> ".join(['[Node %2s: Load(%s) Time(%2s, %s)]' % prop \
								for prop in node_props])
		plan_output = f'Route for vehicle {vehicle_id}:\n  {route}\n' + \
			f'Load of the route: {props[1]}\nTime of the route: {route_time} min\n'

		# print(plan_output)

		#convert to dict
		ddd = []
		for node in node_props:
			dd = {"node":node[0],"load":node[1],"time":[node[2],node[3]]}
			ddd.append(dd)
		r.append({"vehicle_id":vehicle_id,"route":ddd,"total_time":route_time,"load":len(ddd)-2})


		total_time += route_time
	d['solver'] = r
	d['total_time'] = total_time
	# print(f'Total time of all routes: {total_time} min')
	return d

async def solve(data):

	# Create Routing Model
	routing = pywrapcp.RoutingModel(
		data['num_locations'],
		data['num_vehicles'],
		data['depot'],
	)

	# Define weight of each edge
	weight_callback = create_weight_callback(data)
	routing.SetArcCostEvaluatorOfAllVehicles(weight_callback)

	 # Add capacity constraints
	demand_callback = create_demand_callback(data)
	add_capacity_constraints(routing, data, demand_callback)

	# Add time window constraints
	time_callback = create_time_callback(data)
	add_time_window_constraints(routing, data, time_callback)

	# Set first solution heuristic (cheapest addition)
	search_params = pywrapcp.RoutingModel.DefaultSearchParameters()
	# pylint: disable=no-member
	search_params.first_solution_strategy = \
		routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

	assignment = routing.SolveWithParameters(search_params)

	total_time = print_solution(data, routing, assignment)

	return total_time

