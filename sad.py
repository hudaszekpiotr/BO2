
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

#główna klasa
class Sad:
    def __init__(self):
        pass

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

