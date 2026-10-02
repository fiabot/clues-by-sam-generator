from typing import List, Tuple
import sys 
from pathlib import Path
sys.path.append(str(Path.cwd().parent.parent)) 
sys.path.append(str(Path.cwd().parent)) 
sys.path.append(str(Path.cwd())) 
from z3 import If, Sum, And, Or, Not, Implies, Exists, ForAll, unsat
from CluesBySam.models.game_state import Entity, GameState
from CluesBySam.solver.knowledge_base import KnowledgeBase
from CluesBySam.grammar.grammar_to_z3 import expression_to_z3
from CluesBySam.grammar.grammar_to_english import expression_to_english 
class GameSolver:
    def __init__(self, game: GameState,num_labels):
        self.game = game 
        self.num_labels = num_labels
        self.kb = KnowledgeBase(game)
        self.constraints = []
    
    def solve_puzzle(self, starting_name, debug=False):
        is_valid = True 
        options_left = True 
        
        z3_expression =  expression_to_z3(self.kb.person_map[starting_name].clue, self.game)
        if debug:
            print("Starting entities is {} with clue: {}".format(starting_name, expression_to_english(self.kb.person_map[starting_name].clue)))
            print( z3_expression)
        if z3_expression != "":
            self.add_constraint(expression_to_z3(self.kb.person_map[starting_name].clue, self.game))
        rounds = 0 
        while not self.game.is_solved() and is_valid and options_left:
            new_status = self.solve()

            if new_status == -1:
                is_valid = False 

                if debug:
                    print("There was a violation")   
            elif len(new_status) == 0:
                options_left = False 

                if debug: 
                    print("There are no more moves left")
            if is_valid:
                for name, status in new_status:
                    person = self.kb.person_map[name]
                    if debug: 
                        print("{} now has status {}".format(name, status))

                    person.status = status 
                    z3_expression =  expression_to_z3(person.clue, self.game)
                    if z3_expression != "":
                        if debug: 
                            print("Adding new clue: {}".format(expression_to_english(person.clue)))
                            print(z3_expression)
                        self.add_constraint(z3_expression)
            rounds += 1   
                
        return is_valid , self.game.is_solved(), new_status, rounds 

    def add_constraint(self, constraint_code: str):
        """
        Evaluate and add a constraint string to the solver.
        """
        try:
            constraint_code = constraint_code.strip()
            constraint_code = constraint_code.replace("\\n", "\n").replace("\\t", "\t")
            constraint_code = constraint_code.replace("\\", " ")

            # We expose 'kb' to the eval context
            context = {
                "kb": self.kb,
                "If": If,
                "Sum": Sum,
                "And": And,
                "Or": Or,
                "Not": Not,
                "Implies": Implies,
                "Exists": Exists,
                "ForAll": ForAll,
            }
            rule = eval(constraint_code, context)
            self.kb.solver.add(rule)
            self.constraints.append(constraint_code)
        except Exception as e:
            raise e

    def deduce(self) -> List[Tuple[str, int]]:
        """
        Run deduction to find which assignments are false 
        Returns a list of all the statuses that impossible
        """
        proven_false = []

        # First, check if the current state is consistent
        if self.kb.solver.check() == unsat:
            
            return -1

        for name, var in self.kb.vars.items():
            # The KB initializes with knowns, so we only need to check unknowns.
            person = self.kb.person_map[name]
            if person.status != -1:
                continue

            # Assume each state 
            for state in person.poss_labels: 
                self.kb.solver.push()
                self.kb.solver.add(var == state)
                if self.kb.solver.check() == unsat:
                    proven_false.append((name, state))
                self.kb.solver.pop()

        return proven_false
    
    def solve(self) -> List[Tuple[str, int]]:
        """
        Run deduction to eliminate impossible 
        assignments 

        Returns list of all new known assignments 
        """
        proven_status = [] 
        false = self.deduce()

        if false == -1:
            return -1 

        for name, status in false: 
            person = self.kb.person_map[name] 
            person.poss_labels.remove(status)
            if len(person.poss_labels) == 1: 
                proven_status.append((name,person.poss_labels[0] ))
        
        return proven_status 

    def add_fact(self, name: str, status: int):
        """Update the solver with a newly discovered fact."""
        var = self.kb.vars[name]

        self.kb.solver.add(var == status)
     
    def log_state(self, iteration: int, filepath: str = "solver_log.txt"):
        """Log the current state of the KB to a file."""
        with open(filepath, "a") as f:
            f.write(f"\n{'=' * 20} Iteration {iteration} {'=' * 20}\n")

            f.write("\n--- Known Facts ---\n")
            for p in self.kb.people:
                if p.status != -1: 
                    f.write(f"{p.name}: {p.status.value}\n")

            f.write("\n--- Added Constraints (Code) ---\n")
            for i, c in enumerate(self.constraints):
                f.write(f"{i + 1}. {c}\n")

            f.write("\n--- Z3 Solver State ---\n")
            f.write(str(self.kb.solver))
            f.write(f"\n{'=' * 50}\n")
