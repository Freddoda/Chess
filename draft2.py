from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import time
import math
import concurrent.futures
import itertools

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

def nullPiece() -> Piece:
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
    PROMOTE = 3

@dataclass
class Move:
    piece : Piece
    pieceID : int
    startpos : tuple[int,int]
    endpos : tuple[int,int]
    type : MoveType

def newMove(piece : Piece, startpos: tuple[int,int], endpos : tuple[int,int], type : MoveType = MoveType.NORMAL) -> Move:
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
    def __init__(self, boardArr : list[list[Piece]] |tuple[tuple[Piece,...],...], boardObj : Board = Board(0,0,0)):
        self.calculated = False
        self.moves : list[Move] = []
        self.boardArr = boardArr
        self.boardObj = boardObj
        self.checkFinder = checkFinder(self)

    def reCalc(self):
        self.calculated = False

    def setBoard(self, boardArr : list[list[Piece]]):
        self.boardArr = boardArr
        self.checkFinder.boardArr = boardArr

    def calculate(self, turn : pCol):
        if self.calculated:
            return None

        self.moves.clear()
        kingpos : list[tuple[int,int]] = []
        for a in range(8):
            for b in range(8):
                if turn != self.boardArr[a][b].col:
                    continue

                match self.boardArr[a][b].type:
                    case pType.PAWN:
                        self.pawnCalculate((a,b))
                    case pType.KNIGHT:
                        self.knightCalculate((a,b))
                    case pType.BISHOP:
                        self.bishopCalculate((a,b))
                    case pType.ROOK:
                        self.rookCalculate((a,b))
                    case pType.QUEEN:
                        self.bishopCalculate((a,b))
                        self.rookCalculate((a,b))
                    case pType.KING:
                        self.kingCalculate((a,b))
                        kingpos.append((a,b))

        for pos in kingpos:
            self.checkFinder.findChecks(pos[0],pos[1])

        self.calculated = True
    
    def pawnCalculate(self, pos : tuple[int,int]):
        pawn = self.boardArr[pos[0]][pos[1]]

        if pos[1]-1+2*pawn.col.value>7 or pos[1]-1+2*pawn.col.value<0:
            return None

        if self.boardArr[pos[0]][pos[1]-1+2*pawn.col.value] == nullPiece():
            self.moves.append(newMove(pawn,pos,(pos[0],pos[1]-1+2*pawn.col.value)))
            if pawn.moved == (False,False) and self.boardArr[pos[0]][pos[1]-2+4*pawn.col.value] == nullPiece():
                self.moves.append(newMove(pawn,pos,(pos[0],pos[1]-2+4*pawn.col.value)))
        if pos[0]+1<8:
            if (self.boardArr[pos[0]+1][pos[1]-1+2*pawn.col.value] != nullPiece() and
                self.boardArr[pos[0]+1][pos[1]-1+2*pawn.col.value].col != pawn.col):
                self.moves.append(newMove(pawn,pos,(pos[0]+1,pos[1]-1+2*pawn.col.value)))
            if (self.boardArr[pos[0]+1][pos[1]].type == pType.PAWN and self.boardArr[pos[0]+1][pos[1]].moved == (True,False) and
                self.boardArr[pos[0]+1][pos[1]].col != pawn.col):
                self.moves.append(newMove(pawn,pos,(pos[0]+1,pos[1]-1+2*pawn.col.value),MoveType.ENPASSANT))
        if pos[0]-1>-1:
            if (self.boardArr[pos[0]-1][pos[1]-1+2*pawn.col.value] != nullPiece() and
                self.boardArr[pos[0]-1][pos[1]-1+2*pawn.col.value].col != pawn.col):
                self.moves.append(newMove(pawn,pos,(pos[0]-1,pos[1]-1+2*pawn.col.value)))
            if (self.boardArr[pos[0]-1][pos[1]].type == pType.PAWN and self.boardArr[pos[0]-1][pos[1]].moved == (True,False) and
                self.boardArr[pos[0]-1][pos[1]].col != pawn.col):
                self.moves.append(newMove(pawn,pos,(pos[0]-1,pos[1]-1+2*pawn.col.value),MoveType.ENPASSANT))

    def knightCalculate(self, pos : tuple[int,int]):
        self.subknightCalculate(0,pos[0],pos[1])
        self.subknightCalculate(1,pos[0],pos[1])
        self.subknightCalculate(2,pos[0],pos[1])
        self.subknightCalculate(3,pos[0],pos[1])

    def subknightCalculate(self, mode : int, x : int, y : int):
        if not -1<(x if (mode==0 or mode==1) else y)+(2 if (mode==0 or mode==2) else -2)<8:
            return None
        
        knight = self.boardArr[x][y]

        for i in range(-1,3,2):
            if -1<((y if (mode==0 or mode==1) else x))+i<8:
                if self.boardArr[x+(i if not (mode == 0 or mode == 1) else (2 if (mode==0 or mode==2) else -2))
                    ][y+(i if (mode == 0 or mode == 1) else (2 if (mode==0 or mode==2) else -2))
                    ].col != knight.col:
                    self.moves.append(newMove(knight,(x,y),
                        (x+(i if not (mode == 0 or mode == 1) else (2 if (mode==0 or mode==2) else -2)),
                        y+(i if (mode == 0 or mode == 1) else (2 if (mode==0 or mode==2) else -2)))))
                    
    def bishopCalculate(self, pos : tuple[int,int]):
        self.subbishopCalculate(0,pos[0],pos[1])
        self.subbishopCalculate(1,pos[0],pos[1])
        self.subbishopCalculate(2,pos[0],pos[1])
        self.subbishopCalculate(3,pos[0],pos[1])

    def subbishopCalculate(self, dir : int, x : int, y : int):
        bishop=self.boardArr[x][y]
        for n in range(1,min((7-x if dir%2 == 0 else x),(7-y if dir < 2 else y))+1):
            if self.boardArr[x+n if dir%2 == 0 else x-n][y+n if dir<2 else y-n].col==bishop.col:
                return None
            self.moves.append(newMove(bishop,(x,y),(x+n if dir%2 == 0 else x-n,y+n if dir<2 else y-n)))
            if self.boardArr[x+n if dir%2 == 0 else x-n][y+n if dir<2 else y-n].col!=pCol.NONE:
                return None


    def rookCalculate(self, pos : tuple[int,int]):
        self.subrookCalculate(0,pos[0],pos[1])
        self.subrookCalculate(1,pos[0],pos[1])
        self.subrookCalculate(2,pos[0],pos[1])
        self.subrookCalculate(3,pos[0],pos[1])

    def subrookCalculate(self, dir : int, x : int, y : int):
        rook=self.boardArr[x][y]
        for i in range (1,((x if dir<2 else y)*(-1 if dir%2 else 1)+(7 if dir%2 else 0))+1):
            if (self.boardArr[x + (0 if dir>=2 else (i if dir%2 else -i))
                ][y + (0 if dir<2 else (i if dir%2 else -i))].col == rook.col):
                return None
            self.moves.append(newMove(rook,(x,y),
                (x + (0 if dir>=2 else (i if dir%2 else -i)),
                 y + (0 if dir<2 else (i if dir%2 else -i)))))
            if (self.boardArr[x + (0 if dir>=2 else (i if dir%2 else -i))][
                y + (0 if dir<2 else (i if dir%2 else -i))] != nullPiece()):
                return None
            
    def kingCalculate(self, pos : tuple[int,int]):
        king = self.boardArr[pos[0]][pos[1]]
        for a in range(-1,2):
            for b in range(-1,2):
                if a == b and a==0:
                    pass
                else:
                    if self.subkingCalculate(king, pos[0]+a, pos[1]+b):
                        self.moves.append(newMove(king,pos,( pos[0]+a, pos[1]+b)))

        if king.moved==(False,False):

            if self.boardArr[0][pos[1]].type==pType.ROOK and self.boardArr[0][pos[1]].moved==(False,False):
                if self.subkingCalculate(king,pos[0]-1,pos[1]) and self.subkingCalculate(king,pos[0]-2,pos[1]):
                    if self.boardArr[1][pos[0]] == nullPiece():
                        self.moves.append(newMove(king,pos,(pos[0]-2,pos[1]),MoveType.CASTLE))
            
            if self.boardArr[7][pos[1]].type==pType.ROOK and self.boardArr[7][pos[1]].moved==(False,False):
                if self.subkingCalculate(king,pos[0]+1,pos[1]) and self.subkingCalculate(king,pos[0]+2,pos[1]):
                    self.moves.append(newMove(king,pos,(pos[0]+2,pos[1]),MoveType.CASTLE))

    def subkingCalculate(self, king : Piece, x : int, y : int) -> bool:
        if not -1<x<8:
            return False
        if not -1<y<8:
            return False
        if self.boardArr[x][y].col == king.col:
            return False
        
        if self.kingpawnCalculate((x,y),king):
            return False
        
        for n in range(4):
            if self.kingknightCalculate(n,x,y,king):
                return False
            if self.kingrookCalculate(n,x,y,king):
                return False
            if self.kingbishopCalculate(n,x,y,king):
                return False
            
        if self.kingkingCalculate(king,x,y):
            return False
        
        return True

    def kingpawnCalculate(self, pos : tuple[int,int], king : Piece) -> bool:
        if pos[1]-1+2*king.col.value>7 or pos[1]-1+2*king.col.value<0:
            return False
        
        if pos[0]+1<8:
            if (self.boardArr[pos[0]+1][pos[1]-1+2*king.col.value].type == pType.PAWN and
                self.boardArr[pos[0]+1][pos[1]-1+2*king.col.value].col != king.col):
                return True
            
        if pos[0]-1>-1:
            if (self.boardArr[pos[0]-1][pos[1]-1+2*king.col.value].type == pType.PAWN and
                self.boardArr[pos[0]-1][pos[1]-1+2*king.col.value].col != king.col):
                return True
        
        return False
    
    def kingknightCalculate(self, mode : int, x : int, y : int, king : Piece) -> bool:
        if not -1<(x if (mode==0 or mode==1) else y)+(2 if (mode==0 or mode==2) else -2)<8:
            return False

        for i in range(-1,3,2):
            if -1<((y if (mode==0 or mode==1) else x))+i<8:
                square = self.boardArr[x+(i if not (mode == 0 or mode == 1) else (2 if (mode==0 or mode==2) else -2))
                        ][y+(i if (mode == 0 or mode == 1) else (2 if (mode==0 or mode==2) else -2))]
                if square.col != king.col and square.type == pType.KNIGHT:
                    return True
        return False
        
    def kingrookCalculate(self, dir : int, x : int, y : int, king : Piece) -> bool:
        for i in range (1,((x if dir<2 else y)*(-1 if dir%2 else 1)+(7 if dir%2 else 0))+1):
            square = self.boardArr[x + (0 if dir>=2 else (i if dir%2 else -i))][
                    y + (0 if dir<2 else (i if dir%2 else -i))]
            if (square != nullPiece() and square != king):
                if (square.col != king.col and (square.type==pType.ROOK or square.type==pType.QUEEN)):
                    return True
                return False
        return False
    
    def kingbishopCalculate(self, dir : int, x : int, y : int, king : Piece) -> bool:
        for n in range(1,min((7-x if dir%2 == 0 else x),(7-y if dir < 2 else y))+1):
            square = self.boardArr[x+n if dir%2 == 0 else x-n][y+n if dir<2 else y-n]
            if (square != nullPiece() and square != king):
                if (square.col != king.col and (square.type==pType.BISHOP or square.type==pType.QUEEN)):
                    return True
                return False
        return False
    
    def kingkingCalculate(self, king : Piece, x : int, y : int) -> bool:
        for a in range(-1,2):
            for b in range(-1,2):
                if -1<x+a<8 and -1<y+b<8:
                    if self.boardArr[x+a][y+b].type==pType.KING and self.boardArr[x+a][y+b].col != king.col:
                        return True
        return False
        

    def drawMoves(self, screen : pygame.Surface, selectedID : int, turn : pCol):
        for move in self.moves:
            offset = self.boardObj.bOffset
            square = self.boardObj.squareSize
            if move.pieceID == selectedID and move.piece.col==turn:
                pygame.draw.circle(screen,(0,255,0),(offset+square*(move.endpos[0]+0.5),offset+square*(move.endpos[1]+0.5)),15)

