# instalogik

Uproszczony programik do pisania kodu do assembly i automatycznego testowania w pythonie. <br />
Umożliwia generowanie url-a, który może być później zaimportowany na stronie assembly.

Aplikacja www do assembly: https://assembly-lang.org/app/

#### Elementy kodu:
  - `box` - oznacza pudełko, możliwe `A`, `B`, `C` lub `D`
  - `value` - oznacza wartość liczbową bądź pudełko
  - `comparator` - porównanie, czyli jeden z napisów: `=`, `>`, `<`, `<=`, `>=`, `!=`
  - `str` - napis, dowolny string, ale spacje muszą być zamienione przez `%20`
  - `address` - oznacza adres w kodzie, czyli etykieta, numer linii lub adres względny, np. `+1`, `-3`

### Dostępne instrukcje:

  - `set <box> <value>` - ustawia wartość pudełka
  - `dec <box> <value>` - dodaje wartość do pudełka
  - `inc <box> <value>` - zmniejsza wartość pudełka
  - `read <box>` - wczytuje wartość do pudełka
  - `goto <address>` - bezwarunkowy skok do podanego adresu
  - `if <value> <coparator> <value> goto <address1> else <address2>` - skok warunkowy, jeśli porównanie jest prawdziwe,
  to program skoczy do `address1` a w innym wypadku pod `address2`
  - `pstr <str>` - wypisanie napisu
  - `pbox <box>` - wypisanie pudełka
  - `pln` - przejście do nowej linii

### Dodatkowe elementy w kodzie:

  - `# komentarz` - puste linie oraz wszystkie rozpoczynające się od kratki są ignorowane
  - `123.  CODE` - liczby na początku linii poprzedzone kropką traktowane są jako numer
     linii, jeśli liczba nie zgadza się z numerem linii to wystąpi błąd
  - `etykieta:`  - oznaczenie miejsca w kodzie, umożliwia wykonać `goto etykieta`


### Szablon programu:

```
from inst import Code

code = Code("""
read A
if A <= 10 goto next else skip_printing_a
pbox A
pnl
skip_printing_a:
pstr That's%20all%20folks
pnl
""")

print("Kod z numerami lini:")
print(code.get_code_txt())

print("\nUrl do importu na stronie:")
print(code.get_code())

def get_result(param):
    expected_result = []
    if param <= 10:
        expected_result.append(f"{param}\n")
    expected_result.append("That's all folks\n")
    return expected_result

print("\n --- tests ---\n")
for param in range(20):
    result = code.run([param], debug=False)  # debug=True wypisze każdy krok
    assert result == get_result(param)

```

### Przykład programu sortującego dwie liczby:
```
start:
    read A
    read B

sortowanie:
    if A >= B goto posortowane else next
    set C A
    set A B
    set B C

posortowane:
    pbox A
    pbox B
```

### Przykład importu kodu z instalogika:

``` 
from inst import Code

code = Code("""
1. Wczytaj do A
2. Wczytaj do B
3. Jeżeli A > B skocz do następnej inaczej skocz do 7
4. Ustaw C na A
5. Ustaw A na B
6. Ustaw B na C
7. Wypisz pudełko A
8. Przejdź do nowej linii
9. Wypisz pudełko B
""")

assert code.run([9, 7], debug=True) == ["7\n", "9"]
```

Na stronie instalogika w konsoli można zaimportować kod:

    set_code_block("<wygenerowany url>")