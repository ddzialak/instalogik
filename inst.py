import re
import urllib
import urllib.parse
from typing import Dict


def box_to_id(box):
    assert box in {
        "A",
        "B",
        "C",
        "D",
    }, "Invalid box specification {box!r} (expected char A, B, C or D.)"
    return ord(box) - ord("A")


def is_a_box(val):
    return val in {"A", "B", "C", "D"}


def is_a_positive_number(val):
    return str(val).isdigit()


OP_TO_CODE = {val: idx for idx, val in enumerate(["<", "<=", "=", "!=", ">=", ">"])}


def operator_to_code(val):
    assert val in OP_TO_CODE, f"Unrecognized operator {val}"
    return OP_TO_CODE.get(val)


def check_cond(op, v1, v2):
    if op == Code.IF_LT:
        return v1 < v2
    if op == Code.IF_LTE:
        return v1 <= v2
    if op == Code.IF_EQ:
        return v1 == v2
    if op == Code.IF_NEQ:
        return v1 != v2
    if op == Code.IF_GTE:
        return v1 >= v2
    if op == Code.IF_GT:
        return v1 > v2
    raise ValueError(f"Unknown compare op: {op}")


class Instruction:
    def __init__(self, pos):
        self.pos = pos
        self.code = None
        self.debug_info = None

    def resolve_addr(self, addr, labels):
        addr = labels.get(addr, addr)
        if isinstance(addr, int):
            return addr
        if addr[0] in {"+", "-"}:
            return self.pos + int(addr)
        try:
            return int(addr)
        except ValueError:
            pass
        raise ValueError(f"Undefined address '{addr}' in line {self.pos}: {self.debug_info}")

    def resolve_labels(self, labels):
        pass

    def exec(self, machine):
        pass

    def next(self, machine):
        machine.ptr += 1


INSTR = {
    "if": ["b", "s", "in", "ls", "lf"],
    "dec": ["b", "in"],
    "inc": ["b", "in"],
    "set": ["b", "in"],
    "read": ["b"],
    "goto": ["j"],
    "pstr": ["s"],
    "pbox": ["b"],
    "pln": [],
}


def code_instr(pos, instr, *args):
    idx = pos - 1
    assert instr in INSTR
    keys = INSTR[instr]
    assert len(keys) == len(args), f"{instr} bad number of arguments {keys} <> {args}"
    props = [f"i{idx}_t={instr}"]
    for key, _val in zip(keys, args):
        val = str(_val).upper()  # here should be only number or boxes
        assert (
            instr == "pstr" or isinstance(_val, int) or val in "ABCD"
        ), f"Unexpected value: {_val!r}"

        if key == "b":
            val = box_to_id(val)
        elif key in [
            "j",
            "ls",
            "lf",
        ]:  # convert addresses from line number to idx in array
            val = int(val) - 1

        props.append(f"i{idx}_{key}={val}")
    return "&".join(props)


class IfInstr(Instruction):
    def __init__(self, pos, arg1, op, arg2, then_goto, else_goto):
        super().__init__(pos)
        self.arg1 = arg1
        self.op = op
        self.op_code = operator_to_code(op)
        self.arg2 = arg2
        self.then_goto = then_goto
        self.else_goto = else_goto

    def resolve_labels(self, labels):
        self.then_goto = self.resolve_addr(self.then_goto, labels)
        self.else_goto = self.resolve_addr(self.else_goto, labels)
        self.code = code_instr(
            self.pos,
            "if",
            self.arg1,
            self.op_code,
            self.arg2,
            self.then_goto,
            self.else_goto,
        )
        self.debug_info = f"if {self.arg1} {self.op} {self.arg2} goto {self.then_goto} else {self.else_goto}"

    def next(self, machine):
        assert self.code is not None
        left_val = machine.buckets[self.arg1]
        right_val = machine.getval(self.arg2)
        if check_cond(self.op, left_val, right_val):
            machine.ptr = self.then_goto
        else:
            machine.ptr = self.else_goto


