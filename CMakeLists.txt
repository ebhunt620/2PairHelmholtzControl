cmake_minimum_required(VERSION 2.8.3)
project(DAQ_update)

add_definitions("-std=c++11 -Werror=return-type")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")

include_directories(/usr/local/include/libusb/ /usr/local/include/hidapi/ /opt/ros/kinetic/include/opencv-3.2.0-dev/)
#include_directories(mcc-libusb include /opt/ros/kinetic/include/opencv-3.2.0-dev/)
file(GLOB C_FILES ~/Linux_Drivers/USB/mcc-libusb/*.c)

add_executable(${PROJECT_NAME} ${PROJECT_NAME}.cpp)
#target_link_libraries(${PROJECT_NAME} ${CMAKE_THREAD_LIBS_INIT} /usr/local/lib/libhidapi-libusb.so /usr/local/lib/libmccusb.so /usr/local/lib/libhidapi-hidraw.so)
target_link_libraries(${PROJECT_NAME} /usr/local/lib/libhidapi-libusb.so /usr/local/lib/libmccusb.so /usr/local/lib/libhidapi-hidraw.so)
