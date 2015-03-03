from matplotlib import is_interactive
from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib import cbook
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends import get_backends
FigureCanvas, Window, Toolbar2, MainLoop = get_backends()


class FigureManagerEvent(object):
    """Event for when something happens to this figure manager.
    i.e. the figure it controls gets closed

    Attributes
    ----------
    signal : str
        The name of the signal.

    figure_manager : FigureManager
        The figure manager that fired the event.
    """
    def __init__(self, signal, figure_manager):
        self.name = signal
        self.figure_manager = figure_manager


class FigureManager(cbook.EventEmitter):
    """
    The FigureManager creates and wraps the necessary components to display a
    figure, namely the Window, FigureCanvas and Toolbar.  It gets used whenever
    you want the figure in a standalone window.

    Parameters
    ----------
    figure : `matplotlib.figure.Figure`
        The figure to manage.

    num : int
        The figure number.

    Attributes
    ----------

    canvas : `matplotlib.backend_bases.FigureCanvasBase`
        The GUI element on which we draw.

    toolbar : `matplotlib.backend_bases.NavigationToolbar2`
        The toolbar used for interacting with the figure.

    window : `matplotlib.backend_bases.WindowBase`
        The window that holds the canvas and toolbar.

    num : int
        The figure number.
    """
    def __init__(self, figure, num):
        cbook.EventEmitter.__init__(self)
        self.num = num

        self._mainloop = MainLoop()
        self.window = Window('Figure %d' % num)
        self.window.mpl_connect('window_destroy_event', self._destroy)

        self.canvas = FigureCanvas(figure, manager=self)

        self.key_press_handler_id = self.canvas.mpl_connect('key_press_event',
                                                            self.key_press)

        w = int(self.canvas.figure.bbox.width)
        h = int(self.canvas.figure.bbox.height)

        self.window.add_element_to_window(self.canvas, True, True, 0, 'top')

        self.toolbar = self._get_toolbar()
        if self.toolbar is not None:
            h += self.window.add_element_to_window(self.toolbar,
                                                   False, False, 0, 'bottom')

        self.window.set_default_size(w, h)

        if is_interactive():
            self.window.show()

        def notify_axes_change(fig):
            'this will be called whenever the current axes is changed'
            if self.toolbar is not None:
                self.toolbar.update()
        self.canvas.figure.add_axobserver(notify_axes_change)

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
        """Called to destroy this FigureManager, gets called by Gcf through
        event magic.
        """
        self.canvas.destroy()
        if self.toolbar:
            self.toolbar.destroy()
        self.window.destroy()

        self._mainloop.__del__()

    def show(self):
        """Shows the figure"""
        self.window.show()

    def full_screen_toggle(self):
        """Toggles whether we show fullscreen, alternatively call
        `window.fullscreen()`"""
        self._full_screen_flag = not self._full_screen_flag
        self.window.set_fullscreen(self._full_screen_flag)

    def resize(self, w, h):
        """"For gui backends, resize the window (in pixels)."""
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

    def _get_toolbar(self):
        # must be inited after the window, drawingArea and figure
        # attrs are set
        if rcParams['toolbar'] == 'toolbar2':
            toolbar = Toolbar2(self.canvas, self.window)
        else:
            toolbar = None
        return toolbar

    def show_popup(self, msg):
        """
        Display message in a popup -- GUI only
        """
        pass
