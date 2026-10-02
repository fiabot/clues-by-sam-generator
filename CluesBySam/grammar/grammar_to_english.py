from string import Template 
import string 

template_dict = {
    "is": "${a} is ${b}", 
    "amount": "There are ${a} ${b}s ${c}", 
    "atLeast": "There are at least ${a} ${b}s ${c}", 
    "equal": "The number of ${a}s ${b} is the same number of ${c}s ${d}",
    "parity":"There are a ${a} number of ${b} ${c}", 
    "oneOf": "1 of the ${a} ${b}s ${c} is ${d}", 
    "outOf": "${a} out of the ${b} ${c}s ${d} are ${e}", 
    "conditionAll": "All ${a}s ${b} are ${c}", 
    "conditionNum": "${a} of the ${b}s ${c} are ${d}",
    "onlyColumn": "${a} is the only column with ${b} ${c}s" , 
    "onlyRow": "${a} is the only row with ${b} ${c}s" , 
    "moreThan": "There are more ${b}s ${a} then ${c}", 
    "null": "No Clue",  
    "above": "above ${a}", 
    "below": "below ${a}", 
    "left": "left of ${a}", 
    "right" : "right of ${a}", 
    "connected": "connected",
    "directly": "directly ${a}",
    "indirectly": "${a}",
    "in": "in ${a}", 
    "hasState": "${a}s", 
    "neighbors": "neighboring ${a}", 
    "column": "column ${a}", 
    "row": "row ${a}", 
    "edge": "on the edge", 
    "corner": "in the corners", 
    "combination":"${a} and ${b}"

}

def component_to_english(component):
    s = ""
    if isinstance(component, dict):
        kind = next(iter(component))
        values = component[kind]

        if kind == "rule" or kind == "group" or kind == "simpleGroup" or kind == "dir" or kind == "condition": 
            s += expression_to_english(values)
        elif kind in template_dict: 
            param = {}
            alpha = string.ascii_lowercase
            for i, value in enumerate(values): 
                param[alpha[i]] = component_to_english(value)

            temp = Template(template_dict[kind])   
 
            s += temp.safe_substitute(param)
    else:
        s += str(component )
    return s 

def expression_to_english(expression):
    string = ""
    if not isinstance(expression, list):
        return str(expression)
    for component in expression: 
        string += component_to_english(component)
  
    return string 
