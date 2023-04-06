import dataclasses
from typing import Callable
import serial
import re

DEFAULT_BAUD_RATE = 19_200
DEVICE = "/dev/cu.usbmodem2101"

_RE_CORRECT_LINE = re.compile(r"[+-][12] ([0-9A-F]{1,2}:)*[0-9A-F]{1,2}")

@dataclasses.dataclass
class DoubleReader:
    device: str
    on_reader_1_enter: Callable[[str], None] = lambda s: None
    on_reader_1_exit: Callable[[str], None] = lambda s: None
    on_reader_2_enter: Callable[[str], None] = lambda s: None
    on_reader_2_exit: Callable[[str], None] = lambda s: None
    baud_rate: int = DEFAULT_BAUD_RATE

    def run_forever(self):
        with serial.Serial(self.device, self.baud_rate) as ser:
            while True:
                self.loop(ser)
    
    def loop(self, ser: serial.Serial) -> None:
        line = str(ser.readline(), "ascii").strip()
        if not re.fullmatch(_RE_CORRECT_LINE, line):
            return

        reader, uid = line.split(" ")
        is_enter = reader[0] == "+"
        reader_number = int(reader[1])

        if reader_number == 1 and is_enter:
            self.on_reader_1_enter(uid)
        elif reader_number == 1 and not is_enter:
            self.on_reader_1_exit(uid)
        elif reader_number == 2 and is_enter:
            self.on_reader_2_enter(uid)
        elif reader_number == 2 and not is_enter:
            self.on_reader_2_exit(uid)


def _test_reader() -> None:
    def make_print(n: int, is_enter: bool) -> Callable[[str], None]:
        def _print(uid: str):
            print(f"Reader {n} {'ENTER' if is_enter else 'EXIT'} {uid}")
        return _print
    
    DoubleReader(
        DEVICE,
        make_print(1, True),
        make_print(1, False),
        make_print(2, True),
        make_print(2, False),
    ).run_forever()


if __name__ == "__main__":
    _test_reader()
