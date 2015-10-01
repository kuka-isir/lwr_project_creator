@PROJECT_NAME@
============

# Launch in Simulation

```bash
# Start Gazebo + your controller
roslaunch @PROJECT_NAME@ run.launch sim:=true
```

# Launch on Hardware

```bash
# Start RTnet connection
rosrun lwr_scrits rtnet start
# Start your controller
roslaunch @PROJECT_NAME@ run.launch
```
