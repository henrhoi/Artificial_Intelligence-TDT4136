from tkinter import *
import math as m

__author__ = "Henrik Høiness"


class SearchNode:
	"""
	Class for node in board to be searched
	"""

	def __init__(self, x, y):
		"""
		Initializes the search node

		:param x: x-coordinate of node
		:param y: y-coordinate of node
		"""
		self.start = False
		self.solution = False
		self.type = None
		self.in_path = False

		self.x = x
		self.y = y

		self.children = []
		self.parent = None

		self.cost = 0
		self.g = float('inf')  # g(s)
		self.h = None  # h(s)

	def f(self):
		"""
		Method for getting f(node), which is the total cost (cost so far + estimated cost to goal)
		:return: g(node) + h(node)
		"""
		return self.g + self.h

	def __str__(self):
		return "x: " + str(self.x) + ", y: " + str(self.y) + ", cost: " + str(self.cost)


# The agenda loop for A* is written from the pseudocode described in the Supplement - Essentials of the A* Algorithm

def a_star():
	"""
	Method that runs the agenda loop for the A* algorithm
	:return: Boolean whether or not a path was found from A to B
	"""
	closed_nodes = []
	open_nodes = [start]

	while True:
		if not open_nodes:
			return False  # Failure

		current_node = open_nodes.pop(0)
		closed_nodes.append(current_node)

		if current_node.solution:
			return True  # Solution found

		generate_all_successors(current_node)

		for child in current_node.children:
			if child not in open_nodes and child not in closed_nodes:
				attach_and_eval(child, current_node)
				open_nodes.append(child)
				open_nodes.sort(key=lambda x: x.f())  # Sort by lowest estimated cost

			elif current_node.g + child.cost < child.g:  # Found a cheaper path to S
				attach_and_eval(child, current_node)
				if child in closed_nodes:
					propagate_path_improvements(child)


def generate_all_successors(current_node):
	"""
	Method for adding all neighbouring nodes to node.children
	:param current_node: Node to generate successors for
	"""
	for node in all_nodes:
		if node.cost < float('inf'):  # Check if node is not a wall
			if (current_node.x == node.x) and (current_node.y == node.y - 1 or current_node.y == node.y + 1):
				current_node.children.append(node)
			elif (current_node.y == node.y) and (current_node.x == node.x - 1 or current_node.x == node.x + 1):
				current_node.children.append(node)


def attach_and_eval(child, parent):
	"""
	Method for calculating a node's cost so far, and estimated remaining cost

	:param child: Child node in board
	:param parent: Parent node of child node in board
	:return: void
	"""
	child.parent = parent
	child.g = parent.g + child.cost

	# Setting h of child-node - Switches method for calculating distance between part 1 and part 2 boards.
	if part == 1:
		child.h = manhattan_distance(child)

	if part == 2:
		distance = euclid_distance(child)
		child.h = distance * (child.cost / weight)  # (Euclid distance) * (Node cost / Average cost)


def propagate_path_improvements(parent):
	"""
	If a better option is found, this method will propagate on a nodes children and updating its current cost

	:param parent: Node in board
	:return: void
	"""
	for child in parent.children:
		if parent.g + child.cost < child.g:
			child.parent = parent
			child.g = parent.g + child.cost
			propagate_path_improvements(child)


def create_nodes():  # e.g. "boards/board-1-1.txt"
	"""
	Method for initialising the state the script need to have for running the A*-algorithm

	:param filename: Name of file with board
	:return: start_node, goal_node, list of all nodes, board
	"""

	nodes = []
	game_board = []
	start_node = None
	goal_node = None
	file = open(filename, "r")
	for x_coor, line in enumerate(file.readlines()):
		game_board.append([None] * len(line.rstrip()))
		for y_coor, node in enumerate(line.rstrip()):
			game_board[x_coor][y_coor] = node

			if node == '#':  # Found a wall
				wall_node = SearchNode(x_coor, y_coor)
				wall_node.cost = float('inf')
				wall_node.type = node
				nodes.append(wall_node)

			elif node == 'A':  # Found start-node
				start_node = SearchNode(x_coor, y_coor)
				start_node.start = True
				start_node.type = node
				nodes.append(start_node)

			elif node == 'B':  # Found goal-node
				goal_node = SearchNode(x_coor, y_coor)
				goal_node.solution = True
				goal_node.type = node
				nodes.append(goal_node)

			else:  # Found regular path node
				search_node = SearchNode(x_coor, y_coor)
				search_node.cost = cost_dict[node]
				search_node.type = node
				nodes.append(search_node)

	return start_node, goal_node, nodes, game_board


