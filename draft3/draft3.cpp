#include<SDL3/SDL.h>
#include<SDL3/SDL_main.h>
#include<SDL3_ttf/SDL_ttf.h>
#include<chrono>
#include<iostream>
#include<thread>
#include<vector>
#include<array>
#include<cmath>
#include<algorithm>

template <typename T>
bool listContains(const std::vector<T> &list, T item){
    bool contains = false;
    int index = 0;
    while (!contains && index<list.size()){
        if (list[index]==item){
            contains=true;
        } else {
            index++;
        }
    }
    return contains;
}

void renderRect(SDL_Renderer* renderer, std::array<float,2> pos, std::array<float,2> size, std::array<int,3> colour, bool fill){
    SDL_SetRenderDrawColor(renderer, colour[0], colour[1], colour[2], 255);
    SDL_FRect *rect = new SDL_FRect{pos[0],pos[1],size[0],size[1]};
    if (fill) {
        SDL_RenderFillRect(renderer, rect);
    } else {
        SDL_RenderRect(renderer, rect);
    }
    delete rect;
}

void renderCircle(SDL_Renderer* renderer, int x, int y, int rad, std::array<int,3> colour){
    SDL_SetRenderDrawColor(renderer, colour[0], colour[1], colour[2], 255);
    for (int x2 = -rad; x2<=rad; x2++){
        for (int y2 = -rad; y2<=rad; y2++){
            if ((x2 * x2 + y2 * y2)<(rad*rad)){
                SDL_RenderPoint(renderer,x+x2,y+y2);
            }
        }
    }
}

void renderText(TTF_TextEngine *textengine, TTF_Font *font, std::string text, std::array<int,2> pos, std::array<int,3> colour){
    //pos is centered
    TTF_Text* textobj = TTF_CreateText(textengine, font, text.c_str(), 0);
    int* width = new int(0);
    int* height = new int(0);
    TTF_GetTextSize(textobj, width, height);
    TTF_SetTextColor(textobj, colour[0], colour[1], colour[2], 255);

    TTF_DrawRendererText(textobj,pos[0]-(*width)/2,pos[1]-(*height)/2);

    TTF_DestroyText(textobj);
    delete width;
    delete height;
}

enum class pCol {
    BLACK=-1,
    NONE=0,
    WHITE=1,
};

std::array<int,3> getRGB(pCol col){
    std::array<int,3> RGB = {128,128,128};
    switch (col){
        case pCol::WHITE:
            RGB = {255,255,255};
            break;
        case pCol::BLACK:
            RGB = {0,0,0};
            break;
        default:
            break;
    }
    return RGB;
}

enum class pType {
    NONE=0,
    PAWN=1,
    KNIGHT=2,
    BISHOP=3,
    ROOK=4,
    QUEEN=5,
    KING=6
};

std::string getLetter(pType type){
    std::array<std::string,7> letters = {"","P","N","B","R","Q","K"};
    return letters[static_cast<int>(type)];
}

struct Piece {
    pType type;
    pCol colour;
    std::array<bool,2> moved = {false,false};
};

Piece nullPiece(){
    return Piece{pType::NONE, pCol::NONE};
}

bool operator==(const Piece &piece1, const Piece &piece2){
    return (piece1.type == piece2.type && piece1.colour == piece2.colour && piece1.moved == piece2.moved);
} //annoyance

bool operator!=(const Piece &piece1, const Piece &piece2){
    return (piece1.type != piece2.type || piece1.colour != piece2.colour || piece1.moved != piece2.moved);
} //even greater annoyance

enum class mType {
    NORMAL=0,
    CASTLE=1,
    ENPASSANT=2,
    PROMOTE_N,
    PROMOTE_B,
    PROMOTE_R,
    PROMOTE_Q
};

struct Move {
    Piece piece;
    std::array<int,2> startpos;
    std::array<int,2> endpos;
    mType type;
};

bool operator==(const Move &move1, const Move &move2){
    return (move1.startpos == move2.startpos && move1.endpos == move2.endpos && move1.type == move2.type);
} //annoyance

namespace checkFinder{
    struct subcheckret{
        bool check;
        bool pin;
        std::vector<std::array<int,2>> between;
        std::array<int,2> pinnpos;
    };

    struct checkfindret{
        subcheckret up2left;
        subcheckret right2up;
        subcheckret down2right;
        subcheckret left2down;
    };

