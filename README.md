# floornav
platform for 3d navigation above floor 

# requirements
you need to have a python version > 2.7
and these additional libraries:

python-zmq,python-opencv,python-numpy,python-scipy

after clonning the repository run:
> cd scripts
> ./run_chess_simulation.sh 

on the camera simulator window use the keys:
a q -> pitch control
w s -> roll control
e d -> yaw control
r f -> translate x
t g -> translate y
y h -> translate z

on the 3d plot you can see:
black "L" represents the estimated camera position
crayon "L" represents the simulated camera position



