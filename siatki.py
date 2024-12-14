from inst import Code

# Rozwiązanie zadania
# InstaLogik - edycja 2024/25 - Etap II
# Program 4. * trudny

code = Code("""
1. Wczytaj do A
2. Wczytaj do B
3. Jeżeli A < B skocz do następnej inaczej skocz do wczytaj_c_i_d

# sortowanie, pudełko A niech zawiera większą a B mniejszą lub równą
set C A
set A B
set B C

wczytaj_c_i_d:
    read C
    read D

if A < C goto ignore_c else next
if A < D goto ignore_d else next

# C oraz D są mniejsze od A, zatem najpiew
# należy wypisać większą z nich
print_bigger:
    if C > D goto next else print_d

print_c:
    pbox C
    # pozostaje tylko sprawdzić, czy należy wypisać D
    goto wypisz_D_jesli_nie_wieksze_od_B

print_d:
    pbox D
    # wypsaliśmy D, zatem należy jeszcze sprawdzić czy C jest większe od B
    # i jeśli tak, to wypisać B. mamy już podobny fragment, tylko że z pudełkiem
    # D a nie C, zatem możemy skopiować C do D i wykorzystać ten sam fragment kodu
    set D C
    goto wypisz_D_jesli_nie_wieksze_od_B

wypisz_D_jesli_nie_wieksze_od_B:
    if B >= D goto next else end
    pnl
    pbox D
    goto end

print_zero:
    pstr 0
    goto end

ignore_c:
    # wiemy że trzeba odrzucić C, pozostaje zatem
    # wypisać pudełko D jeśli mniejsze lub równe A, inaczej zero
    if A >= D goto next else print_zero
    pbox D
    goto end

ignore_d:
    # wiemy że trzeba odrzucić D, pozostaje zatem
    # wypisać pudełko C jeśli mniejsze lub równe A, inaczej zero
    if A >= C goto next else print_zero
    pbox C
""")

print("--- code ---")
print(code.get_code_txt())

print("\n--- url params ---")
print(code.get_code())

def get_expected_result(inp):
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
    return res


print("\n --- tests ---")
for m in range(1, 8):
    for j in range(1, 8):
        for w1 in range(1, 8):
            for w2 in range(1, 8):
                input_vals = [m, j, w1, w2]
                expected_result = get_expected_result(input_vals)
                code.run_test(input_vals, expected_result, debug=False)
