import random 
import sys 
from pathlib import Path
sys.path.append(str(Path.cwd().parent.parent)) 
sys.path.append(str(Path.cwd().parent)) 
sys.path.append(str(Path.cwd())) 
import re

from src.models.game_state import Entity, GameState
from src.grammar.grammar_to_english import expression_to_english 
from src.grammar.grammar_to_z3 import expression_to_z3 


TERMINALS = ["ENT", "LAB", "W", "H", "EVEN", "ODD", "STATE"]

grammar = {
    "rule": [
        ["is"], ["outOf"], ["null"], ["amount"], ["atLeast"], ["equal"], ["parity"], 
        ["oneOf"], ["outOf"], ["conditionAll"], ["conditionNum"], ["onlyColumn"], 
        ["onlyRow"], ["moreThan"]
    ], 
        "amount": [["NUM (0, |group1|)", "LAB", "group"]], 
        "atLeast": [["NUM (1, |group1|)", "LAB", "group"]], 
        "is": [["ENT", "LAB"]], 
        "equal": [["LAB", "group", "LAB", "group"]],
        "parity":[["EVEN", "LAB", "group"],["ODD", "LAB", "group"] ], 
        "oneOf":[["NUM (1, |group1|)", "LAB", "group", "ENT"]], 
        "outOf": [["NUM (0, |group1|)", "NUM (|num1|, |group2|)", "LAB", "group", "group"]], 
        "conditionAll": [["LAB", "group", "condition"]], 
        "conditionNum": [["NUM (0, |group1|)", "LAB", "group", "condition"]],
        "onlyColumn": [["column", "NUM (0, W)", "LAB"]], 
        "onlyRow": [["row", "NUM (0, H)", "LAB"]],
        "moreThan": [["group", "LAB", "group"]], 
        "null": [[]], 
    "dir":[["above"], ["below"], ["left"], ["right"]], 
        "above": [["ENT"]], 
        "below": [["ENT"]], 
        "left": [["ENT"]], 
        "right" : [["ENT"]], 
    "condition": [["connected"], ["directly"], ["indirectly"], ["in"],  ["hasState"]], 
        "connected": [[]],
        "directly": [["dir"]],                       
        "indirectly": [["dir"]],
        "in": [["row"],["column"]], 
        "hasState": [["STATE"]], 
    "group": [["neighbors"], ["in"],  ["dir"],["edge"], ["corner"], ["combination"], ["hasState"]],
    "simpleGroup":[["neighbors"], ["in"],  ["dir"],["edge"], ["corner"],  ["hasState"]],   
        "neighbors": [["ENT"]], 
        "column": [["NUM (1, W)"]], 
        "row": [["NUM (1, H)"]], 
        "edge":[[]], 
        "corner":[[]], 
        "combination":[["simpleGroup", "simpleGroup"]]

}
def is_terminal(component):
    return component in TERMINALS or "NUM" in component 


def expand(expression): 
    new_expression = []
    for component in expression:
            if isinstance(component, dict):
                 value = component[component.keys()[0]]
            else:
                 value = component 

            if is_terminal(value): 
                new_value = value
            else: 
                possibilities = grammar[value]
                new_component = random.choice(possibilities)
                new_value = expand(new_component)
                new_value = {value: new_value}
            
            if isinstance(component, dict):
                 new_expression.append({component.keys()[0]: new_value})
            else:
                 new_expression.append(new_value)
    return new_expression 


def get_value(string, groups, game: GameState, nums): 
    if string.isdigit():
        return int(string)
    elif string == "W":
        return game.width 
    elif string == "H": 
         return game.height 
    elif "group" in string: 
        # first remove lines 
        string = re.sub(r'\|', '', str(string))

        # then determine which group it's referring to 
        group_num = int(string[-1]) - 1 
        group = groups[group_num]

        # determine number by group type
        if group == "neighbors":
            return 8 
        elif group == "column":
             return game.width 
        elif group == "row": 
             return game.height 
        elif group == "corner":
             return 4 
        elif group == "edge":
             return game.width * 2 + game.height * 2 - 4 
        else: 
             return int(game.width * game.height / 4) 
    elif "num" in string: 
        # first remove lines 
        string = re.sub(r'\|', '', str(string))

        # then determine which group it's referring to 
        num_id = int(string[-1]) - 1 
        return nums[num_id]
        
         
    

def determine_num(num, expression, game, nums): 
     part1, part2 = num.split("(") 
     result = part2.split(")", 1)[0]
     num1, num2 = result.split(",")
     groups = [val for val in expression if isinstance(val, dict) and next(iter(val)) == "group"]
     group_names = [next(iter(val["group"][0]))  for val in groups]
     num1 = get_value(num1.strip(), group_names, game, nums)
     num2 = get_value(num2.strip(), group_names, game, nums)
     return random.randint(num1, num2)

def generate_terminal_value(value, expression, game, nums):
    if value == "ENT":
        new_value = random.choice(game.entities).name
    elif value == "LAB": 
        new_value  = random.choice(game.labels)
    elif value == "STATE": 
        new_value  = random.choice(game.states)
    elif value == "W":
        new_value = game.width 
    elif value == "H": 
        new_value = game.height  
    elif value == "EVEN": 
        new_value = "even"
    elif value == "ODD": 
            new_value = "odd"
    else: 
        new_value = determine_num(value, expression, game, nums)
        nums.append(new_value)
    return new_value 

def fill_in_terminals(expression, game: GameState, terminals=[]):
    new_expression = []
    nums = []
    for component in expression:
            if isinstance(component, dict):
                 value = component[next(iter(component))]
            else:
                 value = component 

            if is_terminal(value): 
                try: 
                    new_value = generate_terminal_value(value, expression, game, nums)
                    # make it so that we don't repeat terminals 
                    i = 0 
                    while new_value in terminals and i < 10000: 
                        new_value = generate_terminal_value(value, expression, game, nums) 
                        i += 1
                    terminals.append(new_value)
                except:
                    return fill_in_terminals(expression, game)
            else: 
                new_value = fill_in_terminals(value, game, terminals=terminals)
            
            if isinstance(component, dict):
                 new_expression.append({next(iter(component)): new_value})
            else:
                 new_expression.append(new_value)
    return new_expression 

def generate_rule(game:GameState): 
    rule = expand(["rule"])
    return fill_in_terminals(rule, game)

if __name__ == "__main__": 
    a = Entity(
    id = "A", name="A", state = "Doctor", 
    row = 0, col = "A", status=1,  poss_labels=[0,1], neighbors=["B", "C"])

    b = Entity(
    id = "B", name="B", state = "Doctor", row = 0, col = "B",
      status=-1,  poss_labels=[0,1], neighbors=["A", "D"])

    c = Entity(
    id = "C", name="C", state = "Doctor", row = 1, col = "A", status=-1,  
    poss_labels=[0,1], neighbors=["A", "D"])

    d = Entity(
    id = "D", name="D", state = "Doctor", row = 1, col = "B", status=-1, 
    poss_labels=[0,1], neighbors=["B", "C"])

    game = GameState(labels = ["criminal", "innocent"], states =["doctor","lawyer"], entities=[a,b,c,d], active_clues=[], width=2, height=2)
 
    rule = generate_rule(game)
    print(rule)
    print(expression_to_english(rule))
    print(expression_to_z3(rule, game))