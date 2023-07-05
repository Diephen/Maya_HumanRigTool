# Maya_HumanRigTool
A automation script for rigging in maya

Maya version: 2018
Python version: 2.7.9


This is a util script for automate human rig setup in Maya. 
The goal is to set up a production rig with advanced features for better animation control, and convert it to a game charater rig with Unreal's character rig convention. 

Production Rig Features:
The production rig is generated following the [Advanced Rigging Toturial](https://www.youtube.com/watch?v=MV4XRgmTynY&list=PL8hZ6hQCGHMXKqaX9Og4Ow52jsU_Y5veH&index=1). 

[Finished]
- IK/FK switch for arms and legs 
- Leg IK: dual control with no-flip (Auto) Knee and pole-vector (Manual) knee 
- Arm IK: hybrid control with FK anf IK forearm 
- Foot Control: smart foot roll, tilt, toe spin, toe wiggle, foot tilt
- Settings for Leg and Arm orient space


[TODO]
- Setup Arm twist 
- Proper hand/finger rig 
- Controller presets, ability to edit controller position/rotation or change to different contoller presets after initial setup
- Controller Mirror edit, animate 
- Convert to game rig (1 to 1 map with only the result joint from production rig)
- Map skin weight 
- Retarget animation from production rig to game rig
- Change hardcoded joint list with interactive input

 
