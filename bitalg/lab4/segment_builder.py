import matplotlib.pyplot as plt
from os import listdir
import json
from matplotlib.collections import LineCollection


class SegmentBuilder:
    def __init__(self, file_name=None, load=False):
        self.make_new_plot()

        self.file_name = file_name or self.get_new_filename()

        if load:
            self.load_segments()

    def get_new_filename(self):
        segments_file_list = [f.split(".")[0] for f in listdir(".") if f.startswith("segment-")]

        if len(segments_file_list) == 0:
            return "segment-1.txt"

        segment_nr = max([int(v.split("-")[1]) for v in segments_file_list]) + 1

        return f"segment-{segment_nr}.txt"

    def make_new_plot(self):
        fig, ax = plt.subplots()
        self.ax = ax
        self.fig = fig

        self.refresh_axis()

        self.segments = []

        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_event)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_event)
        self.temp_line = None

    def on_mouse_event(self, event):
        self.refresh_axis()

        if self.temp_line:
            self.segments.append((self.temp_line, (event.xdata, event.ydata)))
            self.temp_line = None
            xs, ys = self.get_segments_parsed()
        else:
            xs, ys = self.get_segments_parsed()
            xs += [event.xdata]
            ys += [event.ydata]
            self.temp_line = (event.xdata, event.ydata)

        self.ax.plot(xs, ys, 'b.')
        self.draw_segments()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_key_event(self, event):
        if event.key == 's':
            self.save_segments()
        if event.key == 'u':
            self.undo()
        if event.key == 'c':
            self.clear()

    def get_segments_parsed(self):
        xs, ys = [], []
        for (x1, y1), (x2, y2) in self.segments:
            xs.extend([x1, x2])
            ys.extend([y1, y2])

        return xs, ys
    
    def refresh_axis(self):
        plt.cla()
        self.ax.set_xlim([-5, 5])
        self.ax.set_ylim([-5, 5])

    def draw_segments(self):
        self.ax.add_collection(LineCollection(self.segments))

    def save_segments(self):
        file_out = open(self.file_name, "w")
        file_out.write(json.dumps(self.segments))

    def load_segments(self):
        file_in = open(self.file_name, "r")

        self.segments = json.loads(file_in.readline())

        self.ax.plot(*self.get_segments_parsed(), 'b.')
        self.draw_segments()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def clear(self):
        self.segments = []
        self.temp_line = None

        self.refresh_axis()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def undo(self):
        self.segments.pop()
        self.temp_line = None

        self.refresh_axis()
        self.ax.plot(*self.get_segments_parsed(), 'b.')
        self.draw_segments()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def get_segments(self):
        return self.segments

    def show(self):
        plt.show()
