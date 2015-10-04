# floornav
platform for 3d navigation above floor 

# requirements
you need to have a python version > 2.7
and these additional libraries:

python-zmq,python-opencv,python-numpy,python-scipy

#running simulation
after clonning the repository run:
> cd scripts
> ./run_chess_simulation.sh 
<br/>
the simulation open 3 windows

#<h3>1. camera simulation window</h3>
![alt tag](https://raw.github.com/origanoni/floornav/master/images/camera_simulation.png)

on the camera simulator window use the keys:<br/>
a q -> pitch control<br/>
w s -> roll control<br/>
e d -> yaw control<br/>
r f -> translate x<br/>
t g -> translate y<br/>
y h -> translate z<br/>


#<h3>2. 3d plot window</h3>
![alt tag](https://raw.github.com/origanoni/floornav/master/images/plot3d.png)
on the 3d plot you can see:<br/>
black "L" represents the estimated camera position<br/>
crayon "L" represents the simulated camera position<br/>

#<h3>3. chessboard detect window<h3/>
will show marking when detected
![alt tag](https://raw.github.com/origanoni/floornav/master/images/camera_solver.png)