def draw_board():
	"""
	Method for drawing board with path from A* for part 1 of the assignment
	"""
	rec_size = 30
	width = (len(board[0]) + 1) * rec_size
	height = (len(board) + 1) * rec_size

	drawer = Tk()
	window = Canvas(drawer, width=width, height=height)

	for i in range(len(board[0])):
		window.create_text(50 + i * rec_size, 15, fill="black", font="Times 20 italic bold", text=str(i))

	for j in range(len(board)):
		window.create_text(15, 50 + j * rec_size, fill="black", font="Times 20 italic bold", text=str(j))

	for node in all_nodes:
		x = node.x + 1
		y = node.y + 1
		if node.in_path:
			window.create_rectangle(y * rec_size, x * rec_size, y * rec_size + rec_size, x * rec_size + rec_size,
									fill="lightpink")
		else:
			window.create_rectangle(y * rec_size, x * rec_size, y * rec_size + rec_size, x * rec_size + rec_size,
									fill=color_dict[node.type])

		if node.start:
			window.create_text(y * rec_size + 0.5 * rec_size, x * rec_size + 0.5 * rec_size, fill="black",
							   font="Times 20 italic bold", text=node.type)
		elif node.solution:
			window.create_text(y * rec_size + 0.5 * rec_size, x * rec_size + 0.5 * rec_size, fill="black",
							   font="Times 20 italic bold", text=node.type)

	window.pack()
	drawer.mainloop()


def draw_board2():
	"""
	Method for drawing board with path from A* for part 2 of the assignment
	"""
	rec_size = 30
	width = (len(board[0]) + 1) * rec_size
	height = (len(board) + 1) * rec_size

	drawer = Tk()
	window = Canvas(drawer, width=width, height=height)

	for i in range(len(board[0])):
		window.create_text(50 + i * rec_size, 15, fill="black", font="Times 20 italic bold", text=str(i))

	for j in range(len(board)):
		window.create_text(15, 50 + j * rec_size, fill="black", font="Times 20 italic bold", text=str(j))

	total_dict = {**color_dict, **type_color_dict}

	for node in all_nodes:
		x = node.x + 1
		y = node.y + 1
		window.create_rectangle(y * rec_size, x * rec_size, y * rec_size + rec_size, x * rec_size + rec_size,
								fill=total_dict[node.type])
		if node.in_path:
			window.create_text(y * rec_size + 0.5 * rec_size, x * rec_size + 0.5 * rec_size, fill="black",
							   font="Times 22 italic bold", text="•")
		if node.start:
			window.create_text(y * rec_size + 0.5 * rec_size, x * rec_size + 0.5 * rec_size, fill="black",
							   font="Times 20 italic bold", text=node.type)
		if node.solution:
			window.create_text(y * rec_size + 0.5 * rec_size, x * rec_size + 0.5 * rec_size, fill="black",
							   font="Times 20 italic bold", text=node.type)

	window.pack()
	drawer.mainloop()


def getWeight():
	"""
	Calculates the average cost of all nodes
	:return: average cost of all nodes
	"""
	weight = 0
	counter = 0
	for node in all_nodes:
		if not node.start and not node.solution:  # Regular node that can be in path
			weight += node.cost
			counter += 1

	return weight / counter


def euclid_distance(node):
	"""
	:param node: Node in board
	:return: Euclid distance from node to goal
	"""
	return m.sqrt(m.pow(goal.x - node.x, 2) + m.pow(goal.y - node.y, 2))


def manhattan_distance(node):
	"""
	:param node: Node in board
	:return: Manhattan distance from node to goal
	"""
	return abs(goal.x - node.x) + abs(goal.y - node.y)


# Below we will start the A-Star path-finding

filename = "boards/board-2-4.txt"  # Change this filename to do A-star on other boards from file
part = int(filename.split("-")[1])

cost_dict = {"w": 100, "m": 50, "f": 10, "g": 5, "r": 1, ".": 1}
color_dict = {"A": "red", "B": "green", "#": "black", ".": "white"}
type_color_dict = {"w": "blue", "m": "azure3", "f": "darkgreen", "g": "SpringGreen2", "r": "tan4"}

start, goal, all_nodes, board = create_nodes()

# Setting initial state for traversing nodes
start.h = euclid_distance(start)
start.g = 0
goal.h = 0

if part == 2:
	weight = getWeight()

if a_star():
	print("Path found")
	print("Start-node:", start)
	print("Goal-node:", goal)

	node = goal.parent
	while node != start:
		node.in_path = True
		print(node)
		node = node.parent

	if part == 1:
		draw_board()
	if part == 2:
		draw_board2()
