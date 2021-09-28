#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools.py - some helpful functions.

Last Modified: 2021.05.24

Copyright(C) 2021 Shaokun Xie <https://xshaokun.com>
Licensed under the MIT License, see LICENSE file for details
"""

import numpy as np


def nearest(arr,target):
    """get the index of nearest value

    Given a number, find out the index of the nearest element in an 1D array.

    Args:
        arr: array for searching
        target: target number
    """

    index = np.abs(arr-target).argmin()
    
    return index