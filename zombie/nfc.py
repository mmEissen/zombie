import dataclasses
from typing import Callable
import serial
import re
import queue
import enum

DEFAULT_BAUD_RATE = 19_200
DEVICE = "/dev/cu.usbmodem2101"

_RE_CORRECT_LINE = re.compile(r"[+-][12] ([0-9A-F]{1,2}:)*[0-9A-F]{1,2}")


class Color(enum.IntEnum):
    OFF = 0
    BLUE = 1
    GREEN = 2
    CYAN = 3
    RED = 4
    MAGENTA = 5
    YELLOW = 6
    WHITE = 7


@dataclasses.dataclass
class DoubleReader:
    device: str
    on_reader_1_enter: Callable[[str], None] = lambda s: None
    on_reader_1_exit: Callable[[str], None] = lambda s: None
    on_reader_2_enter: Callable[[str], None] = lambda s: None
    on_reader_2_exit: Callable[[str], None] = lambda s: None
    baud_rate: int = DEFAULT_BAUD_RATE
    _write_queue: queue.Queue[bytes] = dataclasses.field(default_factory=queue.Queue)

    def run_forever(self):
        with serial.Serial(self.device, self.baud_rate) as ser:
            while True:
                self.loop(ser)

    def set_lights(self, color_1: Color, color_2: Color) -> None:
        encoded_data = ((color_1 << 3) + color_2 + ord(" ")).to_bytes()
        self._write_queue.put_nowait(encoded_data)
    
    def _read_sensors(self, ser: serial.Serial) -> None:
        if not ser.in_waiting:
            return
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

    def _update_lights(self, ser: serial.Serial) -> None:
        try:
            data = self._write_queue.get_nowait()
        except queue.Empty:
            return
        ser.write(data)

    def loop(self, ser: serial.Serial) -> None:
        self._read_sensors(ser)
        self._update_lights(ser)



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