    void manageChecks(const std::array<std::array<Piece,8>,8> &boardArr, std::vector<Move> &moves, pCol turn);
    void movePopper(std::vector<Move> &moves, std::vector<std::array<int,2>> checkers);
    void movePopper(std::vector<Move> &moves, checkfindret results);
    std::vector<std::array<int,2>> pawnhandle(const std::array<std::array<Piece,8>,8> &boardArr, pCol turn, std::array<int,2> kingpos);
    std::vector<std::array<int,2>> knighthandle(const std::array<std::array<Piece,8>,8> &boardArr, pCol turn, std::array<int,2> kingpos);
    checkfindret bishophandle(const std::array<std::array<Piece,8>,8> &boardArr, pCol turn, std::array<int,2> kingpos);
    checkfindret rookhandle(const std::array<std::array<Piece,8>,8> &boardArr, pCol turn, std::array<int,2> kingpos);
}

class MoveCalculator{
    protected: //inital variables

    bool calculated;
    std::vector<Move> moves;

    public:

    MoveCalculator(){
        moves = {};
        calculated = false;
    }

    void reCalc(){
        moves.clear();
        calculated = false;
    }

    const std::vector<Move> &getMoves(){
        return moves;
    }

    void calculate(pCol turn, const std::array<std::array<Piece,8>,8> &boardArr){
        if (calculated){
            return;
        }

        for (int x=0; x<8; x++){
            for (int y=0; y<8; y++){
                if (boardArr[x][y].colour!=turn){
                    continue;
                }

                switch (boardArr[x][y].type){
                    case pType::PAWN:
                        pawnCalc(x,y, boardArr);
                        break;
                    case pType::KNIGHT:
                        knightCalc(x,y, boardArr);
                        break;
                    case pType::BISHOP:
                        bishopCalc(x,y, boardArr);
                        break;
                    case pType::ROOK:
                        rookCalc(x,y, boardArr);
                        break;
                    case pType::QUEEN:
                        bishopCalc(x,y, boardArr);
                        rookCalc(x,y, boardArr);
                        break;
                    case pType::KING:
                        kingCalc(x,y,boardArr);
                        break;
                    default:
                        break;
                }
            }
        }

        checkFinder::manageChecks(boardArr, moves, turn);

        calculated = true;
    }

    protected: //inner functions

    void pawnCalc(int x, int y, const std::array<std::array<Piece,8>,8> &boardArr){
        Piece pawn = boardArr[x][y];
        bool promote = false;
        if (y-static_cast<int>(pawn.colour)<0 || y-static_cast<int>(pawn.colour)>7){
            return;
        } else if (y-static_cast<int>(pawn.colour)==0 || y-static_cast<int>(pawn.colour)==7){
            promote = true;
        }

        if (boardArr[x][y-static_cast<int>(pawn.colour)] == nullPiece()){
            if (!promote){
                moves.push_back(Move{pawn, std::array<int,2>{x,y}, std::array<int,2>{x,y-static_cast<int>(pawn.colour)}, mType::NORMAL});
                if (pawn.moved == std::array<bool,2>{false,false} && boardArr[x][y - 2*static_cast<int>(pawn.colour)] == nullPiece()){
                    moves.push_back(Move{pawn, std::array<int,2>{x,y}, std::array<int,2>{x,y-2*static_cast<int>(pawn.colour)}, mType::NORMAL});
                }
            } else {
                for (int i = 3; i<=6; i++){
                    moves.push_back(Move{pawn, std::array<int,2>{x,y}, std::array<int,2>{x,y-static_cast<int>(pawn.colour)}, static_cast<mType>(i)});
                }
            }
        }

        for (int n = -1; n <= 1; n+=2){
            if (x+n<0 || x+n>7){
                continue;
            }

            if (boardArr[x+n][y-static_cast<int>(pawn.colour)].colour == static_cast<pCol>(static_cast<int>(pawn.colour)*-1)){
                if (!promote){
                    moves.push_back(Move{pawn, std::array<int,2>{x,y}, std::array<int,2>{x+n,y-static_cast<int>(pawn.colour)}, mType::NORMAL});
                } else {
                    for (int i = 3; i<=6; i++){
                        moves.push_back(Move{pawn, std::array<int,2>{x,y}, std::array<int,2>{x+n,y-static_cast<int>(pawn.colour)}, static_cast<mType>(i)});
                    }
                }
                continue;
            }

            if (boardArr[x+n][y].colour == static_cast<pCol>(static_cast<int>(pawn.colour)*-1) && boardArr[x+n][y].moved==std::array<bool,2>{true,false} && y==static_cast<int>(3.5-0.5*static_cast<int>(pawn.colour))){
                moves.push_back(Move{pawn, std::array<int,2>{x,y}, std::array<int,2>{x+n,y-static_cast<int>(pawn.colour)}, mType::ENPASSANT});
            }
        }
    }