class ReadInstr(Instruction):
    def __init__(self, pos, box):
        assert is_a_box(box), f'Invalid "read" instruction, {box} is not a box.'
        super().__init__(pos)
        self.to_box = box
        self.code = code_instr(self.pos, "read", self.to_box)
        self.debug_info = f"read {self.to_box}"

    def exec(self, machine):
        machine.buckets[self.to_box] = machine.read()


class IncInstr(Instruction):
    def __init__(self, pos, box, val):
        super().__init__(pos)
        assert is_a_box(box), "Expected box but get {box}"
        self.box = box
        self.val = val
        self.code = code_instr(self.pos, "inc", self.box, self.val)
        self.debug_info = f"inc {self.box} {self.val}"

    def exec(self, machine):
        machine.buckets[self.box] += machine.getval(self.val)
        assert (
            -999_999 <= machine.buckets[self.box] <= 999_999
        ), f"Overflow on {self.box} ({machine.buckets[self.box]})"


class DecInstr(Instruction):
    def __init__(self, pos, box, val):
        super().__init__(pos)
        self.box = box
        self.val = val
        self.code = code_instr(self.pos, "dec", self.box, self.val)
        self.debug_info = f"dec {self.box} {self.val}"

    def exec(self, machine):
        machine.buckets[self.box] -= machine.getval(self.val)
        assert (
            -999_999 <= machine.buckets[self.box] <= 999_999
        ), f"Overflow on {self.box} ({machine.buckets[self.box]})"


class SetInstr(Instruction):
    def __init__(self, pos, box, val):
        super().__init__(pos)
        self.box = box
        self.val = val
        assert is_a_box(val) or is_a_positive_number(val)
        self.code = code_instr(self.pos, "set", self.box, self.val)
        self.debug_info = f"set {self.box} {self.val}"

    def exec(self, machine):
        val = machine.getval(self.val)
        assert -999_999 <= val <= 999_999, f"Invalid value {val} (out of range!)"
        machine.buckets[self.box] = val


class GotoInstr(Instruction):
    def __init__(self, pos, addr):
        super().__init__(pos)
        self.addr = addr

    def resolve_labels(self, labels):
        self.addr = self.resolve_addr(self.addr, labels)
        self.code = code_instr(self.pos, "goto", self.addr)
        self.debug_info = f"goto {self.addr}"

    def next(self, machine):
        assert self.code is not None
        machine.ptr = self.addr


class PstrInstr(Instruction):
    def __init__(self, pos, val):
        super().__init__(pos)
        self.val = urllib.parse.unquote(str(val))
        self.code = code_instr(self.pos, "pstr", self.val)
        self.debug_info = f"pstr {self.val}"

    def exec(self, machine):
        machine.add_output_line(self.val)


class PboxInstr(Instruction):
    def __init__(self, pos, box):
        super().__init__(pos)
        self.box = box
        self.code = code_instr(self.pos, "pbox", self.box)
        self.debug_info = f"pbox {self.box}"

    def exec(self, machine):
        machine.add_output_line(str(machine.buckets[self.box]))


class PnlInstr(Instruction):
    def __init__(self, pos):
        super().__init__(pos)
        self.code = code_instr(self.pos, "pln")
        self.debug_info = "pnl"

    def exec(self, machine):
        machine.add_output_line("\n")


