# ros2_gps_publisher

To run it.

On your pc:
```
colcon build
ros2 run ros2_gps_publisher get_cohda_gps 
```

On Cohda:
```
socat SYSTEM:"gpspipe -r" UDP:172.16.1.1:5000
```