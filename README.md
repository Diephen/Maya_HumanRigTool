# Maya_HumanRigTool
A automation scrit for rigging in maya

*Maya version: 2018
*Python version: 2.7.9


This is a WIP maya tool for easier rigging process in Maya. 
The goal is to set up a production rig with advanced features for better animation contorl, and convert it to a game charater rig with Unreal's character rig convention. 

Productino Rig Features:
The production rig is generated following the [Advanced Rigging Toturial](https://www.youtube.com/watch?v=MV4XRgmTynY&list=PL8hZ6hQCGHMXKqaX9Og4Ow52jsU_Y5veH&index=1). 

[Finished]
- IK/FK switch and match for arms and legs 
- Leg IK: dual contorl with no-flip (Auto) Knee and pole-vector (Manual) knee 
- Arm IK: hybrid contorl with FK anf IK forarm 
- Foot Contorl: smart foot roll, tilt, toe spin, toe wiggle, foot tilt
- Setting for Leg and Arm orient space


[TODO]
- Arm twist 
- Proper hand rig 
- Controller presets, ability to edit controller position/rotation or change to different contoller presets after initial setup
- Controller Mirror edit, animate 
- Convert to game rig (1 to 1 map with only the result joint from production rig)
- Map skin weight 
- Retarget animation from production rig to game rig 


 
