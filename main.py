import tkinter as tk
import time
from enum import Enum
from dataclasses import dataclass

class Game:
    def __init__(self, root: tk.Tk):
        self.canvas : tk.Canvas = tk.Canvas(root,width=520,height=620)
        self.canvas.pack()
        self.root : tk.Tk = root

        self.keys=[]
        self.mPos=(0,0)
        self.mButt=[]

        self.board = Board()
        self.pm = PieceManager()

        self.turn = pCol.WHITE #change this after moves ofc

        self.gameloop()

    def gameloop(self):
        startTime : int = int(time.time()*1000)

        self.update()
        self.draw()

        finTime : int = int(time.time()*1000)
        if finTime-startTime<1000/60:
            buffertime=int(1000/60 - (finTime-startTime))
        else:
            buffertime=1
        #print(buffertime)
        self.root.after(buffertime,self.gameloop)

    def update(self):
        #st = time.time()*1000
        if ('q' or 'Q') in self.keys:
            self.root.destroy()
            quit()

        self.turn=self.pm.clickM(self.mButt,self.mPos,self.turn)
        self.pm.findmoves(self.turn)
        self.pm.checkCheck(self.turn)
        #print(time.time()*1000-st)


    def draw(self):
        self.canvas.delete("all")

        self.board.draw(self.canvas)
        self.pm.draw(self.canvas)

        self.canvas.pack()

    def key_press(self, event : tk.Event):
        if event.keysym not in self.keys:
            self.keys.append(event.keysym)
    
    def key_rel(self, event : tk.Event):
        while event.keysym in self.keys:
            self.keys.pop(self.keys.index(event.keysym))
    
    def mouseMov(self, event : tk.Event):
        self.mPos=(event.x,event.y)
    
    def mPress(self, event : tk.Event):
        if event.num not in self.mButt:
            self.mButt.append(event.num)
    
    def mRel(self, event : tk.Event):
        while event.num in self.mButt:
            self.mButt.pop(self.mButt.index(event.num))

class Board:
    def __init__(self):
        self.tileN : int =8
        self.tileS : int =60
        self.white : tuple =(255,255,200)
        self.black : tuple =(20,20,0)  

    def draw(self, canvas : tk.Canvas):
        col = ("white","black")
        for a in range(self.tileN):
            for b in range(self.tileN):
                canvas.create_rectangle(20+a*self.tileS,70+b*self.tileS,20+(a+1)*self.tileS,70+(b+1)*self.tileS,fill=col[(a+b)%2])


#class MovBlock:
#    def __init__(self):
#        self.x=90
#        self.y=90
#        self.size=20
#    
#    def draw(self, canvas : tk.Canvas):
#        canvas.create_rectangle(self.x,self.y,self.x+self.size,self.y+self.size, fill = "red")
#    
#    def move(self, keys : list):
#        if ('a' or 'A') in keys:
#            self.x-=4
#        if ('d' or 'D') in keys:
#            self.x+=4
#        if ('w' or 'W') in keys:
#            self.y-=4
#        if ('s' or 'S') in keys:
#            self.y+=4

class pCol(Enum):
    WHITE = 0
    BLACK = 1

class pType(Enum):
    PAWN=0
    KNIGHT=1
    BISHOP=2
    ROOK=3
    QUEEN=4
    KING=5

@dataclass
class Piece:
    col : pCol
    type : pType
    pos : tuple[int,int]
    selected : bool = False

