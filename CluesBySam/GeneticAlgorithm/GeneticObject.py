import random 
import sys 
from pathlib import Path
sys.path.append(str(Path.cwd().parent.parent)) 
sys.path.append(str(Path.cwd().parent)) 
sys.path.append(str(Path.cwd())) 
from CluesBySam.solver.engine import GameSolver 
from CluesBySam.models.game_state import GameState , Entity 
from CluesBySam.grammar.grammar_constructor import generate_rule 
from CluesBySam.grammar.grammar_to_english import expression_to_english
import random 
from copy import deepcopy 
class CluesBySam: 
    def __init__(self,game: GameState, starting_name: str):
        self.game = game 
        self.is_valid = True
        self.nulls = -1 
        self.rounds = -1 
        self.starting_name = starting_name 
        self.entity_map = {p.name: p for p in self.game.entities}
        
        self.solved_game = deepcopy(game)
        self.solved_entity_map = {p.name: p for p in self.solved_game.entities}
        self.solve(self.solved_game)
        
        

    def solve(self, game_copy: GameState):

        solver = GameSolver(game_copy, len(game_copy.labels))

        
        self.is_valid, self.is_solved, blank_clues, self.rounds = solver.solve_puzzle(self.starting_name) 
        if blank_clues != -1:
            for name, status in blank_clues:
                if name != self.starting_name:
                    self.solved_entity_map[name].clue = [{"rule": [{"null": []}]}]
        
    
    def has_status(self, name):
        return self.solved_entity_map[name].status != -1 


    def num_nulls(self):
        if self.nulls == -1: 
            nulls = 0 
            for entity in self.solved_game.entities:
                if next(iter(entity.clue[0]["rule"][0])) == "null":
                    nulls += 1
            
            self.nulls = nulls 
        return self.nulls 
    
    def num_loops(self):
        return self.rounds 
    
    def mutate(self, mutation_rate = 0.5): 
        new_game = deepcopy(self.game)
        starting_name = self.starting_name 
        number_mutations = int((random.random() * len(new_game.entities)) * mutation_rate) 
        for i in range(number_mutations): 
            entity = random.choice(new_game.entities)
            if random.random() < 0.9: 
                clue = generate_rule(new_game)
                entity.clue = clue 
            else: 
                starting_name = entity.name 
        
        return CluesBySam(new_game, starting_name)
    def cross_over(self, other):
        child1_game = deepcopy(self.game)
        child2_game = deepcopy(other.game)
        entity_map2 = {p.name: p for p in child2_game.entities}

        for entity in child1_game.entities:
            if random.random() < 0.5: 
                # swap clues 
                clue1 = entity.clue 
                entity.clue = entity_map2[entity.name].clue
                entity_map2[entity.name].clue = clue1 
    

        return CluesBySam(child1_game, self.starting_name), CluesBySam(child2_game, other.starting_name)
    

def get_neighbors(names, row, col):
    pos_cols = [col, col + 1, col - 1]
    pos_rows = [row, row + 1 , row -1]
    height = len(names)
    width = len(names[0])
    neighbors = []
    for c in pos_cols:
        for r in pos_rows:
            if not (c == col and r == row) and (c >= 0 and r >= 0 and c < width and r< height):
                neighbors.append(names[r][c])
    return neighbors   
                

def generate_puzzle(names, states, labels, clues=None, starting_name = None):
    entities = []
    state_set = set()
    for i, row in enumerate(names):
        for j, name in enumerate(row):

            state = states[i][j]
            state_set.add(state)
            neighbors = get_neighbors(names, i, j)
            if clues == None:
                entities.append(Entity(name=name, state=state, row=i, col=j, status=-1, poss_labels=[0,1], neighbors=neighbors, labels=labels)) 
            else:
                entities.append(Entity(name=name, state=state, row=i, col=j, status=-1, poss_labels=[0,1], neighbors=neighbors, labels=labels,clue=clues[i][j]))
    game = GameState(labels=labels, states=list(state_set),  entities=entities, active_clues=[], width = len(names[0]), height=len(names))

    if clues == None: 
        for entity in entities:
            clue = generate_rule(game)
            entity.clue = clue 
    if starting_name == None:
        starting_name = random.choice(entities).name

    return CluesBySam(game, starting_name)


if __name__ == "__main__":

    names = [["MissScarlet", "Mr.Green", "Col.Mustard", "LadyLavender"], 
                            ["Prof.Plum", "Mrs.Peacock", "Mrs.White", "Br.Olive"], 
                            ["Ms.Indigo", "Dr.Brown", "SirCopper", "Mx.Garnet"]] 
    states = [["Painter", "Cop", "Cop", "Painter"],  
                    ["Teacher", "Teacher", "Cook", "Teacher"], 
                    ["Cook", "Doctor", "Doctor", "Painter"]] 
    clues = [[ [{'rule': [{'null': []}]}],  [{'rule': [{'null': []}]}],  [{'rule': [{'outOf': [1, 2, 'criminal', {'group': [{'neighbors': ['Mr.Green']}]}, {'group': [{'edge': []}]}]}]}], [{'rule': [{'null': []}]}]]
             ,[[{'rule': [{'null': []}]}],  [{'rule': [{'null': []}]}],[{'rule': [{'parity': ['odd', 'criminal', {'group': [{'hasState': ['Teacher']}]}]}]}],  [{'rule': [{'null': []}]}] ], 
             [ [{'rule': [{'null': []}]}],[{'rule': [{'null': []}]}], [{'rule': [{'onlyColumn': [{'column': [2]}, 0, 'criminal']}]}],[{'rule': [{'null': []}]}]]
             ]
    labels = ["innocent", "criminal"]

    puzzle = generate_puzzle(names, states, labels, clues=clues, starting_name="SirCopper")

    print("Is Valid: {}".format(puzzle.is_valid))
    print("Is Solved:{}".format(puzzle.is_solved))
    print("Number Rounds: {}".format(puzzle.num_loops()))
    print("Num Nulls:{}".format(puzzle.num_nulls()))

    solver = GameSolver(puzzle.game, 2)
    solver.solve_puzzle("SirCopper", debug=True)

    child = puzzle.mutate()

    print("Child is solved:{}".format(puzzle.is_solved))

    child1, child2 = child.cross_over(generate_puzzle(names, states, labels))
    print("Child1 is solved: {}, Child2 is Solved:{}".format(child1.is_solved, child2.is_solved) )

    

