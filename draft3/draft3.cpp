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

enum class pCol {
    NONE=0,
    WHITE=1,
    BLACK=2
};

enum class pType {
    NONE=0,
    PAWN=1,
    KNIGHT=2,
    BISHOP=3,
    ROOK=4,
    QUEEN=5,
    KING=6
};

struct Piece {
    pType type;
    pCol colour;
    std::array<bool,2> moved = {false,false};
};

Piece nullPiece(){
    return Piece{pType::NONE, pCol::NONE};
}

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

class Chess{
    public:
    int squareSize, squareBuffer;
    std::array<std::array<Piece,8>,8> boardArr;

    Chess(int squareSize, int squareBuffer){
        this->squareSize = squareSize;
        this->squareBuffer = squareBuffer;
        //construct board array
    }

    void update(){

    }

    void draw(SDL_Renderer *renderer, TTF_TextEngine *textengine, TTF_Font *font){
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);

        boardDraw(renderer, textengine, font);

        SDL_RenderPresent(renderer);
    }

    void boardDraw(SDL_Renderer *renderer, TTF_TextEngine *textengine, TTF_Font *font){  
        for (int x = 0; x<8; x++){
            for (int y = 0; y<8; y++){
                renderRect(renderer,{static_cast<float>(squareBuffer + x*squareSize), static_cast<float>(squareBuffer + y*squareSize)},
                            {static_cast<float>(squareSize), static_cast<float>(squareSize)}, {255*((x+y+1)%2),255*((x+y+1)%2),255*((x+y+1)%2)},true);
                //draw pieces too
            }
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
    Uint32 buttons;

    std::chrono::nanoseconds start;
    std::chrono::nanoseconds end;
    std::chrono::nanoseconds duration;
    std::chrono::nanoseconds frametime(16666667);

    const char* base_path = SDL_GetBasePath(); 
    std::string font_path = std::string(base_path) + "Arial.ttf";
    TTF_Font* font = TTF_OpenFont(font_path.c_str(), 60);
    if (font == NULL){
        std::cout<<SDL_GetError();
    }

    int squareSize = 80;
    int squareBuffer = 20;

    window = SDL_CreateWindow("Chess", 8*squareSize + 2*squareBuffer, 8*squareSize + 2*squareBuffer, SDL_WINDOW_OPENGL);

    renderer = SDL_CreateRenderer(window,NULL);
    textEngine = TTF_CreateRendererTextEngine(renderer);

       if (window == NULL) {
        SDL_LogError(SDL_LOG_CATEGORY_ERROR, "Could not create window: %s\n", SDL_GetError());
        return 1;
    }

    Chess game(squareSize, squareBuffer);

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
        buttons = SDL_GetMouseState(&mouseX, &mouseY);

        game.update();
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

