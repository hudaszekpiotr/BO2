#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Callable
from solution_classes import Solution, DaySolution, FruitTypeInfo
from model_limits import check_fruit_limits, check_harvest_limits, \
    check_warehouse_limits, check_minimum_amount_sold, check_if_warehouse_sold, \
    check_if_today_amount_correct, check_if_non_negative
from copy import deepcopy
import random
import math
import numpy as np

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

    #losuje dopuszcalnego sąsiada initial_solution
    def draw_solution(self, initial_solution, neighbour_type):

        #funkcja do użycia po zmianie rozwiązania w jednym dniu jednego typu owoców
        #po zmianie stan magazynowy się zmienia co wpływa na sprzedaż następnego dnia
        #UWAGA nie działa jesli zminimy rozwiązanie dla więcej niz jednego dnia lub typu
        def update_warehouse(prev_solution, solution, day, type):
            if day != 0 and day != 29:
                solution.days[day].warehouse[type] = solution.days[day - 1].warehouse[type] + \
                                                     solution.days[day].harvested[type] - \
                                                     solution.days[day].sold_market[type] - \
                                                     solution.days[day].sold_wholesale[type]

                delta = solution.days[day].warehouse[type] - prev_solution.days[day].warehouse[type]
                if delta > 0:
                    if solution.days[day + 1].sold_market[type] + delta <= self.fruit_types[type].demand[day + 1]:
                        solution.days[day + 1].sold_market[type] += delta
                    else:
                        delta_wholesale = solution.days[day + 1].sold_market[type] + delta - self.fruit_types[type].demand[day + 1]
                        solution.days[day + 1].sold_wholesale[type] += delta_wholesale
                        solution.days[day + 1].sold_market[type] = self.fruit_types[type].demand[day + 1]
                else:
                    if solution.days[day + 1].sold_wholesale[type] + delta >= 0:
                        solution.days[day + 1].sold_wholesale[type] += delta
                    else:
                        delta += solution.days[day + 1].sold_wholesale[type]
                        solution.days[day + 1].sold_wholesale[type] = 0
                        solution.days[day + 1].sold_market[type] += delta

        #UWAGA nie działa, nie uzywac, nie usuwac
        def neighbour0(org_solution):
            solution = deepcopy(org_solution)
            prev_solution = deepcopy(org_solution)
            random_days = random.sample(range(0, 30), 2)
            random_types = random.sample(range(0, len(self.fruit_types)), 1)
            #random_part_of_sol = random.randint(0, 2)

            for day in random_days:
                for type in random_types:

                    changed = solution.days[day].harvested[type] + random.randint(-2, 2)
                    if changed >= 0 and changed + sum(solution.days[day].harvested) - solution.days[day].harvested[type] + changed <= self.max_daily_harvest:
                        solution.days[day].harvested[type] = changed

                    changed = solution.days[day].sold_market[type] + random.randint(-2, 2)
                    if 0 <= changed <= self.fruit_types[type].demand[day] and changed <= solution.days[day-1].warehouse[type] + solution.days[day].harvested[type]:
                        solution.days[day].sold_market[type] = changed

                    changed = solution.days[day].sold_wholesale[type] + random.randint(-2, 2)
                    if 0 <= changed <= solution.days[day - 1].warehouse[type] + solution.days[day].harvested[type] - solution.days[day].sold_market[type]:
                        solution.days[day].sold_wholesale[type] = changed
                    update_warehouse(prev_solution, solution, day, type)

            return solution

        #losuje sąsiada w pobliżu org_solution, sąsiad może być rozwiązaniem nie dopuszczalnym
        #zmienia w losowym dniu losowy typ o sprzedaż na markecie lub na skupie lub zbiory
        def neighbour1(org_solution):
            solution = deepcopy(org_solution)
            prev_solution = deepcopy(org_solution)
            day = random.randint(0, 29)
            type = random.randint(0, len(self.fruit_types)-1)
            part_of_sol = random.randint(0, 2)
            if part_of_sol == 0:
                changed = solution.days[day].harvested[type] + random.randint(-2, 2)
                if changed >= 0 and changed + sum(solution.days[day].harvested) - solution.days[day].harvested[type] + changed <= self.max_daily_harvest:
                    solution.days[day].harvested[type] = changed

            if part_of_sol == 1:
                changed = solution.days[day].sold_market[type] + random.randint(-2, 2)
                if 0 <= changed <= self.fruit_types[type].demand[day] and changed <= solution.days[day-1].warehouse[type] + solution.days[day].harvested[type]:
                    solution.days[day].sold_market[type] = changed

            if part_of_sol == 2:
                changed = solution.days[day].sold_wholesale[type] + random.randint(-2, 2)
                if 0 <= changed <= solution.days[day - 1].warehouse[type] + solution.days[day].harvested[type] - solution.days[day].sold_market[type]:
                    solution.days[day].sold_wholesale[type] = changed
            update_warehouse(prev_solution, solution, day, type)

            return solution

        #wybór jednego z typów sąsiedztwa
        neighbour_types = [neighbour0, neighbour1]
        neighbour = neighbour_types[neighbour_type]

        #prubuje zznalezc sasiada jesli w ciagu 100 losowan nie znajdzie akceptowalnego rzuca wyjątek
        for _ in range(100):
            sol = neighbour(initial_solution)
            if self.check_if_sol_acceptable(sol):
                return sol

        raise Exception("error nie znaleziono otoczenia")

    # znajduje jak najlepsze rozwiazanie metoda Symulowanego Wyżarzania
    def find_solution(self, T_start, T_stop, iterations_in_temp, epsilon, iterations_epsilon, alpha, neighbour_type, initial_sol):
        solution = self.create_initial_population()[initial_sol][0]
        print(solution)
        best_solution = solution
        best_profit = self.calculate_objective_fun(solution)
        T = T_start
        sol_fun_list = []

        while T > T_stop:
            print(best_profit)
            for j in range(iterations_in_temp):
                candidate_sol = self.draw_solution(solution, neighbour_type)
                candidate_sol_fun = self.calculate_objective_fun(candidate_sol)
                delta = candidate_sol_fun - self.calculate_objective_fun(solution)
                if delta >= 0:
                    solution = candidate_sol
                    if candidate_sol_fun > best_profit:
                        best_solution = solution
                        best_profit = candidate_sol_fun
                else:
                    drawn_num = np.random.rand()
                    if drawn_num < math.exp(-delta/T):
                        solution = candidate_sol
            T = alpha * T
            while len(sol_fun_list) > iterations_epsilon - 1:
                sol_fun_list.pop(0)
            sol_fun_list.append(self.calculate_objective_fun(solution))

            if len(sol_fun_list) == iterations_epsilon and max(sol_fun_list)-min(sol_fun_list) <= epsilon:
                print("kryt stopu 2")
                return best_solution, best_profit
        print("kryt stopu 1")
        return best_solution, best_profit

    def generate_all_to_wholesale(self, harvest_strategies: List[List]):
        """
        Funkcja generuje startowe rozwiązanie z założeniem, że wszystkie zebrane
        owoce idą na sprzedaż do skupu tego samego dnia. Parametr harvest_strategies to
        lista list gdzie wewnątrzne listy to poszczególne strategie zbiorów. Strategia składa
        się z ilości dni przez ile dana strategia obowiązuje oraz listy odpowiadającej maksymalnej
        ilości owoców z danego typu zbieranej w ciągu dnia. Przykładow omamy 3 typy owoców: jabłka, gruszki, śliwki.
        harvest_strategies może wyglądać następująco

        [[15,[20, 30, 25]], [15,[10, 25, 19]]] co oznacza, że przez
        pierwsze 15 dni zbierazmy dziennie 20kg jabłek, 30kg gruszek, 25kg śliwek a przez kolejne 15 dni
        10kg jabłek, 25kg gruszek, 19kg śliwek. Oczywiście, jeżeli danego w sadzie zostało już mniej owoców niż
        wynika to z powyższych paramterów to zbieramy tą mniejszą ilość owoców tym samym wykańczając zapasy
        danego owocu w sadzie.

        :param harvest_strategies:
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

        day_id = 0
        for strategy in harvest_strategies:
            harvest_per_type = strategy[1]
            for i in range(strategy[0]):
                for j, f_type in enumerate(self.fruit_types):
                    # Ile owoców wciąż mamy w sadzie
                    f_left = fruits_left[f_type.name]

                    # Określenie wielkości zbiorów danego dnia
                    if harvest_per_type[j] <= f_left:
                        solution.days[day_id].harvested[j] = harvest_per_type[j]
                        fruits_left[f_type.name] -= harvest_per_type[j]
                    else:
                        solution.days[day_id].harvested[j] = f_left
                        fruits_left[f_type.name] -= f_left
                    solution.days[day_id].sold_wholesale[j] = solution.days[day_id].harvested[j]
                day_id += 1

        return solution

    def generate_satisfy_demand(self, harvest_strategies: List[List], demand_rate: float):
        """
        Funkcja generuje startowe rozwiązanie z założeniem, że każde dnia staramy się spełnić
        popyt na dany owoc. Parametr demand_rate przyjmujący wartości z zakresu [0-1] określa
        jaki procent popytu dla każdego owocu staramy się zadowolić naszym startowym rozwiązaniem
        Przykładowo demand_rate=0.6 oznacza, że każdego dnia staramy się zaspokoić 60% popytu
        na każdy owoc aż do wyczerpania zasobów owoców. Parametr harvest_strategies działa identycznie jak w
        funkcji generate_all_to_wholesale.

        :param harvest_strategies:
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

        day_id = 0
        for strategy in harvest_strategies:
            harvest_per_type = strategy[1]
            for i in range(strategy[0]):
                for j, f_type in enumerate(self.fruit_types):
                    # Ile owoców wciąż mamy w sadzie
                    f_left = fruits_left[f_type.name]

                    # Określenie wielkości zbiorów danego dnia
                    if harvest_per_type[j] <= f_left:
                        solution.days[day_id].harvested[j] = harvest_per_type[j]
                        fruits_left[f_type.name] -= harvest_per_type[j]
                    else:
                        solution.days[day_id].harvested[j] = f_left
                        fruits_left[f_type.name] -= f_left

                    # Popyt jaki staramy się zaspokoić
                    demand = int(f_type.demand[day_id] * demand_rate)
                    if day_id == 0:
                        # Pierwszy dzień (brak magazynu z dnia poprzedniego)
                        if demand >= solution.days[day_id].harvested[j]:
                            solution.days[day_id].sold_market[j] = solution.days[day_id].harvested[j]
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = 0
                        else:
                            solution.days[day_id].sold_market[j] = demand
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = solution.days[day_id].harvested[j] - demand
                            solution.days[day_id].sold_wholesale[j] = int(percent_to_wholesale * leftovers)
                    else:
                        if demand > solution.days[day_id - 1].warehouse[j]:
                            # Popyt większy niż ilość owoców z magazynu z poprzedniego dnia
                            solution.days[day_id].sold_market[j] = solution.days[day_id - 1].warehouse[j]
                            if demand - solution.days[day_id - 1].warehouse[j] >= solution.days[day_id].harvested[j]:
                                # Sytuacja gdy owoce z magazynu nie zaspokoiły popytu na targu a ilość
                                # zebranych owoców jest na tyle niska że możemy wszystkie również przeznaczyć
                                # do sprzedaży na targu
                                solution.days[day_id].sold_market[j] += solution.days[day_id].harvested[j]
                                # pozostałości przeznaczone do skupu lub magazynu
                                leftovers = 0
                            else:
                                # Sytuacja gdy owoce z magazynu nie zaspokoiły popytu na targu a ilość
                                # zebranych owoców wystarcza na zaspokojenie tego popytu oraz zostaje nam
                                # jeszcze trochę wolnych owoców
                                solution.days[day_id].sold_market[j] = demand
                                # pozostałości przeznaczone do skupu lub magazynu
                                leftovers = solution.days[day_id].harvested[j] - (demand - solution.days[day_id - 1].warehouse[j])
                                solution.days[day_id].sold_wholesale[j] = int(percent_to_wholesale * leftovers)
                        elif demand == solution.days[day_id - 1].warehouse[j]:
                            # Popyt równy owocom z magazynu
                            solution.days[day_id].sold_market[j] = solution.days[day_id - 1].warehouse[j]
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = solution.days[day_id].harvested[j]
                            solution.days[day_id].sold_wholesale[j] = int(percent_to_wholesale * leftovers)
                        else:
                            # Popyt mniejszy niż owoce z magazynu
                            solution.days[day_id].sold_market[j] = demand
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = solution.days[day_id].harvested[j]
                            solution.days[day_id].sold_wholesale[j] = int(percent_to_wholesale * leftovers) + \
                                                                 solution.days[day_id - 1].warehouse[j] - demand

                    # Jeśli część owoców przeznaczona do magazynu zmieści się w nim to możemy je tam wsadzić.
                    # W innym wypadku również trafiają one do skupu.
                    if leftovers - int(percent_to_wholesale * leftovers) + sum(
                            solution.days[day_id].warehouse) <= self.warehouse_capacity:
                        solution.days[day_id].warehouse[j] = leftovers - int(percent_to_wholesale * leftovers)
                    else:
                        solution.days[day_id].sold_wholesale[j] += leftovers - int(percent_to_wholesale * leftovers)
                day_id += 1

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

        har_per_type1 = self.max_daily_harvest // fruit_types_count
        har_per_type2 = int(0.9 * self.max_daily_harvest) // fruit_types_count
        har_per_type3 = int(0.7 * self.max_daily_harvest) // fruit_types_count
        har_per_type4 = int(0.5 * self.max_daily_harvest) // fruit_types_count

        all_strategies = []

        harvest_strategies1 = []
        harvest_per_type = [har_per_type1] * fruit_types_count
        harvest_strategies1.append([7, harvest_per_type])
        harvest_per_type = [har_per_type2] * fruit_types_count
        harvest_strategies1.append(([7, harvest_per_type]))
        harvest_per_type = [har_per_type3] * fruit_types_count
        harvest_strategies1.append(([7, harvest_per_type]))
        harvest_per_type = [har_per_type4] * fruit_types_count
        harvest_strategies1.append(([9, harvest_per_type]))
        all_strategies.append(harvest_strategies1)

        harvest_strategies2 = []
        harvest_per_type = [har_per_type3] * fruit_types_count
        harvest_strategies2.append([7, harvest_per_type])
        harvest_per_type = [har_per_type4] * fruit_types_count
        harvest_strategies2.append(([7, harvest_per_type]))
        harvest_per_type = [har_per_type1] * fruit_types_count
        harvest_strategies2.append(([7, harvest_per_type]))
        harvest_per_type = [har_per_type2] * fruit_types_count
        harvest_strategies2.append(([9, harvest_per_type]))
        all_strategies.append(harvest_strategies2)

        # Strategia polegająca na przeznaczaniu całych zbiorów do skupu
        # z założeniem, że z każdego typu zbieramy tyle samo owoców
        # (elemety w liście harvest_per_type są równe)
        solution = self.generate_all_to_wholesale(harvest_strategies1)
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        solution = self.generate_all_to_wholesale(harvest_strategies2)
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        # Strategia polegająca na zaspokajaniu popytu
        # z założeniem, że z każdego typu zbieramy tyle samo owoców
        # (elemety w liście harvest_per_type są równe)
        solution = self.generate_satisfy_demand(harvest_strategies1, 0.6)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(harvest_strategies1, 1)
        solutions.append(deepcopy(solution))

        solution = self.generate_satisfy_demand(harvest_strategies2, 0.6)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(harvest_strategies2, 1)
        solutions.append(deepcopy(solution))

        # Edycja listy strategii zbiorów w taki sposób, że owoców
        # pierwszego typu zbieramy najwięcej a każdych następnych
        # coraz mniej.
        for i in range(len(all_strategies)):
            # Pętla po listach ze strategiami (elementy z all_strategies)
            for strat_id in range(len(all_strategies[i])):
                # Pętla po danych strategiach w danej liście ze strategiami
                # (elementy na przykład z harvest_strategies1)
                for fruit_id in range(len(all_strategies[i][strat_id][1])):
                    # Pętla po zbiorach danego typu owocu w danej strategii
                    i_end = fruit_types_count-1-fruit_id
                    if fruit_id < i_end:
                        multiplier = (fruit_types_count-1-fruit_id)/fruit_types_count
                        all_strategies[i][strat_id][1][fruit_id] += int(all_strategies[i][strat_id][1][i_end]*multiplier)
                        all_strategies[i][strat_id][1][-fruit_id-1] -= int(all_strategies[i][strat_id][1][i_end]*multiplier)
                    else:
                        break

        # Strategia polegająca na przeznaczaniu całych zbiorów do skupu
        # ze zmienionym parametrem harvest_per_type
        solution = self.generate_all_to_wholesale(harvest_strategies1)
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        solution = self.generate_all_to_wholesale(harvest_strategies2)
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        # Strategia polegająca na zaspokajaniu popytu
        # ze zmienionym parametrem harvest_per_type
        solution = self.generate_satisfy_demand(harvest_strategies1, 0.6)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(harvest_strategies1, 1)
        solutions.append(deepcopy(solution))

        solution = self.generate_satisfy_demand(harvest_strategies2, 0.6)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(harvest_strategies2, 1)
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
        seven = check_if_non_negative(solution)

        #print(one, two, four, five, six)

        return one and two and four and five and six and seven

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

        return profit
