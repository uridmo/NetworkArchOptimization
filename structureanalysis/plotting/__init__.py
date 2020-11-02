#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 15:19:16 2019

@author: alexanderhammett

The package was originally created by Alexander Hammett. Under his permission
the package was altered to work with the data structure of this project. Aswell
some graphical modifications were made.
"""

from .plot import plot
from .plotForces import plotForces
from matplotlib.pyplot import close

def save_all_plots(model,displacements,internal_forces,title):
    
    for i in range(len(displacements)):

        plotForces(model, i, title, savePlot=True)
        plot(model, displacements, internal_forces, i, 'Deformed Shape', title, showExtrema=False,savePlot=True)
        plot(model, displacements, internal_forces, i, 'Displacement X', title, showExtrema=False,savePlot=True)
        plot(model, displacements, internal_forces, i, 'Displacement Y', title, showExtrema=False,savePlot=True)
        plot(model, displacements, internal_forces, i, 'Rotation Z', title, showExtrema=False,savePlot=True)
        plot(model, displacements, internal_forces, i, 'Normal Force', title, showExtrema=False,savePlot=True)
        plot(model, displacements, internal_forces, i, 'Shear Force', title, showExtrema=False,savePlot=True)
        plot(model, displacements, internal_forces, i, 'Moment', title, showExtrema=False,savePlot=True)
        
        close('all')
        
    return

def plot_internal_forces(model,displacements,internal_forces):
    
    for i in range(len(displacements)):

        plotForces(model, i, '', savePlot=False)
        plot(model, displacements, internal_forces, i, 'Deformed Shape', '', showExtrema=False,savePlot=False)
        plot(model, displacements, internal_forces, i, 'Normal Force', '', showExtrema=False,savePlot=False)
        plot(model, displacements, internal_forces, i, 'Shear Force', '', showExtrema=False,savePlot=False)
        plot(model, displacements, internal_forces, i, 'Moment', '', showExtrema=False,savePlot=False)
        
#        close('all')
        
    return
