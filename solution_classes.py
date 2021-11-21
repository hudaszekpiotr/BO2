#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Callable

# postać rozwiązania dla 1 dnia
class DaySolution:
    def __init__(self, fruit_types):
        self.harvested = [0] * fruit_types  # lista zebranych owoców danego dnia (każdy indeks to inny typ owocu)
        self.sold_market = [0] * fruit_types  # lista owoców sprzedanych na targu (każdy indeks to inny typ owocu)
        self.sold_wholesale = [0] * fruit_types  # lista owoców sprzedanych w skupie (każdy indeks to inny typ owocu)
        self.warehouse = [0] * fruit_types  # lista owoców, które po danym dniu trafiły do magazynu (każdy indeks to inny typ owocu)


# postać rozwiązania aby dostać ile owoców sprzedanych 8 dnia typu 2 należy solution.days[7].sold[1]
class Solution:
    def __init__(self, fruit_types: int):
        """
        :param fruit_types: ilość typów owoców
        """
        self.days = []
        for _ in range(30):
            d = DaySolution(fruit_types)
            self.days.append(d)

    def __str__(self):
        txt = ""
        for i, day in enumerate(self.days):
            txt += f"Day {i + 1}\nharvested: {day.harvested}\nsold_market: {day.sold_market}\n" \
                   f"sold_wholesale: {day.sold_wholesale}\nwarehouse: {day.warehouse}\n\n"
        txt += "\n\n\n\n"
        return txt


# informacje o danym typie owoców: nazwa, ilośc w sadzie, cena bazowa, cena skupu, mnożnik
class FruitTypeInfo:
    def __init__(self, name: str, quantity: int, planting_cost: int, base_price: List,
                 wholesale_price: List, demand: List, min_market_sold: int, multiplier: Callable):
        self.name = name  # nazwa owocu
        self.quantity = quantity  # ilość owoców danego typu
        self.planting_cost = planting_cost  # koszt zasadzenia i wyhodowania owoców
        self.base_price = base_price  # lista cen (indeksy to poszczególne dni miesiąca)
        self.wholesale_price = wholesale_price  # lista cen (indeksy to poszczególne dni miesiąca)
        self.demand = demand  # lista popytów
        self.min_market_sold = min_market_sold  # minimalna ilość jaka musi zostać sprzedana na targu w ciągu miesiąca
        self.multiplier = multiplier  # funkcja

    # sprawdza nmożnik w zależności od spełninia popytu
    def check_multiplier(self, demand, sold):
        k = (sold / demand) * 100
        return self.multiplier(k)