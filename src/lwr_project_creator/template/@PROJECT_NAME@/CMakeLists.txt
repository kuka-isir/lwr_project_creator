cmake_minimum_required(VERSION 2.8.3)
project(@PROJECT_NAME@)

find_package(catkin REQUIRED COMPONENTS
    rtt_ros
    cmake_modules
)

find_package(Eigen REQUIRED)
find_package(orocos_kdl REQUIRED)

include_directories(
    include
    ${catkin_INCLUDE_DIRS}
    ${Eigen_INCLUDE_DIRS}
    ${orocos_kdl_INCLUDE_DIRS}
    ${USE_OROCOS_INCLUDE_DIRS}
)

orocos_component(${PROJECT_NAME} src/${PROJECT_NAME}.cpp)
set_property(TARGET ${PROJECT_NAME} APPEND PROPERTY COMPILE_DEFINITIONS RTT_COMPONENT)

target_link_libraries(${PROJECT_NAME}
    ${catkin_LIBRARIES}
    ${USE_OROCOS_LIBRARIES}
    ${orocos_kdl_LIBRARIES}
)

file(GLOB headers include/${PROJECT_NAME}/*.h include/${PROJECT_NAME}/*.hpp )
orocos_install_headers( FILES ${headers} )
orocos_generate_package(INCLUDE_DIRS include)

install(DIRECTORY scripts/
 DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/scripts
 PATTERN ".svn" EXCLUDE)
 
install(DIRECTORY launch/
 DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
 PATTERN ".svn" EXCLUDE)

