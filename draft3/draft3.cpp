#include<SDL3/SDL.h>
#include<SDL3/SDL_main.h>
#include<SDL3_ttf/SDL_ttf.h>
#include<chrono>
#include<iostream>
#include<thread>
#include<vector>
#include<array>

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

class MoveCalculator{
    protected:

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

    std::vector<Move> &getMoves(){
        return moves;
    }

    void calculate(std::array<std::array<Piece,8>,8> &boardArr, pCol turn){
        if (calculated){
            return;
        }

        for (int x=0; x<8; x++){
            for (int y=0; y<8; y++){
                switch (boardArr[x][y].type){
                    case pType::NONE:
                        break;
                    case pType::PAWN:
                        //pawn calc function
                        break;
                    case pType::KNIGHT:
                        //knight calc function
                        break;
                    case pType::BISHOP:
                        //bishop calc function
                        break;
                    case pType::ROOK:
                        //rook calc function
                        break;
                    case pType::QUEEN:
                        //queen calc function
                        break;
                    case pType::KING:
                        //king calc function
                        break;
                }
            }
        }

        //check stuff

        calculated = true;
    }
};

class Chess{
    public:
    int squareSize, squareBuffer, pieceSize;
    std::array<std::array<Piece,8>,8> boardArr;
    std::array<int,2> selectedPos;
    pCol turn;
    MoveCalculator mCalc;
    std::vector<Move> moves;

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
        mCalc = MoveCalculator();
        moves = mCalc.getMoves();
    }

    void update(Uint32 mButtons, float mouseX, float mouseY){

        mCalc.calculate(boardArr,turn);
        select(mButtons, mouseX, mouseY);

    }

    void draw(SDL_Renderer *renderer, TTF_TextEngine *textengine, TTF_Font *font){
        SDL_SetRenderDrawColor(renderer, 127, 127, 127, 255);
        SDL_RenderClear(renderer);

        boardDraw(renderer, textengine, font);
        movesDraw(renderer);

        SDL_RenderPresent(renderer);
    }

    void boardDraw(SDL_Renderer *renderer, TTF_TextEngine *textengine, TTF_Font *font){  
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
    }

    void movesDraw(SDL_Renderer *renderer){
        if (selectedPos == std::array<int,2>{-1,-1}){
            return;
        }

        renderCircle(renderer,squareBuffer+squareSize/2+squareSize*selectedPos[0],squareBuffer+squareSize/2+squareSize*selectedPos[1],
                     8, std::array<int,3>{255,0,0});

        for (Move move: moves){
            if (move.startpos != selectedPos){
                continue;
            }

            renderCircle(renderer,squareBuffer+squareSize/2+squareSize*move.startpos[0],squareBuffer+squareSize/2+squareSize*move.startpos[1],
                         12, std::array<int,3>{0,255,0});
        }
    }

    void select(Uint32 mButtons, float mouseX, float mouseY){
        if (!(mButtons & SDL_BUTTON_LEFT)){
            return;
        }

        if(mouseX<squareBuffer || mouseX>squareBuffer+8*squareSize || mouseY<squareBuffer || mouseY>squareBuffer+8*squareSize){
            selectedPos = {-1,-1};
            return;
        }

        for (Move move: moves){
            if (move.startpos != selectedPos){
                continue;
            }
            //move stuff
        }

        if (boardArr[std::floor((mouseX-squareBuffer)/squareSize)][std::floor((mouseY-squareBuffer)/squareSize)].colour == turn){
            selectedPos = {static_cast<int>(std::floor((mouseX-squareBuffer)/squareSize)),
                        static_cast<int>(std::floor((mouseY-squareBuffer)/squareSize))};
        }
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

    const char* base_path = SDL_GetBasePath(); 
    std::string font_path = std::string(base_path) + "Arial.ttf";
    TTF_Font* font = TTF_OpenFont(font_path.c_str(), pieceSize);
    if (font == NULL){
        std::cout<<SDL_GetError();
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
        game.draw(renderer, textEngine, font);

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
    TTF_CloseFont(font);


    SDL_Quit();
    return 0;
}

