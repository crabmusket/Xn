# Xn: the procedural dungeon generator

# This procedural map-maker aims to recreate the feel of
# The X18 and other laboratory 'dungeons' in the S.T.A.L.K.E.R.
# video game series by arranging premade 'rooms' in a connected,
# sensible fashion.

# This is a test of the generating algorithm and overall process.

import random
import math
import copy

N = 0 # NORTH
S = 1 # SOUTH
E = 2 # EAST
W = 3 # WEST
COMPASS = ["N", "S", "E", "W"]
DIRECTIONS = [(0, -1, 0), (0, 1, 0), (1, 0, 0), (-1, 0, 0)]

# Simple 3D vector addition with iterables
def vadd(v1, v2):
	return (v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2])

class Door:
	"""Represents an entrance/exit point for a room."""
	def __init__(self, loc, dir):
		self.loc = loc
		self.dir = dir
	def __str__(self):
		return "%d %d %d %s" % (self.loc[0], self.loc[1], self.loc[2], COMPASS[self.dir])

class RoomShape:
	"""Represents a single room blueprint."""
	def __init__(self, name, dimensions, doors):
		"""Constructor
		Arguments:
		name -- a string giving a user-friendly name for the room
		dimensions -- a tuple of (x, y, z) dimensions of the room (whole numbers, please)
		doors -- a list specifying the coordinates of doors within the room and their directions
		"""
		if " " in name:
			raise Exception("Rooms cannot have spaces in their names.")
		self.name = name
		self.width = dimensions[0]
		self.length = dimensions[1]
		self.levels = dimensions[2]
		self.doors = doors
	def __str__(self):
		string = "%s %d %d %d %d " % (self.name, self.width, self.length, self.levels, len(self.doors))
		string += " ".join([str(d) for d in self.doors])
		return string

class Room:
	"""Represents an instance of a room in the final layout."""
	def __init__(self, shape, pos = (0, 0, 0), orient = N):
		self.shape = shape
		self.orientation = orient
		self.position = pos
	def __str__(self):
		return "%s %d %d %d %s" % (self.shape.name, self.position[0], self.position[1], self.position[2], COMPASS[self.orientation])

class Arrangement:
	"""An arrangement of Rooms representing a dungeon."""
	def __init__(self, x, y, z):
		if x <= 0 or y <= 0 or z <= 0:
			raise Exception("Grid sizes must be > 0!")
		self.levels = z
		self.length = y
		self.width = x
		self.grid = [[[0 for i in xrange(x)] for j in xrange(y)] for k in xrange(z)]
		self.shapes = []
		self.rooms = []
		self.doors = [[] for i in xrange(z)]
		self.corridors = []

	def test(self, pos, sparse = 1):
		"""Test to see if a position is available."""
		if pos[0] >  sparse-1 and pos[0] < self.width  - sparse and \
		   pos[1] >  sparse-1 and pos[1] < self.length - sparse and \
		   pos[2] >  -1       and pos[2] < self.levels:
			for j in xrange(-sparse, sparse + 1):
				for i in xrange(-sparse, sparse + 1):
					if self.grid[pos[2]][pos[1] + j][pos[0] + i] != 0:
						return False
			return True
		return False

	def set_grid(self, pos, val):
		if pos[0] > -1 and pos[0] < self.width and \
		   pos[1] > -1 and pos[1] < self.length and \
		   pos[2] > -1 and pos[2] < self.levels:
			self.grid[pos[2]][pos[1]][pos[0]] = val

	def get_grid(self, pos):
		if pos[0] > -1 and pos[0] < self.width and \
		   pos[1] > -1 and pos[1] < self.length and \
		   pos[2] > -1 and pos[2] < self.levels:
			return self.grid[pos[2]][pos[1]][pos[0]]
		return None

	def testshape(self, shape, pos, orient, sparse = 1):
		"""Test to see is a room can be placed at a position."""
		if shape is None:
			raise Exception("Testing None Room!")
		startx = pos[0]
		starty = pos[1]
		startz = pos[2]
		for k in xrange(shape.levels):
			for j in xrange(shape.length):
				for i in xrange(shape.width):
					x = startx + i
					y = starty + j
					z = startz + k
					if x >= self.width or y >= self.length or z >= self.levels:
						return False
					if not self.test((x, y, z), sparse):
						return False
		return True

	def add(self, room, pos, orient):
		if room is None:
			raise Exception("Trying to add None Room!")
		if room in self.rooms:
			raise Exception("Trying to add a Room twice!")
		# Assume the room is valid in this location
		self.rooms.append(room)
		room.position = pos
		room.orientation = orient
		# Remember each shape used
		if room.shape not in self.shapes:
			self.shapes.append(room.shape)
		# Mark grid for collision testing
		startx = pos[0]
		starty = pos[1]
		startz = pos[2]
		for k in xrange(room.shape.levels):
			for j in xrange(room.shape.length):
				for i in xrange(room.shape.width):
					x = startx + i
					y = starty + j
					z = startz + k
					self.grid[z][y][x] = room
		# Remember doors on each floor
		for d in copy.deepcopy(room.shape.doors):
			d.loc = vadd(d.loc, pos)
			self.doors[d.loc[2]].append(d)

	def remove(self, room):
		if room is None or room not in self.rooms:
			raise Exception("Trying to remove Room not in Arrangement!")

	def render(self):
		string = ""
		for z in xrange(self.levels):
			for y in xrange(self.length):
				for x in xrange(self.width):
					g = self.grid[z][y][x]
					if g is None or g == 0:
						string += "."
					elif g == 1:
						string += "/"
					elif isinstance(g, Room):
						string += "#"
					else:
						string += "?"
				string += "\n"
			string += "\n"
		return string

	def list(self):
		# List of shapes we use:
		string = str(len(self.shapes)) + "\n"
		string += "\n".join([str(s) for s in self.shapes]) + "\n"
		# List of rooms
		string += str(len(self.rooms)) + "\n"
		string += "\n".join([str(r) for r in self.rooms]) + "\n"
		# List of corridor segments
		string += str(len(self.corridors)) + "\n"
		string += "\n".join(["%d %d %d" % (c[0], c[1], c[2]) for c in self.corridors]) + "\n"
		return string

	def __str__(self):
		return self.list()