    void knightCalc(int x, int y, const std::array<std::array<Piece,8>,8> &boardArr){
        Piece knight = boardArr[x][y];
        for (int n=0; n<4; n++){

            if (x*!(n%2)+y*(n%2)-2+4*static_cast<int>(n/2)>7 || x*!(n%2)+y*(n%2)-2+4*static_cast<int>(n/2)<0){
                continue;
            }

            for (int i=-1; i<=1; i+=2){

                if (x*(n%2)+y*!(n%2)+i>7 || x*(n%2)+y*!(n%2)+i<0){
                    continue;
                }

                if (boardArr[x+!(n%2)*(-2+4*static_cast<int>(n/2))+(n%2)*i][y+(n%2)*(-2+4*static_cast<int>(n/2))+!(n%2)*i].colour==knight.colour){
                    continue;
                }

                moves.push_back(Move{knight,std::array<int,2>{x,y},
                                    std::array<int,2>{x+!(n%2)*(-2+4*static_cast<int>(n/2))+(n%2)*i,y+(n%2)*(-2+4*static_cast<int>(n/2))+!(n%2)*i}});
            }
        }
    }

    void bishopCalc(int x, int y, const std::array<std::array<Piece,8>,8> &boardArr){
        Piece bishop = boardArr[x][y];

        for (int i=0; i<4; i++){
            for (int n=1; n<=std::min(x*(1-2*(i%2))+7*(i%2),y*(1-2*(i<2))+7*(i<2)); n++){

                Piece square = boardArr[x+n*(1-2*!(i%2))][y+n*(1-2*!(i<2))];

                if (square.colour==bishop.colour){
                    break;
                }

                moves.push_back(Move{bishop,std::array<int,2>{x,y},std::array<int,2>{x+n*(1-2*!(i%2)),y+n*(1-2*!(i<2))}});

                if (square.colour!=pCol::NONE){
                    break;
                }

            }
        }
    }

    void rookCalc(int x, int y, const std::array<std::array<Piece,8>,8> &boardArr){
        Piece rook = boardArr[x][y];

        for (int i=0; i<4; i++){
            for (int n=1; n<= (x*(1-2*(i%2))+7*(i%2))*(i<2)+(y*(1-2*(i%2))+7*(i%2))*!(i<2); n++){
                Piece square = boardArr[x+n*(1-2*!(i%2))*(i<2)][y+n*(1-2*!(i%2))*!(i<2)];

                if (square.colour==rook.colour){
                    break;
                }
                moves.push_back(Move{rook,std::array<int,2>{x,y},std::array<int,2>{x+n*(1-2*!(i%2))*(i<2),
                                                                                   y+n*(1-2*!(i%2))*!(i<2)}});
                if (square.colour!=pCol::NONE){
                    break;
                }
            }
        }
    }

    void kingCalc(int x, int y, const std::array<std::array<Piece,8>,8> &boardArr){
        Piece king = boardArr[x][y];
        for (int modX=-1; modX<=1; modX++){
            for (int modY=-1; modY<=1; modY++){
                if (x+modX>7 || y+modY>7 || x+modX<0 || y+modY<0){
                    continue;
                }

                if (boardArr[x+modX][y+modY].colour==king.colour){
                    continue;
                }

                if (!isposCheck(x+modX,y+modY,boardArr,king)){
                    moves.push_back(Move{king,std::array<int,2>{x,y},std::array<int,2>{x+modX,y+modY},mType::NORMAL});
                }
            }
        }

        if (king.moved[0] || isposCheck(x,y,boardArr,king)){
            return;
        }
        for (int i=-1; i<2; i+=2){
            if (boardArr[static_cast<int>(3.5+3.5*i)][y].moved[0]){
                continue;
            }
            if (isposCheck(x+1*i,y,boardArr,king) || isposCheck(x+2*i,y,boardArr,king)){
                continue;
            }
            if (boardArr[x+1*i][y]!=nullPiece() || boardArr[x+2*i][y]!=nullPiece()){
                continue;
            }
            moves.push_back(Move{king,std::array<int,2>{x,y},std::array<int,2>{x+i*2,y},mType::CASTLE});
        }
    }

