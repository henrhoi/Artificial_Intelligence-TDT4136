# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent


class ReflexAgent(Agent):
	"""
	  A reflex agent chooses an action at each choice point by examining
	  its alternatives via a state evaluation function.

	  The code below is provided as a guide.  You are welcome to change
	  it in any way you see fit, so long as you don't touch our method
	  headers.
	"""

	def getAction(self, gameState):
		"""
		You do not need to change this method, but you're welcome to.

		getAction chooses among the best options according to the evaluation function.

		Just like in the previous project, getAction takes a GameState and returns
		some Directions.X for some X in the set {North, South, West, East, Stop}
		"""
		# Collect legal moves and successor states
		legalMoves = gameState.getLegalActions()

		# Choose one of the best actions
		scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
		bestScore = max(scores)
		bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
		chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

		"Add more of your code here if you want to"

		return legalMoves[chosenIndex]

	def evaluationFunction(self, currentGameState, action):
		"""
		Design a better evaluation function here.

		The evaluation function takes in the current and proposed successor
		GameStates (pacman.py) and returns a number, where higher numbers are better.

		The code below extracts some useful information from the state, like the
		remaining food (newFood) and Pacman position after moving (newPos).
		newScaredTimes holds the number of moves that each ghost will remain
		scared because of Pacman having eaten a power pellet.

		Print out these variables to see what you're getting, then combine them
		to create a masterful evaluation function.
		"""
		# Useful information you can extract from a GameState (pacman.py)
		successorGameState = currentGameState.generatePacmanSuccessor(action)
		currentPos = currentGameState.getPacmanPosition()
		currentFood = currentGameState.getFood()

		newPos = successorGameState.getPacmanPosition()
		newFood = successorGameState.getFood()
		newGhostStates = successorGameState.getGhostStates()
		newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

		"*** YOUR CODE HERE ***"

		# Checking if newPos is a food in current Food-map, that will give higher evaluation
		isFood = 200 if currentFood[newPos[0]][newPos[1]] else 0

		# Checking the minimum manhattan distance from new position to the ghosts
		min_ghost_distance = min(manhattanDistance(newPos, ghost_pos.configuration.pos) for ghost_pos in newGhostStates)
		ghost_punishment = 0

		# Giving a punishment to the evaluation if the new position is close to a ghost
		if min_ghost_distance < 2:
			ghost_punishment = -200
		if min_ghost_distance < 1:
			ghost_punishment = -300
		if min_ghost_distance == 0: # If the new position is on a ghost, it will have the smallest evaluation possible
			ghost_punishment = float("-inf")

		# If the ghosts can be eaten, the punishment is not to be considered
		ghost_punishment = -1 if sum(newScaredTimes) > 5 and min_ghost_distance > 5 else ghost_punishment

		# If pacman can eat a ghost in less than two moves and the ghost can be eaten, the move will get points for that
		if ghost_punishment == -1 and min_ghost_distance < 2:
			ghost_punishment = 50  # Punishment is positive

		# Adding a heuristic on the closest food, and withdraws points if the new position is far away from any food.
		# This gave a lot of improvements, and stopped pacman from standing still or going in circle.
		# This addition was inspired by A-star algorithm
		food_list = newFood.asList()

		if food_list:
			min_food_distance = min([abs(manhattanDistance(newPos, food)) for food in food_list])
		else:
			min_food_distance = 0

		return successorGameState.getScore() + isFood + ghost_punishment - 2*min_food_distance