class checkFinder:
    def __init__(self, movecalc : MoveCalculator):
        self.moves = movecalc.moves
        self.boardArr = movecalc.boardArr

    def findChecks(self, x : int, y : int):
        king = self.boardArr[x][y]

        self.pawnHandle(x, y, king)
        self.knightHandle(x, y, king)
        self.brHandle(x,y, king, True)
        self.brHandle(x,y, king, False)

    def pawnHandle(self, x : int, y : int, king : Piece):
        if x-1+2*king.col.value>7 or x-1+2*king.col.value<0:
            return None
        
        pawns : list[tuple[int,int]]= []
        
        if x+1<8:
            if (self.boardArr[x+1][y-1+2*king.col.value].type == pType.PAWN and
                self.boardArr[x+1][y-1+2*king.col.value].col != king.col):
                pawns.append((x+1,y-1+2*king.col.value))
            
        if x-1>-1:
            if (self.boardArr[x-1][y-1+2*king.col.value].type == pType.PAWN and
                self.boardArr[x-1][y-1+2*king.col.value].col != king.col):
                pawns.append((x-1,y-1+2*king.col.value))
        
        if len(pawns) == 0:
            return None
        
        n=0
        while n<len(self.moves):
            move = self.moves[n]
            popped = False
            if move.piece.col == king.col:
                if len(pawns) == 1:
                    if not (move.piece == king or move.endpos == pawns[0]):
                        self.moves.pop(n)
                        popped=True
                else:
                    if move.piece != king:
                        self.moves.pop(n)
                        popped=True

            if popped==False:
                n+=1

    def knightHandle(self,  x : int, y : int, king : Piece):
        knights : list[tuple[int,int]] = []
        for mode in range(4):
            if not -1<(x if (mode==0 or mode==1) else y)+(2 if (mode==0 or mode==2) else -2)<8:
                continue

            for i in range(-1,3,2):
                if not -1<((y if (mode==0 or mode==1) else x))+i<8:
                    continue

                n1 = x+(i if not (mode == 0 or mode == 1) else (2 if (mode==0 or mode==2) else -2))
                n2 = y+(i if (mode == 0 or mode == 1) else (2 if (mode==0 or mode==2) else -2))
                if self.boardArr[n1][n2].col != king.col and self.boardArr[n1][n2].type == pType.KNIGHT:
                    knights.append((n1,n2))
        
        if len(knights) == 0:
            return None
        
        poppedMoves : list[Move] = []
        for move in self.moves:
            if move.piece.col != king.col:
                continue

            if move.piece == king:
                continue

            if len(knights) == 1 and move.endpos==knights[0]:
                continue

            poppedMoves.append(move)

        for move in poppedMoves:
            self.moves.pop(self.moves.index(move))

    def brHandle(self, x : int, y : int, king : Piece, mode : bool):
        checks : list[list[tuple[int,int]]] = []
        pins : list[tuple[Piece,list[tuple[int,int]]]] = []
        for dir in range(4):
            between : list[tuple[int,int]] = []
            pin = nullPiece()
            for n in range(1,((min((7-x if dir%2 == 0 else x),(7-y if dir < 2 else y))) if mode else 
                              ((x if dir<2 else y)*(-1 if dir%2 else 1)+(7 if dir%2 else 0)))+1):
                n1 = (x+n if dir%2 == 0 else x-n) if mode else (x + (0 if dir>=2 else (n if dir%2 else -n)))
                n2 = (y+n if dir<2 else y-n) if mode else (y + (0 if dir<2 else (n if dir%2 else -n)))
                if (self.boardArr[n1][n2] == nullPiece()):
                    between.append((n1,n2))
                    continue

                if self.boardArr[n1][n2].col == king.col:
                    if not pin==nullPiece():
                        break
                    pin = self.boardArr[n1][n2]
                    continue

                if (self.boardArr[n1][n2].type==(pType.BISHOP if mode else pType.ROOK) or self.boardArr[n1][n2].type==pType.QUEEN):
                    between.append((n1,n2))
                    if pin == nullPiece():
                        checks.append(between)
                    else:
                        pins.append((pin,between))
                break
        
        poppedmoves = []
        for move in self.moves:
            if move.piece.col != king.col:
                continue
            if move.piece == king:
                continue

            for check in checks:
                if not move.endpos in check:
                    poppedmoves.append(move)
            
            for pinn in pins:
                if move.piece == pinn[0]:
                    if not move.endpos in pinn[1]:
                        poppedmoves.append(move)

        for move in poppedmoves:
            self.moves.pop(self.moves.index(move))

