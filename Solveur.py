from random import *
from itertools import *

def compteBon(result = -1, a = -1, b= -1, c= -1, d= -1, e = -1, f = -1):
    """Si aucun paramètre n'est rentré, la fonction effectue un tirage
    sinon, elle trouve le bon compte"""

    nbTuiles = 6

    tuiles = [a,b,c,d,e,f]

    def possibilites(listTuiles, nbEtapes, facon):
        nonlocal result, distMin

        for tuile in listTuiles:
            if 0 <= tuile < 1000 and abs(tuile - result) < distMin:
                    try:
                        distMin = abs(tuile - result)
                        facons[distMin][nbEtapes] = facon
                    except:
                        print(distMin, nbEtapes)

        for i1, i2 in combinations(range(len(listTuiles)), 2):
            if listTuiles[i1] < listTuiles[i2]:
                i1, i2 = i2, i1

            tuile1, tuile2 = listTuiles[i1], listTuiles[i2]

            listTemp = listTuiles[:]
            listTemp[i1] += tuile2
            del listTemp[i2]
            possibilites(listTemp, nbEtapes+1, facon + "\n" + str(tuile1) + " + " + str(tuile2) + " = " + str(tuile1 + tuile2) )

            listTemp = listTuiles[:]
            listTemp[i1] -= tuile2
            del listTemp[i2]
            possibilites(listTemp, nbEtapes+1, facon + "\n" + str(tuile1) + " - " + str(tuile2) + " = " + str(tuile1-tuile2) )

            listTemp = listTuiles[:]
            listTemp[i1] *= tuile2
            del listTemp[i2]
            possibilites(listTemp, nbEtapes+1, facon + "\n" + str(tuile1) + " * " + str(tuile2) + " = " + str(tuile1*tuile2) )

            if tuile2 != 0 and tuile1 % tuile2 == 0:
                listTemp = listTuiles[:]
                listTemp[i1] += tuile2
                del listTemp[i2]
                possibilites(listTemp, nbEtapes+1, facon + "\n" + str(tuile1) + " / " + str(tuile2) + " = " + str(tuile1//tuile2) )



    suiteMsg = ""
    if result == -1:
        resultat = randint(100, 1000)

        tuiles = [1,2,3,4,5,6,7,8,9,10]*2 + [25,50,75,100]
        shuffle(tuiles)

        tuiles = tuiles[:6]

        suiteMsg += "\nA trouver : " + str(resultat)

    else:

        distMin = float("inf")

        facons = [ [ () for i in range(nbTuiles) ] for a in range(1001) ]
        possibilites(tuiles, 0, "")

        suiteMsg += "\nResultat : " + str(result) + "\n\nDistance minimale : " + str(distMin) + "\nDes solutions possibles : \n"
        for i in facons[distMin]:
            if i: suiteMsg += i + "\n"

    Msg = "Tuiles : " + " ".join(map(str,tuiles)) + suiteMsg + "\n-"
    return Msg


while 1:
    mode = input("Mode :\n1 - Tirage \n2 - Solveur \n3 - Quitter\n\n")

    if mode == "3":
        break

    elif mode != "1" and mode != "2":
        print("Entree invalide")

    elif mode == "1":
        print(compteBon())

    else:
        result = input("Nombre a atteindre : ")
        if not(result.isdigit()):
            print("Entree invalide")
            continue
        else:
            result = int(result)
            try:
                tuiles = list( map(int, input("Tuiles (séparées par des espaces) : ").split() ) )
            except:
                print("Entree invalide")
                continue
            else:
                a,b,c,d,e,f = tuiles
                print(compteBon(result, a,b,c,d,e,f) )

    print("\n-----------------\n")
