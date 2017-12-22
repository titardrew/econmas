from pyglet import window, clock, graphics
from pyglet.gl import *


class WorldVisualizer(window.Window):
    def __init__(self, world, width=800, height=800, frequency=.01):

        window.Window.__init__(self, width=width, height=height, fullscreen=False)

        self.cell_size = width // max(world.map.shape)
        self.screen_width = width
        self.screen_height = height
        self.columns = width // self.cell_size
        self.rows = height // self.cell_size
        self.cells_vertex_list = []
        self.ants = []
        self.world = world
        self.paused = False
        self.frequency = frequency

        self.grid_batch = graphics.Batch()
        self.ant_batch = graphics.Batch()

        self._initialize()
        self._draw_grid()

    def _initialize(self):
        glClearColor(0, 0, 0, 1)
        for row in range(len(self.world.map)):
            current_row = self.world.map[row]
            self.cells_vertex_list.append([])
            for col in range(len(current_row)):
                cell = self.cell_position(col, row)
                self.cells_vertex_list[row].append(cell)

    def translate(self, pixel_x, pixel_y):
        """Translate pixel coordinates (pixel_x,pixel_y), into grid coordinates"""
        x = pixel_x * self.columns // self.screen_width
        y = pixel_y * self.rows // self.screen_height
        return x, y

    def cell_position(self, col, row):
        x1, y1 = col * self.cell_size, row * self.cell_size
        x2, y2 = col * self.cell_size + self.cell_size, row * self.cell_size + self.cell_size
        return tuple((x1, y1, x2, y2))

    def _draw_grid(self):
        # Horizontal lines
        for i in range(self.rows):
            self.grid_batch.add(2, GL_LINES, None, ('v2i', (0, i * self.cell_size,
                                                                      self.screen_width, i * self.cell_size)))
        # Vertical lines
        for j in range(self.columns + 1):
            self.grid_batch.add(2, GL_LINES, None, ('v2i', (j * self.cell_size, 0,
                                                                      j * self.cell_size, self.screen_height)))

    def draw(self):
        self.clear()
        self._draw()
        glColor4f(0.23, 0.23, 0.23, 1.0)
        self.grid_batch.draw()

    def _draw(self):
        glBegin(GL_QUADS)
        for row in range(len(self.world.map)):
            current_row = self.world.map[row]
            for col in range(len(current_row)):
                glColor4f(0, self.world.map[row][col], 0, 1.0)
                x1, y1, x2, y2 = self.cells_vertex_list[row][col]
                glVertex2f(x1, y1)
                glVertex2f(x1, y2)
                glVertex2f(x2, y2)
                glVertex2f(x2, y1)
        glEnd()

    def quicker(self):
        clock.unschedule(self._do)
        self.frequency += .01
        print(self.frequency)
        self._schedule()

    def slower(self):
        clock.unschedule(self._do)
        self.frequency = max(self.frequency - .01, .001)
        print(self.frequency)
        self._schedule()

    def on_mouse_release(self, x, y, button, modifiers):
        x, y = self.translate(x, y)
        self.world.harvest(0.9, (y, x))

    def on_key_release(self, symbol, modifiers):
        if symbol == 32:
            self.paused = not self.paused
        elif symbol == 65362:
            self.quicker()
        elif symbol == 65364:
            self.slower()
