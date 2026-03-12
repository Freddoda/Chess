import pygame
from dataclasses import dataclass
from enum import Enum
import time

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
        self.boardarray : list[list[Piece | None]] =[[],[],[],[],[],[],[],[]]
        bRank = (pType.ROOK,pType.KNIGHT,pType.BISHOP,pType.QUEEN,pType.KING,pType.BISHOP,pType.KNIGHT,pType.ROOK)
        num = 1
        for a in range(8):
            for b in range(8):
                if b==0 or b==7:
                    self.boardarray[a].append(Piece(num,bRank[a],pCol(1-b/7)))
                    num+=1
                elif b==1 or b==6:
                    self.boardarray[a].append(Piece(num,pType.PAWN,pCol(1-(b-1)/5)))
                    num+=1
                else:
                    self.boardarray[a].append(None)

class Chess:
    def __init__(self, screen : pygame.Surface, board : Board):
        self.screen = screen
        self.boardObj = board
        self.boardArr = board.boardarray
        self.IDselect = 0

    def update(self, mousepos : tuple[int,int], click : tuple[int,int,int]):
        pass
    
    def draw(self):
        pass

bOffset = 20
squareSize = 80

screen = pygame.display.set_mode((2*bOffset+8*squareSize,2*bOffset+8*squareSize))
board = Board(squareSize,bOffset)
game = Chess(screen,board)

interval = 0.166666667

Running = True
while Running:
    start = time.time_ns()

    for Event in pygame.event.get():
        if Event.type == pygame.QUIT:
            Running = False
    

    keys = pygame.key.get_pressed()
    mousepos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if keys[pygame.K_ESCAPE]:
        Running=False

    game.update(mousepos, click)
    game.draw()

    finish = time.time_ns()
    sleepT = max(0,interval - (finish-start)/1000000000)
    time.sleep(sleepT)
    

pygame.quit()