class Code:
    A = "A"
    B = "B"
    C = "C"
    D = "D"

    IF_LT = "<"
    IF_LTE = "<="
    IF_EQ = "="
    IF_NEQ = "!="
    IF_GTE = ">="
    IF_GT = ">"

    def __init__(self, code_txt=None):
        self.labels = {"next": "+1", "n": "+1"}
        self.code_lines: Dict[int, Instruction] = {}
        if code_txt:
            for line in code_txt.splitlines():
                self.add_line(line)

    @property
    def pos(self):
        return len(self.code_lines)

    def resolve_labels(self):
        self.labels["next"] = '+1'
        self.labels["end"] = self.next_line_no()
        for instr in self.code_lines.values():
            instr.resolve_labels(self.labels)

    def append(self, code_i):
        pos = self.next_line_no()
        self.code_lines[pos] = code_i

    def label(self, name):
        assert name not in self.labels, f"Overused label {name}"
        self.labels[name] = self.next_line_no()

    def i_if(self, arg1, op, arg2, then_goto, else_goto):
        self.append(IfInstr(self.next_line_no(), arg1, op, arg2, then_goto, else_goto))

    def i_read(self, box):
        self.append(ReadInstr(self.next_line_no(), box))

    def i_dec(self, box, val):
        self.append(DecInstr(self.next_line_no(), box, val))

    def i_inc(self, box, val):
        self.append(IncInstr(self.next_line_no(), box, val))

    def i_set(self, box, val):
        self.append(SetInstr(self.next_line_no(), box, val))

    def i_goto(self, addr):
        self.append(GotoInstr(self.next_line_no(), addr))

    def i_pstr(self, s):
        self.append(PstrInstr(self.next_line_no(), s))

    def i_pbox(self, box):
        self.append(PboxInstr(self.next_line_no(), box))

    def i_nl(self):
        self.append(PnlInstr(self.next_line_no()))

    i_pnl = i_nl

    INSTALOGIK_MAP = {
        "Wczytaj do": "read",
        "Ustaw": "set",
        "Zwiększ": "inc",
        "Zmniejsz": "dec",
        "Jeżeli": "if",
        "Skocz do": "goto",
        "Wypisz pudełko": "pbox",
        "Wypisz napis": "pstr",
        "Przejdź do nowej linii": "pnl",
    }

    all_keys = "|".join(list(INSTALOGIK_MAP.keys()) + list(INSTALOGIK_MAP.values()))
    LINE_INSTA_REGEX = re.compile(f'^([0-9]*\\.)\\W*({all_keys})(.*)')

    def insta_line(self, line):
        regex = self.LINE_INSTA_REGEX.match(line)
        if not regex:
            return None, line

        lineno, cmd, args = regex.groups()
        inst = self.INSTALOGIK_MAP.get(cmd, cmd)
        if inst == "if":
            args = args.replace("inaczej skocz do", "else").replace("skocz do", "goto")
            args = args.replace("następnej", "+1").replace("końca", "end")
            args = args.replace("≥", ">=").replace("≠", "!=").replace("≤", "<=")
        elif inst == "goto":
            args = args.replace("następnej", "+1").replace("końca", "end")
        elif inst == "pstr":
            args = args.strip().strip("'").replace(" ", "%20")
        elif inst == "set":
            args = args.replace("na", "")

        return int(lineno.rstrip(".")), f"{inst} {args}"

    def add_line(self, line):
        line = line.strip()
        if not line or line.startswith("#"):
            return

        lineno, line = self.insta_line(line)
        elements = line.split()

        if len(elements) == 1 and elements[0].endswith(":"):
            if len(elements[0]) > 1:
                self.label(elements[0][:-1])
        else:
            cmd = elements[0].lower()
            func = getattr(self, f"i_{cmd}", None)
            if func is None:
                raise ValueError(f"line {self.pos} invalid, command '{cmd}' not found in: '{line}'")
            args = [int(elt) if elt.isdigit() else elt for elt in elements[1:]]
            if cmd == "if":
                assert (
                    len(args) == 7
                ), f'Invalid number of args in "if" command in {line=}'
                assert (
                    str(args[3]).lower() == "goto" and str(args[5]).lower() == "else"
                ), f'Invalid "if": {line=} ({args[3]})'
                args.pop(5)
                args.pop(3)
            func(*args)
            assert lineno is None or lineno == self.pos, f"Invalid line number {lineno} (expected {self.pos})"

    def next_line_no(self):
        return self.pos + 1

    def get_code(self):
        for instr in self.code_lines.values():
            instr.resolve_labels(self.labels)

        buf = [f"i_len={self.pos}"]
        for lineno in range(1, self.next_line_no()):
            instr = self.code_lines[lineno]
            instr.resolve_labels(self.labels)
            buf.append(instr.code)
        return "&".join(buf)

    def get_code_txt(self, with_line_no=True):
        self.resolve_labels()
        lines = []
        for idx, instr in sorted(self.code_lines.items()):
            if with_line_no:
                lines.append(f"{idx:3}. {instr.debug_info}")
            else:
                lines.append(instr.debug_info)
        return "\n".join(lines)

    def run(self, input_lines, debug=False, as_numbers=False):
        print(f"Inputs: {input_lines}")
        steps, result = Machine(input_lines).exec(self, debug=debug)
        if as_numbers:
            result = [int(val) for val in " ".join(result).split()]
        print(f"Steps: {steps}, result: {result}")
        return result

    def run_test(self, input_lines, expected_outputs, debug=False):
        as_numbers = all(isinstance(val, int) for val in expected_outputs)

        result = self.run(input_lines, debug=debug, as_numbers=as_numbers)
        if not as_numbers:
            expected_outputs = [str(e) for e in expected_outputs]
        if result != expected_outputs:
            raise AssertionError(f"For input lines: {input_lines} expected result was {expected_outputs}"
                                 f"but program returned: {result}")
        return result


