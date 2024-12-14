import random

from inst import Code

# Read 5 unique numbers from range 1 .. 8 (random order)
# and print out 3 missing number

NUM_READS = 5
NUM_NUMBERS = 8
TOTAL_SUM = 2 ** (NUM_NUMBERS + 1) - 2

assert TOTAL_SUM < 1_000_000

# 1 => 2^7
# 8 => 2^1

c = Code(f"""
set D {TOTAL_SUM}
dec C {NUM_READS}

next_val:
  inc C 1
  set A C
  if C < 1 goto next else +2
  read A

calc:
  set B 1
_calc_inner:
  inc B B
  inc A 1
  if A <= {NUM_NUMBERS} goto _calc_inner else next
  

  if D >= B goto next else no_print
  dec D B
  if C < 1 goto next_val else next
  pbox C
  pnl
no_print:
  if C >= {NUM_NUMBERS} goto next else next_val
  
""")


print(" --- url params ---")
print(c.get_code())

print("\n --- code ---")
print(c.get_code_txt(with_line_no=True))


def check_nums(numbers):
    input = list(numbers)
    random.shuffle(input)
    expected_output = [x for x in range(1, 9) if x not in input]
    c.run_test(input, expected_output)


print("--- all test cases ---")
for i in range(1, 7):
    for j in range(i + 1, 8):
        for k in range(j + 1, 9):
            check_nums(set(x for x in range(1, 9) if x not in [i, j, k]))