    bool isposCheck(int x, int y, const std::array<std::array<Piece,8>,8> &boardArr, Piece king){
        if (checkFinder::pawnhandle(boardArr, king.colour, std::array<int,2>{x,y}).size()>0){
            return true;
        }
        if (checkFinder::knighthandle(boardArr, king.colour, std::array<int,2>{x,y}).size()>0){
            return true;
        }
        checkFinder::checkfindret bishops = checkFinder::bishophandle(boardArr, king.colour, std::array<int,2>{x,y});
        if (bishops.down2right.check || bishops.up2left.check || bishops.left2down.check || bishops.right2up.check){
            return true;
        }
        checkFinder::checkfindret rooks = checkFinder::rookhandle(boardArr, king.colour, std::array<int,2>{x,y});
        if (rooks.down2right.check || rooks.up2left.check || rooks.left2down.check || rooks.right2up.check){
            return true;
        }
        return false;
    }
};

namespace checkFinder{
    void manageChecks(const std::array<std::array<Piece,8>,8> &boardArr, std::vector<Move> &moves, pCol turn){
        int kx = -1;
        int ky = -1;
        for (int n1=0; n1<8; n1++){
            for (int n2=0; n2<8; n2++){
                if (boardArr[n1][n2].type == pType::KING && boardArr[n1][n2].colour == turn){
                    kx = n1;
                    ky = n2;
                    break;
                }
            }
            if (kx>-1 && ky>-1){
                break;
            }
        }

        movePopper(moves,pawnhandle(boardArr, turn, {kx,ky}));
        movePopper(moves,knighthandle(boardArr, turn, {kx,ky}));
        movePopper(moves,bishophandle(boardArr, turn, {kx,ky}));
        movePopper(moves,rookhandle(boardArr, turn, {kx,ky}));
    }

    void movePopper(std::vector<Move> &moves, std::vector<std::array<int,2>> checkers){
        if (checkers.size()==0){
            return;
        }
        std::vector<int> poppedMoves;
        for (Move &move : moves){
            if (move.piece.type == pType::KING){
                continue;
            }
            if (checkers.size()==1 && move.endpos==checkers[0]){
                continue;
            }
            poppedMoves.push_back(std::distance(moves.begin(),std::find(moves.begin(),moves.end(),move)));
        }
        if (poppedMoves.size()==0){
            return;
        }
        std::reverse(poppedMoves.begin(),poppedMoves.end());
        for (int n : poppedMoves){
            moves.erase(moves.begin()+n);
        }
    }

    void movePopper(std::vector<Move> &moves, checkfindret results){
        std::array<subcheckret*,4> resArr = {&results.up2left,&results.right2up,&results.down2right,&results.left2down};
        for (subcheckret* &res : resArr){
            if (res->pin || res->check){
                std::vector<int> poppedMoves;

                for (Move &move: moves){
                    if (res->pin){
                        if (move.startpos!=res->pinnpos){
                            continue;
                        } else if (listContains(res->between, move.endpos)){
                            continue;
                        }
                    }
                    if (res->check){
                        if (move.piece.type==pType::KING){
                            continue;
                        } else if (listContains(res->between, move.endpos)){
                            continue;
                        }
                    }
                    poppedMoves.push_back(std::distance(moves.begin(),std::find(moves.begin(),moves.end(),move)));
                }

                std::reverse(poppedMoves.begin(),poppedMoves.end());
                for (int n : poppedMoves){
                    moves.erase(moves.begin()+n);
                }
            }
        }
    }

    std::vector<std::array<int,2>> pawnhandle(const std::array<std::array<Piece,8>,8> &boardArr, pCol turn, std::array<int,2> kingpos){
        std::vector<std::array<int,2>> pawns;
        if (kingpos[1]==static_cast<int>(static_cast<int>(turn)*(-3.5)+3.5)){
            return pawns;
        }
        if (kingpos[0]<7){
            if (boardArr[kingpos[0]+1][kingpos[1]-static_cast<int>(turn)].type == pType::PAWN &&
                boardArr[kingpos[0]+1][kingpos[1]-static_cast<int>(turn)].colour == static_cast<pCol>(static_cast<int>(turn)*(-1))){
                    pawns.push_back(std::array<int,2> {kingpos[0]+1,kingpos[1]-static_cast<int>(turn)});
            }
        }
        if (kingpos[0]>0){
            if (boardArr[kingpos[0]-1][kingpos[1]-static_cast<int>(turn)].type == pType::PAWN &&
                boardArr[kingpos[0]-1][kingpos[1]-static_cast<int>(turn)].colour == static_cast<pCol>(static_cast<int>(turn)*(-1))){
                    pawns.push_back(std::array<int,2> {kingpos[0]-1,kingpos[1]-static_cast<int>(turn)});
            }
        }
        return pawns;
    }

