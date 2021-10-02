toInc = 0


for i in range(0, 100, 1):

    toRet = toInc

    print(toRet, end = ' ')

    if toRet <= 0:
        toRet = 0.01
    if toRet >= 1:
        toRet = 0.99

    if toRet == 0.5:
        toRet = 0
    elif toRet > 0.5:
        toRet = (2 * toRet) - 1
    elif toRet < 0.5:
        toRet = -(1 - (2 * toRet))

    print(toRet)

    toInc += 0.01