def scoreEvaluationFunction(currentGameState):
	"""
	This default evaluation function just returns the score of the state.
	"""
	return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
	"""
	This class provides some common elements to all of your
	multi-agent searchers.  Any methods defined here will be available
	to the MinimaxPacmanAgent, AlphaBetaPacmanAgent.
	"""

	def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
		self.index = 0  # Pacman is always agent index 0
		self.evaluationFunction = util.lookup(evalFn, globals())
		self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
	"""
	Your minimax agent (question 2)
	"""
	"*** YOUR CODE HERE***"

	def getAction(self, gameState):
		"""
		Returns the minimax action from the current gameState using self.depth
		and self.evaluationFunction.
		"""

		return self.decide_next_value(gameState, 0)[0]

	def decide_next_value(self, state, depth):
		"""
		Calls the correct method for calculating next action, value pair for state.
		This has to be done because it needs to handle multiple min-layers in Minimax-tree

		:param state: Current state of game
		:param depth: Current depth of Minimax-tree
		:return: action, action_evaluation (either MIN or MAX)
		"""
		if depth == self.depth * state.getNumAgents() or state.isWin() or state.isLose():
			return None, self.evaluationFunction(state)

		agent_index = depth % state.getNumAgents()
		if agent_index >= 1:
			return self.min_value(state, depth)

		else:
			return self.max_value(state, depth)

	def max_value(self, state, current_depth):
		"""
		Calculates the action with maximum value in Minimax-tree

		:param current_depth: Current depth in Minimax-tree
		:param state: Current gamestate
		:return: action, action_evaluation
		"""

		best_value = None, float("-inf")
		possible_actions = state.getLegalActions(0)
		if not possible_actions:
			return None, self.evaluationFunction(state)

		for action in possible_actions:
			next_state = state.generateSuccessor(0, action)
			action_value = self.decide_next_value(next_state, current_depth + 1)[1]
			best_value = max(best_value, (action, action_value), key=lambda x: x[1])

		return best_value

	def min_value(self, state, current_depth):
		"""
		Calculates the action for a ghost with minimum value in Minimax-tree

		:param state: Current gamestate
		:param current_depth: Current depth in Minimax-tree. current_depth % state.getNumAgents gives current ghost
		:return: action, action_evaluation
		"""

		best_value = None, float("inf")
		agent_index = current_depth % state.getNumAgents()
		possible_actions = state.getLegalActions(agent_index)
		if not possible_actions:
			return None, self.evaluationFunction(state)

		for action in possible_actions:
			next_state = state.generateSuccessor(agent_index, action)
			action_value = self.decide_next_value(next_state, current_depth + 1)[1]
			best_value = min(best_value, (action, action_value), key=lambda x: x[1])

		return best_value


class AlphaBetaAgent(MultiAgentSearchAgent):
	"""
	Your minimax agent with alpha-beta pruning (question 3)
	"""

	"*** YOUR CODE HERE***"

	def getAction(self, game_state):
		"""
		Returns the minimax action using self.depth and self.evaluationFunction
		"""

		alpha = None, float("-inf")
		beta = None, float("inf")

		return self.decide_next_value(game_state, 0, alpha, beta)[0]

	def decide_next_value(self, state, depth, alpha, beta):
		"""
		Calls the correct method for calculating next action, value pair for state.
		This has to be done because it needs to handle multiple min-layers in Minimax-tree

		:param state: Current state of game
		:param depth: Current depth of Minimax-tree
		:param alpha: Alpha-value for pruning at this evaluation
		:param beta: Beta-value for pruning at this evaluation
		:return: action, action_evaluation (either MIN or MAX)
		"""

		if depth == self.depth * state.getNumAgents() or state.isWin() or state.isLose():
			return None, self.evaluationFunction(state)

		agent_index = depth % state.getNumAgents()
		if agent_index >= 1:
			return self.min_value(state, depth, alpha, beta)

		else:
			return self.max_value(state, depth, alpha, beta)

	def max_value(self, state, current_depth, alpha, beta):
		"""
		Calculates the action with maximum value in Minimax-tree

		:param state: Current state in game
		:param current_depth: Current depth in Minimax-tree
		:param alpha: The value of the best (i.e., highest-value) choice we have found so far at any choice point along the path for MAX.
		:param beta: The value of the best (i.e., lowest-value) choice we have found so far at any choice point along the path for MIN.
		:return: action, action_evaluation
		"""

		best_value = None, float("-inf")
		possible_actions = state.getLegalActions(0)
		if not possible_actions:
			return None, self.evaluationFunction(state)

		for action in possible_actions:
			next_state = state.generateSuccessor(0, action)
			action_value = self.decide_next_value(next_state, current_depth + 1, alpha, beta)[1]
			best_value = max(best_value, (action, action_value), key=lambda x: x[1])
			if best_value[1] > beta[1]:
				return best_value
			alpha = max(alpha, best_value, key=lambda x: x[1])

		return best_value

	def min_value(self, state, current_depth, alpha, beta):
		"""
		Calculates the action for a ghost with minimum value in Minimax-tree

		:param current_depth: Current depth in Minimax-tree
		:param state: Current gamestate
		:param current_depth: Current depth in Minimax-tree. current_depth % state.getNumAgents() will give current ghost
		:param alpha: The value of the best (i.e., highest-value) choice we have found so far at any choice point along the path for MAX.
		:param beta: The value of the best (i.e., lowest-value) choice we have found so far at any choice point along the path for MIN.
		:return: action, action_evaluation
		"""

		best_value = None, float("inf")
		agent_index = current_depth % state.getNumAgents()
		possible_actions = state.getLegalActions(agent_index)
		if not possible_actions:
			return None, self.evaluationFunction(state)

		for action in possible_actions:
			next_state = state.generateSuccessor(agent_index, action)
			action_value = self.decide_next_value(next_state, current_depth + 1, alpha, beta)[1]
			best_value = min(best_value, (action, action_value), key=lambda x: x[1])

			if best_value[1] < alpha[1]:
				return best_value
			beta = min(beta, best_value, key=lambda x: x[1])

		return best_value
