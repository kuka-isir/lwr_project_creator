cmake_minimum_required(VERSION 2.8.3)
project(lwr_project_creator)
find_package(catkin REQUIRED)
catkin_python_setup()
catkin_package()

install(DIRECTORY src/lwr_project_creator/template 
    DESTINATION ${CATKIN_PACKAGE_PYTHON_DESTINATION})