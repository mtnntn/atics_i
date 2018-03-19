# Advanced Topics In Computer Science - First Module Assignment
This repository maintains the code for the first module assignment of the Advanced Topics In Computer Science course held at the University of Rome "Roma Tre".

## Environment Requirements
There are 2 way to run the code: using a docker container, use a Conda Environment.

For the first solution please refer to the repository https://github.com/floydhub/dl-docker and follow the step in order to install the Environment in which deploy and run the code.

The second alternative is based on a Conda Environment (https://www.anaconda.com/).
There are two conda environment available:
  
  - `environments/dl_gpu_py35.py` : this Environment contains Tensorflow with GPU support and Keras. In order to execute the code with this Environment is necessary that you've also installed the NVIDIA drivers, Cuda, set all the Environment variables (PATH and LD_LIBRARY_PATH) and correctly followed all the steps specified on the Tensorflow and Keras installation instructions. For details see https://www.tensorflow.org/install/install_linux and https://keras.io/#installation .

  - `environments/dl_cpu_py35.py` : this environment contains Tensorflow without GPU support and therefore the code executed in this environment will not be enhanced by the GPU.
  This lack in performance allow a simpler configuration: you have only to import the environment and activate it.

## Project: 1	- Deep Learning for truth discovery

- Implement using python/Keras the following approaches for truth inference using Neural Networks:

	- the approach proposed by Marshall, Argueta, and Wang in https://www3.nd.edu/~sslab/pdf/mass17.pdf
	
	- the approach proposed by Li, Qin, Ren, and Liu in http://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8195344

- Train the two models using several standard datasets commonly used for evaluation of truth discovery algorithms

- Compare them to the baseline methods available in python at: https://github.com/MengtingWan/KDEm

### Marshall, Argueta, and	Wang approach
#### Summary
#### Repository structure

### Li, Qin, Ren, and Liu approach
#### Summary
#### Repository structure

### Extract datasets for evaluation
- Details

### Compare the approaches with the baseline methods
#### Repository Structure
