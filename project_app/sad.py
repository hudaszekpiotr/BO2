#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Callable
from project_app.solution_classes import Solution, FruitTypeInfo
from project_app.model_limits import check_fruit_limits, check_harvest_limits, \
    check_warehouse_limits, check_if_warehouse_sold, \
    check_if_today_amount_correct, check_if_non_negative, check_if_sold_market_less_than_demand
from copy import deepcopy
import math
import numpy as np
import random

# główna klasa
class Orchard:
    def __init__(self, fruit_types: List[FruitTypeInfo], employee_cost: Callable,
                 warehouse_cost: Callable, max_daily_harvest: int, warehouse_capacity: int, num_days: int):
        """
        :param fruit_types: lista obiektów klasy FruitTypeInfo (każdy indeks to inny typ owocu)
        :param employee_cost: funkcja zwracająca koszta zebrania
                              pewnej ilości owoców
        :param warehouse_cost: funkcja zwracająca koszta magazynowania
                           pewnej ilości owoców
        :param max_daily_harvest: maksymalna dzienna ilość zbiorów
        :param warehouse_capacity: maksymalna pojemność magazynu
        :param num_days: liczba dni w ciągu których prowadzone są zbiory
        """
        self.fruit_types = fruit_types
        self.employee_cost = employee_cost
        self.warehouse_cost = warehouse_cost
        self.max_daily_harvest = max_daily_harvest
        self.warehouse_capacity = warehouse_capacity
        self.num_draws = 0
        self.num_ok_draws = 0
        self.num_days = num_days

    #funkcja do użycia po zmianie rozwiązania w jednym dniu jednego typu owoców
    #po zmianie stan magazynowy się zmienia co wpływa na sprzedaż następnego dnia
    #UWAGA nie działa jesli zminimy rozwiązanie dla więcej niz jednego dnia lub typu
    def update_warehouse(self, prev_solution, solution, day, type):
        if day != 0 and day != self.num_days-1:
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

    #losuje dopuszcalnego sąsiada initial_solution
    def draw_solution(self, initial_solution):
        #losuje sąsiada w pobliżu org_solution, sąsiad może być rozwiązaniem nie dopuszczalnym
        #zmienia w losowym dniu losowy typ o sprzedaż na markecie lub na skupie lub zbiory
        def neighbour1(org_solution):
            solution = deepcopy(org_solution)
            prev_solution = deepcopy(org_solution)
            day = random.randint(0, self.num_days-1)
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
            self.update_warehouse(prev_solution, solution, day, type)

            return solution

        #prubuje zznalezc sasiada jesli w ciagu 100 losowan nie znajdzie akceptowalnego rzuca wyjątek
        for _ in range(100):
            sol = neighbour1(initial_solution)
            self.num_draws += 1
            if self.check_if_sol_acceptable(sol):
                self.num_ok_draws += 1
                return sol

        raise Exception("error nie znaleziono otoczenia")

    # metoda wybierająca rodziców
    def selection(self, population):
        parents = []
        while len(parents) < 2:
            candidate1 = random.randint(0, len(population)-1)
            candidate2 = random.randint(0, len(population)-1)
            while candidate1 == candidate2:
                candidate2 = random.randint(0, len(population)-1)
            if population[candidate1][1] > population[candidate2][1]:
                parents.append(population[candidate1])
            else:
                parents.append(population[candidate2])
        #print(f"{parents[0][1]},{parents[1][1]}")
        return parents

    #metoda krzyżująca dwa rozwiązania sol1 i sol2
    def crossover(self, sol1: Solution, sol2: Solution, bruteforce_comapre=False):
        if (not self.check_if_sol_acceptable(sol1)) or (not self.check_if_sol_acceptable(sol2)):
            raise Exception("error podano niedopuszczalne rozw. do skrzyżowania")

        for _ in range(100):
            if bruteforce_comapre:
                begin = 1
                end = 1
                child = Solution(len(self.fruit_types), self.num_days)
                part1 = deepcopy(sol1.days[0:1])
                part2 = deepcopy(sol2.days[1:])
                child.days = part1+part2
            else:
                begin = random.randint(3, self.num_days-2)
                end = random.randint(begin+1, self.num_days-1)
                part1 = deepcopy(sol1.days[0:begin])
                part2 = deepcopy(sol2.days[begin:end])
                part3 = deepcopy(sol1.days[end:])
                child = Solution(len(self.fruit_types), self.num_days)
                child.days = part1 + part2 + part3

            for i in range(len(self.fruit_types)-1):
                self.update_warehouse(sol2, child, begin - 1, i)
                self.update_warehouse(sol1, child, end - 1, i)

            if self.check_if_sol_acceptable(child):
                return child
        return None

    # znajduje jak najlepsze rozwiazanie metoda Symulowanego Wyżarzania
    def simulated_annealing(self, T_start, T_stop, iterations_in_temp, epsilon, iterations_epsilon, alpha,
                            initial_sol, verbose=True, bruteforce_comapre=None):
        """

        :param T_start:
        :param T_stop:
        :param iterations_in_temp:
        :param epsilon:
        :param iterations_epsilon:
        :param alpha:
        :param initial_sol:
        :param verbose:
        :param bruteforce_comapre: lista stretegii zbiorów przekazywana podczas porównania z ręczym obliczeniem
                                    rozwiązania
        :return:
        """
        solution = self.create_initial_population(bruteforce_comapre=bruteforce_comapre)[initial_sol][0]
        best_solution = solution
        best_profit = self.calculate_objective_fun(solution)
        T = T_start                         #Temperatura
        sol_fun_list = []                   #lista długości iterations_epsilon ostatnich rozw (potrzebna do 2 kryt stopu)
        self.num_draws = 0
        self.num_ok_draws = 0
        profit_lst = []

        while T > T_stop:               #1 kryterium stopu
            if verbose:
                print(f"best profit: {best_profit} | temperature: {T}")
            for j in range(iterations_in_temp):
                candidate_sol = self.draw_solution(solution)        #losowanie sąsiada z otoczenia
                candidate_sol_fun = self.calculate_objective_fun(candidate_sol)     #wyznaczenie fun celu dla wylosowanego
                delta = candidate_sol_fun - self.calculate_objective_fun(solution)  #zmiana wart funkcji celu pomiędzy starym a nowym rozw
                if delta >= 0:      #polepszenie rozwiazania
                    solution = candidate_sol
                    profit_lst.append(candidate_sol_fun)
                    if candidate_sol_fun > best_profit:
                        best_solution = solution
                        best_profit = candidate_sol_fun
                else:
                    drawn_num = np.random.rand()
                    if drawn_num < math.exp(delta/T):
                        solution = candidate_sol    #przyjęcie jako gorszego rozwiązania jako aktualne
            T = alpha * T       #liniowa zmiana tempertury
            while len(sol_fun_list) > iterations_epsilon - 1:
                sol_fun_list.pop(0)
            sol_fun_list.append(self.calculate_objective_fun(solution))

            if len(sol_fun_list) == iterations_epsilon and max(sol_fun_list)-min(sol_fun_list) <= epsilon:
                print("kryt stopu 2")
                return best_solution, best_profit, (self.num_draws, self.num_ok_draws), profit_lst
        print("kryt stopu 1")
        return best_solution, best_profit, (self.num_draws, self.num_ok_draws), profit_lst

    def genetic_algorithm(self, max_iter_no_progress, max_iter, replacement_rate=0.5, mutation_proba=0.2,
                          verbose: bool=True, random_demand_rate: bool=False, return_best_results: bool=False, bruteforce_comapre=None):
        """
        Metoda znajdująca rozwiązanie optymalne za pomocą algorytmu genetycznego

        :param bruteforce_comapre: lista stretegii zbiorów przekazywana podczas porównania z ręczym obliczeniem
                                    rozwiązania
        :param return_best_results: Parametr używany podczas eksperymentów. Jeśli jest ustawiony na True
                                    to funkcja zwraca dodatkową listę z najlepszymi wynikami w każdej iteracji.
        :param random_demand_rate: Parametr random_demand_rate przekazywaniy do funkcji generującej
                                  rozwiązanie początkowe.
        :param max_iter_no_progress: Maksymalna ilość iteracji bez poprawy funkcji celu
        :param max_iter: Łączna maksymalna ilość iteracji algorytmu
        :param replacement_rate: Procent populacji jaki jest zastępowany przez potomków
                                w każdej iteracji algorytmu (liczba z zakresu 0-1).
        :param mutation_proba: Prawdopodobieństwo wystąpienia mutacji u dziecka
                               (liczba z zakresu 0-1).
        :param verbose: wyświetlaj numer iteracji i dotychczas najlepszy wynik
        :return: Znalezione rozwiązanie, koszt rozwiązania, ilość wykonanych iteracji
        """
        solutions = self.create_initial_population(random_demand_rate=random_demand_rate, bruteforce_comapre=bruteforce_comapre)

        # population to lista list, w której przechowujemy rozwiązania.
        # Poszczególne elementy listy population to dwuelementowe
        # listy o następującej postaci [rozwiązanie, funkcja celu dla rozwiązania]
        population = [[sol[0], self.calculate_objective_fun(sol[0])] for sol in solutions]
        # sortowanie populacji po wartości funkcji celu
        population = sorted(population, key=lambda x: x[1])

        # licznik iteracji bez poprawy funkcji celu
        iter_with_no_progress = 0
        # licznik wszystkich iteracji
        iterations = 0
        # wartość funkcji celu dla najleoszego rozwiązania
        best_cost = -np.inf

        # lista best_results przechowuje najlepsze wyniki w każdej iteracji
        best_results = []

        while iter_with_no_progress <= max_iter_no_progress and iterations <= max_iter:
            # Kryterium stopu algorytmu jest osiągnięcie maksymalnej liczby iteracji bez poprawy
            # lub osiągnięcie maksymalnej iteracji w ogóle.
            iterations += 1

            # licznik dzieci utworzonych w danej iteracji
            children_count = 0
            # lista przechowująca nowe rozwiązania (dzieci)
            children = []
            # aktualny procent populacji, która zostanie
            # zastąpiona przez nowych członków
            replaced = 0

            while replaced < replacement_rate:
                # nowych potomków tworzymy tak długo dopóki procent
                # populacji jaki zostanie zastąpiony przez potomków
                # jest mniejszy niż replacement_rate

                # w każdej iteracji tworzę 2 nowych potomków
                # więc aktualizuję children_count i replaced
                children_count += 2
                replaced = children_count/len(population)

                parents = self.selection(population)
                parents = [parents[i][0] for i in range(len(parents))]

                testing = False
                if bruteforce_comapre is not None:
                    testing = True

                child1 = self.crossover(parents[0], parents[1], bruteforce_comapre=testing)
                child2 = self.crossover(parents[1], parents[0], bruteforce_comapre=testing)

                if child1 is None or child2 is None:
                    children_count -= 2
                    replaced = children_count / len(population)
                    continue

                # następnie losujemy liczbę z zakresu 0-1 i sprawdzamy
                # czy mamy dokonać mutacji jednego oraz drugiego dziecka.
                if random.uniform(0, 1) <= mutation_proba:
                    try:
                        child1 = self.draw_solution(child1, 1)
                    except:
                        pass
                if random.uniform(0, 1) <= mutation_proba:
                    try:
                        child2 = self.draw_solution(child2, 1)
                    except:
                        pass

                # dołączenie dzieci do listy children
                children.append(deepcopy(child1))
                children.append(deepcopy(child2))

            for i in range(len(children)):
                # podmienienie najsłabszych elementów z populacji przez
                # nowych potomków
                population[i] = [deepcopy(children[i]), self.calculate_objective_fun(children[i])]
            # ponowne sortowanie populacji zawierającej nowych członków
            population = sorted(population, key=lambda x: x[1])

            if population[-1][1] > best_cost:
                # jeślli funkcja celu najlepszego członka obecnej populacji jest
                # lepsza niż dotychczasowo najlepsza to podmień najlepszy koszt
                # oraz zresetuj licznik iteracji bez poprawy
                best_cost = population[-1][1]
                iter_with_no_progress = 0
            else:
                # w innym przypadku zwiększamy licznik iteracji bez poprawy
                iter_with_no_progress += 1

            if verbose:
                print(f"best profit: {population[-1][1]} | iteration number: {iterations}")
            if return_best_results:
                best_results.append(population[-1][1])

        if return_best_results:
            return population[-1][0], population[-1][1], iterations, best_results
        else:
            return population[-1][0], population[-1][1], iterations

    def generate_all_to_wholesale(self, harvest_strategies: List[List]):
        """
        Funkcja generuje startowe rozwiązanie z założeniem, że wszystkie zebrane
        owoce idą na sprzedaż do skupu tego samego dnia. Parametr harvest_strategies to
        lista list gdzie wewnątrzne listy to poszczególne strategie zbiorów. Strategia składa
        się z ilości dni przez ile dana strategia obowiązuje oraz listy odpowiadającej maksymalnej
        ilości owoców z danego typu zbieranej w ciągu dnia. Przykładowo mamy 3 typy owoców: jabłka, gruszki, śliwki.
        harvest_strategies może wyglądać następująco:

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

        solution = Solution(fruit_types_count, self.num_days)

        day_id = 0
        for strategy in harvest_strategies:
            harvest_per_type = strategy[1]
            for i in range(strategy[0]):
                for fruit_id, f_type in enumerate(self.fruit_types):
                    # Ile owoców wciąż mamy w sadzie
                    f_left = fruits_left[f_type.name]

                    # Określenie wielkości zbiorów danego dnia
                    if harvest_per_type[fruit_id] <= f_left:
                        solution.days[day_id].harvested[fruit_id] = harvest_per_type[fruit_id]
                        fruits_left[f_type.name] -= harvest_per_type[fruit_id]
                    else:
                        solution.days[day_id].harvested[fruit_id] = f_left
                        fruits_left[f_type.name] -= f_left
                    solution.days[day_id].sold_wholesale[fruit_id] = solution.days[day_id].harvested[fruit_id]
                day_id += 1

        return solution

    def generate_satisfy_demand(self, harvest_strategies: List[List], demand_rate: float = 1, random_demand_rate: bool = False):
        """
        Funkcja generuje startowe rozwiązanie z założeniem, że każdego dnia staramy się spełnić
        popyt na dany owoc. Parametr demand_rate przyjmujący wartości z zakresu [0-1] określa
        jaki procent popytu dla każdego owocu staramy się zadowolić naszym startowym rozwiązaniem
        Przykładowo demand_rate=0.6 oznacza, że każdego dnia staramy się zaspokoić 60% popytu
        na każdy owoc aż do wyczerpania zasobów owoców. Parametr harvest_strategies działa identycznie jak w
        funkcji generate_all_to_wholesale.

        :param random_demand_rate: jeśli True to dla każdego owocu losuj demand_rate z przedziału [0.3-1]
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

        solution = Solution(fruit_types_count, self.num_days)

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
                for fruit_id, f_type in enumerate(self.fruit_types):
                    # Ile owoców wciąż mamy w sadzie
                    f_left = fruits_left[f_type.name]

                    # Określenie wielkości zbiorów danego dnia
                    if harvest_per_type[fruit_id] <= f_left:
                        solution.days[day_id].harvested[fruit_id] = harvest_per_type[fruit_id]
                        fruits_left[f_type.name] -= harvest_per_type[fruit_id]
                    else:
                        solution.days[day_id].harvested[fruit_id] = f_left
                        fruits_left[f_type.name] -= f_left

                    if random_demand_rate:
                        demand_rate = random.uniform(0.3, 1)

                    # Popyt jaki staramy się zaspokoić
                    demand = int(f_type.demand[day_id] * demand_rate)
                    if day_id == 0:
                        # Pierwszy dzień (brak magazynu z dnia poprzedniego)
                        if demand >= solution.days[day_id].harvested[fruit_id]:
                            solution.days[day_id].sold_market[fruit_id] = solution.days[day_id].harvested[fruit_id]
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = 0
                        else:
                            solution.days[day_id].sold_market[fruit_id] = demand
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = solution.days[day_id].harvested[fruit_id] - demand
                            solution.days[day_id].sold_wholesale[fruit_id] = int(percent_to_wholesale * leftovers)
                    else:
                        if demand > solution.days[day_id - 1].warehouse[fruit_id]:
                            # Popyt większy niż ilość owoców z magazynu z poprzedniego dnia
                            solution.days[day_id].sold_market[fruit_id] = solution.days[day_id - 1].warehouse[fruit_id]
                            if demand - solution.days[day_id - 1].warehouse[fruit_id] >= solution.days[day_id].harvested[fruit_id]:
                                # Sytuacja gdy owoce z magazynu nie zaspokoiły popytu na targu a ilość
                                # zebranych owoców jest na tyle niska że możemy wszystkie również przeznaczyć
                                # do sprzedaży na targu
                                solution.days[day_id].sold_market[fruit_id] += solution.days[day_id].harvested[fruit_id]
                                # pozostałości przeznaczone do skupu lub magazynu
                                leftovers = 0
                            else:
                                # Sytuacja gdy owoce z magazynu nie zaspokoiły popytu na targu a ilość
                                # zebranych owoców wystarcza na zaspokojenie tego popytu oraz zostaje nam
                                # jeszcze trochę wolnych owoców
                                solution.days[day_id].sold_market[fruit_id] = demand
                                # pozostałości przeznaczone do skupu lub magazynu
                                leftovers = solution.days[day_id].harvested[fruit_id] - (demand - solution.days[day_id - 1].warehouse[fruit_id])
                                solution.days[day_id].sold_wholesale[fruit_id] = int(percent_to_wholesale * leftovers)
                        elif demand == solution.days[day_id - 1].warehouse[fruit_id]:
                            # Popyt równy owocom z magazynu
                            solution.days[day_id].sold_market[fruit_id] = solution.days[day_id - 1].warehouse[fruit_id]
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = solution.days[day_id].harvested[fruit_id]
                            solution.days[day_id].sold_wholesale[fruit_id] = int(percent_to_wholesale * leftovers)
                        else:
                            # Popyt mniejszy niż owoce z magazynu
                            solution.days[day_id].sold_market[fruit_id] = demand
                            # pozostałości przeznaczone do skupu lub magazynu
                            leftovers = solution.days[day_id].harvested[fruit_id]
                            solution.days[day_id].sold_wholesale[fruit_id] = int(percent_to_wholesale * leftovers) + \
                                                                 solution.days[day_id - 1].warehouse[fruit_id] - demand

                    # Jeśli część owoców przeznaczona do magazynu zmieści się w nim to możemy je tam wsadzić.
                    # W innym wypadku również trafiają one do skupu.
                    if leftovers - int(percent_to_wholesale * leftovers) + sum(
                            solution.days[day_id].warehouse) <= self.warehouse_capacity:
                        solution.days[day_id].warehouse[fruit_id] = leftovers - int(percent_to_wholesale * leftovers)
                    else:
                        solution.days[day_id].sold_wholesale[fruit_id] += leftovers - int(percent_to_wholesale * leftovers)
                day_id += 1

        return solution

    def create_initial_population(self, random_demand_rate: bool = False, bruteforce_comapre=None):
        """
        Funkcja generuje populację rozwiązań początkowych. Funckja zwraca listę
        krotek, gdzie pierwszy element krotki to rozwiązanie a drugi to informacja
        czy rozwiązanie spełnia ograniczenia.

        :param bruteforce_comapre: lista stretegii zbiorów przekazywana podczas porównania z ręczym obliczeniem
                                    rozwiązania
        :return:
        """
        if bruteforce_comapre is not None:
            solutions = []
            for strategy in bruteforce_comapre:
                solution = self.generate_all_to_wholesale(harvest_strategies=strategy)
                solutions.append(solution)
                solution = self.generate_satisfy_demand(harvest_strategies=strategy, demand_rate=1)
                solutions.append(solution)
                solution = self.generate_satisfy_demand(harvest_strategies=strategy, demand_rate=0.5)
                solutions.append(solution)
            result = []
            for el in solutions:
                result.append((el, self.check_if_sol_acceptable(el)))
            return result

        fruit_types_count = len(self.fruit_types)

        solutions = []

        # Zmienne har_per_type określają ile owoców danego typu
        # chcemy zbierać. Zakładamy tutaj, że wszystkich owoców zbieramy
        # po równo. Musimy również pamiętać że łączne zbiory nie mogą
        # przekroczyć dziennego limitu zbiorów. Symbol // oznacza dzielenie
        # całkowite.
        har_per_type1 = self.max_daily_harvest // fruit_types_count
        har_per_type2 = int(0.9 * self.max_daily_harvest) // fruit_types_count
        har_per_type3 = int(0.7 * self.max_daily_harvest) // fruit_types_count
        har_per_type4 = int(0.5 * self.max_daily_harvest) // fruit_types_count

        # lista do przechowywania poszczególnych strategii zbiorów
        all_strategies = []

        x = self.num_days//4
        # harvest_strategies1 to lista będąca strategią zbiorów
        harvest_strategies1 = []

        # zapis [har_per_type1] * fruit_types_count oznacza stworzenie
        # listy o długości fruit_types_count wypełnionej wartością har_per_type1.
        harvest_per_type = [har_per_type1] * fruit_types_count
        harvest_strategies1.append([x, harvest_per_type])
        harvest_per_type = [har_per_type2] * fruit_types_count
        harvest_strategies1.append(([x, harvest_per_type]))
        harvest_per_type = [har_per_type3] * fruit_types_count
        harvest_strategies1.append(([x, harvest_per_type]))
        harvest_per_type = [har_per_type4] * fruit_types_count
        harvest_strategies1.append(([self.num_days-3*x, harvest_per_type]))
        all_strategies.append(harvest_strategies1)

        harvest_strategies2 = []
        harvest_per_type = [har_per_type3] * fruit_types_count
        harvest_strategies2.append([x, harvest_per_type])
        harvest_per_type = [har_per_type4] * fruit_types_count
        harvest_strategies2.append(([x, harvest_per_type]))
        harvest_per_type = [har_per_type1] * fruit_types_count
        harvest_strategies2.append(([x, harvest_per_type]))
        harvest_per_type = [har_per_type2] * fruit_types_count
        harvest_strategies2.append(([self.num_days-3*x, harvest_per_type]))
        all_strategies.append(harvest_strategies2)

        # Strategia polegająca na przeznaczaniu całych zbiorów do skupu
        # z założeniem, że z każdego typu zbieramy tyle samo owoców
        # (elemety w liście harvest_per_type są równe)
        solution = self.generate_all_to_wholesale(all_strategies[0])
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        solution = self.generate_all_to_wholesale(all_strategies[1])
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        # Strategia polegająca na zaspokajaniu popytu
        # z założeniem, że z każdego typu zbieramy tyle samo owoców
        # (elemety w liście harvest_per_type są równe)
        solution = self.generate_satisfy_demand(all_strategies[0], 0.6, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(all_strategies[0], 1, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))

        solution = self.generate_satisfy_demand(all_strategies[1], 0.6, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(all_strategies[1], 1, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))

        all_strategies2 = deepcopy(all_strategies)
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

        # Edycja listy strategii zbiorów w taki sposób, że
        # dla sąsiadujących ze sobą typów owoców w sposób losowy
        # dobieramy różnicę z pewnego zakresu i dla jednego owocu
        # z pary dodajemy tą różnicę a dla drugiego odejmujemy.
        # Przykładowo ze strategii [20, 20, 20, 20, 20] może powstać
        # strategia [23, 17, 16, 24, 20]. Dla pierwszej pary różnica
        # to -3, dla drugiej 4 a piąta liczba nie ma pary więc została taka jak oryginalnie.
        for i in range(len(all_strategies2)):
            # Pętla po listach ze strategiami (elementy z all_strategies)
            for strat_id in range(len(all_strategies2[i])):
                # Pętla po danych strategiach w danej liście ze strategiami
                # (elementy na przykład z harvest_strategies1)
                for fruit_id in range(0,len(all_strategies2[i][strat_id][1]),2):
                    # Pętla po zbiorach danego typu owocu w danej strategii
                    if fruit_id <= len(all_strategies2[i][strat_id][1])-2:
                        percent = random.uniform(0.85, 1.15)
                        defaul_fruits = all_strategies2[i][strat_id][1][fruit_id]
                        fruit_delta = defaul_fruits-int(defaul_fruits * percent)
                        all_strategies2[i][strat_id][1][fruit_id] -= fruit_delta
                        all_strategies2[i][strat_id][1][fruit_id+1] += fruit_delta

        # Strategia polegająca na przeznaczaniu całych zbiorów do skupu
        # ze zmienionym parametrem harvest_per_type
        solution = self.generate_all_to_wholesale(all_strategies[0])
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        solution = self.generate_all_to_wholesale(all_strategies[1])
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        # Strategia polegająca na zaspokajaniu popytu
        # ze zmienionym parametrem harvest_per_type
        solution = self.generate_satisfy_demand(all_strategies[0], 0.6, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(all_strategies[0], 1, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))

        solution = self.generate_satisfy_demand(all_strategies[1], 0.6, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(all_strategies[1], 1, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))



        # Strategia polegająca na przeznaczaniu całych zbiorów do skupu
        # ze zmienionym parametrem harvest_per_type
        solution = self.generate_all_to_wholesale(all_strategies2[0])
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        solution = self.generate_all_to_wholesale(all_strategies2[1])
        solutions.append(deepcopy(solution))
        solution.days = solution.days[::-1]
        solutions.append(deepcopy(solution))

        # Strategia polegająca na zaspokajaniu popytu
        # ze zmienionym parametrem harvest_per_type
        solution = self.generate_satisfy_demand(all_strategies2[0], 0.6, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(all_strategies2[0], 1, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))

        solution = self.generate_satisfy_demand(all_strategies2[1], 0.6, random_demand_rate=random_demand_rate)
        solutions.append(deepcopy(solution))
        solution = self.generate_satisfy_demand(all_strategies2[1], 1, random_demand_rate=random_demand_rate)
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
        # Z ograniczenia trzeciego zrezygnowaliśmy
        #three = check_minimum_amount_sold(solution, self.fruit_types)
        four = check_warehouse_limits(solution, self.warehouse_capacity)
        five = check_if_warehouse_sold(solution)
        six = check_if_today_amount_correct(solution)
        seven = check_if_non_negative(solution)
        eight = check_if_sold_market_less_than_demand(solution, self.fruit_types)

        #print(one, two, four, five, six)

        return one and two and four and five and six and seven and eight

    def format_solution(self, solution: Solution):
        txt = ""
        for i, day in enumerate(solution.days):
            harvested_types = "zebrane: "
            market_types = "sprzedane na targu: "
            wholesale_types = "sprzedane w skupie: "
            warehouse_types = "do magazynu: "

            for j in range(len(day.harvested)):
                harvested_types += f"{self.fruit_types[j].name}:{day.harvested[j]}, "
                market_types += f"{self.fruit_types[j].name}:{day.sold_market[j]}, "
                wholesale_types += f"{self.fruit_types[j].name}:{day.sold_wholesale[j]}, "
                warehouse_types += f"{self.fruit_types[j].name}:{day.warehouse[j]}, "

            mark_len = max(len(harvested_types), len(market_types), len(wholesale_types), len(warehouse_types))
            pause = "".join(['='] * mark_len)

            txt += f"{pause}\nDay {i + 1}\n{harvested_types}\n{market_types}\n" \
                   f"{wholesale_types}\n{warehouse_types}\n{pause}\n\n"
        txt += "\n"
        return txt

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





