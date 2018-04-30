def printf(x):
    for i in x:
        print(i)
x = [i * 2 for i in range(10) if i % 2 == 0]
printf(x)
