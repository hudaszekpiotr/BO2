#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Callable


# postać rozwiązania aby dostać ile owoców sprzedanych 8 dnia typu 2 należy solution.days[8].sold[2]
class Solution:
    def __init__(self, fruit_types):
        self.days = [DaySolution(fruit_types)] * 30


# postać rozwiązania dla 1 dnia
class DaySolution:
    def __init__(self, fruit_types):
        self.harvested = [0] * fruit_types       # lista zebranych owoców danego dnia
        self.sold_market = [0] * fruit_types     # lista owoców sprzedanych na targu
        self.sold_wholesale = [0] * fruit_types  # lista owoców sprzedanych w skupie
        self.warehouse = [0] * fruit_types       # lista owoców, które po danym dniu trafiły do magazynu


# informacje o danym typie owoców: nazwa, ilośc w sadzie, cena bazowa, cena skupu, mnożnik
class FruitTypeInfo:
    def __init__(self, name: str, quantity: int, base_price: List,
                 wholesale_price: List, demand: List, multiplier: Callable):
        self.name = name
        self.quantity = quantity
        self.base_price = base_price  # lista cen
        self.wholesale_price = wholesale_price  # lista cen
        self.demand = demand  # lista popytów
        self.multiplier = multiplier  # funkcja


    # sprawdza nmożnik w zależności od spełninia popytu
    def check_multiplier(self, demand, sold):
        k = (sold/demand) *100
        return self.multiplier(k)


# główna klasa
class Sad:
    def __init__(self, fruit_types: List[FruitTypeInfo], employee_cost, magaz_cost):
        self.fruit_types = fruit_types  # lista obiektów klasy FruitTypeInfo
        self.employee_cost = employee_cost
        self.magaz_cost = magaz_cost

    # znajduje jak najlepsze rozwiazanie, docelowo jakiś algorytm np. genetyczny
    def find_solution(self):
        pass

    # sprawdza wszystkie ograniczenia dla danego rozwiązania w najprostszej wersji
    # zwraca bool, w bardziej skomplikowanej informacje gdzie błąd i ewentualnie kara
    def check_if_sol_acceptable(self, solution: Solution):
        # sprawdza czy nie zebraliśmy więcej owoców niż jest w sadzie dla każdego rodzaju
        def check_fruit_limits():
            pass

        # sprawdza czy nie zebraliśmy więcej owoców w żadnym dniu niż robotnicy są w stanie
        def check_workers():
            pass

        # sprawdza czy magazyn nie został przepełniony
        def check_magaz():
            pass

        # inne ograniczenia.....

        # wywołanie powyższych funkcji funkcji i zwrócenie wyniku
        pass

    def calculate_objective_fun(self, solution: Solution):
        """
        Funckja oblicza wartośc funkcji celu dla rozwiązania
        :param solution: obiekt reprezentujący rozwiązanie
        :return: profit - wartośc funkcji celu
        """
        profit = 0

        for day_id, day in enumerate(solution.days):
            for fruit_type_id in range(len(self.fruit_types)):
                fruit = self.fruit_types[fruit_type_id]
                demand = fruit.demand[day_id]
                sold_market = day.sold_market[fruit_type_id]
                market_price = fruit.base_price[day_id]*fruit.check_multiplier(demand=demand, sold=sold_market)
                sold_wholesale = day.sold_wholesale[fruit_type_id]
                wholesale_price = fruit.wholesale_price[day_id]

                profit += sold_market*market_price + sold_wholesale*wholesale_price

            cost = self.employee_cost[sum(day.harvested)] + self.magaz_cost[sum(day.warehouse)]
            profit -= cost

        return profit