class PieceManager:
    def __init__(self):
        self.pieces : list[Piece] = []
        self.taken : list[Piece] = []
        self.moves : list[tuple[int,int]] = []

        colours = (pCol.WHITE,pCol.BLACK)
        backrank = (pType.ROOK,pType.KNIGHT,pType.BISHOP,pType.QUEEN,pType.KING,pType.BISHOP,pType.KNIGHT,pType.ROOK)

        for a in range(2):
            for b in range(2):
                for c in range(8):
                    if b==1:
                        self.pieces.append(Piece(colours[-a+1],backrank[c],(c,a*7)))
                    else:
                        self.pieces.append(Piece(colours[-a+1],pType.PAWN,(c,1+a*5)))
    
    def draw(self, canvas : tk.Canvas):
        tileS : int =60
        col = ("white","black")
        for piece in self.pieces:
            canvas.create_rectangle(20+(piece.pos[0]+0.5)*tileS-20,70+(piece.pos[1]+0.5)*tileS-20,
                                    20+(piece.pos[0]+0.5)*tileS+20,70+(piece.pos[1]+0.5)*tileS+20, 
                                    fill=col[piece.col.value], outline=col[1-piece.col.value])
            canvas.create_text(20+(piece.pos[0]+0.5)*tileS,70+(piece.pos[1]+0.5)*tileS, text=self.getletter(piece), 
                               anchor='center',font=('consolas',24), fill=col[1-piece.col.value])
        for move in self.moves:
            canvas.create_oval(20+(move[0]+0.5)*tileS-10,70+(move[1]+0.5)*tileS-10,
                                    20+(move[0]+0.5)*tileS+10,70+(move[1]+0.5)*tileS+10, 
                                    fill="green", outline="")

    def getletter(self, piece : Piece) -> str:
        char : str = ""
        match piece.type:
            case pType.PAWN:
                char = "P"
            case pType.ROOK:
                char = "R"
            case pType.KNIGHT:
                char = "N"
            case pType.BISHOP:
                char = "B"
            case pType.KING:
                char = "K"
            case pType.QUEEN:
                char = "Q"
        return char

    def findmoves(self,turn:pCol):
        self.moves : list[tuple[int,int]] = []
        for piece in self.pieces:
            if piece.selected and piece.col == turn:
                match piece.type:

                    case pType.PAWN:
                        if -1<piece.pos[1]+(-1+2*piece.col.value)<8:
                            self.moves.append((piece.pos[0],piece.pos[1]+(-1+2*piece.col.value)))
                            if piece.pos[1]==7-(piece.col.value*5+1):
                                self.moves.append((piece.pos[0],piece.pos[1]+(-2+4*piece.col.value)))
                            for x in self.pieces:
                                if x.pos == (piece.pos[0],piece.pos[1]+(-1+2*piece.col.value)):
                                    if (piece.pos[0],piece.pos[1]+(-1+2*piece.col.value)) in self.moves:
                                        self.moves.pop(self.moves.index((piece.pos[0],piece.pos[1]+(-1+2*piece.col.value))))
                                if x.pos == (piece.pos[0],piece.pos[1]+(-2+4*piece.col.value)):
                                    if (piece.pos[0],piece.pos[1]+(-2+4*piece.col.value)) in self.moves:
                                        self.moves.pop(self.moves.index((piece.pos[0],piece.pos[1]+(-2+4*piece.col.value))))
                                if x.pos == (piece.pos[0]-1,piece.pos[1]+(-1+2*piece.col.value)) and not (x.col == piece.col):
                                    self.moves.append((piece.pos[0]-1,piece.pos[1]+(-1+2*piece.col.value)))
                                if x.pos == (piece.pos[0]+1,piece.pos[1]+(-1+2*piece.col.value)) and not (x.col == piece.col):
                                    self.moves.append((piece.pos[0]+1,piece.pos[1]+(-1+2*piece.col.value)))
                    
                    case pType.KNIGHT:
                        #add moves that won't take you off the board
                        if piece.pos[0]-2>=0:
                            if piece.pos[1]-1>=0:
                                self.moves.append((piece.pos[0]-2,piece.pos[1]-1))
                            if piece.pos[1]+1<=7:
                                self.moves.append((piece.pos[0]-2,piece.pos[1]+1))
                        if piece.pos[0]+2<=7:
                            if piece.pos[1]-1>=0:
                                self.moves.append((piece.pos[0]+2,piece.pos[1]-1))
                            if piece.pos[1]+1<=7:
                                self.moves.append((piece.pos[0]+2,piece.pos[1]+1))
                        if piece.pos[1]-2>=0:
                            if piece.pos[0]-1>=0:
                                self.moves.append((piece.pos[0]-1,piece.pos[1]-2))
                            if piece.pos[0]+1<=7:
                                self.moves.append((piece.pos[0]+1,piece.pos[1]-2))
                        if piece.pos[1]+2<=7:
                            if piece.pos[0]-1>=0:
                                self.moves.append((piece.pos[0]-1,piece.pos[1]+2))
                            if piece.pos[0]+1<=7:
                                self.moves.append((piece.pos[0]+1,piece.pos[1]+2))

                        #remove moves which overlap with existing pieces
                        for x in self.pieces:
                            if x.pos in self.moves and x.col==piece.col:
                                self.moves.pop(self.moves.index(x.pos))

                    case pType.ROOK:

                        access=True
                        for i in range(1,piece.pos[0]+1):
                            if access:
                                self.moves.append((piece.pos[0]-i,piece.pos[1]))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]-i,piece.pos[1]):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,8-piece.pos[0]):
                            if access:
                                self.moves.append((piece.pos[0]+i,piece.pos[1]))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]+i,piece.pos[1]):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,piece.pos[1]+1):
                            if access:
                                self.moves.append((piece.pos[0],piece.pos[1]-i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0],piece.pos[1]-i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,8-piece.pos[1]):
                            if access:
                                self.moves.append((piece.pos[0],piece.pos[1]+i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0],piece.pos[1]+i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                    case pType.BISHOP:

                        access=True
                        for i in range(1,(piece.pos[0]+1 if piece.pos[0]+1<=piece.pos[1]+1 else piece.pos[1]+1)):
                            if access:
                                self.moves.append((piece.pos[0]-i,piece.pos[1]-i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]-i,piece.pos[1]-i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)
                        
                        access=True
                        for i in range(1,(8-piece.pos[0] if 8-piece.pos[0]<piece.pos[1]+1 else piece.pos[1]+1)):
                            if access:
                                self.moves.append((piece.pos[0]+i,piece.pos[1]-i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]+i,piece.pos[1]-i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,(8-piece.pos[0] if 8-piece.pos[0]<8-piece.pos[1] else 8-piece.pos[1])):
                            if access:
                                self.moves.append((piece.pos[0]+i,piece.pos[1]+i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]+i,piece.pos[1]+i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,(piece.pos[0]+1 if piece.pos[0]+1<8-piece.pos[1] else 8-piece.pos[1])):
                            if access:
                                self.moves.append((piece.pos[0]-i,piece.pos[1]+i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]-i,piece.pos[1]+i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)
                        
                    case pType.QUEEN:

                        access=True
                        for i in range(1,piece.pos[0]+1):
                            if access:
                                self.moves.append((piece.pos[0]-i,piece.pos[1]))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]-i,piece.pos[1]):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,8-piece.pos[0]):
                            if access:
                                self.moves.append((piece.pos[0]+i,piece.pos[1]))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]+i,piece.pos[1]):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,piece.pos[1]+1):
                            if access:
                                self.moves.append((piece.pos[0],piece.pos[1]-i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0],piece.pos[1]-i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,8-piece.pos[1]):
                            if access:
                                self.moves.append((piece.pos[0],piece.pos[1]+i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0],piece.pos[1]+i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)
                        
                        access=True
                        for i in range(1,(piece.pos[0]+1 if piece.pos[0]+1<=piece.pos[1]+1 else piece.pos[1]+1)):
                            if access:
                                self.moves.append((piece.pos[0]-i,piece.pos[1]-i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]-i,piece.pos[1]-i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)
                        
                        access=True
                        for i in range(1,(8-piece.pos[0] if 8-piece.pos[0]<piece.pos[1]+1 else piece.pos[1]+1)):
                            if access:
                                self.moves.append((piece.pos[0]+i,piece.pos[1]-i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]+i,piece.pos[1]-i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,(8-piece.pos[0] if 8-piece.pos[0]<8-piece.pos[1] else 8-piece.pos[1])):
                            if access:
                                self.moves.append((piece.pos[0]+i,piece.pos[1]+i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]+i,piece.pos[1]+i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)

                        access=True
                        for i in range(1,(piece.pos[0]+1 if piece.pos[0]+1<8-piece.pos[1] else 8-piece.pos[1])):
                            if access:
                                self.moves.append((piece.pos[0]-i,piece.pos[1]+i))
                                for x in self.pieces:
                                    if x.pos==(piece.pos[0]-i,piece.pos[1]+i):
                                        access=False
                                        if x.col==piece.col:
                                            self.moves.pop(len(self.moves)-1)
                    
                    case pType.KING:
                        if piece.pos[0]-1>-1:
                            self.moves.append((piece.pos[0]-1,piece.pos[1]))
                        if piece.pos[0]+1<8:
                            self.moves.append((piece.pos[0]+1,piece.pos[1]))
                        if piece.pos[1]-1>-1:
                            self.moves.append((piece.pos[0],piece.pos[1]-1))
                        if piece.pos[1]+1<8:
                            self.moves.append((piece.pos[0],piece.pos[1]+1))
                        if piece.pos[0]-1>-1 and piece.pos[1]-1>-1:
                            self.moves.append((piece.pos[0]-1,piece.pos[1]-1))
                        if piece.pos[0]-1>-1 and piece.pos[1]+1<8:
                            self.moves.append((piece.pos[0]-1,piece.pos[1]+1))
                        if piece.pos[0]+1<8 and piece.pos[1]-1>-1:
                            self.moves.append((piece.pos[0]+1,piece.pos[1]-1))
                        if piece.pos[0]+1<8 and piece.pos[1]+1<8:
                            self.moves.append((piece.pos[0]+1,piece.pos[1]+1))
                        for x in self.pieces:
                            if x.pos in self.moves and x.col==piece.col:
                                self.moves.pop(self.moves.index(x.pos))
                            

                print(self.moves)
    
    def checkCheck(self,turn:pCol):
        Sp=None
        for Ap in self.pieces:
            if Ap.selected:
                Sp=Ap
        if Sp != None:
            for Bp in self.pieces:
                if Bp.type==pType.KING and Bp.col==turn:
                    for Cp in self.pieces:
                        if Cp.type == pType.PAWN and Cp.col !=turn:
                            #find existing checks
                            if Sp != Bp:
                                if Cp.pos == (Bp.pos[0]-1,Bp.pos[1]-(Cp.col.value*2-1)):
                                    i=0
                                    while i<len(self.moves):
                                        if self.moves[i]!=(Bp.pos[0]-1,Bp.pos[1]-(Cp.col.value*2-1)):
                                            self.moves.pop(i)
                                        else:
                                            i+=1
                                if Cp.pos == (Bp.pos[0]+1,Bp.pos[1]-(Cp.col.value*2-1)):
                                    i=0
                                    while i<len(self.moves):
                                        if self.moves[i]!=(Bp.pos[0]+1,Bp.pos[1]-(Cp.col.value*2-1)):
                                            self.moves.pop(i)
                                        else:
                                            i+=1
                            #find checks which could be moved into
                            else:
                                self.pawnChPredict(Cp,Bp,-1,-1)
                                self.pawnChPredict(Cp,Bp,0,-1)
                                self.pawnChPredict(Cp,Bp,1,-1)
                                self.pawnChPredict(Cp,Bp,-1,0)
                                self.pawnChPredict(Cp,Bp,+1,0)
                                self.pawnChPredict(Cp,Bp,-1,1)
                                self.pawnChPredict(Cp,Bp,0,1)
                                self.pawnChPredict(Cp,Bp,1,1)

                        elif Cp.type == pType.KNIGHT and Cp.col !=turn:
                            self.knChPredict(Cp,Bp,-1,-1)
                            self.knChPredict(Cp,Bp,0,-1)
                            self.knChPredict(Cp,Bp,1,-1)
                            self.knChPredict(Cp,Bp,-1,0)
                            self.knChPredict(Cp,Bp,0,0)
                            self.knChPredict(Cp,Bp,1,0)
                            self.knChPredict(Cp,Bp,-1,1)
                            self.knChPredict(Cp,Bp,0,1)
                            self.knChPredict(Cp,Bp,1,1)

                        elif Cp.type == pType.ROOK and Cp.col !=turn:
                            self.Rookcheckfn(Bp,Cp,False,True)
                            self.Rookcheckfn(Bp,Cp,True,True)
                            self.Rookcheckfn(Bp,Cp,False,False)
                            self.Rookcheckfn(Bp,Cp,True,False)
                            if Bp.selected:
                                self.Rookcheckpr(Bp,Cp,True,True)
                                self.Rookcheckpr(Bp,Cp,False,True)
                                self.Rookcheckpr(Bp,Cp,True,False)
                                self.Rookcheckpr(Bp,Cp,False,False)
                        
                        elif Cp.type == pType.BISHOP and Cp.col!=turn:
                            self.Bishopcheckfn(Bp,Cp,True,True)
                            self.Bishopcheckfn(Bp,Cp,False,False)
                            self.Bishopcheckfn(Bp,Cp,False,True)
                            self.Bishopcheckfn(Bp,Cp,True,False)

            print(self.moves)

    def pawnChPredict(self,Pawn : Piece, King : Piece, Off1 : int, Off2 : int):
        if Pawn.pos == (King.pos[0]+Off1+1,King.pos[1]+Off2-(Pawn.col.value*2-1)) or Pawn.pos == (King.pos[0]+Off1-1,King.pos[1]+Off2-(Pawn.col.value*2-1)):
            i=0
            while i<len(self.moves):
                if self.moves[i]==(King.pos[0]+Off1,King.pos[1]+Off2):
                    self.moves.pop(i)
                else:
                    i+=1
    
    def knChPredict(self, Knight : Piece, King : Piece, Off1 : int, Off2 : int):
        bsX = King.pos[0]+Off1
        bsY = King.pos[1]+Off2
        if (
            Knight.pos == (bsX+2,bsY+1) or
            Knight.pos == (bsX+2,bsY-1) or
            Knight.pos == (bsX-2,bsY+1) or
            Knight.pos == (bsX-2,bsY-1) or
            Knight.pos == (bsX+1,bsY+2) or
            Knight.pos == (bsX-1,bsY+2) or
            Knight.pos == (bsX+1,bsY-2) or
            Knight.pos == (bsX-1,bsY-2)
        ):
            if 0 == Off1 and 0 == Off2:
                if not King.selected:
                    i=0
                    while i<len(self.moves):
                        if self.moves[i]!=Knight.pos:
                            self.moves.pop(i)
                        else:
                            i+=1
            else:
                if King.selected:
                    i=0
                    while i<len(self.moves):
                        if self.moves[i]==(bsX,bsY):
                            self.moves.pop(i)
                        else:
                            i+=1
    
    def Rookcheckfn(self,King:Piece,Rook:Piece,vert:bool,low:bool):
        pinned : Piece
        pin = False
        check = False
        between : list[tuple[int,int]] = []
        if low:
            for i in range(1,King.pos[1 if vert else 0]+1):
                if Rook.pos == ((King.pos[0],King.pos[1]-i) if vert else (King.pos[0]-i,King.pos[1])):
                    check=True
                if not check:
                    between.append(((King.pos[0],King.pos[1]-i) if vert else (King.pos[0]-i,King.pos[1])))
        if not low:
            for i in range(1,8-King.pos[1 if vert else 0]):
                if Rook.pos == ((King.pos[0],King.pos[1]+i) if vert else (King.pos[0]+i,King.pos[1])):
                    check=True
                if not check:
                    between.append(((King.pos[0],King.pos[1]+i) if vert else (King.pos[0]+i,King.pos[1])))
        if check:
            for piece in self.pieces:
                if piece.pos in between:
                    if check:
                        check = False
                        if piece.col==King.col:
                            pin=True
                            pinned = piece
                    elif pin:
                        pin = False
        if check:
            if King.selected:
                if (((King.pos[0]-1,King.pos[1]) if not vert else (King.pos[0],King.pos[1]-1)) in self.moves
                and not ((King.pos[0]-1,King.pos[1]) if not vert else (King.pos[0],King.pos[1]-1)) == Rook.pos):
                    self.moves.pop(self.moves.index((King.pos[0]-1,King.pos[1]) if not vert else (King.pos[0],King.pos[1]-1)))
                if (((King.pos[0]+1,King.pos[1]) if not vert else (King.pos[0],King.pos[1]+1)) in self.moves
                and not ((King.pos[0]+1,King.pos[1]) if not vert else (King.pos[0],King.pos[1]+1)) == Rook.pos):
                    self.moves.pop(self.moves.index((King.pos[0]+1,King.pos[1]) if not vert else (King.pos[0],King.pos[1]+1)))
            else:
                i=0
                while i<len(self.moves):
                    if not(self.moves[i] in between or self.moves[i]==Rook.pos):
                        self.moves.pop(i)
                    else:
                        i+=1
        elif pin:
            if pinned.selected:
                i=0
                while i<len(self.moves):
                    if not(self.moves[i] in between or self.moves[i]==Rook.pos):
                        self.moves.pop(i)
                    else:
                        i+=1

    def Rookcheckpr(self,King:Piece,Rook:Piece,horz:bool,low:bool):
        access = [True,True]
        n=0
        while access[0] or access[1]:
            for i in range(2):
                if access[i]:
                    if -1 < King.pos[1 if horz else 0]-n+2*i*n < 8:
                        for piece in self.pieces:
                            if horz:
                                if piece.pos == (King.pos[0]-1*(1 if low else -1),King.pos[1]-n+2*i*n):
                                    if piece==Rook:
                                        move = 0
                                        while move<len(self.moves):
                                            if self.moves[move][0] == King.pos[0]-1*(1 if low else -1) and not self.moves[move] == Rook.pos:
                                                self.moves.pop(move)
                                            else:
                                                move+=1
                                    else:
                                        access[i] = False
                            if not horz:
                                if piece.pos == (King.pos[0]-n+2*i*n,King.pos[1]-1*(1 if low else -1)):
                                    if piece==Rook:
                                        move = 0
                                        while move<len(self.moves):
                                            if self.moves[move][1] == King.pos[1]-1*(1 if low else -1) and not self.moves[move] == Rook.pos:
                                                self.moves.pop(move)
                                            else:
                                                move+=1
                                    else:
                                        access[i] = False
                    else:
                        access[i] = False
            n+=1

    def Bishopcheckfn(self,King:Piece,Bishop:Piece,left:bool,up:bool):
        pinned : Piece
        pin = False
        check = False
        between : list[Piece] = []
        betweenpos : list[tuple[int,int]] = []
        for i in range(1,min(King.pos[0]+1 if left else 8-King.pos[0],
                             King.pos[1]+1 if up else 8-King.pos[1])):
            for piece in self.pieces:
                if not check:
                    if piece.pos==(King.pos[0]-(i if left else -i),
                                King.pos[1]-(i if up else -i)):
                        if piece==Bishop:
                            check=True
                        else:
                            between.append(piece)
                    if not check:
                        betweenpos.append((King.pos[0]-(i if left else -i),King.pos[1]-(i if up else -i)))
            if check:
                if len(between)>0:
                    check=False
                    if len(between)==1:
                        pinned = between[0]
                        pin = True
                elif King.selected:
                    n=0
                    while n<len(self.moves):
                        if self.moves[n] in (((King.pos[0]-1,King.pos[1]-1),(King.pos[0]+1,King.pos[1]+1)) 
                                             if up==left else 
                                             ((King.pos[0]-1,King.pos[1]+1),(King.pos[0]+1,King.pos[1]-1))):
                            self.moves.pop(n)
                        else:
                            n+=1
                else:
                    n=0
                    while n<len(self.moves):
                        if not (self.moves[n] in betweenpos or self.moves[n]==Bishop.pos):
                            self.moves.pop(n)
                        else:
                            n+=1
            if pin:
                if pinned.selected:
                    n=0
                    while n<len(self.moves):
                        if not (self.moves[n] in betweenpos or self.moves[n]==Bishop.pos):
                            self.moves.pop(n)
                        else:
                            n+=1


    def clickM(self, mButt : list[int], mPos : tuple[int,int],turn : pCol) -> pCol:
        if 1 in mButt:
            for move in self.moves:
                if 50+60*move[0]-30<mPos[0]<50+60*move[0]+30 and 100+60*move[1]-30<mPos[1]<100+60*move[1]+30:
                    for piece in self.pieces:
                        if piece.pos==move:
                            self.pieces.pop(self.pieces.index(piece))
                        if piece.selected:
                            piece.pos=move
                    turn = pCol.WHITE if turn==pCol.BLACK else pCol.BLACK

            for piece in self.pieces:
                piece.selected=False
                if 50+60*piece.pos[0]-30<mPos[0]<50+60*piece.pos[0]+30 and 100+60*piece.pos[1]-30<mPos[1]<100+60*piece.pos[1]+30:
                    piece.selected = True
        return turn


root = tk.Tk()
root.title("chess")

game = Game(root)

root.bind("<KeyPress>",game.key_press)
root.bind("<KeyRelease>",game.key_rel)
root.bind("<Motion>",game.mouseMov)
root.bind("<ButtonPress>",game.mPress)
root.bind("<ButtonRelease>",game.mRel)

root.mainloop()