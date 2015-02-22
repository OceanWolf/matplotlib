from matplotlib import is_interactive
from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib import cbook
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends import get_backends
(FigureCanvas, Window, Toolbar2, MainLoop,
    old_new_figure_manager) = get_backends()


class FigureManagerEvent(object):
    def __init__(self, s, fm):
        self.name = s
        self.figure_manager = fm


class FigureManager(cbook.EventEmitter):
    def __init__(self, canvas, num):
        cbook.EventEmitter.__init__(self)
        self.canvas = canvas
        canvas.manager = self
        self.num = num

        self.key_press_handler_id = self.canvas.mpl_connect('key_press_event',
                                                            self.key_press)

        self.mainloop = MainLoop()
        self.window = Window('Figure %d' % num)
        self.window.mpl_connect('window_destroy_event', self._destroy)

        w = int(self.canvas.figure.bbox.width)
        h = int(self.canvas.figure.bbox.height)

        self.window.add_element_to_window(self.canvas, True, True, 0, True)

        self.toolbar = self._get_toolbar(canvas)
        if self.toolbar is not None:
            h += self.window.add_element_to_window(self.toolbar,
                                                   False, False, 0)

        self.window.set_default_size(w, h)

        if is_interactive():
            self.window.show()

        def notify_axes_change(fig):
            'this will be called whenever the current axes is changed'
            if self.toolbar is not None:
                self.toolbar.update()
        self.canvas.figure.add_axobserver(notify_axes_change)

        self.canvas.grab_focus()

    def key_press(self, event):
        """
        Implement the default mpl key bindings defined at
        :ref:`key-event-handling`
        """
        key_press_handler(event, self.canvas, self.canvas.toolbar)

    def _destroy(self, event=None):
        # Callback from the when the window wants to destroy itself
        s = 'window_destroy_event'
        event = FigureManagerEvent(s, self)
        self._callbacks.process(s, event)

    def destroy(self, *args):
        self.window.destroy()
        self.canvas.destroy()
        if self.toolbar:
            self.toolbar.destroy()

        self.mainloop.__del__()

    def show(self):
        self.window.show()

    def full_screen_toggle(self):
        self._full_screen_flag = not self._full_screen_flag
        self.window.set_fullscreen(self._full_screen_flag)

    def resize(self, w, h):
        self.window.resize(w, h)

    def get_window_title(self):
        """
        Get the title text of the window containing the figure.
        Return None for non-GUI backends (e.g., a PS backend).
        """
        return self.window.get_window_title()

    def set_window_title(self, title):
        """
        Set the title text of the window containing the figure.  Note that
        this has no effect for non-GUI backends (e.g., a PS backend).
        """
        self.window.set_window_title(title)

    def show_popup(self, msg):
        """
        Display message in a popup -- GUI only
        """
        pass

    def _get_toolbar(self, canvas):
        # must be inited after the window, drawingArea and figure
        # attrs are set
        if rcParams['toolbar'] == 'toolbar2':
            toolbar = Toolbar2(canvas, self.window)
        else:
            toolbar = None
        return toolbar


def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    show = kwargs.pop('show', None)
    if old_new_figure_manager is None:
        FigureClass = kwargs.pop('FigureClass', Figure)
        thisFig = FigureClass(*args, **kwargs)
        manager = new_figure_manager_given_figure(num, thisFig)
    else:  # TODO remove once Gcf removed from backends.
        manager = old_new_figure_manager(num, *args, **kwargs)
        manager.mainloop = MainLoop
    return manager


def new_figure_manager_given_figure(num, figure):
    canvas = FigureCanvas(figure)
    manager = FigureManager(canvas, num)
    return manager