shapes = [
	RoomShape("elevatorN", (1, 1, 5),
		[Door((0, 0, 0), N),
		 Door((0, 0, 2), N),
		 Door((0, 0, 4), N)]),
	RoomShape("elevatorS", (1, 1, 5),
		[Door((0, 0, 0), S),
		 Door((0, 0, 2), S),
		 Door((0, 0, 4), S)]),
	RoomShape("elevatorE", (1, 1, 5),
		[Door((0, 0, 0), E),
		 Door((0, 0, 2), E),
		 Door((0, 0, 4), E)]),
	RoomShape("elevatorW", (1, 1, 5),
		[Door((0, 0, 0), W),
		 Door((0, 0, 2), W),
		 Door((0, 0, 4), W)]),
	RoomShape("stairs", (1, 1, 2),
		[Door((0, 0, 0), N),
		 Door((0, 0, 1), S)]),
	RoomShape("stairsW", (1, 1, 2),
		[Door((0, 0, 0), E),
		 Door((0, 0, 1), W)]),
	RoomShape("foyerN", (3, 3, 2),
		[Door((1, 0, 0), N),
		 Door((1, 0, 1), N)]),
	RoomShape("foyerE", (3, 3, 2),
		[Door((2, 1, 0), E),
		 Door((2, 1, 1), E)]),
	RoomShape("foyerW", (3, 3, 2),
		[Door((0, 1, 0), W),
		 Door((0, 1, 1), W)]),
	RoomShape("officeN", (2, 2, 1),
		[Door((0, 0, 0), N)]),
	RoomShape("officeS", (2, 2, 1),
		[Door((0, 1, 0), S)]),
	RoomShape("officeE", (2, 2, 1),
		[Door((1, 0, 0), E)]),
	RoomShape("officeW", (2, 2, 1),
		[Door((0, 0, 0), W)]),
	RoomShape("commonN", (3, 2, 1),
		[Door((1, 1, 0), S),
		 Door((1, 0, 0), N)]),
	RoomShape("commonS", (3, 2, 1),
		[Door((1, 1, 0), S),
		 Door((1, 0, 0), N)]),
	RoomShape("commonE", (2, 3, 1),
		[Door((0, 1, 0), W),
		 Door((1, 2, 0), E)]),
	RoomShape("commonW", (2, 3, 1),
		[Door((0, 1, 0), W),
		 Door((1, 0, 0), E)]),
]

singleshapes = [
	shapes[0], shapes[1], shapes[2], shapes[3],
	shapes[6], shapes[7], shapes[8],
]

