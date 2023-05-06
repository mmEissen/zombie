import threading
from zombie import nfc
import time
import requests
import dataclasses
import urllib.parse


_CONFIRM_DELAY = 0.2


@dataclasses.dataclass
class TouchPoint:
    device: str
    server_url: str
    _left_uid: str = ""
    _right_uid: str = ""
    _confirmed_progress: int = 0
    _enter_time: int = 0
    _was_confirmed: bool = False
    _error: bool = False
    _last_lights: tuple[nfc.Color, nfc.Color] = (nfc.Color.OFF, nfc.Color.OFF)

    def __post_init__(self) -> None:
        self._lock = threading.Lock()
        self._nfc = nfc.DoubleReader(
            self.device,
            self.enter_left,
            self.exit_left,
            self.enter_right,
            self.exit_right,
        )

    @property
    def left_uid(self) -> str:
        with self._lock:
            return self._left_uid
    
    @left_uid.setter
    def left_uid(self, value: str) -> None:
        with self._lock:
            self._left_uid = value
    
    @property
    def right_uid(self) -> str:
        with self._lock:
            return self._right_uid
    
    @right_uid.setter
    def right_uid(self, value: str) -> None:
        with self._lock:
            self._right_uid = value

    @property
    def error(self) -> bool:
        with self._lock:
            return self._error
    
    @error.setter
    def error(self, value: bool) -> None:
        with self._lock:
            self._error = value
    
    def _url(self, uid: str) -> str:
        query = {"uid": uid}
        return f"{self.server_url}/player?{urllib.parse.urlencode(query)}"

    def left_url(self) -> str:
        return self._url(self.left_uid)

    def right_url(self) -> str:
        return self._url(self.right_uid)

    @property
    def confirmed_progress(self) -> bool:
        with self._lock:
            return self._confirmed_progress
    
    @confirmed_progress.setter
    def confirmed_progress(self, value: bool) -> None:
        with self._lock:
            self._confirmed_progress = value

    def is_confirmed(self) -> bool:
        return self.confirmed_progress == 100

    def _is_confirmed(self) -> bool:
        return self._confirmed_progress == 100


    def _on_both_entered(self):
        self._enter_time = time.time()
    
    def _on_one_exit(self):
        self._enter_time = 0
        self.confirmed_progress = 0
        self.error = False
        self._was_confirmed = False

    def enter_left(self, uid: str) -> None:
        self.left_uid = uid
        if self.right_uid:
            self._on_both_entered()
    
    def exit_left(self, uid: str) -> None:
        self.left_uid = ""
        self._on_one_exit()
    
    def enter_right(self, uid: str) -> None:
        self.right_uid = uid
        if self.left_uid:
            self._on_both_entered()
    
    def exit_right(self, uid: str) -> None:
        self.right_uid = ""
        self._on_one_exit()

    def _register_touch(self) -> None:
        print("touch...")
        try:
            response = requests.put(
                f"{self.server_url}/api/touch",
                json={
                    "left_uid": self._left_uid,
                    "right_uid": self._right_uid,
                },
            )
        except Exception:
            self._error = True
            return
        if response.status_code >= 400:
            self._error = True
        print(response)

    def _set_lights(self, left: nfc.Color, right: nfc.Color) -> None:
        if (left, right) == self._last_lights:
            return
        self._last_lights = (left, right)
        self._nfc.set_lights(left, right)

    def _update_lights(self):
        if self._error:
            self._set_lights(nfc.Color.RED, nfc.Color.RED)
            return
        if self._confirmed_progress >= 100:
            self._set_lights(nfc.Color.GREEN, nfc.Color.GREEN)
            return
        left = nfc.Color.BLUE if self._left_uid else nfc.Color.OFF
        right = nfc.Color.BLUE if self._right_uid else nfc.Color.OFF
        self._set_lights(left, right)

    def loop(self) -> None:
        with self._lock:
            if self._enter_time:
                self._confirmed_progress = min(100, int(100 * (time.time() - self._enter_time) / _CONFIRM_DELAY))
            if self._is_confirmed() and not self._was_confirmed:
                self._was_confirmed = True
                self._register_touch()
            self._update_lights()
        time.sleep(0.05)
    
    def run_forever(self) -> None:
        threading.Thread(target=self._nfc.run_forever, name="nfc-serial-thread", daemon=True).start()
        while True:
            self.loop()

    def run_concurrent(self) -> None:
        threading.Thread(target=self.run_forever, name="model-thread", daemon=True).start()