    std::vector<std::array<int,2>> knighthandle(const std::array<std::array<Piece,8>,8> &boardArr, pCol turn, std::array<int,2> kingpos){
        std::vector<std::array<int,2>> knights;
        for (int n=0; n<4; n++){

            if (kingpos[0]*!(n%2)+kingpos[1]*(n%2)-2+4*static_cast<int>(n/2)>7 || kingpos[0]*!(n%2)+kingpos[1]*(n%2)-2+4*static_cast<int>(n/2)<0){
                continue;
            }

            for (int i=-1; i<=1; i+=2){

                if (kingpos[0]*(n%2)+kingpos[1]*!(n%2)+i>7 || kingpos[0]*(n%2)+kingpos[1]*!(n%2)+i<0){
                    continue;
                }

                if (boardArr[kingpos[0]+!(n%2)*(-2+4*static_cast<int>(n/2))+(n%2)*i][kingpos[1]+(n%2)*(-2+4*static_cast<int>(n/2))+!(n%2)*i].colour!=static_cast<pCol>(static_cast<int>(turn)*(-1))
                    || boardArr[kingpos[0]+!(n%2)*(-2+4*static_cast<int>(n/2))+(n%2)*i][kingpos[1]+(n%2)*(-2+4*static_cast<int>(n/2))+!(n%2)*i].type!=pType::KNIGHT){
                    continue;
                }
                
                knights.push_back(std::array<int,2>{kingpos[0]+!(n%2)*(-2+4*static_cast<int>(n/2))+(n%2)*i,kingpos[1]+(n%2)*(-2+4*static_cast<int>(n/2))+!(n%2)*i});
            }
        }
        return knights;
    }

    checkfindret bishophandle(const std::array<std::array<Piece,8>,8> &boardArr, pCol turn, std::array<int,2> kingpos){
        checkfindret results;
        std::array<subcheckret*,4> resArr = {&results.up2left,&results.right2up,&results.down2right,&results.left2down};
        int mod1;
        int mod2;
        bool check;
        bool pin;
        bool pinmode;
        std::vector<std::array<int,2>> between;
        for (int n=0; n<4; n++){
            if (n==0 || n==1){
                mod1=-1;
            } else {
                mod1=1;
            }
            if (n==1 || n==2){
                mod2=1;
            } else {
                mod2=-1;
            }
            check = false;
            pin = false;
            std::array<int,2> pinnpos;
            pinmode = false;
            between.clear();
            for (int i=1; i<=std::min((-1*mod1)*kingpos[0]+mod1*3.5+3.5,(-1*mod2)*kingpos[1]+mod2*3.5+3.5);i++){
                if (boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].colour==turn && boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].type!=pType::KING){
                    if (pinmode){
                        between.clear();
                        break;
                    } else {
                        pinmode = true;
                        pinnpos = {kingpos[0]+mod1*i,kingpos[1]+mod2*i};
                    }
                }
                between.push_back({kingpos[0]+mod1*i,kingpos[1]+mod2*i});
                if (static_cast<int>(boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].colour)==static_cast<int>(turn)*(-1)){
                    if (boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].type==pType::BISHOP || boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].type==pType::QUEEN){
                        if (pinmode){
                            pin = true;
                        } else {
                            check=true;
                        }
                        break;
                    }
                }
            }
            resArr[n]->check=check;
            resArr[n]->pin=pin;
            if (pin || check){
                resArr[n]->between=between;
                if (pin){
                    resArr[n]->pinnpos=pinnpos;
                }
            }
        }
        return results;
    }

    checkfindret rookhandle(const std::array<std::array<Piece,8>,8> &boardArr, pCol turn, std::array<int,2> kingpos){
        checkfindret results;
        std::array<subcheckret*,4> resArr = {&results.up2left,&results.right2up,&results.down2right,&results.left2down};
        int mod1;
        int mod2;
        bool check;
        bool pin;
        bool pinmode;
        std::vector<std::array<int,2>> between;
        for (int n=0; n<4; n++){
            if (n%2){
                mod1=0;
                if (n==1){
                    mod2=1;
                } else {
                    mod2=-1;
                }
            } else {
                mod2=0;
                if (n==2){
                    mod1=1;
                } else {
                    mod1=-1;
                }
            }
            check = false;
            pin = false;
            std::array<int,2> pinnpos;
            pinmode = false;
            between.clear();
            for (int i=1; i<= std::abs(mod1)*((-1*mod1)*kingpos[0]+mod1*3.5+3.5) + std::abs(mod2)*((-1*mod2)*kingpos[1]+mod2*3.5+3.5); i++){
                if (boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].colour==turn && boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].type!=pType::KING){
                    if (pinmode){
                        between.clear();
                        break;
                    } else {
                        pinmode = true;
                        pinnpos = {kingpos[0]+mod1*i,kingpos[1]+mod2*i};
                    }
                }
                between.push_back({kingpos[0]+mod1*i,kingpos[1]+mod2*i});
                if (static_cast<int>(boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].colour)==static_cast<int>(turn)*(-1)){
                    if (boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].type==pType::ROOK || boardArr[kingpos[0]+mod1*i][kingpos[1]+mod2*i].type==pType::QUEEN){
                        if (pinmode){
                            pin = true;
                        } else {
                            check=true;
                        }
                        break;
                    }
                }
            }
            resArr[n]->check=check;
            resArr[n]->pin=pin;
            if (pin || check){
                resArr[n]->between=between;
                if (pin){
                    resArr[n]->pinnpos=pinnpos;
                }
            }
        }
        return results;
    }
}

