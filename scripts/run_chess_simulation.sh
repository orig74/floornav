#!/bin/bash
pkill -9 -f camera_sim.py
pkill -9 -f chess_board_nav.py
pkill -9 -f wx3dplot.py
SRC_DIR=../src
python ${SRC_DIR}/camera_sim.py &
python ${SRC_DIR}/chess_board_nav.py &
python ${SRC_DIR}/wx3dplot.py & 
