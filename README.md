LWR Project Creator
=====
[![Build Status](https://travis-ci.org/kuka-isir/lwr_project_creator.svg?branch=master)](https://travis-ci.org/kuka-isir/lwr_project_creator)

This simple tool generates a controller for the Kuka LWR4+ at ISIR.

#### GUI
```bash
lwr_create_pkg
```
#### Console version
```bash
lwr_create_pkg --help
```
Example :
```bash
lwr_create_pkg rtt_lwr_sin_controller
# Use -c or --class_name SinController to override the class name.
```

> Maintainer: Antoine Hoarau <hoarau.robotics@gmail.com>