class Chess{
    public:
    int squareSize, squareBuffer, pieceSize;
    std::array<std::array<Piece,8>,8> boardArr;
    std::array<int,2> selectedPos;
    pCol turn;
    MoveCalculator mCalc;

    Chess(int squareSize, int squareBuffer, int pieceSize){
        this->squareSize = squareSize;
        this->squareBuffer = squareBuffer;
        this->pieceSize = pieceSize;
        selectedPos={-1,-1};
        turn = pCol::WHITE;
        std::array<Piece,8> emptyline;
        emptyline.fill(nullPiece());
        boardArr.fill(emptyline);
        std::array<pType,8> backRank = {pType::ROOK, pType::KNIGHT, pType::BISHOP, pType::QUEEN, pType::KING, pType::BISHOP, pType::KNIGHT, pType::ROOK};
        for (int a=0; a<8; a++){
            for (int b=0; b<8; b++){
                pCol col;
                if (b<2){
                    col = pCol::BLACK;
                } else {
                    col = pCol::WHITE;
                }

                if (b==0 || b==7){
                    this->boardArr[a][b]=Piece{backRank[a],col};
                } else if (b==1 || b==6){
                    this->boardArr[a][b]=Piece{pType::PAWN,col};
                } else {
                    this->boardArr[a][b]=nullPiece();
                }
            }
        }
    }

    void update(Uint32 mButtons, float mouseX, float mouseY){

        mCalc.calculate(turn, boardArr);
        select(mButtons, mouseX, mouseY);

    }

    void draw(SDL_Renderer *renderer, TTF_TextEngine *textengine){
        SDL_SetRenderDrawColor(renderer, 127, 127, 127, 255);
        SDL_RenderClear(renderer);

        boardDraw(renderer, textengine);
        movesDraw(renderer, textengine);

        SDL_RenderPresent(renderer);
    }

