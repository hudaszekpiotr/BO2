#!/usr/bin/python
# -*- coding: utf-8 -*-
from project_app.solution_classes import Solution, FruitTypeInfo
from typing import List


def check_fruit_limits(solution: Solution, fruit_types: List[FruitTypeInfo]):
    """
    Funkcja sprawdzająca czy łączne zbiory danego
    typu owocu nie przekraczają fizycznej ilości danego typu owocu.

    Zwraca True jeśli limit został spełniony, w innym przypadku
    zwraca False

    :param solution: rozwiązanie
    :param fruit_types: lista typów owoców
    :return: boolean
    """
    # Lista przechowująca łączne zbiory każdego typu.
    # Indeks odpowiada typowi owocu.
    total_harvested = [0] * len(fruit_types)

    for day in solution.days:
        harv = day.harvested
        # w poniższej pętli dodaję do łącznej
        # liczby zbiorów zbiory z danego danego dnia
        for i in range(len(total_harvested)):
            total_harvested[i] += harv[i]

    result = True
    for id, fruit in enumerate(fruit_types):
        if total_harvested[id] > fruit.quantity:
            # Jeśli łączna ilość zebranych owoców
            # z danego typu będzie większa niż
            # istniejąca ilość owoców, to znaczy
            # że warunek nie został spełniony i nie musimy dalej wykonywać pętli
            result = False
            break
    return result


def check_harvest_limits(solution: Solution, max_daily_harvest: int):
    """
    Funkcja sprawdzająca czy dzienne zbiory wszystkich
    owoców łącznie nie przekraczają dziennego limitu zbiorów.

    Zwraca True jeśli limit został spełniony, w innym przypadku
    zwraca False

    :param solution: rozwiązanie
    :param max_daily_harvest: maksymalna dzienna ilość zbiorów
    :return: boolean
    """
    result = True
    for day in solution.days:
        # Jeśli któregoś dnia ilość zebranych
        # owoców będzie większa niż dopuszczalny limit
        # to warunek nie jest spełniony i można przerwać
        # dalszą pętlę
        if sum(day.harvested) > max_daily_harvest:
            result = False
            break
    return result


def check_warehouse_limits(solution: Solution, warehouse_capacity: int):
    """
    Funkcja sprawdzająca czy zbiory przekazane do magazynu
    nie przekraczają jego pojemności.

    Zwraca True jeśli limit został spełniony, w innym przypadku
    zwraca False

    :param solution: rozwiązanie
    :param warehouse_capacity: maksymalna pojemność magazynu
    :return: boolean
    """
    result = True
    for day in solution.days:
        # Jeśli któregoś dnia ilość owoców przekazanych
        # do magazynu będzie większa niż jego pojemność
        # to warunek nie jest spełniony i można przerwać
        # dalszą pętlę
        if sum(day.warehouse) > warehouse_capacity:
            result = False
            break
    return result


def check_minimum_amount_sold(solution: Solution, fruit_types: List[FruitTypeInfo]):
    """
    Funkcja sprawdza, czy w ciągu miesiąca zostały
    na targu sprzedane minimlane, z góry założone, ilości
    dla każdego typu owocu.

    Zwraca True jeśli limit został spełniony, w innym przypadku
    zwraca False

    :param solution:
    :param fruit_types: lista obiektów klasy FruitTypeInfo
    :return: boolean
    """
    # Lista przechowująca łączną sprzedaż na targu każdego typu.
    # Indeks odpowiada typowi owocu.
    total_market_sold = [0] * len(fruit_types)

    for day in solution.days:
        sold = day.sold_market
        # w poniższej pętli dodaję do łącznej
        # liczby sprzedanych owoców sprzedaż z danego dnia
        for i in range(len(total_market_sold)):
            total_market_sold[i] += sold[i]

    result = True
    for id, fruit in enumerate(fruit_types):
        if total_market_sold[id] < fruit.min_market_sold:
            # Jeśli łączna ilość sprzedanych na targu owoców
            # z danego typu będzie mniejsza niż
            # wymagany limit to znaczy, że warunek nie został spełniony
            # i nie musimy dalej wykonywać pętli
            result = False
            break
    return result


def check_if_warehouse_sold(solution: Solution) -> bool:
    """
    Sprawdza czy owoce, które dnia poprzdzającego zostały przekazane do magazyni zostały sprzedane
    w obecym dniu.

    :param solution:
    :return:
    """
    result = True
    for i, day in enumerate(solution.days):
        if i > 0:
            prev_warehouse = sum(solution.days[i - 1].warehouse)
            today_sold = sum(day.sold_market) + sum(day.sold_wholesale)
            if today_sold < prev_warehouse:
                # Jeśli sprzedano mniej niż poprzedniego dnia
                # włożono do magazynu to znaczy, że warunek nie został spełniony
                result = False
                break
    return result


def check_if_today_amount_correct(solution: Solution) -> bool:
    """
    Sprawdza czy w danym dniu rozwiązania ilość owoców sprzedanych oraz przekazanych
    do magazynu jest rówa ilości owoców zebranych plus owoców z poprzedniego dnia.

    :param solution:
    :return:
    """
    result = True
    for i, day in enumerate(solution.days):
        harvest = sum(day.harvested)
        today_sold = sum(day.sold_market) + sum(day.sold_wholesale)
        today_warehouse = sum(day.warehouse)
        if i > 0:
            prev_warehouse = sum(solution.days[i - 1].warehouse)
            if today_sold + today_warehouse != harvest + prev_warehouse:
                result = False
                break
        else:
            if today_sold + today_warehouse != harvest:
                result = False
                break
    return result


def check_if_non_negative(solution: Solution) -> bool:
    """
    Funkcja sprawdzająca, czy wszystkie parametry w rozwiązaniu są
    nieujemne.

    :param solution:
    :return:
    """

    def is_non_negative(arr):
        result = True
        for el in arr:
            if el < 0:
                result = False
                break
        return result

    result = True
    for i, day in enumerate(solution.days):
        if not (is_non_negative(day.harvested) and is_non_negative(day.sold_market)
                and is_non_negative(day.sold_wholesale) and is_non_negative(day.warehouse)):
            result = False
            break
    return result


def check_if_sold_market_less_than_demand(solution: Solution, fruit_types: List[FruitTypeInfo]) -> bool:
    """
    Funkcja sprawdzająca czy ilość owoców sprzedanych na targu jest
    mniejsza lub równa od popytu
    :param fruit_types:
    :param solution:
    :return:
    """
    result = True
    for i, day in enumerate(solution.days):
        for fruit_id in range(len(fruit_types)):
            # Sprawdź czy ilość owoców sprzedanych na targu
            # nie jest większa niż popyt danego dnia
            if day.sold_market[fruit_id] > fruit_types[fruit_id].demand[i]:
                result = False
                break
    return result
