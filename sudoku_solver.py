import json
from copy import deepcopy

class SudokuSolver:
	"""
	Sudoku Solver based on the Backtracking algorithm.

	Backtracking algorithm demonstrates the best in the average case, according to:
	Berggren, P., & Nilsson, D. (2012). A study of Sudoku Solving Algorithms.

	Implementation is adopted from:
	https://techwithtim.net/tutorials/python-programming/sudoku-solver-backtracking/

	Improved, commented, and adjusted by: Alexander Ulyanov
	"""


	def __init__(self, input):
		"""
		Constructor

		:param input: the input board as a 2-D list (0's are the empty cells)
		"""
		self.input = input
		self.solution = deepcopy(input)


	def solve(self):
		"""
		Recursively solves the Sudoku, using backtracking algorithm

		:return: True if the board is solved, False otherwise
		"""
		empty_cell = SudokuSolver._find_empty_cell(self.solution)

		if not empty_cell:
			return True
		else:
			row, col = empty_cell

		for i in range(1, len(self.solution)+1):
			if SudokuSolver._is_valid(self.solution, i, (row, col)):
				self.solution[row][col] = i
				if self.solve():
					return True
				self.solution[row][col] = 0

		return False


	def get_input(self):
		"""
		Get the raw input of the Sudoku

		:return: the input of the Sudoku as a 2-D list
		"""
		return self.input


	def get_solution(self):
		"""
		Get the raw solution of the Sudoku

		:return: solved Sudoku board as a 2-D list
		"""
		return self.solution


	def get_str_input(self):
		"""
		Get the raw input of the Sudoku

		:return: the input of the Sudoku as a string
		"""
		return str(self.get_input())


	def get_str_solution(self):
		"""
		Get the raw solution of the Sudoku

		:return: solved Sudoku board as a string
		"""
		return str(self.get_solution())


	def get_formatted_str_input(self):
		"""
		Get the formatted input for the Sudoku

		:return: Sudoku input as a formatted string
		"""
		return SudokuSolver._print_board(self.get_input())


	def get_formatted_str_solution(self):
		"""
		Get the formatted solution of the Sudoku

		:return: solved Sudoku board as a formatted string
		"""
		return SudokuSolver._print_board(self.get_solution())


	# Static utility methods

	def _find_empty_cell(board):
		"""
		Find the first empty cell on the board

		:return: a tuple with coordinates of the empty cell on the board, if found, `None` otherwise
		"""
		for i in range(len(board)):
			for j in range(len(board[i])):
				if board[i][j] == 0:
					return (i, j)
		return None


	def _is_valid(board, number, position):
		"""
		Checks if the proposed number is valid

		:param board: the board where to search for an empty cell
		:param number: the proposed number
		:param position: the position of the proposed number
		:return: True, if the same number does not already exist in the row, column, and the small box; False otherwise
		"""
		# Check if the number is not already present in the row
		for i in range(len(board[0])):
			if board[position[0]][i] == number and position[1] != i:
				return False

		# Check if the number is not already present in the column
		for i in range(len(board)):
			if board[i][position[1]] == number and position[0] != i:
				return False

		# Check if th number is not already present in the small box
		box_x = position[1] // 3
		box_y = position[0] // 3

		for i in range(box_y*3, box_y*3 + 3):
			for j in range(box_x * 3, box_x*3 + 3):
				if board[i][j] == number and (i,j) != position:
					return False

		return True


	def _print_board(board):
		"""
		Formats the board into a string so each row is on a new line.

		Template:
		[[.., .., ..],
		 [.., .., ..],
		 [.., .., ..]]

		:param board: the board as a 2-D list
		:return: a string containing formatted board
		"""
		result = "["
		for i in range(len(board)):
			if i > 0:
				result += " "
			result += json.dumps(board[i])
			if i < len(board)-1:
				result += ",\n"
		result += "]"
		return result


	def is_valid_board(input):
		"""
		Checks if the board passed in as a 2-D list is a valid Sudoku board

		:param input: board as a 2-D list
		:return: True, if the board is valid; False, otherwise
		"""
		board = None

		# 1. Make sure it's a list
		if not isinstance(board, list):
			return False

		# 2. Make sure it's 9x9 and only contains digits 0-9

		# Check the number of rows
		if len(board) != 9:
			return False

		# Check the number of columns in each row, and that each element is a number from 0 to 9
		for row in board:
			if len(row) != 9:
				return False
			for element in row:
				if not (isinstance(element, int) and element >= 0 and element <=9):
					return False

		# If everything is ok, we are good to go!
		return True