    void boardDraw(SDL_Renderer *renderer, TTF_TextEngine *textengine){  

        const char* base_path = SDL_GetBasePath(); 
        std::string font_path = std::string(base_path) + "Arial.ttf";
        TTF_Font* font = TTF_OpenFont(font_path.c_str(), pieceSize);
        if (font == NULL){
            std::cout<<SDL_GetError();
        }

        for (int x = 0; x<8; x++){
            for (int y = 0; y<8; y++){
                renderRect(renderer,{static_cast<float>(squareBuffer + x*squareSize), static_cast<float>(squareBuffer + y*squareSize)},
                            {static_cast<float>(squareSize), static_cast<float>(squareSize)}, {255*((x+y+1)%2),255*((x+y+1)%2),255*((x+y+1)%2)},true);
                if (boardArr[x][y]==nullPiece()){
                    continue;
                }
                renderRect(renderer,{static_cast<float>(squareBuffer + (x)*squareSize + 0.5*(squareSize-pieceSize)), 
                                    static_cast<float>(squareBuffer + y*squareSize + 0.5*(squareSize-pieceSize))},
                            {static_cast<float>(pieceSize), static_cast<float>(pieceSize)}, getRGB(boardArr[x][y].colour),true);
                renderRect(renderer,{static_cast<float>(squareBuffer + (x)*squareSize + 0.5*(squareSize-pieceSize)), 
                                    static_cast<float>(squareBuffer + y*squareSize + 0.5*(squareSize-pieceSize))},
                            {static_cast<float>(pieceSize), static_cast<float>(pieceSize)}, 
                            getRGB(static_cast<pCol>(static_cast<int>(boardArr[x][y].colour)*(-1))),false);
                renderText(textengine,font,getLetter(boardArr[x][y].type), 
                            {static_cast<int>(squareBuffer + (x+0.5)*squareSize), static_cast<int>(squareBuffer + (y+0.5)*squareSize)},
                            getRGB(static_cast<pCol>(static_cast<int>(boardArr[x][y].colour)*(-1))));
            }
        }

        TTF_CloseFont(font);
    }

    void movesDraw(SDL_Renderer *renderer, TTF_TextEngine *engine){
        if (selectedPos == std::array<int,2>{-1,-1}){
            return;
        }

        const char* base_path = SDL_GetBasePath(); 
        std::string font_path = std::string(base_path) + "Arial.ttf";
        TTF_Font* font = TTF_OpenFont(font_path.c_str(), squareSize/2);
        if (font == NULL){
            std::cout<<SDL_GetError();
        }
        std::array<std::string,4> letters = {"N","B","R","Q"};

        renderCircle(renderer,squareBuffer+squareSize/2+squareSize*selectedPos[0],squareBuffer+squareSize/2+squareSize*selectedPos[1],
                     8, std::array<int,3>{255,0,0});

        for (Move move: mCalc.getMoves()){
            if (move.startpos != selectedPos){
                continue;
            }

            if (static_cast<int>(move.type)<3){
                renderCircle(renderer,squareBuffer+squareSize/2+squareSize*move.endpos[0],squareBuffer+squareSize/2+squareSize*move.endpos[1],
                            12, std::array<int,3>{0,255,0});
                continue;
            }
            renderText(engine, font, letters[static_cast<int>(move.type)-3],
                        std::array<int,2>{squareBuffer+squareSize/4+squareSize/2*!(static_cast<int>(move.type)%2)+squareSize*move.endpos[0],
                                          squareBuffer+squareSize/4+squareSize/2*(static_cast<int>(move.type)>4)+squareSize*move.endpos[1]},
                       std::array<int,3>{0,255,0});
        }

        TTF_CloseFont(font);
    }

    void select(Uint32 mButtons, float mouseX, float mouseY){
        if (!(mButtons & SDL_BUTTON_LEFT)){
            return;
        }

        if(mouseX<squareBuffer || mouseX>squareBuffer+8*squareSize || mouseY<squareBuffer || mouseY>squareBuffer+8*squareSize){
            selectedPos = {-1,-1};
            return;
        }

        for (Move move: mCalc.getMoves()){
            if (move.startpos != selectedPos){
                continue;
            }
            
            if (std::floor((mouseX-squareBuffer)/squareSize) == move.endpos[0] && std::floor((mouseY-squareBuffer)/squareSize) == move.endpos[1]){
                if (static_cast<int>(move.type)<3){    
                    moveProcess(move);
                    return;
                }

                if ( ((((static_cast<int>(mouseX)-squareBuffer)%squareSize<squareSize/2) && static_cast<int>(move.type)%2) || 
                      (((static_cast<int>(mouseX)-squareBuffer)%squareSize>=squareSize/2) && !(static_cast<int>(move.type)%2))) &&
                     ((((static_cast<int>(mouseY)-squareBuffer)%squareSize<squareSize/2) && !(static_cast<int>(move.type)>4)) || 
                      (((static_cast<int>(mouseY)-squareBuffer)%squareSize>=squareSize/2) && static_cast<int>(move.type)>4)) )
                    {
                    moveProcess(move);
                    return;
                    }
            }
        }

        if (boardArr[std::floor((mouseX-squareBuffer)/squareSize)][std::floor((mouseY-squareBuffer)/squareSize)].colour == turn){
            selectedPos = {static_cast<int>(std::floor((mouseX-squareBuffer)/squareSize)),
                        static_cast<int>(std::floor((mouseY-squareBuffer)/squareSize))};
            return;
        }

        selectedPos = {-1,-1};
    }

