@PROJECT_NAME@
============

# Launch in Simulation

```bash
# Start Gazebo simulation
roslaunch rtt_lwr_gazebo lwr_gazebo.launch
# Start your controller in simulation
roslaunch @PROJECT_NAME@ run.launch sim:=true
```
# Launch on Hardware

```bash
# Start RTnet connection
rosrun lwr_scrits rtnet start
# Start your controller
roslaunch @PROJECT_NAME@ run.launch
```
