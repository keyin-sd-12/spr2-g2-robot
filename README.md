
# RoboMaster S1 Obstacle Course Project

## Project Overview

This project involves programming the DJI RoboMaster S1 to navigate an obstacle course, stopping at designated performance points (`A`–`H`) to perform specific tasks. The robot must respond to markers at certain posts, perform actions based on those markers, and reset at specified points. The program is designed to be flexible and adaptable, allowing for easy modifications to the course layout and tasks.

## Functionality Overview

The program is designed to navigate the RoboMaster S1 through a defined obstacle course with specific actions at each marker point. It utilizes a recursive approach to handle dynamic tasks efficiently.

### Key Function: `move_forward_to_point`

- **Purpose**: Guides the robot from one designated point to another on the course.
- **Recursive Behavior**:
  - On encountering a 'Person' (`P`) marker, the robot:
    1. **First Recursive Call**: Moves back to the starting point (`A`) using `move_forward_to_point`.
    2. **Second Recursive Call**: Returns to the original position where the marker was encountered, again using `move_forward_to_point`.
  - This recursive handling ensures the task of 'rescuing' is completed before continuing along the course.

### Course Navigation

1. **Start**: Begin at position (`A`).
2. **Move to End**: Navigate to position (`H`), handling markers (`F`, `D`, `P`) as they appear.
3. **Return Journey**: Once reaching position (`H`), return directly to the start (`A`), bypassing zigzag routes.

This approach enables the robot to adaptively manage its path, accommodating changes in the course's requirements and marker configurations.

## Input Data

The course layout and robot behavior are configured using three primary data structures: `DICT_STOPS`, `SET_RESETS`, and `SET_MARKERS`.

### `DICT_STOPS`

This dictionary defines the key stop points along the robot's path and the distances the robot must travel to reach each point. The distances are specified in centimeters.

```python
DICT_STOPS = {
    'name':     ['A', 'B0',   'B',   'C',   'D',   'E',   'F',   'G',    'H'],
    'distance': [  0,  576,   279,   661,   496,   412,   468,   438,    573]
}
```

- **Names**: The points along the course (`A` to `H`) where the robot performs actions.
- **Distances**: The distance in centimeters that the robot must travel to reach each subsequent point.

The robot navigates the course by sequentially moving through these distances, and upon reaching the end, it reverses the distances to return to the start.

### `SET_RESETS`

This set defines the points at which the robot can pause and reset its position. These points allow the robot to recalibrate and prepare for the next segment of the course.

```python
SET_RESETS = {'A', 'B', 'D', 'F', 'H'}
```

### `SET_MARKERS`

This set specifies the points where the robot looks for markers, which dictate actions such as shooting, skipping, or rescuing.

```python
SET_MARKERS = {'C', 'E', 'F', 'G'}
```

## How to Use

1. **Setup**: Ensure the RoboMaster S1 is positioned at the start point (`A`).
2. **Run the Program**: Execute the program to navigate the obstacle course.
3. **Modify the Course**: Update `DICT_STOPS`, `SET_RESETS`, and `SET_MARKERS` to customize the course layout and tasks.

## Customization

- **Adding Points**: Add new positions to `DICT_STOPS` with the corresponding task requirements.
- **Removing Points**: Remove existing positions from `DICT_STOPS` to simplify the course.
- **Changing Reset or Marker Points**: Modify `SET_RESETS` and `SET_MARKERS` to adjust where the robot can pause for repositioning and/or looking for markers