    void moveProcess(Move move){
        
        for (std::array<Piece,8> &col : boardArr){
            for (Piece &piece : col){
                if (piece.moved == std::array<bool,2>{true,false}){
                    piece.moved = std::array<bool,2>{true,true};
                }
            }
        }
        if (move.piece.moved == std::array<bool,2>{false,false}){
            move.piece.moved = std::array<bool,2>{true,false};
        }

        boardArr[move.startpos[0]][move.startpos[1]] = nullPiece();
        boardArr[move.endpos[0]][move.endpos[1]] = move.piece;
        switch (move.type){

            case mType::ENPASSANT:
                boardArr[move.endpos[0]][move.endpos[1]+static_cast<int>(move.piece.colour)] = nullPiece();
                break;
            case mType::PROMOTE_N:
                boardArr[move.endpos[0]][move.endpos[1]].type = pType::KNIGHT;
                break;
            case mType::PROMOTE_B:
                boardArr[move.endpos[0]][move.endpos[1]].type = pType::BISHOP;
                break;
            case mType::PROMOTE_R:
                boardArr[move.endpos[0]][move.endpos[1]].type = pType::ROOK;
                break;
            case mType::PROMOTE_Q:
                boardArr[move.endpos[0]][move.endpos[1]].type = pType::QUEEN;
                break;
            case mType::CASTLE:
                if (move.endpos[0]<move.startpos[0]){
                    boardArr[move.endpos[0]+1][move.endpos[1]]=boardArr[0][move.endpos[1]];
                    boardArr[0][move.endpos[1]] = nullPiece();
                } else {
                    boardArr[move.endpos[0]-1][move.endpos[1]]=boardArr[7][move.endpos[1]];
                    boardArr[7][move.endpos[1]] = nullPiece();
                }
                break;
            default:
                break;
        }

        turn = static_cast<pCol>( -1 * static_cast<int>(turn) );
        mCalc.reCalc();
    }
};

int main(int argc, char* argv[]){
    SDL_Window* window;                    // Declare a window pointer
    SDL_Renderer* renderer;
    TTF_TextEngine* textEngine;
    TTF_Init();
    bool done = false;
    SDL_Init(SDL_INIT_VIDEO);              // Initialize SDL3

    const bool *keys = SDL_GetKeyboardState(NULL);
    float mouseX;
    float mouseY;
    Uint32 mButtons;

    std::chrono::nanoseconds start;
    std::chrono::nanoseconds end;
    std::chrono::nanoseconds duration;
    std::chrono::nanoseconds frametime(16666667);

    int squareSize = 80;
    int squareBuffer = 20;
    int pieceSize = 50;

    window = SDL_CreateWindow("Chess", 8*squareSize + 2*squareBuffer, 8*squareSize + 2*squareBuffer, SDL_WINDOW_OPENGL);

    renderer = SDL_CreateRenderer(window,NULL);
    textEngine = TTF_CreateRendererTextEngine(renderer);

       if (window == NULL) {
        SDL_LogError(SDL_LOG_CATEGORY_ERROR, "Could not create window: %s\n", SDL_GetError());
        return 1;
    }

    Chess game(squareSize, squareBuffer, pieceSize);

    while (!done) {
        start = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now().time_since_epoch());

        SDL_Event event;

        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_EVENT_QUIT){
                done = true;
            }
        }
        if (keys[SDL_SCANCODE_ESCAPE]){
            done = true;
        }
        mButtons = SDL_GetMouseState(&mouseX, &mouseY); //returns bitmask, use 'bitwise and' (&) and bitmask for intended Mbutton to check if clicked

        game.update(mButtons, mouseX, mouseY);
        game.draw(renderer, textEngine);

        SDL_UpdateWindowSurface(window);

        end = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now().time_since_epoch());
        duration = end - start;
        if (frametime>duration){
            std::this_thread::sleep_for(frametime-duration);
        }
    }
    

    SDL_DestroyWindow(window);
    SDL_DestroyRenderer(renderer);
    TTF_DestroyRendererTextEngine(textEngine);


    SDL_Quit();
    return 0;
}