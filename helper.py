#!/usr/bin/python
# -*- coding: utf-8 -*-


def sell_on_market(demand, harvest, warehouse_yesterday):
    """
    Ta funkcja oblicza ile owoców danego typu
    sprzedano w danym dniu na targu i ile z
    tych zebranych i magazywnowach w dniu poprzednim
    zostanie do zmagazynowania lub sprzedania w skupie.

    Zwaracane zmienne:
    sold_market - tyle kilogramów sprzedaliśmy na targu
    warehouse_left - tyle owoców z poprzedniego dnia zostało niesprzedanych na targu
    harvest_left - tyle świeżo zebranych owoców zostało niesprzedanych na targu

    :param demand: Popyt na dany owoc na dany dzień.
    :param harvest: Ilość zebranych owoców danego typu w danym dniu.
    :param warehouse_yesterday: Ilość owoców danego rodzaju,
                                które pozostały z poprzedniego dnia.
    :return: (sold_market, warehouse_left, harvest_left)
    """
    warehouse_left = 0
    harvest_left = 0

    if demand < 0 or harvest < 0 or warehouse_yesterday < 0:
        raise ValueError()

    if warehouse_yesterday == 0:
        # Przypadek gdy nie ma nic w magazynie z poprzedniego dnia
        if demand > harvest:
            # Jeśli popyt jest większy
            # niż zbiory sprzedajemy na targu
            # wszystko co zebraliśmy. Nie zostaje
            # nam nic do zmagazynowania lub sprzedania w skupie.
            sold_market = harvest
        else:
            # Jeśli popyt jest mniejszy lub równy zbiorom to jesteśmy w stanie zaspokoić
            # cały popyt. Zostaje nam również pewna liczba zebranych owoców.
            sold_market = demand
            harvest_left = harvest - demand

    elif demand > warehouse_yesterday:
        # Przypadek gdy mamy w magazynie owoce z poprzedniego dnia
        # lecz jest ich mniej niż wymaga tego popyt.
        if demand-warehouse_yesterday > harvest:
            # Jeśli dzisiejsze zbiory są za małe żeby
            # zaspokoić pozostały popyt, to przeznaczamy całe
            # zbiory na sprzedaż i nie zosają nam nadwyżki
            sold_market = warehouse_yesterday + harvest
        else:
            # Jeśli popyt jest mniejszy lub równy owocom z magazynu plus
            # pewna ilość owoców zebranych, to jesteśmy w stanie zaspokoić
            # cały popyt. Zostaje nam również pewna liczba zebranych owoców.
            sold_market = demand
            harvest_left = harvest - (demand-warehouse_yesterday)
    else:
        # Przypadek, gdy ilość owoców w magazynie jest większa
        # lub równa niż popyt. W tym przypadku jesteśmy w stanie zaspokoić cały popyt
        # oraz zostaje nam pewna ilość owoców z magazynu z poprzedniego dnia i wszystkie
        # owoce zebrane dzisiaj.
        sold_market = demand
        warehouse_left = demand-warehouse_yesterday
        harvest_left = harvest

    return sold_market, warehouse_left, harvest_left

