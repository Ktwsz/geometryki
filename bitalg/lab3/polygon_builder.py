import matplotlib.pyplot as plt
from os import listdir
import json


class PolygonBuilder:
    def __init__(self, file_name=None, load=False):#, triangulation_func=None):
        self.make_new_plot()

        self.file_name = file_name if file_name is not None else self.get_new_filename()

        if load:
            self.load_polygon()
        #self.triangulation_func = triangulation_func

    def get_new_filename(self):
        polygons_file_list = [f.split(".")[0] for f in listdir(".") if f.split(".")[0].split("-")[0] == "polygon"]

        if len(polygons_file_list) == 0:
            return "polygon-1.txt"

        polygon_nr = max(map(lambda x: int(x.split("-")[1]), polygons_file_list)) + 1
        return f"polygon-{polygon_nr}.txt"

    def make_new_plot(self):
        fig, ax = plt.subplots()
        ax.set_xlim([-5, 5])
        ax.set_ylim([-5, 5])
        line, = ax.plot([0], [0])
        point, = ax.plot([0], [0], '.')
        #diag, = ax.plot([0], [0], 'r')

        self.line = line
        self.point = point
        #self.diag = diag
        #self.diag.set_visible(False)

        self.point_xs = []
        self.point_ys = []
        self.line_xs = []
        self.line_ys = []
        #self.diagonals_lines = []

        line.figure.canvas.mpl_connect('button_press_event', self.on_press_event)
        line.figure.canvas.mpl_connect('key_press_event', self.on_key_press_event)

        #self.triangulation_visible = False

    def on_press_event(self, event):
        if event.inaxes != self.line.axes:
            return

        self.point_xs.append(event.xdata)
        self.point_ys.append(event.ydata)

        self.draw_plot_points()
        #self.draw_plot_diagonals()

        if len(self.line_xs) == 0:
            self.line_xs = 2*[event.xdata]
            self.line_ys = 2*[event.ydata]
            return

        self.line_xs.pop()
        self.line_ys.pop()

        self.line_xs.extend([event.xdata, self.line_xs[0]])
        self.line_ys.extend([event.ydata, self.line_ys[0]])

        self.draw_plot_lines()

    def draw_plot_points(self):
        self.point.set_data(self.point_xs, self.point_ys)
        self.point.figure.canvas.draw()

    def draw_plot_lines(self):
        self.line.set_data(self.line_xs, self.line_ys)
        self.line.figure.canvas.draw()

    #def draw_plot_diagonals(self):
    #    if not self.triangulation_visible:
    #        self.diagonals_lines.clear()
    #        self.diag.set_visible(False)
    #        plt.draw()
    #    elif len(self.point_xs) > 3:
    #        self.add_triangulation()
    #        self.diag.set_visible(True)
    #        self.diag.set_data(*list(zip(*self.diagonals_lines)))
    #        self.diag.figure.canvas.draw()

    def on_key_press_event(self, event):
        if event.key == 'c':
            self.clear_polygon()
        if event.key == 'u':
            self.clear_last_point()
        #if event.key == 'v':
        #    self.triangulation_visible = not self.triangulation_visible
        if event.key == 's':
            self.save_polygon()

        self.draw_plot_lines()
        self.draw_plot_points()
        #self.draw_plot_diagonals()

    def get_points(self):
        return list(zip(self.point_xs, self.point_ys))

    def save_polygon(self):
        points = self.get_points()

        file_out = open(self.file_name, "w")
        file_out.write(json.dumps(points))

    def load_polygon(self):
        self.clear_polygon()

        file_in = open(self.file_name, "r")

        points_arr = json.loads(file_in.readline())

        self.point_xs, self.point_ys = list(zip(*points_arr))
        self.point_xs, self.point_ys = list(self.point_xs), list(self.point_ys)

        self.line_xs, self.line_ys = list(zip(*(points_arr + [points_arr[0]])))
        self.line_xs, self.line_ys = list(self.line_xs), list(self.line_ys)

        self.draw_plot_lines()
        self.draw_plot_points()

    def clear_polygon(self):
        self.line_xs.clear()
        self.line_ys.clear()
        self.point_xs.clear()
        self.point_ys.clear()
        self.triangulation_visible = False

    def clear_last_point(self):
        self.line_xs = self.line_xs[:-2]
        self.line_ys = self.line_ys[:-2]
        self.line_xs.append(self.line_xs[0])
        self.line_ys.append(self.line_ys[0])

        self.point_xs = self.point_xs[:-1]
        self.point_ys = self.point_ys[:-1]

    def show(self):
        plt.show()

    #def add_triangulation(self):
    #    if len(self.point_xs) < 4:
    #        return

    #    self.diagonals_lines = self.get_triangulation()

    #def get_triangulation(self):
    #    if self.triangulation_func is None:
    #        return

    #    points = self.get_points()

    #    self.diagonals_lines_ix = self.triangulation_func(points)
    #    return [[(self.point_xs[i1], self.point_xs[i2]), (self.point_ys[i1], self.point_ys[i2])] for i1, i2 in self.diagonals_lines_ix]

    def get_polygon(self):
        return self.get_points()
