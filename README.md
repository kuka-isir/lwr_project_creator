LWR Project Creator
=====

This simple tool generates an example project from a template.

## Install
The package is uploaded to pypi, to downloading/installing is made easy.
```bash
sudo -E pip install lwr_project-creator
```
## Upgrades
If you've already installed lwr_project-creator, please use this command to update it:
```bash
sudo -E pip install lwr_project-creator --upgrade
```

## Run the M3 CMake project generator
Using the  GUI :
```bash
lwr_create_pkg
```
or the console version :
```bash
lwr_create_pkg --help
```
Example :
```bash
lwr_create_pkg rtt_lwr_sin_controller SinController
```
### The generated files

* **mycontroller.cpp**: The source file that contains your component class (inherits from the M3Component class).
* **mycontroller.h**: The header file associated.
* **factory_proxy.cpp**: This file is used by the m3 system to instantiate your component.
* (OPTIONAL) **mycontroller.proto**: A protobuf file that can be used to communicate with your controller (using python for example). This is used in the m3 software.
* (OPTIONAL) **mycontroller.py**: The python interface to your controller
* (OPTIONAL) **controller_example.py**: An example on how to use the python interface

### The generated project

```bash
myproject
|-- src
|   `-- myproject
|       |-- mycomponent
|       |   |-- my_class.cpp
|       |   |-- my_class_factory.cpp
|       |   `-- CMakeLists.txt
|       `-- CMakeLists.txt
|-- include
|   `-- myproject
|       `-- mycomponent
|           `-- my_class.h
|-- proto
|   `-- myproject
|       `-- mycomponent
|           `-- my_class.proto
|-- python
|   `-- myproject
|       |-- mycomponent
|       |   |-- __init__.py
|       |   |-- my_class.py
|       |   `-- my_class_example.py
|       `-- __init__.py
|-- robot_config
|   |-- mycomponent
|   |   `-- my_class_v1.yml
|   `-- m3_config.yml
`-- CMakeLists.txt
```
## Compile your project
If you don't have the M3_CMAKE_MODULES var set (latest version of m3 software):
```
echo $M3_CMAKE_MODULES
```
Then,you might want to get some useful FindXXX.cmake (for M3 system, Yamlccp, protobuf etc):
```
cd /path/to/your/project
git clone https://github.com/ahoarau/meka-cmake-modules.git
```
Then you can compile your project safely:

```bash
cd /path/to/your/project
mkdir build
cd build
cmake .. -DCMAKE_CXX_FLAGS="-std=C++0x" -DCMAKE_BUILD_TYPE=Release
make
```


## Run your project ##
Let M3 knows there's an external path to check out (you should do that in all terminals you open):
```bash
source /path/to/your/project/setup.bash
```
Run the server as usual:
```bash
m3rt_server_run
```
Your component should be at the top of the available components lists (default name is controller_example_v1).

Vizualize the robot in rviz :
```bash
roslaunch meka_description m3ens_viz.launch
```
Add a robot model and change 'fixed frame' to 'T0'.
Now **enable** your component and see the robot moves:

```bash
# First load your project's environnement variables
source /path/to/your/project/setup.bash
cd /path/to/your/project/python/componentdir/mycontroller/
python mycontroller_example.py
```

Good luck !

Based on lwr_project_creator.py provided by Meka Robotics, LLC.

> Maintainer: Antoine Hoarau <hoarau.robotics@gmail.com>
