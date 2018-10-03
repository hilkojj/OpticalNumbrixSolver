import time
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import puzzlereader


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class Puzzle:

    def __init__(self, grid, diagonal):
        self.grid = grid
        self.diagonal = diagonal
        self.solutions = []
        self.width = len(grid)
        self.height = len(grid[0])
        self.given = []  # given numbers
        self.tried = []
        self.goal = 1
        self.starting_pos = None

        for row in grid:
            print(row)

        for x in range(self.width):
            for y in range(self.height):
                number = self.get(Position(x, y))
                if number == 1:
                    self.starting_pos = Position(x, y)
                if number:
                    self.given.append(number)
                if number > self.goal:
                    self.goal = number

    def undo(self, until):
        for x in range(self.width):
            for y in range(self.height):
                number = self.get(Position(x, y))
                if number > until and number not in self.given:
                    self.set(Position(x, y), 0)

        self.tried = [trial for trial in self.tried if trial[1] > until]

    def find(self, number):
        for x in range(self.width):
            for y in range(self.height):
                pos = Position(x, y)
                if self.get(pos) == number:
                    return pos

    def pos_in_grid(self, pos):
        return (
                0 <= pos.x < self.width
                and
                0 <= pos.y < self.height
        )

    def neighbours(self, pos):
        if self.diagonal:
            ns = []
            for x in range(pos.x - 1, pos.x + 2):
                for y in range(pos.y - 1, pos.y + 2):
                    if x == pos.x and y == pos.y:
                        continue
                    n = Position(x, y)
                    if self.pos_in_grid(n):
                        ns.append(n)
            return ns
        else:
            ns = [
                Position(pos.x, pos.y - 1),
                Position(pos.x + 1, pos.y),
                Position(pos.x, pos.y + 1),
                Position(pos.x - 1, pos.y)
            ]
            return [n for n in ns if self.pos_in_grid(n)]

    def get(self, pos):
        return self.grid[pos.y][pos.x]

    def set(self, pos, number):
        self.grid[pos.y][pos.x] = number

    def solve(self, pos=None):

        if not pos:

            if not self.starting_pos:
                self.given.append(1)
                grid = self.grid
                # no 1 found
                for x in range(self.width):
                    for y in range(self.height):
                        pos = Position(x, y)
                        if self.get(pos) == 0:
                            self.grid = grid
                            self.grid = self.copy_grid()
                            self.set(pos, 1)
                            self.solve(pos)

                return

            pos = self.starting_pos

        number = self.get(pos)
        next = number + 1
        next_is_given = next in self.given

        if number == self.goal:  # goal reached
            return True

        for neighb in self.neighbours(pos):
            neighb_n = self.get(neighb)
            if not (
                    (neighb_n == 0 and not next_is_given)
                    or
                    neighb_n == next
            ):
                continue  # neighbour is not valid

            if (pos, next) in self.tried:
                continue

            self.set(neighb, next)
            self.tried.append((pos, next))
            if not self.solve(neighb):
                self.undo(number)
            else:
                self.solutions.append(self.copy_grid())
                self.undo(number)

    def copy_grid(self):
        return [row[:] for row in self.grid]


# p = Puzzle([
#     [1, 0, 0],
#     [0, 5, 0],
#     [0, 0, 9]
# ])
# p = Puzzle([
#     [7, 0, 3, 0, 1, 0,59, 0,81],
#     [0, 0, 0,33,34,57, 0, 0, 0],
#     [9, 0,31, 0, 0, 0,63, 0,79],
#     [0,29, 0, 0, 0, 0, 0,65, 0],
#     [11,12,0, 0,39, 0, 0,66,77],
#     [0, 13,0, 0, 0, 0, 0,67, 0],
#     [15,0,23, 0, 0, 0,69, 0,75],
#     [0, 0, 0,43,42,49, 0, 0, 0],
#     [19,0,21, 0,45, 0,47, 0, 73]
# ], False)
# p = Puzzle([
#     [35, 0,  0,  0,  0,14],
#     [0, 29, 30, 31, 16, 0],
#     [0, 28, 19, 18, 17, 0],
#     [0, 21, 20,  5,  6, 0],
#     [0, 22,  3,  4,  7, 0],
#     [24, 0, 0,   0,  0, 9],
# ])
p = Puzzle(puzzlereader.puzzle_from_img("./0606HidatoVeryHard11and12.gif", 6), True)

start_time = time.time()
p.solve()

print(len(p.solutions), "solutions")

print("time:", time.time() - start_time)

font = ImageFont.truetype("c:/windows/fonts/x-files.ttf", 25)

i = 0
for solution in p.solutions:
    p.grid = solution

    img = Image.new("RGBA", (600, 600), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    y = 0
    for row in p.grid:
        x = 0
        for number in row:

            if number:
                if number in p.given:
                    draw.chord((x * 62 + 30, y * 62 + 30, x * 62 + 70, y * 62 + 70), 0, 360, fill='lightgreen')

                draw.text((x * 62 + 40, y * 62 + 40), str(number), (0, 20, 80), font=font)

                next_pos = p.find(number + 1)

                if next_pos:
                    draw.line(
                        [(x * 62 + 45, y * 62 + 45), (next_pos.x * 62 + 45, next_pos.y * 62 + 45)],
                        (255, 100, 50), 2
                    )

            x += 1
        y += 1

    i += 1
    img.save("solution_{}.png".format(str(i)))
