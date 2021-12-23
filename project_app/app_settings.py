#!/usr/bin/python
# -*- coding: utf-8 -*-
from project_app.solution_classes import FruitTypeInfo
from project_app.sad import Orchard


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


num_days = 30
gruszki = FruitTypeInfo(name="gruszki", quantity=742, planting_cost=85, base_price=[3]*num_days,
                        wholesale_price=[3]*num_days, demand=[2]*(num_days//3)+[4]*(num_days-num_days//3), min_market_sold=10,
                        multiplier=multiplier1)

jablka = FruitTypeInfo(name="jabłka", quantity=535, planting_cost=62, base_price=[3]*num_days,
                        wholesale_price=[3] * num_days, demand=[5]*(num_days//3)+[8]*(num_days//3)+[3]*(num_days-2*(num_days//3)), min_market_sold=12,
                        multiplier=multiplier1)

sliwki = FruitTypeInfo(name="sliwki", quantity=800, planting_cost=91, base_price=[5]*num_days,
                       wholesale_price=[4]*num_days, demand=[10]*num_days, min_market_sold=12,
                       multiplier=multiplier2)

wisnie = FruitTypeInfo(name="wisnie", quantity=1000, planting_cost=110, base_price=[7]*num_days,
                       wholesale_price=[5]*num_days, demand=[10]*num_days, min_market_sold=20,
                       multiplier=multiplier2)

orchard = Orchard(fruit_types=[wisnie, jablka, gruszki, sliwki], employee_cost=employee_cost,
                  warehouse_cost=warehouse_cost, max_daily_harvest=100, warehouse_capacity=40, num_days=num_days)

