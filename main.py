#!/usr/bin/python
# -*- coding: utf-8 -*-
from sad import Orchard, FruitTypeInfo, Solution, DaySolution

def main():
    num_days = 30
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

    orchard = Orchard([wisnie, jablka, gruszki, sliwki], employee_cost, warehouse_cost, 100, 40, num_days)

    initial_population = orchard.create_initial_population()
    txt_to_write = ""
    for el in initial_population:
        txt_to_write += str(el[1])
        txt_to_write += "\n"
        txt_to_write += str(el[0])
        txt_to_write += "\n\n"
        print(el[1])

    with open("rozwiazania.txt", "w") as f:
        f.write(txt_to_write)

    profit_lists = []
    
    # sol, profit, (num_draws, num_ok_draws), profit_list = orchard.simulated_annealing(T_start=1000, T_stop=1, iterations_in_temp=100,
    #                                                                       epsilon=4, iterations_epsilon=10, alpha=0.99,
    #                                                                       neighbour_type=1, initial_sol=2)
    # print("Solution: {}".format(sol))
    # print(profit)
    # print("ile procent losowanych rozwiązań spełnia ograniczenia:")
    # print(num_ok_draws/num_draws*100)

    for init_pop in range(11):
        sol, profit, (num_draws, num_ok_draws), profit_list = orchard.simulated_annealing(T_start=500, T_stop=1, iterations_in_temp=10, epsilon=2, iterations_epsilon=10,
                                                                alpha=0.99,
                                                                neighbour_type=1, initial_sol=init_pop)
        profit_lists.append(profit_list)


    return profit_lists

    sol, profit = orchard.genetic_algorithm(max_iter_no_progress=400, max_iter=3000, replacement_rate=0.4,
                                            mutation_proba=0.4)
    print(sol, profit)

main()
