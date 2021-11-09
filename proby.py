#!/usr/bin/python
# -*- coding: utf-8 -*-
from main import FruitTypeInfo
harvested = [2,4,6,2,5,6,2]


def multiplier1(k):
    if k < 30:
        return 1.5
    if k < 50:
        return 1.2
    if k < 80:
        return 1.1
    if k <= 100:
        return 1


def multiplier2(k):
    if k < 30:
        return 1.2
    if k < 50:
        return 1.1
    if k < 80:
        return 1.1
    if k <= 100:
        return 1
gruszki = FruitTypeInfo("gruszki", 100, [0]*30, [0]*30, [2]*30, multiplier1)
jablka = FruitTypeInfo("jabłka", 100, [0]*30, [0]*30, [2]*30, multiplier2)

fruits = [gruszki, jablka]
for f in fruits:
    print(f.name)
