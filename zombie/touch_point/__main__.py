import click

from zombie.touch_point import gui, touch_point


@click.command()
@click.argument("device_path")
@click.argument("server_url")
def main(device_path: str, server_url: str):
    model = touch_point.TouchPoint(device_path, server_url)
    model.run_concurrent()

    gui.launch_window(model)


main()
