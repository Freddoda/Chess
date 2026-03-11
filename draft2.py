import pygame
from dataclasses import dataclass
from enum import Enum

pygame.init()

class pType(Enum):
    PAWN=0
    KNIGHT=1
    BISHOP=2
    ROOK=3
    QUEEN=4
    KING=5

class pCol(Enum):
    WHITE=0
    BLACK=1

@dataclass
class Piece:
    ID : int
    type : pType
    col : pCol

class Board:
    def __init__(self,squareSize:int,bOffset:int):
        self.bOffest = bOffset
        self.squareSize = squareSize
        self.board : list[list[Piece]] =[[],[],[],[],[],[],[],[]]

class Chess:
    def __init__(self, screen : pygame.Surface, board : Board):
        self.screen = screen
        self.B = board
        self.board = board.board

bOffset = 20
squareSize = 80

screen = pygame.display.set_mode((2*bOffset+8*squareSize,2*bOffset+8*squareSize))
board = Board(squareSize,bOffset)
game = Chess(screen,board)