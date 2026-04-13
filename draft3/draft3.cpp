#include<SDL3/SDL.h>
#include<SDL3/SDL_main.h>
#include<SDL3_ttf/SDL_ttf.h>
#include<chrono>
#include<iostream>
#include<thread>

class Chess{
    public:
        int squareSize, squareBuffer;

        Chess(int squareSize, int squareBuffer){
            this->squareSize = squareSize;
            this->squareSize = squareBuffer;
        }

        void update(){

        }

        void draw(){

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
    int* mouseX = new int(0);
    int* mouseY = new int(0);

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

        game.update();
        game.draw();

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
    delete mouseX;
    delete mouseY;


    SDL_Quit();
    return 0;
}

