#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Autor: Fadiga

from __future__ import (unicode_literals, absolute_import, division,
                        print_function)

import os
import sys
sys.path.append(os.path.abspath('../'))

from models import Store
from Common.fixture import AdminFixture


class FixtInit(AdminFixture):

    """docstring for FixtInit"""

    def __init__(self):
        super(AdminFixture, self).__init__()
        self.LIST_CREAT.append(Store(name=u"magasin N°1", stock_maxi=5000),)
