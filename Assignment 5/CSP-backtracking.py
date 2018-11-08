#!/usr/bin/python3
import copy
import itertools
from tkinter import *

__author__ = "Henrik Høiness"


class CSP:
	"""
	Class for representing a Constraint Satisfaction Problem - in this task Sudoku
	"""
	def __init__(self):
		# self.variables is a list of the variable names in the CSP
		self.variables = []

		# self.domains[i] is a list of legal values for variable i
		self.domains = {}

		# self.constraints[i][j] is a list of legal value pairs for
		# the variable pair (i, j)
		self.constraints = {}

		# Number of backtracks done in CSP.backtracking_search()
		self.backtracking_number = 0

		# Number of failed backtracks done in CSP.backtracking_search()
		self.failed_backtracking_number = 0

	def add_variable(self, name, domain):
		"""
		Add a new variable to the CSP. 'name' is the variable name
		and 'domain' is a list of the legal values for the variable.
		"""
		self.variables.append(name)
		self.domains[name] = list(domain)
		self.constraints[name] = {}

	def get_all_possible_pairs(self, a, b):
		"""
		Get a list of all possible pairs (as tuples) of the values in
		the lists 'a' and 'b', where the first component comes from list
		'a' and the second component comes from list 'b'.
		"""
		return itertools.product(a, b)

	def get_all_arcs(self):
		"""
		Get a list of all arcs/constraints that have been defined in
		the CSP. The arcs/constraints are represented as tuples (i, j),
		indicating a constraint between variable 'i' and 'j'.
		"""
		return [(i, j) for i in self.constraints for j in self.constraints[i]]

	def get_all_neighboring_arcs(self, var):
		"""
		Get a list of all arcs/constraints going to/from variable
		'var'. The arcs/constraints are represented as in get_all_arcs().
		"""
		return [(i, var) for i in self.constraints[var]]

	def add_constraint_one_way(self, i, j, filter_function):
		"""
		Add a new constraint between variables 'i' and 'j'. The legal
		values are specified by supplying a function 'filter_function',
		that returns True for legal value pairs and False for illegal
		value pairs. This function only adds the constraint one way,
		from i -> j. You must ensure that the function also gets called
		to add the constraint the other way, j -> i, as all constraints
		are supposed to be two-way connections!
		"""
		if j not in self.constraints[i]:
			# First, get a list of all possible pairs of values between variables i and j
			self.constraints[i][j] = self.get_all_possible_pairs(self.domains[i], self.domains[j])

		# Next, filter this list of value pairs through the function
		# 'filter_function', so that only the legal value pairs remain
		self.constraints[i][j] = list(filter(lambda value_pair: filter_function(*value_pair), self.constraints[i][j]))

	def add_all_different_constraint(self, variables):
		"""
		Add an Alldiff constraint between all of the variables in the
		list 'variables'.
		"""
		for (i, j) in self.get_all_possible_pairs(variables, variables):
			if i != j:
				self.add_constraint_one_way(i, j, lambda x, y: x != y)

	def backtracking_search(self):
		"""
		This functions starts the CSP solver and returns the found
		solution.
		"""
		# Make a so-called "deep copy" of the dictionary containing the
		# domains of the CSP variables. The deep copy is required to
		# ensure that any changes made to 'assignment' does not have any
		# side effects elsewhere.
		assignment = copy.deepcopy(self.domains)

		# Run AC-3 on all constraints in the CSP, to weed out all of the
		# values that are not arc-consistent to begin with
		self.inference(assignment, self.get_all_arcs())

		# Setting initial values for tracking backtracking
		self.backtracking_number = 1
		self.failed_backtracking_number = 0

		# Call backtrack with the partial assignment 'assignment'
		return self.backtrack(assignment)

	def backtrack(self, assignment):
		"""
		The function 'Backtrack' based on the pseudocode in the
		textbook.

		The function is called recursively, with a partial assignment of
		values 'assignment'. 'assignment' is a dictionary that contains
		a list of all legal values for the variables that have *not* yet
		been decided, and a list of only a single value for the
		variables that *have* been decided.

		When all of the variables in 'assignment' have lists of length
		one, i.e. when all variables have been assigned a value, the
		function should return 'assignment'. Otherwise, the search
		should continue. When the function 'inference' is called to run
		the AC-3 algorithm, the lists of legal values in 'assignment'
		should get reduced as AC-3 discovers illegal values.
		"""

		# Returning assignment when all assignments have length one
		if sum(len(domain) for domain in assignment.values()) == len(assignment):
			return assignment

		variable = self.select_unassigned_variable(assignment)
		for value in assignment[variable]:
			assignment_cp = copy.deepcopy(assignment)
			assignment_cp[variable] = value
			if self.inference(assignment_cp, self.get_all_arcs()):
				# Found inference calling backtrack recursively
				self.backtracking_number += 1
				result = self.backtrack(assignment_cp)
				if result:
					return result

		# Backtracking failed
		self.failed_backtracking_number += 1
		return

	def select_unassigned_variable(self, assignment):
		"""
		The function 'Select-Unassigned-Variable' based on the pseudocode
		in the textbook. Should return the name of one of the variables
		in 'assignment' that have not yet been decided, i.e. whose list
		of legal values has a length greater than one.
		"""
		# Assuming that at least one item has two or more legal values
		# Choosing the variable with the least amount of possible values
		return min(assignment.keys(),key=lambda var: float("inf") if len(assignment[var]) < 2 else len(assignment[var]))

	def inference(self, assignment, queue):
		"""
		The function 'AC-3' based on the pseudocode in the textbook.
		'assignment' is the current partial assignment, that contains
		the lists of legal values for each undecided variable. 'queue'
		is the initial queue of arcs that should be visited.
		"""
		while queue:
			xi, xj = queue.pop(0)
			if self.revise(assignment, xi, xj):
				if not assignment[xi]:
					return False
				for xk, _ in self.get_all_neighboring_arcs(xi):
					if xk != xj:
						queue.append((xk, xi))
		return True

	def revise(self, assignment, xi, xj):
		"""
		The function 'Revise' is based from the pseudocode in the textbook.
		'assignment' is the current partial assignment, that contains
		the lists of legal values for each undecided variable. 'xi' and
		'xj' specifies the arc that should be visited. If a value is
		found in variable xi's domain that doesn't satisfy the constraint
		between xi and xj, the value should be deleted from xi's list of
		legal values in 'assignment'.
		"""
		revised = False

		for x in assignment[xi]:
			arcs = list(self.get_all_possible_pairs([x], assignment[xj]))
			if not sum(arc in self.constraints[xi][xj] for arc in arcs):
				revised = True
				assignment[xi].remove(x) if x in assignment[xi] else None

		return revised