class posState(Enum):
    ACTIVE = 0
    STALEMATE = 1
    CHECKMATE = 2

class Position:
    def __init__(self, boardArr : list[list[Piece]], turn : pCol, state : posState = posState.ACTIVE):
        self.boardArr = tuple([tuple(
            [(piece.ID*3 + piece.moved[0] + piece.moved[1]) 
            for piece in column]) for column in boardArr])
        self.materialBal : int = 0
        self.state = state
        if self.state == posState.ACTIVE:
            ((self.materialBal + 
            self.materialVal(square) * ((1 if square.col == turn else -1) if square != nullPiece() else 0) 
            for square in row) for row in boardArr)
        elif self.state == posState.CHECKMATE:
            self.materialBal = -50
        self.moves : list[Move] = []
        self.nextPos : tuple = ()
        self.turn = turn

    def getBoard(self, key:dict[int,Piece]) -> tuple[tuple[Piece,...],...]:
        return tuple(tuple([self.pieceProcess(key[square//3],square) for square in column]) for column in self.boardArr)
    
    def pieceProcess(self, piece : Piece, num : int):
        if num%3==1:
            piece.moved=(True,False)
        elif num%3==2:
            piece.moved=(True,False)
        return piece
    
    def giveMoves(self, moves : list[Move]):
        self.moves = moves
    
    def givePos(self, nextPos : tuple):
        self.nextPos = nextPos
    
    def materialVal(self, piece : Piece) -> int:
        match (piece):
            case pType.PAWN:
                return 1
            case pType.KNIGHT:
                return 3
            case pType.BISHOP:
                return 3
            case pType.ROOK:
                return 5
            case pType.QUEEN:
                return 9
            case _:
                return 0
            
    def giveState(self, state : posState, key:dict[int,Piece]):
        self.materialBal=0
        match (state):
            case posState.ACTIVE:
                ((self.materialBal + 
                self.materialVal(key[square]) * ((1 if key[square].col == self.turn else -1) if square != 0 else 0) 
                for square in row) for row in self.boardArr)
            case posState.CHECKMATE:
                self.materialBal = -50
            case posState.STALEMATE:
                pass

class Bot:
    def __init__(self, colour : pCol, comple : bool = False):
        self.col = colour
        self.calculating = False
        self.result : concurrent.futures.Future
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.depth = 5 if comple else 3
        self.quitted = False
        self.comple = comple
    
    def quit(self):
        self.quitted = True
    
    def botcalc(self, boardArr : list[list[Piece]], turn : pCol) -> Move:
        if turn == self.col and not self.calculating:
            self.result = self.executor.submit(self.calculate, boardArr)
            self.calculating=True
        
        if self.calculating: 
            if self.result.done():
                return self.result.result()
            
        return newMove(nullPiece(), (0,0), (0,0))
                

    def recalc(self):
        self.calculating=False

    def calculate(self, boardArr : list[list[Piece]]) -> Move:
        currentPos = Position(boardArr, self.col)
        posKey = {piece.ID: piece for column in boardArr for piece in column}
        start = time.time_ns()
        for i in range(self.depth):
            if self.quitted:
                break
            
            if i<4:
                with PosFuture(currentPos,posKey) as posfu:
                    posfu.startCalc()
            else:
                self.prep4thread(currentPos,posKey,i)
            
            print(f"{i}={(time.time_ns()-start)/1000000000}")

        chosenMove = newMove(nullPiece(),(0,0),(0,0))

        if self.comple:
            chosenMove = self.complexEval(currentPos)
        else:
            chosenMove = self.simpleEval(currentPos)

        return chosenMove
    
    def prep4thread(self, position : Position, key : dict[int, Piece], iteration : int):
        if iteration == 4:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                posThreads = executor.map(threadStart,position.nextPos,itertools.repeat(key,len(position.nextPos)))
                position.givePos(tuple(posThreads))
            return None
        
        if len(position.nextPos)>0:
            for pos in position.nextPos:
                self.prep4thread(pos,key,iteration-1)

    def simpleEval(self, pos : Position) -> Move:
        return newMove(nullPiece(),(0,0),(0,0))

    def complexEval(self, pos : Position) -> Move:
        return newMove(nullPiece(),(0,0),(0,0))

def threadStart(position : Position, key : dict[int, Piece]) -> Position:
    posfu = PosFuture(position,key)
    posfu.startCalc()
    return posfu.position

class PosFuture:
    def __init__(self, position : Position, key : dict[int, Piece]):
        self.position = position
        self.key = key
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def setPos(self, position : Position):
        self.position = position

    def startCalc(self):
        self.posCalc(self.position)
    
    def posCalc(self, position : Position):

        if len(position.moves)>0:
            for pos in position.nextPos:
                self.posCalc(pos)
            return None
        
        boardArr = position.getBoard(self.key)
        moveCalc = MoveCalculator(boardArr)
        moveCalc.calculate(position.turn)
        position.giveMoves(moveCalc.moves)
        if len(position.moves)>0:
            self.posProcessor(position)
            return None
        
        position.giveState(posState.STALEMATE,self.key)
        
        for x in range(8):
            for y in range(8):
                if boardArr[x][y].type == pType.KING and boardArr[x][y].col == position.turn:
                    if not moveCalc.subkingCalculate(boardArr[x][y],x,y):
                        position.giveState(posState.CHECKMATE,self.key)
    
    def posProcessor(self, position : Position):
        posList = []
        boardTup = position.getBoard(self.key)
        for move in position.moves:
            boardArr = list(list(column) for column in boardTup)

            for a in range(8):
                for b in range(8):
                    if boardArr[a][b].moved==(True,False):
                        boardArr[a][b].moved=(True,True)
            if not move.piece.moved[0]:
                move.piece.moved=(True,False)

            boardArr[move.endpos[0]][move.endpos[1]] = move.piece
            boardArr[move.startpos[0]][move.startpos[1]] = nullPiece()
            if move.type == MoveType.ENPASSANT:
                boardArr[move.endpos[0]][move.endpos[1]+1-2*move.piece.col.value] = nullPiece()
            elif move.type == MoveType.CASTLE:
                if move.endpos[0]<move.startpos[0]:
                    boardArr[move.endpos[0]+1][move.endpos[1]] = boardArr[0][move.endpos[1]]
                    boardArr[0][move.endpos[1]]=nullPiece()
                else:
                    boardArr[move.endpos[0]-1][move.endpos[1]] = boardArr[7][move.endpos[1]]
                    boardArr[7][move.endpos[1]]=nullPiece()
            posList.append(Position(boardArr, pCol(position.turn.value*(-1)+1)))
        position.givePos(tuple(posList))


class Chess:
    def __init__(self, window : pygame.Window, board : Board, bot : int = 0, playerCol : pCol = pCol.WHITE):
        self.window = window
        self.screen = window.get_surface()
        self.boardObj = board
        self.boardArr = board.boardarray
        self.moveCalc = MoveCalculator(self.boardArr,self.boardObj)
        self.moveSet = self.moveCalc.moves
        self.IDselect = 0
        self.turn : pCol = pCol.WHITE
        self.isbot = bool(bot)
        self.bot : Bot
        self.playerCol : pCol
        if self.isbot:
            self.bot = Bot(pCol(playerCol.value*(-1)+1), bool(bot-1))
            self.playerCol = playerCol

    def update(self, mousepos : tuple[int,int], click : tuple[bool,bool,bool]):
        self.select(mousepos,click)

        self.moveCalc.calculate(self.turn)
        if self.isbot:
            self.moveMake(self.bot.botcalc(self.boardArr,self.turn))
    
    def draw(self):
        self.screen.fill((128,128,128))

        self.boardObj.draw(self.screen)
        self.drawSelected()
        self.moveCalc.drawMoves(self.screen,self.IDselect,self.turn)

        self.window.flip()

    def select(self, mousepos : tuple[int,int], click : tuple[bool,bool,bool]):
        offset = self.boardObj.bOffset
        square = self.boardObj.squareSize
        if not click[0]:
            return None
        if not (offset<mousepos[0]<offset+8*square and offset<mousepos[1]<offset+8*square):
            self.IDselect = 0
            return None
        if self.IDselect == 0:
            self.IDselect = self.boardArr[math.floor((mousepos[0]-offset)/square)][math.floor((mousepos[1]-offset)/square)].ID
            return None

        for move in self.moveCalc.moves:
            if move.pieceID == self.IDselect and move.piece.col == self.turn and (self.turn == self.playerCol if self.isbot else True):
                if (math.floor((mousepos[0]-offset)/square),math.floor((mousepos[1]-offset)/square)) == move.endpos:
                    self.moveMake(move)
                    return None
                    
        self.IDselect = self.boardArr[math.floor((mousepos[0]-offset)/square)][math.floor((mousepos[1]-offset)/square)].ID
        return None

    def moveMake(self, move : Move):
        if move.piece == nullPiece():
            return None
        print('a')
        for a in range(8):
            for b in range(8):
                if self.boardArr[a][b].moved==(True,False):
                    self.boardArr[a][b].moved=(True,True)
        if not move.piece.moved[0]:
            move.piece.moved=(True,False)

        self.boardArr[move.endpos[0]][move.endpos[1]] = move.piece
        self.boardArr[move.startpos[0]][move.startpos[1]] = nullPiece()
        if move.type == MoveType.ENPASSANT:
            self.boardArr[move.endpos[0]][move.endpos[1]+1-2*move.piece.col.value] = nullPiece()
        elif move.type == MoveType.CASTLE:
            if move.endpos[0]<move.startpos[0]:
                self.boardArr[move.endpos[0]+1][move.endpos[1]] = self.boardArr[0][move.endpos[1]]
                self.boardArr[0][move.endpos[1]]=nullPiece()
            else:
                self.boardArr[move.endpos[0]-1][move.endpos[1]] = self.boardArr[7][move.endpos[1]]
                self.boardArr[7][move.endpos[1]]=nullPiece()
        self.moveCalc.reCalc()
        self.turn=pCol(self.turn.value*(-1)+1)
        if self.isbot:
            self.bot.recalc()

    
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
    
    def quit(self):
        if self.isbot:
            self.bot.quit()

if __name__ == "__main__":
    import pygame
    pygame.init()

    bOffset = 20
    squareSize = 80
    piecesize = 50

    Bot_mode = ""
    while Bot_mode not in ("012") or len(Bot_mode)!=1:
        Bot_mode = input("0 for no bot, 1 for simple 3 deep bot, 2 for less simple 5 deep bot\n")
    Bot_col = ""
    while Bot_col not in ("12") or len(Bot_col)!=1:
        if Bot_mode != ("1" or "2"):
            Bot_col = "1"
            break
        Bot_col = input("1 to play as white, 2 to play as black\n")

    window = pygame.Window("Chess",(2*bOffset+8*squareSize,2*bOffset+8*squareSize))
    board = Board(squareSize,bOffset,piecesize)
    game = Chess(window,board,int(Bot_mode),pCol(int(Bot_col)-1))

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

    game.quit()
    pygame.quit()