# Functions that determine how many rooms are placed on each floor

def simple_density(length, width, height, floor):
	if floor is 0:
		return 1
	else:
		return 2

def even_density(length, width, height, floor):
	if floor is 0:
		return 1
	else:
		return (length + width) / 2

def increasing_density(length, width, height, floor):
	return int((floor + 1) / float(height) * (length + width) / 2)

def decreasing_density(length, width, height, floor):
	return int((1 - (floor + 1) / float(height)) * (length + width) / 2)

densityfunctions = {
	"simple": simple_density,
	"even": even_density,
	"increasing": increasing_density,
	"decreasing": decreasing_density,
}

# Functions that determine the starting point of each floor search

def constant_offset(length, width, height, floor):
	return [(width-2)/2, (length-1)/2]

def random_offset(length, width, height, floor):
	return [random.choice(range(width)), random.choice(range(length))]

offsetfunctions = {
	"constant": constant_offset,
	"random": random_offset,
}

WIDTH = 10
LENGTH = 10
LEVELS = 15
SEED = 451
DENSITY = "even"
OFFSET = "constant"
VERTSPACE = False
SPARSITY = 1

def generate():
	global WIDTH
	global LENGTH
	global LEVELS
	global SEED
	global DENSITY
	global OFFSET
	global VERTSPACE
	global SPARSITY
	random.seed(SEED)
	a = Arrangement(WIDTH, LENGTH, LEVELS)
	for k in xrange(LEVELS):
		# Box-pack the floor with the correct number of rooms
		rooms = densityfunctions[DENSITY](WIDTH, LENGTH, LEVELS, k)
		for r in xrange(rooms):
			s = None
			# Choose a shape that fits vertically
			shapelist = shapes
			if rooms == 1:
				shapelist = singleshapes
			random.shuffle(shapelist)
			for i in xrange(len(shapelist)):
				s = shapelist[i]
				if s.levels > LEVELS - k or (rooms == 1 and s.levels is 1):
					continue
				break
			# Spiral search for a horizontal position that is acceptable
			cur = offsetfunctions[OFFSET](WIDTH, LENGTH, LEVELS, k)
			horiz = [1, 0, -1, 0]
			vert = [0, -1, 0, 1]
			index = 0
			steps = 1
			step = 0
			while cur[0] < a.width and cur[1] < a.length:
				if a.testshape(s, (cur[0], cur[1], k), N, SPARSITY):
					r = Room(s)
					a.add(r, (cur[0], cur[1], k), N)
					break
				cur[0] += horiz[index]
				cur[1] += vert[index]
				step += 1
				if step is steps:
					step = 0
					index += 1
					if index % 2 == 0:
						steps += 1
					if index > 3:
						index = 0
		# Link doors with corridors
		if len(a.doors[k]) > 0:
			# Set up goal nodes outside each door
			targets = []
			for d in a.doors[k]:
				target = vadd(d.loc, DIRECTIONS[d.dir])
				targets.append(target)
			# Pick a random target to start from
			random.shuffle(targets)
			start = targets.pop()
			# Open list of positions to explore
			open = [start]
			a.set_grid(start, [None, 0])
			openc = 1
			while openc > 0:
				# Use open list as a queue -> BFS
				node = open.pop(0)
				tile = a.get_grid(node)
				openc -= 1
				# Add neighbours to open list
				for i in xrange(0, 4):
					neigh = vadd(node, DIRECTIONS[i])
					n = a.get_grid(neigh)
					if n is not None:
						# As-yet-unexplored square
						if n == 0:
							open.append(neigh)
							openc += 1
							dist = tile[1] + 1
							gridval = [node, dist]
							a.set_grid(neigh, gridval)
						# Square containing not a room but an already-explored tile
						elif isinstance(n, list):
							if n[1] > tile[1] + 1:
								a.set_grid(neigh, [node, tile[1] + 1])
			# Walk back from targets to source replacing with 1
			for t in targets:
				t_ = a.get_grid(t)
				while isinstance(t_, list):
					a.set_grid(t, 1)
					a.corridors.append(t)
					if t_[0] is not None:
						t = t_[0]
						t_ = a.get_grid(t_[0])
					else:
						break
			# Replace unwalked tiles with 0
			for j in xrange(a.length):
				for i in xrange(a.width):
					g = a.grid[k][j][i]
					if g != 1 and not isinstance(g, Room):
						a.grid[k][j][i] = 0
	return a
