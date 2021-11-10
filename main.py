#!/usr/bin/python
# -*- coding: utf-8 -*-
from sad import Orchard, FruitTypeInfo, Solution, DaySolution

def main():
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


    gruszki = FruitTypeInfo("gruszki", 100, [0]*30, [0]*30, [2]*30, 10, multiplier1)
    jablka = FruitTypeInfo("jabłka", 100, [0]*30, [0]*30, [2]*30, 12, multiplier2)

    def employee_cost(kilograms):
        if 0 <= kilograms <= 10:
            cost = 30
        elif 10 < kilograms <= 20:
            cost = 40
        elif 20 < kilograms <= 40:
            cost = 60
        elif 40 < kilograms <= 60:
            cost = 90
        elif 60 < kilograms <= 100:
            cost = 100
        else:
            cost = 200
        return cost

    def warehouse_cost(kilograms):
        if 0 <= kilograms <= 10:
            cost = 15
        elif 10 < kilograms <= 20:
            cost = 20
        elif 20 < kilograms <= 30:
            cost = 25
        else:
            cost = 30
        return cost

    orchard = Orchard([jablka, gruszki], employee_cost, warehouse_cost, 100, 40)


main()