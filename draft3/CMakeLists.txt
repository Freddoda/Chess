cmake_minimum_required(VERSION 3.10.0)

project(Chess LANGUAGES CXX)

add_executable(Chess draft3.cpp)

find_package(SDL3 REQUIRED)
target_link_libraries(Chess PRIVATE SDL3::SDL3)
find_package(SDL3_ttf REQUIRED)
target_link_libraries(Chess PRIVATE SDL3_ttf::SDL3_ttf)

configure_file(${CMAKE_SOURCE_DIR}/Arial.ttf ${CMAKE_CURRENT_BINARY_DIR} COPYONLY)

include(CTest)
enable_testing()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)