#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Callable
from solution_classes import Solution, DaySolution, FruitTypeInfo
from model_limits import check_fruit_limits, check_harvest_limits, \
    check_warehouse_limits, check_minimum_amount_sold, check_if_warehouse_sold, check_if_today_amount_correct
from copy import deepcopy

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

    def generate_all_to_wholesale(self, harvest_per_type: List[int]):
        """
        Funkcja generuje startowe rozwiązanie z założeniem, że wszystkie zebrane
        owoce idą na sprzedaż do skupu tego samego dnia. Parametr harvest_per_type to
        lista odpowiadająca maksymalnej ilości owoców z danego typu zbieranej w ciągu dnia. Przykładowo
        mamy 3 typy owoców: jabłka, gruszki, śliwki. harvest_per_type może wyglądać następująco
        [20, 30, 25] co oznacza że w ciągu dnia zbieramy 20kg jabłek, 30kg gruszek, 25kg śliwek.
        Jesli jednak w sadzie zostało mniej np śliwek, załóżmy 19kg, to zbieramy całą tą ilość.

        :param harvest_per_type:
        :return: startowe rozwiązanie
        """
        # ilość rodzajów owoców
        fruit_types_count = len(self.fruit_types)

        # Słownik fruits_left jest wykorzystywany do zapamiętywania
        # ile owoców danego typu zostało w sadzie po każdym dniu zbiorów
        fruits_left = {}
        for f_type in self.fruit_types:
            fruits_left[f_type.name] = f_type.quantity

        solution = Solution(fruit_types_count)
        for i, _ in enumerate(solution.days):
            for j, f_type in enumerate(self.fruit_types):
                # Ile owoców wciąż mamy w sadzie
                f_left = fruits_left[f_type.name]

                # Określenie wielkości zbiorów danego dnia
                if harvest_per_type[j] <= f_left:
                    solution.days[i].harvested[j] = harvest_per_type[j]
                    fruits_left[f_type.name] -= harvest_per_type[j]
                else:
                    solution.days[i].harvested[j] = f_left
                    fruits_left[f_type.name] -= f_left
                solution.days[i].sold_wholesale[j] = solution.days[i].harvested[j]
        return solution

    def generate_satisfy_demand(self, harvest_per_type: List[int], demand_rate: float):
        """
        Funkcja generuje startowe rozwiązanie z założeniem, że każde dnia staramy się spełnić
        popyt na dany owoc. Parametr demand_rate przyjmujący wartości z zakresu [0-1] określa
        jaki procent popytu dla każdego owocu staramy się zadowolić naszym startowym rozwiązaniem
        Przykładowo demand_rate=0.6 oznacza, że każdego dnia staramy się zaspokoić 60% popytu
        na każdy owoc aż do wyczerpania zasobów owoców. Parametr harvest_per_type działa identycznie jak w
        funkcji generate_all_to_wholesale.

        :param harvest_per_type:
        :param demand_rate:
        :return: startowe rozwiązanie
        """
        # ilość rodzajów owoców
        fruit_types_count = len(self.fruit_types)

        # Słownik fruits_left jest wykorzystywany do zapamiętywania
        # ile owoców danego typu zostało w sadzie po każdym dniu zbiorów
        fruits_left = {}
        for f_type in self.fruit_types:
            fruits_left[f_type.name] = f_type.quantity

        solution = Solution(fruit_types_count)

        # Po sprzedaży owoców na targu pewna ilość musi trafić
        # do skupu i pewna do magazynu jeśli się tam zmieści.
        # percent_to_wholesale określa jaki procent tych owoców
        # początkowo chcemy dać do skupu podczas gdy reszta trafi do magazynu.
        # Jeśli reszta nie zmieści się w magazynie to na koniec też przeznaczamy
        # ją do skupu.
        percent_to_wholesale = 0.7

        for i, day in enumerate(solution.days):
            for j, f_type in enumerate(self.fruit_types):
                # Ile owoców wciąż mamy w sadzie
                f_left = fruits_left[f_type.name]

                # Określenie wielkości zbiorów danego dnia
                if harvest_per_type[j] <= f_left:
                    solution.days[i].harvested[j] = harvest_per_type[j]
                    fruits_left[f_type.name] -= harvest_per_type[j]
                else:
                    solution.days[i].harvested[j] = f_left
                    fruits_left[f_type.name] -= f_left

                # Popyt jaki staramy się zaspokoić
                demand = int(f_type.demand[i]*demand_rate)
                if i == 0:
                    # Pierwszy dzień (brak magazynu z dnia poprzedniego)
                    if demand >= solution.days[i].harvested[j]:
                        solution.days[i].sold_market[j] = solution.days[i].harvested[j]
                        # pozostałości przeznaczone do skupu lub magazynu
                        leftovers = 0
                    else:
                        solution.days[i].sold_market[j] = demand
                        # pozostałości przeznaczone do skupu lub magazynu
                        leftovers = solution.days[i].harvested[j] - demand
                        solution.days[i].sold_wholesale[j] = int(percent_to_wholesale * leftovers)
                else:
                    if demand > solution.days[i - 1].warehouse[j]:
                        # Popyt większy niż ilość owoców z magazynu z poprzedniego dnia
                        solution.days[i].sold_market[j] = solution.days[i - 1].warehouse[j]
                        if demand - solution.days[i - 1].warehouse[j] >= solution.days[i].harvested[j]:
                            # Sytuacja gdy owoce z magazynu nie zaspokoiły popytu na targu a ilość
                            # zebranych owoców jest na tyle niska że możemy wszystkie również przeznaczyć
                            # do sprzedaży na targu
                            solution.days[i].sold_market[j] += solution.days[i].harvested[j]
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = 0
                        else:
                            # Sytuacja gdy owoce z magazynu nie zaspokoiły popytu na targu a ilość
                            # zebranych owoców wystarcza na zaspokojenie tego popytu oraz zostaje nam
                            # jeszcze trochę wolnych owoców
                            solution.days[i].sold_market[j] = demand
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = solution.days[i].harvested[j] - (demand - solution.days[i - 1].warehouse[j])
                            solution.days[i].sold_wholesale[j] = int(percent_to_wholesale * leftovers)
                    elif demand == solution.days[i - 1].warehouse[j]:
                        # Popyt równy owocom z magazynu
                        solution.days[i].sold_market[j] = solution.days[i - 1].warehouse[j]
                        # pozostałości przeznaczone do skupu lub magazynu
                        leftovers = solution.days[i].harvested[j]
                        solution.days[i].sold_wholesale[j] = int(percent_to_wholesale * leftovers)
                    else:
                        # Popyt mniejszy niż owoce z magazynu
                        solution.days[i].sold_market[j] = demand
                        # pozostałości przeznaczone do skupu lub magazynu
                        leftovers = solution.days[i].harvested[j]
                        solution.days[i].sold_wholesale[j] = int(percent_to_wholesale*leftovers) + \
                                                             solution.days[i-1].warehouse[j] - demand

                # Jeśli część owoców przeznaczona do magazynu zmieści się w nim to możemy je tam wsadzić.
                # W innym wypadku również trafiają one do skupu.
                if leftovers - int(percent_to_wholesale * leftovers) + sum(solution.days[i].warehouse) <= self.warehouse_capacity:
                    solution.days[i].warehouse[j] = leftovers - int(percent_to_wholesale * leftovers)
                else:
                    solution.days[i].sold_wholesale[j] += leftovers - int(percent_to_wholesale * leftovers)
        return solution

    def create_initial_population(self):
        """
        Funkcja generuje populację rozwiązań początkowych. Funckja zwraca listę
        krotek, gdzie pierwszy element krotki to rozwiązanie a drugi to informacja
        czy rozwiązanie spełnia ograniczenia.

        :return:
        """
        fruit_types_count = len(self.fruit_types)
        solutions = []

        max_har_per_type = self.max_daily_harvest // fruit_types_count
        harvest_per_type = [max_har_per_type] * fruit_types_count

        # Strategia polegająca na przeznaczaniu całych zbiorów do skupu
        # z założeniem, że z każdego typu zbieramy tyle samo owoców
        # (elemety w liście harvest_per_type są równe)
        solution = self.generate_all_to_wholesale(harvest_per_type)
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        # Strategia polegająca na zaspokajaniu popytu
        # z założeniem, że z każdego typu zbieramy tyle samo owoców
        # (elemety w liście harvest_per_type są równe)
        solution = self.generate_satisfy_demand(harvest_per_type, 0.6)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(harvest_per_type, 1)
        solutions.append(deepcopy(solution))

        # Edycja listy harvest_per_type w taki sposób, że owoców
        # pierwszego typu zbieramy najwięcej a każdych następnych
        # coraz mniej.
        for i in range(fruit_types_count):
            i_end = fruit_types_count-1-i
            if i < i_end:
                multiplier = (fruit_types_count-1-i)/fruit_types_count
                harvest_per_type[i] += int(harvest_per_type[i_end]*multiplier)
                harvest_per_type[-i-1] -= int(harvest_per_type[i_end]*multiplier)
            else:
                break

        # Strategia polegająca na przeznaczaniu całych zbiorów do skupu
        # ze zmienionym parametrem harvest_per_type
        solution = self.generate_all_to_wholesale(harvest_per_type)
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        # Strategia polegająca na zaspokajaniu popytu
        # ze zmienionym parametrem harvest_per_type
        solution = self.generate_satisfy_demand(harvest_per_type, 0.6)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(harvest_per_type, 1)
        solutions.append(deepcopy(solution))

        result = []
        for el in solutions:
            result.append((el, self.check_if_sol_acceptable(el)))
        return result

    def check_if_sol_acceptable(self, solution: Solution) -> bool:
        """
        Sprawdza wszystkie ograniczenia dla danego rozwiązania w najprostszej wersji
        zwraca bool, w bardziej skomplikowanej informacje gdzie błąd i ewentualnie kara

        :param solution:
        :return:
        """
        one = check_fruit_limits(solution, self.fruit_types)
        two = check_harvest_limits(solution, self.max_daily_harvest)
        #three = check_minimum_amount_sold(solution, self.fruit_types)
        four = check_warehouse_limits(solution, self.warehouse_capacity)
        five = check_if_warehouse_sold(solution)
        six = check_if_today_amount_correct(solution)

        #print(one, two, four, five, six)

        return one and two and four and five and six

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

        for fruit in self.fruit_types:
            profit -= fruit.planting_cost

        # Funkcja zwraca zysk z wartością ujemną. Dzięki temu
        # problem staje się problemem minimalizacji funkcji celu.
        profit = -profit

        return profit
