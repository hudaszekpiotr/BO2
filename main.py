from sad import Sad, FruitTypeInfo, Solution, DaySolution

def main():
    def multiplier1(k):
        if k < 30:
            return 1.5
        if k < 50:
            return 1.2
        if k < 80:
            return 1.1
        if k <= 100:
            return 1

    def multiplier2(k):
        if k < 30:
            return 1.2
        if k < 50:
            return 1.1
        if k < 80:
            return 1.1
        if k <= 100:
            return 1


    gruszki = FruitTypeInfo("gruszki", 100, [0]*30, [0]*30, multiplier1)
    jablka = FruitTypeInfo("jabłka", 100, [0]*30, [0]*30, multiplier2)
    sad = Sad([jablka, gruszki], [0]*15, [0]*10)

    #print(gruszki.check_multiplier(10, 5))
    #print(sad.magaz_cost)

main()