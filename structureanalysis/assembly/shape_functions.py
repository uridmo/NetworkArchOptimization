# -*- coding: utf-8 -*-
"""
Created on Tue May 14 07:09:34 2019

@author: umorf

The shape functions an their derivatives. They correspond to the actual 
displacement curve of a beam with infinte shear stiffness.
"""

def n1(x,L):
    return 1-x/L

def n2(x,L):
    return x/L

def n3(x,L):
    return 1-3*x**2/L**2+2*x**3/L**3
def n31(x,L):
    return -6*x/L**2+6*x**2/L**3

def n4(x,L):
    return x-2*x**2/L+x**3/L**2
def n41(x,L):
    return 1-4*x/L+3*x**2/L**2

def n5(x,L):
    return 3*x**2/L**2-2*x**3/L**3
def n51(x,L):
    return 6*x/L**2-6*x**2/L**3

def n6(x,L):
    return -x**2/L+x**3/L**2
def n61(x,L):
    return -2*x/L+3*x**2/L**2