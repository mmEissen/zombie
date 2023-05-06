import dataclasses
import tkinter

import qrcode

from PIL import ImageTk

from zombie.touch_point import touch_point


class Screen:
    class TouchIndicator:
        ACTIVE_COLOR = "#0000FF"
        INACTIVE_COLOR = "#AAAAAA"
        CONFIRMED_COLOR = "#00FF00"
        ERROR_COLOR = "#FF0000"

        def __init__(self, parent: tkinter.Tk) -> None:
            self.root = tkinter.Frame(
                parent, bg=self.ACTIVE_COLOR
            )

            self.left = tkinter.Frame(
                self.root,
                bg=self.INACTIVE_COLOR,
            )
            self.left_label = tkinter.Label(self.left)
            self.left_label.pack()
            self.right = tkinter.Frame(
                self.root,
                bg=self.CONFIRMED_COLOR,
            )
            # self.right_label = tkinter.Label(self.right)
            # self.right_label.pack()

            self.left.pack(anchor=tkinter.W, fill=tkinter.BOTH, expand=True, side=tkinter.LEFT)
            self.right.pack(anchor=tkinter.W, fill=tkinter.BOTH, expand=True, side=tkinter.LEFT)

        def sync(self, model: touch_point.TouchPoint) -> None:
            left_uid = model.left_uid
            self.left_image = _to_qr_image(model.left_url())

            right_uid = model.right_uid
            # self.right_image = _to_qr_image(model.right_url())

            confirmed = model.is_confirmed()

            self.left_label.configure(image=self.left_image)
            # self.right_label.configure(image=self.right_image)
            
            if model.error:
                self.left.configure(background=self.ERROR_COLOR)
                self.right.configure(background=self.ERROR_COLOR)
                return

            if confirmed:
                self.left.configure(background=self.CONFIRMED_COLOR)
                self.right.configure(background=self.CONFIRMED_COLOR)
                return

            if left_uid:
                self.left.configure(background=self.ACTIVE_COLOR)
            else:
                self.left.configure(background=self.INACTIVE_COLOR)

            if right_uid:
                self.right.configure(background=self.ACTIVE_COLOR)
            else:
                self.right.configure(background=self.INACTIVE_COLOR)

    def __init__(self, root: tkinter.Tk) -> None:
        self.root = root
        self._touch_indicator = self.TouchIndicator(self.root)
        self._touch_indicator.root.pack(expand=True, fill=tkinter.BOTH)

    def sync(self, model: touch_point.TouchPoint) -> None:
        self._touch_indicator.sync(model)


def launch_window(model: touch_point.TouchPoint) -> None:
    root = tkinter.Tk()

    root.geometry("640x480")
    # root.attributes("-fullscreen", True)

    gui = Screen(root)

    while True:
        gui.sync(model)
        root.update_idletasks()
        root.update()


def _to_qr_image(url: str) -> ImageTk.PhotoImage:
    image = qrcode.make(url, error_correction=qrcode.ERROR_CORRECT_L, box_size=8)
    return ImageTk.PhotoImage(image)
