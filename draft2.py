import pygame
from dataclasses import dataclass
from enum import Enum
import time
import math

pygame.init()

class pType(Enum):
    NONE=-1
    PAWN=0
    KNIGHT=1
    BISHOP=2
    ROOK=3
    QUEEN=4
    KING=5

class pCol(Enum):
    NONE=-1
    WHITE=0
    BLACK=1

@dataclass
class Piece:
    ID : int
    type : pType
    col : pCol
    moved : tuple[int,int] = (False,False)

def nullPiece():
    return Piece(0,pType.NONE,pCol.NONE)

def getLetter(piece : Piece):
    match piece.type:
        case pType.PAWN:
            return 'P'
        case pType.KNIGHT:
            return 'N'
        case pType.BISHOP:
            return 'B'
        case pType.ROOK:
            return 'R'
        case pType.KING:
            return 'K'
        case pType.QUEEN:
            return 'Q'
        case _ :
            return ''
        
class MoveType(Enum):
    NORMAL = 0
    ENPASSANT = 1
    CASTLE = 2

@dataclass
class Move:
    piece : Piece
    pieceID : int
    startpos : tuple[int,int]
    endpos : tuple[int,int]
    type : MoveType

def newMove(piece : Piece, startpos: tuple[int,int], endpos : tuple[int,int], type : MoveType = MoveType.NORMAL):
    return Move(piece,piece.ID,startpos,endpos,type)

class Board:
    def __init__(self,squareSize:int,bOffset:int,pieceSize:int):
        self.bOffset = bOffset
        self.squareSize = squareSize
        self.pieceSize = pieceSize
        self.boardarray : list[list[Piece]] =[[],[],[],[],[],[],[],[]]
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
                    self.boardarray[a].append(nullPiece())

    def draw(self,screen:pygame.Surface):
        font = pygame.font.SysFont('arial',self.pieceSize)
        for a in range(8):
            for b in range(8):
                pygame.draw.rect(screen,((255,255,255) if a%2 == b%2 else (0,0,0)),
                    pygame.Rect(self.bOffset+a*self.squareSize,self.bOffset+b*self.squareSize,self.squareSize,self.squareSize))
                if self.boardarray[a][b] != nullPiece():
                    piece = self.boardarray[a][b]
                    pygame.draw.rect(screen,((255,255,255) if piece.col==pCol.WHITE else (0,0,0)),
                        pygame.Rect(self.bOffset+(a+0.5)*self.squareSize-self.pieceSize*0.5,self.bOffset+(b+0.5)*self.squareSize-self.pieceSize*0.5,
                                    self.pieceSize,self.pieceSize))
                    pygame.draw.rect(screen,((255,255,255) if piece.col!=pCol.WHITE else (0,0,0)),
                        pygame.Rect(self.bOffset+(a+0.5)*self.squareSize-self.pieceSize*0.5,self.bOffset+(b+0.5)*self.squareSize-self.pieceSize*0.5,
                                    self.pieceSize,self.pieceSize),2)
                    text = font.render(getLetter(piece),True,((255,255,255) if piece.col!=pCol.WHITE else (0,0,0)))
                    screen.blit(text,(self.bOffset+(a+0.5)*self.squareSize-text.width*0.5,
                                      self.bOffset+(b+0.5)*self.squareSize-self.pieceSize*0.5-3))
                    
class MoveCalculator:
    def __init__(self, boardObj : Board):
        self.calculated = False
        self.moves : set[Move] = set()
        self.boardObj = boardObj
        self.boardArr = boardObj.boardarray

    def reCalc(self):
        self.calculated = False

    def calculate(self):
        if self.calculated:
            return None

        self.moves.clear()
        for a in range(8):
            for b in range(8):
                pass #calculate moves

        self.calculated = True
    
    def drawMoves(self,selectedID):
        for move in self.moves:
            if move.pieceID == selectedID:
                pass #draw moves

class Chess:
    def __init__(self, window : pygame.Window, board : Board):
        self.window = window
        self.screen = window.get_surface()
        self.boardObj = board
        self.boardArr = board.boardarray
        self.moveCalc = MoveCalculator(self.boardObj)
        self.moveSet = self.moveCalc.moves
        self.IDselect = 0

    def update(self, mousepos : tuple[int,int], click : tuple[bool,bool,bool]):
        self.select(mousepos,click)
        self.moveCalc.calculate()
    
    def draw(self):
        self.screen.fill((128,128,128))

        self.boardObj.draw(self.screen)
        self.drawSelected()

        self.window.flip()

    def select(self, mousepos : tuple[int,int], click : tuple[bool,bool,bool]):
        offset = self.boardObj.bOffset
        square = self.boardObj.squareSize
        if click[0]:
            if offset<mousepos[0]<offset+8*square and offset<mousepos[1]<offset+8*square:

                if not self.IDselect == 0:
                    for move in self.moveCalc.moves:
                        if move.pieceID == self.IDselect:
                            if (math.floor((mousepos[0]-offset)/square),math.floor((mousepos[1]-offset)/square)) == move.endpos:
                                self.boardArr[move.endpos[0]][move.endpos[1]] = move.piece
                                self.boardArr[move.startpos[0]][move.startpos[1]] = nullPiece()
                                self.moveCalc.reCalc()
                                return None
                            
                self.IDselect = self.boardArr[math.floor((mousepos[0]-offset)/square)][math.floor((mousepos[1]-offset)/square)].ID
                return None

            self.IDselect = 0
    
    def drawSelected(self):
        offset = self.boardObj.bOffset
        square = self.boardObj.squareSize
        if self.IDselect!=0:
            for a in range(8):
                for b in range(8):
                    if self.boardArr[a][b].ID == self.IDselect:
                        x = a
                        y = b

            pygame.draw.circle(self.screen,(255,0,0),(offset+square*(x+0.5),offset+square*(y+0.5)),5)

bOffset = 20
squareSize = 80
piecesize = 50

window = pygame.Window("Chess",(2*bOffset+8*squareSize,2*bOffset+8*squareSize))
board = Board(squareSize,bOffset,piecesize)
game = Chess(window,board)

interval = 0.016666667

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