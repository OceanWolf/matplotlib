import matplotlib
matplotlib.use('GTK3AGG')
matplotlib.rcParams['toolbar'] = 'toolmanager'
from matplotlib.figure import Figure
from matplotlib.backend_managers import FigureManager
from matplotlib.backends import get_backend
from matplotlib.backend_tools import ToolBase


backend = get_backend()

fig1 = Figure()
canvas1 = backend.FigureCanvas(fig1)
ax1 = fig1.add_subplot(111)
ax1.plot([1, 2, 3])

fig2 = Figure()
canvas2 = backend.FigureCanvas(fig2)
ax2 = fig2.add_subplot(111)
ax2.plot([3, 2, 1])


class SwitchFigure(ToolBase):
    description = "change Figure"
    default_keymap = 'f'

    def __init__(self, *args, **kwargs):
        self.fig = kwargs.pop('newfig')
        self.figmanager = kwargs.pop('figuremanager')
        ToolBase.__init__(self, *args, **kwargs)

    def trigger(self, *args, **kwargs):
        self.figmanager.figure = self.fig

manager = FigureManager(fig1, 1)
manager.toolmanager.add_tool('f1', SwitchFigure, newfig=fig2, figuremanager=manager)
manager.show()
manager.mpl_connect('window_destroy_event', manager.destroy)
manager._mainloop()