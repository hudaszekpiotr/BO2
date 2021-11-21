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


    gruszki = FruitTypeInfo(name="gruszki", quantity=742, planting_cost=120, base_price=[5]*30,
                            wholesale_price=[3]*30, demand=[2]*10+[4]*20, min_market_sold=10,
                            multiplier=multiplier1)

    jablka = FruitTypeInfo(name="jabłka", quantity=535, planting_cost=100, base_price=[4]*30,
                            wholesale_price=[3] * 30, demand=[5]*10+[8]*10+[3]*10, min_market_sold=12,
                            multiplier=multiplier1)

    sliwki = FruitTypeInfo(name="sliwki", quantity=800, planting_cost=140, base_price=[6]*30,
                           wholesale_price=[4]*30, demand=[2]*30, min_market_sold=12,
                           multiplier=multiplier2)

    wisnie = FruitTypeInfo(name="wisnie", quantity=1000, planting_cost=130, base_price=[4]*30,
                           wholesale_price=[1]*30, demand=[3]*30, min_market_sold=20,
                           multiplier=multiplier2)

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

    orchard = Orchard([wisnie, jablka, gruszki, sliwki], employee_cost, warehouse_cost, 100, 40)

    #initial_population = orchard.create_initial_population()
    # for el in initial_population:
    #     print(el[1])
    #     print(el[0])
    #     print("\n\n")
    #
    # for el in initial_population:
    #     print(el[1])
    # print(len(initial_population))


    sol, profit = orchard.find_solution(T_start=1000, T_stop=20, iterations_in_temp=20, epsilon=2, iterations_epsilon=10, alpha = 0.99, neighbour_type = 1, initial_sol = 2)
    print(sol, profit)


main()