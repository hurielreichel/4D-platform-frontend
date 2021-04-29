# 4D-platform-frontend
This repository holds the many tools available for operating with different files in STDL's 4D platform. 

## Overview
This is a toolbox for large scale 3D models manipulation, processing, conversion and geographical registration. It is mainly designed to offer solutions suitable for models that can weight hundreds of gigabytes and that are used in the domain of environment survey and land registering. It was initially developed to offer the required tools needed to allow massive data processing and preparation for the [eratosthene framework](https://github.com/swiss-territorial-data-lab/eratosthene-framework), the Swiss Territorial Data Lab 4D Platform.

The 4D Framework uses a common and very simple [format](https://github.com/swiss-territorial-data-lab/eratosthene-framework/blob/master/FORMAT.md) for all the implemented tools. This format offers a simple way of storing massive amount of graphical primitives. This allows the platform to manipulate all sort of 3D models, from large scale point-based models to more refined vector models. The main aim of this toolbox is to simplify front-end procedures to allow easy data injections in the platform.

To this point it's complementary to to the [dalai-suite toolbox](https://github.com/nils-hamel/dalai-suite), but it's intended to replace it, maintaining everything on python language.

## 4D-platform-frontend

Each implemented tool comes with its own documentation that explains the implemented solution and examples of usage and results :

### Models format conversion

* [Geotiff colouring based on Z value](src/z-from-geotiff)

* [LAS to UV3](src/las-to-uv3)

* [RGB Geotiff to UV3](src/rbg-from-geotiff)

* [RGB Geotiff with elevation from DEM to UV3](src/rgb-z-uv3)

* [Mesh to UV3](src/mesh-to-uv3)

A detailed documentation of specific file formats used by the tools of this suite can be found of the format page.

## Copyright and License

4D-platform-frontend - Huriel Reichel, Nils Hamel
Copyright (c) 2021 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.

## Dependencies

Python 3.8.5 or superior. Older versions were not tested.

the following libraries may be installed either by pip or conda. 

* laspy 1.7.0

* matplotlib 3.3.3

* GDAL 3.2.0 (In linux, it's recommended to install gdal through the terminal >> sudo apt-get install gdal-bin)

* Numpy 1.19.4

* Pymesh 2.0.3

Conda may properly install PyMesh, but it's not recomended. In https://pymesh.readthedocs.io/en/latest/installation.html you'll find deeper information on how to install PyMesh . The easiest way is probably through docker, as explained below:

* Have the input file to be converted in the same folder as the mesh-to-uv3.py script and navigate to this folder with cd in you computer's terminal.

```
$ cd /path/to/code/and/input_file/
```

* Once you're on the proper folder, run the docker image from PyMesh

```
/path/to/code/and/input_file/$ docker run -it --rm -v `pwd`:/models pymesh/pymesh bash
```
or maybe the following if in linux:

```
/path/to/code/and/input_file/$ sudo docker run -it --rm -v `pwd`:/models pymesh/pymesh bash
```

* Once rooted, do:

```
root@e53224f5136b:~# cd /models
```

And finally run the code as explained above.
```


