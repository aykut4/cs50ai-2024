import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for k, v in self.domains.items():
            consistent_domain = set([word for word in v if len(word) == k.length])
            self.domains[k] = consistent_domain

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # if any word xi, where i=[0, len(self.domains[x].words)], cannot coexist with any word yj, where j=[0, len(self.domains[y].words)], rmeove xi
        overlap_indexes = self.crossword.overlaps[x, y]
        if overlap_indexes == None:
            return False

        to_be_eliminated = set()

        for wordx in self.domains[x]:
            arc_consistent = False
            for wordy in self.domains[y]:
                if wordx[overlap_indexes[0]] == wordy[overlap_indexes[1]]:
                    arc_consistent = True
                    break

            if not arc_consistent:
                to_be_eliminated.add(wordx)

        if len(to_be_eliminated) == 0:
            return False

        self.domains[x] = self.domains[x] - to_be_eliminated
        return True

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = [arc for arc, indexes in self.crossword.overlaps.items() if indexes != None]

        while len(arcs) != 0:
            arc = arcs.pop(0)
            if self.revise(arc[0], arc[1]) == True:
                if len(self.domains[arc[0]]) == 0:
                    return False

                arcs.extend([(neighbor, arc[0]) for neighbor in self.crossword.neighbors(arc[0]) if neighbor != arc[1] and (neighbor, arc[0]) not in arcs])

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(list(assignment.values())) != len(set(assignment.values())):
            return False

        for variable, value in assignment.items():
            if variable.length != len(value):
                return False

            neighbors = self.crossword.neighbors(variable)
            for neighbor in neighbors:
                overlapping_indexes = self.crossword.overlaps[variable, neighbor]
                if neighbor in assignment and value[overlapping_indexes[0]] != assignment[neighbor][overlapping_indexes[1]]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var) - set(assignment.keys())
        if len(neighbors) == 0:
            return self.domains[var]

        ordered_vars = dict()
        for word in self.domains[var]:
            heuristic = 0
            for neighbor in neighbors:
                overlapping_indexes = self.crossword.overlaps[var, neighbor]
                if overlapping_indexes != None:
                    for neighbor_word in self.domains[neighbor]:
                        if word[overlapping_indexes[0]] != neighbor_word[overlapping_indexes[1]]:
                            heuristic = heuristic + 1
            ordered_vars[word] = heuristic

        return sorted(ordered_vars, key=ordered_vars.get, reverse=False)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = []
        for variable in self.crossword.variables:
            if variable not in assignment:
                unassigned_variables.append((variable, len(self.domains[variable]), len(self.crossword.neighbors(variable))))
        unassigned_variables = sorted(unassigned_variables, key=lambda x:(x[1], -x[2]))
        return unassigned_variables[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        unassigned_variable = self.select_unassigned_variable(assignment)
        ordered_domain_values_of_unassigned_variable = self.order_domain_values(unassigned_variable, assignment)
        for value in ordered_domain_values_of_unassigned_variable:
            assignment[unassigned_variable] = value
            ret = self.backtrack(assignment)
            if ret and self.consistent(ret):
                return ret
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
