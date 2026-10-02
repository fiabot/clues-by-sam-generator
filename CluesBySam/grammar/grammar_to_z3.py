
def label_to_num(label, game):
    return game.labels.index(label)

def condition_to_z3(condition, game, group =  "[]"):
    kind = next(iter(condition))
    values = condition[kind] 

    if kind == "connected":
        return "kb.is_connected_to_group(n, {})".format(group)
    elif kind == "directly":
        kind = next(iter(values[0]["dir"][0]))
        values = values[0]["dir"][0][kind] 
        if kind == "above":
            return "kb.is_directly_above(n,'{}')".format(values[0])
        elif kind == "below":
            return "kb.is_directly_below(n,'{}')".format(values[0])
        elif kind == "left":
            return "kb.is_directly_left(n,'{}')".format(values[0])
        elif kind == "right":
            return "kb.is_directly_right(n,'{}')".format(values[0])
    elif kind == "indirectly":
        kind = next(iter(values[0]["dir"][0]))
        values = values[0]["dir"][0][kind] 
        if kind == "above":
            return "kb.is_above(n,'{}')".format(values[0])
        elif kind == "below":
            return "kb.is_below(n,'{}')".format(values[0])
        elif kind == "left":
            return "kb.is_left_of(n,'{}')".format(values[0])
        elif kind == "right":
            return "kb.is_right_of(n,'{}')".format(values[0])
    elif kind == "in":
        kind = next(iter(values[0]))
        values = values[0][kind] 
        if kind == "row":
            return "kb.is_in_row(n,'{}')".format(values[0])
        elif kind == "column":
            return "kb.is_in_col(n, '{}')".format(values[0])
    elif kind == "hasState":
        return "kb.is_state(n, '{}')".format(values[0])


def group_to_z3(group, game):
    kind = next(iter(group))
    values = group[kind]

    if kind == "neighbors":
        return "kb.get_neighbors('{}')".format(values[0])
    elif kind == "in":
        kind = next(iter(values[0]))
        values = values[0][kind] 
        if kind == "row":
            return "kb.get_row({})".format(values[0])
        elif kind == "column":
            return "kb.get_row({})".format(values[0])
    elif kind == "edge":
        return "kb.get_edges()" 
    elif kind == "corner":
        return "kb.get_corners()" 
    elif kind == "hasState":
        return "kb.get_state('{}')".format(values[0])
    elif kind == "dir":
        kind = next(iter(values[0]))
        values = values[0][kind] 

        if kind == "above":
            return "kb.get_above('{}')".format(values[0])
        elif kind == "below":
            return "kb.get_below('{}')".format(values[0])
        elif kind == "left":
            return "kb.get_left_of('{}')".format(values[0])
        elif kind == "right":
            return "kb.get_right_of('{}')".format(values[0])
    elif kind == "combination":
        group1 = group_to_z3(values[0]["simpleGroup"][0], game)
        group2 = group_to_z3(values[1]["simpleGroup"][0], game)

        return "[n for n in {} if n in {}]".format(group1, group2)

    

def rule_to_z3(rule,game):
    kind = next(iter(rule))
    values = rule[kind]

    if kind == "is":
        return "kb.is_status('{}', {})".format(values[0], label_to_num(values[1], game))
    elif kind == "amount":
        group = component_to_z3(values[2], game)
        return "kb.count_status({},{}) == {}".format(group, label_to_num(values[1],game), values[0]) 
    elif kind == "atLeast":
        group = component_to_z3(values[2], game)
        return "kb.count_status({},{}) >= {}".format(group, label_to_num(values[1],game), values[0]) 
    elif kind == "equal":
        group1 = component_to_z3(values[1], game)
        group2 = component_to_z3(values[3], game)
        return "kb.count_status({},{}) == kb.count_status({},{})".format(group1, label_to_num(values[0], game),group2, label_to_num(values[2], game)) 
    elif kind == "parity":
        group = component_to_z3(values[2], game)
        remainder = 0 if values[0] == "even" else 1 
        return "kb.count_status({},{}) % 2 == {}".format(group, label_to_num(values[1], game),remainder) 
    elif kind == "oneOf":
        group = component_to_z3(values[2],game)
        statement1 = rule_to_z3({"amount": [values[0], values[1], values[2]]}, game)
        statement2 = rule_to_z3({"is": [values[3], values[1]]}, game)
        statement3 = "kb.in_group('{}', {})".format(values[3], group)
        return "And ({}, {}, {})".format(statement1, statement2, statement3) 
    elif kind == "outOf":
        statement1 = rule_to_z3({"amount": [values[0], values[2], values[4]]}, game)
        statement2 = rule_to_z3({"amount": [values[1], values[2], values[3]]}, game)
        return "And ({}, {})".format(statement1, statement2) 
    elif kind == "conditionAll":
        group = component_to_z3(values[1], game)
        condition = condition_to_z3(values[2]["condition"][0], game, group)
        return "kb.count_status({},{}) == kb.count_status([n for n in {} if {}],{})".format(group, label_to_num(values[0], game), group, condition, label_to_num(values[0], game)) 
    elif kind == "conditionNum":
        group = component_to_z3(values[2], game)
        condition = condition_to_z3(values[3]["condition"][0], game, group)
        return "kb.count_status([n for n in {} if {}],{}) == {}".format( group, condition, label_to_num(values[1], game), values[0]) 
    elif kind == "onlyRow":
        row = values[0]["row"][0]
        statement1 = "kb.count_status(kb.get_row({}), {}) == {}".format(row, label_to_num(values[2], game), values[1])
        statement2 = "And([kb.count_status(kb.get_row(r), {}) != {} for r in range(1, {}) if r != {}])".format(label_to_num(values[2], game),values[1],game.height, row )

        return  "And ({}, {})".format(statement1, statement2)
    elif kind == "onlyColumn":
        row = values[0]["column"][0]
        statement1 = "kb.count_status(kb.get_col({}), {}) == {}".format(row, label_to_num(values[2], game), values[1])
        statement2 = "And([kb.count_status(kb.get_col(r), {}) != {} for r in range(1, {}) if r != {}])".format(label_to_num(values[2], game), values[1],game.height, row )

        return  "And ({}, {})".format(statement1, statement2)
    elif kind == "moreThan":
        group1 = component_to_z3(values[0], game)
        group2 = component_to_z3(values[2], game)
        return "kb.count_status({},{}) > kb.count_status({},{})".format(group1, label_to_num(values[1], game), group2, label_to_num(values[1], game)) 
    else:
        return ""


def component_to_z3(component, game):
     if isinstance(component, dict):
        kind = next(iter(component))
        values = component[kind]

        if kind == "rule":
            return rule_to_z3(values[0], game)
        elif kind == "group":
            return group_to_z3(values[0], game)

    
def expression_to_z3(expression, game):
    string = ""
    if not isinstance(expression, list):
        return str(expression)
    for component in expression: 
        string += component_to_z3(component, game)
  
    return string 