def create_sudoku_csp(filename):
	"""
	Instantiate a CSP representing the Sudoku board found in the text
	file named 'filename' in the current directory.
	"""
	csp = CSP()
	board = list(map(lambda x: x.strip(), open(filename, 'r')))

	for row in range(9):
		for col in range(9):
			if board[row][col] == '0':
				csp.add_variable('{}-{}'.format(row, col), map(str, range(1, 10)))
			else:
				csp.add_variable('{}-{}'.format(row, col), [board[row][col]])

	for row in range(9):
		csp.add_all_different_constraint(['{}-{}'.format(row, col) for col in range(9)])
	for col in range(9):
		csp.add_all_different_constraint(['{}-{}'.format(row, col) for row in range(9)])
	for box_row in range(3):
		for box_col in range(3):
			cells = []
			for row in range(box_row * 3, (box_row + 1) * 3):
				for col in range(box_col * 3, (box_col + 1) * 3):
					cells.append('{}-{}'.format(row, col))
			csp.add_all_different_constraint(cells)

	return csp


def print_sudoku_solution(solution):
	"""
	Convert the representation of a Sudoku solution as returned from
	the method CSP.backtracking_search(), into a human readable
	representation.
	"""
	for row in range(9):
		for col in range(9):
			print(solution['{}-{}'.format(row, col)][0], end=" ")
			if col == 2 or col == 5:
				print('|', end=" "),
		print()
		if row == 2 or row == 5:
			print('------+-------+------')


def draw_board(solution, backtracking_number, failed_backtracking_number, boardname=""):
	"""
	Method for drawing sudoku board with solution from CSP-backtracking with kTinker
	"""
	rec_size = 35
	width = 9 * rec_size + 3
	height = 9 * rec_size + 3

	drawer = Tk()
	drawer.winfo_toplevel().title("Solved {}".format(boardname))
	window = Canvas(drawer, width=width, height=height)

	def exit_tkinter():
		drawer.destroy()

	def stop_solving():
		global solving
		solving = False
		drawer.destroy()

	for row in range(9):
		for col in range(9):
			x = row + 0.1
			y = col + 0.1

			# Drawing thicker lines on certain rows and columns
			col_space = 1 if col == 3 or col == 6 else 0
			row_space = 1 if row == 3 or row == 6 else 0

			window.create_rectangle(y * rec_size + col_space, x * rec_size + row_space, y * rec_size + rec_size,
									x * rec_size + rec_size,
									fill="white")

			window.create_text(y * rec_size + 0.5 * rec_size, x * rec_size + 0.5 * rec_size,
							   fill="black", font="Times 20 italic bold", text=(solution['{}-{}'.format(row, col)][0]))

	next_button = Button(drawer, text="Solve next board",
						 width=30, command=exit_tkinter, height=2)
	stop_button = Button(drawer, text="Stop solving",
						 width=30, command=stop_solving, height=2)

	label1 = Label(drawer, text="Number of backtracks: {}".format(backtracking_number))
	label2 = Label(drawer, text="Number of failed backtracks: {}".format(failed_backtracking_number))

	window.pack()
	label1.pack()
	label2.pack()
	next_button.pack()
	stop_button.pack()

	drawer.mainloop()


def main():
	board_paths = [("Easy", "sudokus/easy.txt"),
				 ("Medium", "sudokus/medium.txt"),
				 ("Hard", "sudokus/hard.txt"),
				 ("Very hard", "sudokus/veryhard.txt"),
				 ("Worlds Toughest 2012", "sudokus/worldstoughest2012.txt")]
	for filepath in board_paths:
		if solving:
			print(">  Solving {}".format(filepath[0]), end="\n\n")
			csp = create_sudoku_csp(filepath[1])
			solution = csp.backtracking_search()
			draw_board(solution, csp.backtracking_number, csp.failed_backtracking_number, filepath[0])

	if not solving:
		print("Stopped solving")

solving = True
main()
