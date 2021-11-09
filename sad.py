#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Callable


# postać rozwiązania aby dostać ile owoców sprzedanych 8 dnia typu 2 należy solution.days[7].sold[1]
class Solution:
    def __init__(self, fruit_types):
        self.days = [DaySolution(fruit_types)] * 30


# postać rozwiązania dla 1 dnia
class DaySolution:
    def __init__(self, fruit_types):
        self.harvested = [0] * fruit_types  # lista zebranych owoców danego dnia (każdy indeks to inny typ owocu)
        self.sold_market = [0] * fruit_types  # lista owoców sprzedanych na targu (każdy indeks to inny typ owocu)
        self.sold_wholesale = [0] * fruit_types  # lista owoców sprzedanych w skupie (każdy indeks to inny typ owocu)
        self.warehouse = [0] * fruit_types  # lista owoców, które po danym dniu trafiły do magazynu (każdy indeks to inny typ owocu)


# informacje o danym typie owoców: nazwa, ilośc w sadzie, cena bazowa, cena skupu, mnożnik
class FruitTypeInfo:
    def __init__(self, name: str, quantity: int, base_price: List,
                 wholesale_price: List, demand: List, min_market_sold: int, multiplier: Callable):
        self.name = name  # nazwa owocu
        self.quantity = quantity  # ilość owoców danego typu
        self.base_price = base_price  # lista cen (indeksy to poszczególne dni miesiąca)
        self.wholesale_price = wholesale_price  # lista cen (indeksy to poszczególne dni miesiąca)
        self.demand = demand  # lista popytów
        self.min_market_sold = min_market_sold  # minimalna ilość jaka musi zostać sprzedana na targu w ciągu miesiąca
        self.multiplier = multiplier  # funkcja

    # sprawdza nmożnik w zależności od spełninia popytu
    def check_multiplier(self, demand, sold):
        k = (sold / demand) * 100
        return self.multiplier(k)


# główna klasa
class Orchard:
    def __init__(self, fruit_types: List[FruitTypeInfo], employee_cost: Callable,
                 warehouse_cost: Callable, max_daily_harvest: int, warehouse_capacity: int):
        """

        :param fruit_types: lista obiektów klasy FruitTypeInfo (każdy indeks to inny typ owocu)
        :param employee_cost: funkcja zwracająca koszta zebrania
                              pewnej ilości owoców
        :param warehouse_cost: funkcja zwracająca koszta magazynowania
                           pewnej ilości owoców
        :param max_daily_harvest: maksymalna dzienna ilość zbiorów
        :param warehouse_capacity: maksymalna pojemność magazynu
        """
        self.fruit_types = fruit_types
        self.employee_cost = employee_cost
        self.warehouse_cost = warehouse_cost
        self.max_daily_harvest = max_daily_harvest
        self.warehouse_capacity = warehouse_capacity

    # znajduje jak najlepsze rozwiazanie, docelowo jakiś algorytm np. genetyczny
    def find_solution(self):
        pass

    def check_fruit_limits(self, solution: Solution):
        """
        Funkcja sprawdzająca czy łączne zbiory danego
        typu owocu nie przekraczają fizycznej ilości danego typu owocu.

        Zwraca True jeśli limit został spełniony, w innym przypadku
        zwraca False

        :param solution: rozwiązanie
        :return: boolean
        """
        # Lista przechowująca łączne zbiory każdego typu.
        # Indeks odpowiada typowi owocu.
        total_harvested = [0] * len(self.fruit_types)

        for day in solution.days:
            harv = day.harvested
            # w poniższej pętli dodaję do łącznej
            # liczby zbiorów zbiory z danego danego dnia
            for i in range(len(total_harvested)):
                total_harvested[i] += harv[i]

        result = True
        for id, fruit in enumerate(self.fruit_types):
            if total_harvested[id] > fruit.quantity:
                # Jeśli łączna ilość zebranych owoców
                # z danego typu będzie większa niż
                # istniejąca ilość owoców, to znaczy
                # że warunek nie został spełniony i nie musimy dalej wykonywać pętli
                result = False
                break
        return result

    def check_harvest_limits(self, solution: Solution):
        """
        Funkcja sprawdzająca czy dzienne zbiory wszystkich
        owoców łącznie nie przekraczają dziennego limitu zbiorów.

        Zwraca True jeśli limit został spełniony, w innym przypadku
        zwraca False

        :param solution: rozwiązanie
        :return: boolean
        """
        result = True
        for day in solution.days:
            # Jeśli któregoś dnia ilość zebranych
            # owoców będzie większa niż dopuszczalny limit
            # to warunek nie jest spełniony i można przerwać
            # dalszą pętlę
            if sum(day.harvested) > self.max_daily_harvest:
                result = False
                break
        return result

    def check_warehouse_limits(self, solution: Solution):
        """
        Funkcja sprawdzająca czy zbiory przekazane do magazynu
        nie przekraczają jego pojemności.

        Zwraca True jeśli limit został spełniony, w innym przypadku
        zwraca False

        :param solution: rozwiązanie
        :return: boolean
        """
        result = True
        for day in solution.days:
            # Jeśli któregoś dnia ilość owoców przekazanych
            # do magazynu będzie większa niż jego pojemność
            # to warunek nie jest spełniony i można przerwać
            # dalszą pętlę
            if sum(day.warehouse) > self.warehouse_capacity:
                result = False
                break
        return result

    def check_minimum_amount_sold(self, solution: Solution):
        """
        Funkcja sprawdza, czy w ciągu miesiąca zostały
        na targu sprzedane minimlane, z góry założone, ilości
        dla każdego typu owocu.

        Zwraca True jeśli limit został spełniony, w innym przypadku
        zwraca False

        :param solution:
        :return: boolean
        """
        # Lista przechowująca łączną sprzedaż na targu każdego typu.
        # Indeks odpowiada typowi owocu.
        total_market_sold = [0] * len(self.fruit_types)

        for day in solution.days:
            sold = day.sold_market
            # w poniższej pętli dodaję do łącznej
            # liczby sprzedanych owoców sprzedaż z danego dnia
            for i in range(len(total_market_sold)):
                total_market_sold[i] += sold[i]

        result = True
        for id, fruit in enumerate(self.fruit_types):
            if total_market_sold[id] < fruit.min_market_sold:
                # Jeśli łączna ilość sprzedanych na targu owoców
                # z danego typu będzie mniejsza niż
                # wymagany limit to znaczy, że warunek nie został spełniony
                # i nie musimy dalej wykonywać pętli
                result = False
                break
        return result

    def check_if_sol_acceptable(self, solution: Solution) -> bool:
        """
        Sprawdza wszystkie ograniczenia dla danego rozwiązania w najprostszej wersji
        zwraca bool, w bardziej skomplikowanej informacje gdzie błąd i ewentualnie kara

        :param solution:
        :return:
        """
        one = self.check_fruit_limits(solution)
        two = self.check_harvest_limits(solution)
        three = self.check_minimum_amount_sold(solution)
        four = self.check_warehouse_limits(solution)

        return one and two and three and four

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
                market_price = fruit.base_price[day_id] * fruit.check_multiplier(demand=demand, sold=sold_market)
                sold_wholesale = day.sold_wholesale[fruit_type_id]
                wholesale_price = fruit.wholesale_price[day_id]

                profit += sold_market * market_price + sold_wholesale * wholesale_price

            cost = self.employee_cost(sum(day.harvested)) + self.warehouse_cost(sum(day.warehouse))
            profit -= cost

        return profit
