import PySimpleGUI as sg

class PSGTools:

    # TODO: move these to their own module, tools for psg.  no need to keep here.

    @staticmethod
    def offset_window(location: tuple[int or None, int or None],
                      offset: tuple[int or None, int or None]) -> tuple:
        """Offset window launch location"""
        location: list[int, int] = list(location)
        if location[0] is not None and offset[0] is not None:
            location[0] += offset[0]
        if location[1] is not None and offset[1] is not None:
            location[1] += offset[1]
        return tuple(location)

    @staticmethod
    def layout_tester(layout: list[list], timeout: int = None):
        print('Testing')
        window = sg.Window('Testing', layout)
        while True:
            if timeout is not None:
                event, values = window.read(timeout=timeout)
            else:
                event, values = window.read()
            if event in [sg.WIN_CLOSED, 'Quit']:
                break
            print(event, values)
        window.close()
        print('Testing Complete')