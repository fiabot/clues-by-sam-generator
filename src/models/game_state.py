from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class Entity(BaseModel):
    name: str
    state: str
    row: int  # 1-5
    col: int  # A-D
    status: int
    clue: Optional[List] = None  # The clue revealed by this person, if any
    poss_labels: List[int] 
    neighbors: List[str] = []  # Names of neighboring people


class GameState(BaseModel):
    labels: List[str]
    states: List[str]
    entities: List[Entity]
    active_clues: List[str]
    width: int 
    height: int 

    def is_solved(self):
        for entity in self.entities:
            if entity.status == -1:
                return False 
        return True 