class Machine:
    def __init__(self, input_lines):
        self.buckets = {}
        self.ptr = 0
        self.counts = {}

        self.input_lines = list(input_lines)
        self.lines_to_read = []
        self.outputs = []

    def getval(self, val):
        if isinstance(val, int):
            return val
        return self.buckets[val]

    def read(self):
        assert self.lines_to_read, f"No more data on input at line {self.ptr}"
        return self.lines_to_read.pop(0)

    def add_output_line(self, val):
        assert (
            not self.lines_to_read
        ), f"Program output before read all input lines, not read: {self.lines_to_read}"
        self.outputs.append(val)

    def get_debug_state(self, step, instr):
        buckets_str = " ".join(
            f"{box}={val:<3}" for box, val in sorted(self.buckets.items())
        )
        in_out_crc = len(self.lines_to_read) + len(self.outputs)
        return f"{buckets_str} [{step:03}] {self.ptr:3} {instr.debug_info}"

    def exec(self, code, debug=False):
        self.ptr = 1
        self.counts = {}
        self.buckets = {"A": 0, "B": 0, "C": 0, "D": 0}
        self.outputs = []

        code.resolve_labels()
        self.lines_to_read = list(self.input_lines)
        step = 0
        in_out_crc = None
        while self.ptr < code.next_line_no():
            instr: Instruction = code.code_lines[self.ptr]
            if step > 10_000:
                raise AssertionError(f"Too much steps: {self.get_debug_state(step, instr)}")
            step += 1
            self.counts[self.ptr] = self.counts.get(self.ptr, 0) + 1
            if debug:
                buckets_str = " ".join(
                    f"{box}={val:<3}" for box, val in sorted(self.buckets.items())
                )
                in_out_crc = len(self.lines_to_read) + len(self.outputs)
                print(self.get_debug_state(step, instr))
            instr.exec(self)
            instr.next(self)
            if debug:
                if in_out_crc != len(self.lines_to_read) + len(self.outputs):
                    print(f"input: {self.lines_to_read}, output: {self.outputs}")

        self.outputs[:] = ("".join(self.outputs)).splitlines(keepends=True)
        assert not self.lines_to_read, f"Leftovers on input: {self.lines_to_read}"

        return step, self.outputs
