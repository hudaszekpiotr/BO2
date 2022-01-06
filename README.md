# BO2
Projekt z BO2 model zbierania owoców w sadzie

Do poprawnego działania programu konieczne jest zainstalowanie pakietów z pliku ```requirements.txt```

## Instrukcja obsługi interfejsu
Aby móc korzystać z terminala do obsługi programu należy w terminalu przejść folderu zawierającego m.in. foldery ```project_app``` oraz ```wyniki```.

Przykładowa komenda uruchamiająca algorytm symulowanego wyrzarzania:
```python -m project_app annealing --t_start 5000 --t_stop 800 --iter_in_temp 100 --epsilon 2 --iter_epsilon 10 --alpha 0.99 --initial_sol 11 --verbose```

Znaczenie poszczególnych parametrów:
- ```--t_start``` temperatura początkowa
- ```--t_stop``` temperatura końcowa
- ```--iter_in_temp``` ilość iteracji wykonywanych dla jednej temperatury
- ```--epsilon``` minimalna wartość o którą musi zmienić się funkcja celu przez okres iteracji określony przez ```--iter_epsilon``` aby algorytm nie zakończył działania
- ```--iter_epsilon``` ilość iteracji po której algorytm zakończy działanie jeśli funkcja celu nie zmieniła się o więcej niż epsilon
- ```--alpha``` współczynnik o jaki zmniejszana jest temperatura
- ```--initial_sol``` numer rozwiązania początkowego
- ```--verbose``` parametr opcjonalny, jego użycie skutkuje wyświetlaniem aktualnej temperatury oraz najlpeszego zysku w trakcie pracy algorytmu


Przykładowa komenda uruchamiająca algorytm genetyczny:
```python -m project_app genetic --iter_no_progress 600 --max_iter 3000 --replacement_rate 0.6 --mutation_proba 0.7 --verbose```

Znaczenie poszczególnych parametrów:
- ```--iter_no_progress``` maksymalna liczba iteracji bez poprawy wyniku
- ```--max_iter``` maksymalna liczba  iteracji
- ```--replacement_rate``` procent populacji zastępowany przez nowe pokolenie po każdej iteracji
- ```--mutation_proba``` prawdopodobieństwo wystąpienia mutacji
- ```--verbose``` parametr opcjonalny, jego użycie skutkuje wyświetlaniem aktualnej iteracji oraz najlpeszego zysku w trakcie pracy algorytmu

## Wyniki
Wyniki działania algorytmu są zapisywanie w folderze ```wyniki``` w pliku ```algorytm_genetyczny.txt``` lub ```algorytm_wyrzarzania.txt```.
