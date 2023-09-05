#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch the Taxi2 GUI"""

import multiprocessing

from itaxotools.hapsolutely import run

if __name__ == '__main__':
    multiprocessing.freeze_support()
    run()
