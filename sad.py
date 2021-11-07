
#postać rozwiązania aby dostać ile owoców sprzedanych 8 dnia typu 2 należy solution.days[8].sold[2]
class Solution:
    def __init__(self, fruit_types):
        self.days = [DaySolution(fruit_types)] * 30

#postać rozwiązania dla 1 dnia
class DaySolution:
    def __init__(self, fruit_types):
        self.sold = [0]*fruit_types         #lista zebranych owoców danego dnia
        self.harvested = [0]*fruit_types    #lista spredanych
        #coś jeszcze jak trzeba

#informacje o danym typie owoców: nazwa, ilośc w sadzie, cena bazowa, cena skupu, mnożnik
class FruitTypeInfo:
    def __init__(self, name, quantity, base_price, wholesale_price, multiplier):
        self.name = name
        self.quantity = quantity
        self.base_price = base_price
        self.wholesale_price = wholesale_price
        self.multiplier = multiplier
    #sprawdza nmożnik w zależności od spełninia popytu
    def check_multiplier(self, demand, sold):
        k = (sold/demand) *100
        return self.multiplier(k)


#główna klasa
class Sad:
    def __init__(self, fruit_types, employee_cost, magaz_cost):
        self.fruit_types = fruit_types
        self.employee_cost = employee_cost
        self.magaz_cost = magaz_cost

    #znajduje jak najlepsze rozwiazanie, docelowo jakiś algorytm np. genetyczny
    def find_solution(self):
        pass

    #sprawdza wszystkie ograniczenia dla danego rozwiązania w najprostszej wersji
    #zwraca bool, w bardziej skomplikowanej informacje gdzie błąd i ewentualnie kara
    def check_if_sol_acceptable(self, solution: Solution):
        #sprawdza czy nie zebraliśmy więcej owoców niż jest w sadzie dla każdego rodzaju
        def check_fruit_limits():
            pass

        #sprawdza czy nie zebraliśmy więcej owoców w żadnym dniu niż robotnicy są w stanie
        def check_workers():
            pass

        #sprawdza czy magazyn nie został przepełniony
        def check_magaz():
            pass

        #inne ograniczenia.....

        #wywołanie powyższych funkcji funkcji i zwrócenie wyniku
        pass

    #oblicza wartośc funkcji celu dla rozwiązania
    def calculate_objective_fun(self, solution: Solution):
        pass



