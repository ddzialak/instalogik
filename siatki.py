from inst import Code

# Rozwiązanie zadania
# InstaLogik - edycja 2024/25 - Etap II
# Program 4. * trudny

code = Code("""
1. Wczytaj do A
2. Wczytaj do B
3. Wczytaj do C
4. Wczytaj do D
5. Jeżeli A ≥ B skocz do następnej inaczej skocz do 18
6. Jeżeli C ≥ D skocz do następnej inaczej skocz do 14
7. Jeżeli C < A skocz do następnej inaczej skocz do 17
8. Wypisz pudełko C
9. Przejdź do nowej linii
10. Jeżeli B ≥ D skocz do następnej inaczej skocz do 13
11. Wypisz pudełko D
12. Skocz do końca
13. Skocz do końca
14. Jeżeli A ≥ D skocz do następnej inaczej skocz do końca
15. Wypisz pudełko D
16. Skocz do końca
17. Przejdź do nowej linii
18. Jeżeli C > D skocz do następnej inaczej skocz do końca
19. Jeżeli B ≥ C skocz do następnej inaczej skocz do końca
20. Wypisz pudełko C
21. Przejdź do nowej linii
22. Jeżeli A ≥ D skocz do następnej inaczej skocz do 24
23. Wypisz pudełko D
24. Skocz do końca
25. Jeżeli B ≥ D skocz do następnej inaczej skocz do końca
26. Wypisz pudełko B
27. Skocz do końca
28. Jeżeli B ≥ D skocz do następnej inaczej skocz do końca
29. Wypisz pudełko D
30. Skocz do końca
31. Wypisz napis '0'
""")

print(code.get_code_txt())
print(code.get_code())

def verify(inp, response):
    t1, t2, w1, w2 = inp
    if w2 > w1:
        w1, w2 = w2, w1
    if t2 > t1:
        t1, t2 = t2, t1

    res = []
    if t1 >= w1:
        res.append(w1)
        if t2 >= w2:
            res.append(w2)
    else:
        if t1 >= w2:
            res.append(w2)
    if not res:
        res.append(0)

    assert res == response, f"Expected {res} but received: {response}"


for m in range(1, 8):
    for j in range(1, 8):
        for w1 in range(1, 8):
            for w2 in range(1, 8):
                result = code.run([m, j, w1, w2], debug=True)
                result = [int(line.strip()) for line in result]
                verify([m, j, w1, w2], result)