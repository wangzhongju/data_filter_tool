cmake_minimum_required(VERSION 3.5)
project(img_filter)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
set(SOURCE_FILES ./src/main.cpp)

# fing opencv
set(OpenCV_DIR "/home/goldenridge/opencv3/opencv-3.3.1/build")
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})
link_directories(${OpenCV_LIBRARY_DIRS})

#set(PCL_DIR /usr/share/pcl-1.8)
#find_package(PCL REQUIRED)
#include_directories(${PCL_INCLUDE_DIRS})
#link_directories(${PCL_LIBRARY_DIRS})
 
# Boost setting
find_package(Boost COMPONENTS program_options REQUIRED)
find_package(Boost COMPONENTS system ...)
include_directories(${Boost_INCLUDE_DIRS})
link_directories(${Boost_LIBRARY_DIRS})

# pcl setting
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

add_executable(${PROJECT_NAME} ${SOURCE_FILES})
target_link_libraries (${PROJECT_NAME} ${OpenCV_LIBS} ${PCL_LIBRARIES} ${Boost_LIBRARIES} gflags pthread)
