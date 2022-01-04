#!/usr/bin/python
# -*- coding: utf-8 -*-
from copy import deepcopy
from project_app.model_limits import check_fruit_limits, check_harvest_limits, \
    check_warehouse_limits, check_if_warehouse_sold, \
    check_if_today_amount_correct, check_if_non_negative, check_if_sold_market_less_than_demand
from project_app.solution_classes import FruitTypeInfo
import numpy as np
from typing import List


class DaySolution:
    def __init__(self, harvested, sold_market, sold_wholesale, warehouse):
        self.harvested = harvested  # lista zebranych owoców danego dnia (każdy indeks to inny typ owocu)
        self.sold_market = sold_market  # lista owoców sprzedanych na targu (każdy indeks to inny typ owocu)
        self.sold_wholesale = sold_wholesale # lista owoców sprzedanych w skupie (każdy indeks to inny typ owocu)
        self.warehouse = warehouse


class Solution:
    def __init__(self, days):
        self.days = days

    def __str__(self):
        txt = ""
        for i, day in enumerate(self.days):
            txt += f"Day {i + 1}\nharvested: {day.harvested}\nsold_market: {day.sold_market}\n" \
                   f"sold_wholesale: {day.sold_wholesale}\nwarehouse: {day.warehouse}\n\n"
        txt += "\n\n\n\n"
        return txt


def calculate_objective_fun(solution: Solution, fruit_types: List[FruitTypeInfo]):
    profit = 0

    for day_id, day in enumerate(solution.days):
        for fruit_type_id in range(len(fruit_types)):
            fruit = fruit_types[fruit_type_id]
            demand = fruit.demand[day_id]
            sold_market = day.sold_market[fruit_type_id]
            market_price = fruit.base_price[day_id] * fruit.check_multiplier(demand=demand, sold=sold_market)
            sold_wholesale = day.sold_wholesale[fruit_type_id]
            wholesale_price = fruit.wholesale_price[day_id]

            profit += sold_market * market_price + sold_wholesale * wholesale_price

        cost = employee_cost(sum(day.harvested)) + warehouse_cost(sum(day.warehouse))
        profit -= cost

    for fruit in fruit_types:
        profit -= fruit.planting_cost

    return profit


def warehouse_cost(kilograms):
    if 0 <= kilograms <= 1:
        cost = 1
    elif 1 < kilograms <= 2:
        cost = 2
    else:
        cost = 3
    return cost


def multiplier(k):
    if k < 30:
        return 1.5
    if k < 50:
        return 1.2
    if k < 80:
        return 1.1
    if k <= 100:
        return 1


def employee_cost(kilograms):
    if 0 <= kilograms <= 1:
        cost = 1.5
    elif 1 < kilograms <= 2:
        cost = 2
    else:
        cost = 3
    return cost


day_solutions = [# Nic nie zbieramy
                 DaySolution([0,0],[0,0],[0,0],[0,0]),
                 # Zbieramy 1 kilogram jednego typu
                 DaySolution([0,1],[0,1],[0,0],[0,0]),
                 DaySolution([0,1],[0,0],[0,1],[0,0]),
                 DaySolution([0,1],[0,0],[0,0],[0,1]),
                 DaySolution([1,0],[1,0],[0,0],[0,0]),
                 DaySolution([1,0],[0,0],[1,0],[0,0]),
                 DaySolution([1,0],[0,0],[0,0],[1,0]),
                # Zbieramy po jednym kilogramie z kązdego typu
                 DaySolution([1,1],[1,1],[0,0],[0,0]),
                 DaySolution([1,1],[1,0],[0,1],[0,0]),
                 DaySolution([1,1],[1,0],[0,0],[0,1]),
                 DaySolution([1,1],[0,1],[1,0],[0,0]),
                 DaySolution([1,1],[0,0],[1,1],[0,0]),
                 DaySolution([1,1],[0,0],[1,0],[0,1]),
                 DaySolution([1,1],[0,1],[0,0],[1,0]),
                 DaySolution([1,1],[0,0],[0,1],[1,0]),
                # Zbieramy 2 kilogramy z jednego typu
                DaySolution([2,0],[2,0],[0,0],[0,0]),
                DaySolution([2,0],[0,0],[2,0],[0,0]),
                DaySolution([2,0],[1,0],[1,0],[0,0]),
                DaySolution([2,0],[1,0],[0,0],[1,0]),
                DaySolution([2,0],[0,0],[1,0],[1,0]),
                DaySolution([0,2],[0,2],[0,0],[0,0]),
                DaySolution([0,2],[0,0],[0,2],[0,0]),
                DaySolution([0,2],[0,1],[0,1],[0,0]),
                DaySolution([0,2],[0,1],[0,0],[0,1]),
                DaySolution([0,2],[0,0],[0,1],[0,1])
]

day_solutions2 = []
for sol in day_solutions:
    harvested = sol.harvested
    market = sol.sold_market
    wholesale = sol.sold_wholesale
    warehouse = sol.warehouse

    s1 = DaySolution(harvested, [market[0]+1, market[1]], wholesale, warehouse)
    s2 = DaySolution(harvested, [market[0], market[1]+1], wholesale, warehouse)
    s3 = DaySolution(harvested, market, [wholesale[0]+1, wholesale[1]], warehouse)
    s4 = DaySolution(harvested, market, [wholesale[0], wholesale[1]+1], warehouse)
    day_solutions2.append(s1)
    day_solutions2.append(s2)
    day_solutions2.append(s3)
    day_solutions2.append(s4)

day_solutions += day_solutions2

gruszki = FruitTypeInfo(name="gruszki", quantity=3, planting_cost=1.5, base_price=[2,1.5],
                        wholesale_price=[1,1], demand=[1,3], min_market_sold=1,
                        multiplier=multiplier)

jablka = FruitTypeInfo(name="jabłka", quantity=3, planting_cost=2, base_price=[2,3],
                        wholesale_price=[1,1.5], demand=[2,2], min_market_sold=12,
                        multiplier=multiplier)


def check_limits(solution:Solution):
    one = check_fruit_limits(solution, [gruszki, jablka])
    two = check_harvest_limits(solution, 2)
    # three = check_minimum_amount_sold(solution, self.fruit_types)
    four = check_warehouse_limits(solution, 1)
    five = check_if_warehouse_sold(solution)
    six = check_if_today_amount_correct(solution)
    seven = check_if_non_negative(solution)
    eight = check_if_sold_market_less_than_demand(solution, [gruszki, jablka])
    return one and two and four and five and six and seven and eight


def main():
    valid_solutions = 0
    best_solutions = []
    best_profit = -np.inf
    for day1_id in range(len(day_solutions)):
        for day2_id in range(len(day_solutions)):
            solution = Solution([deepcopy(day_solutions[day1_id]), deepcopy(day_solutions[day2_id])])
            if check_limits(solution):
                valid_solutions += 1
                profit = calculate_objective_fun(solution, [gruszki, jablka])
                if profit > best_profit:
                    best_profit = profit
                    best_solutions = [deepcopy(solution)]
                elif profit == best_profit:
                    best_solutions.append(deepcopy(solution))

    txt = ""
    for sol in best_solutions:
        txt += f"{sol}"
    txt += f"Zysk: {best_profit}\nPoprawne rozwiązania: {valid_solutions}\nIlość dziennych rozwiązań: {len(day_solutions)}"
    print(txt)
    return best_solutions, best_profit, valid_solutions

if __name__ == '__main__':
    main()