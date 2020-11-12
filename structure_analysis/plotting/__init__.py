#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 15:19:16 2019

@author: alexanderhammett

The package was originally created by Alexander Hammett. Under his permission
the package was altered to work with the data structure of this project. Aswell
some graphical modifications were made.
"""

from matplotlib.pyplot import close

from .plot_internal_forces import plot_internal_forces
from .plot_loads import plot_loads


def save_all_plots(model, displacements, internal_forces, title):
    for i in range(len(displacements)):
        plot_loads(model, i, title, save_plot=True)
        plot_internal_forces(model, displacements, internal_forces, i, 'Deformed Shape', title, show_extrema=False,
                             save_plot=True)
        plot_internal_forces(model, displacements, internal_forces, i, 'Displacement X', title, show_extrema=False,
                             save_plot=True)
        plot_internal_forces(model, displacements, internal_forces, i, 'Displacement Y', title, show_extrema=False,
                             save_plot=True)
        plot_internal_forces(model, displacements, internal_forces, i, 'Rotation Z', title, show_extrema=False,
                             save_plot=True)
        plot_internal_forces(model, displacements, internal_forces, i, 'Normal Force', title, show_extrema=False,
                             save_plot=True)
        plot_internal_forces(model, displacements, internal_forces, i, 'Shear Force', title, show_extrema=False,
                             save_plot=True)
        plot_internal_forces(model, displacements, internal_forces, i, 'Moment', title, show_extrema=False,
                             save_plot=True)

        close('all')

    return


def plot_all_internal_forces(model, displacements, internal_forces):
    for i in range(len(displacements)):
        plot_loads(model, i, '', save_plot=False)
        plot_internal_forces(model, displacements, internal_forces, i, 'Deformed Shape', '', show_extrema=False,
                             save_plot=False)
        plot_internal_forces(model, displacements, internal_forces, i, 'Normal Force', '', show_extrema=False,
                             save_plot=False)
        plot_internal_forces(model, displacements, internal_forces, i, 'Shear Force', '', show_extrema=False,
                             save_plot=False)
        plot_internal_forces(model, displacements, internal_forces, i, 'Moment', '', show_extrema=False,
                             save_plot=False)

    #        close('all')

    return
