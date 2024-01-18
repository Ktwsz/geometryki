from enum import Enum
from functools import cmp_to_key


def det(a, b, c, d):
    return a * d - b * c


class EventType(Enum):
    BEGIN = 0
    END = 1
    INTERSECT = 2


class Event:
    def __init__(self, position, type, segment_id=None, end_position=None, intersect_ids=None):
        self.position = position
        self.segment_id = segment_id
        self.end_position = end_position
        self.type = type
        self.intersect_ids = intersect_ids

        if self.end_position:
            self.vector = (self.end_position[0] - self.position[0], self.end_position[1] - self.position[1])

    def __eq__(self, other):
        if self.type != other.type:
            return False

        if self.type == EventType.INTERSECT:
            return min(self.intersect_ids) == min(other.intersect_ids) and max(self.intersect_ids) == max(other.intersect_ids)

        return self.segment_id == other.segment_id

    @staticmethod
    def cmp_xs(event_1, event_2):
        event_1_x, event_1_y = event_1.position
        event_2_x, event_2_y = event_2.position

        if event_1_x != event_2_x:
            return event_1_x-event_2_x

        return event_2_y-event_1_y

    @staticmethod
    def get_sweep_intersect(e):
        if not e.end_position:
            return e.position[1]

        global sweep_x

        A = e.position[0]

        t = (sweep_x - A) / e.vector[0]

        return e.position[1] + t * e.vector[1]

    @staticmethod
    def cmp_ys(event_1, event_2):
        p1_y = Event.get_sweep_intersect(event_1)
        p2_y = Event.get_sweep_intersect(event_2)

        return p2_y - p1_y

    @staticmethod
    def get_intersect(event_1, event_2):
        if event_1 is None or event_2 is None:
            return None
        if event_1.type == EventType.INTERSECT or event_2.type == EventType.INTERSECT:
            return None

        Ax, Ay = event_1.position
        Cx, Cy = event_2.position

        ABx, ABy = event_1.vector

        CDx, CDy = event_2.vector

        W = det(CDx, -ABx, CDy, -ABy)

        if W == 0:
            return None

        Wt = det(Ax-Cx, -ABx, Ay-Cy, -ABy)
        t = Wt/W

        Wm = det(CDx, Ax-Cx, CDy, Ay-Cy)
        m = Wm/W

        p = (Cx + t * CDx, Cy + t * CDy)

        if 0 <= t and t <= 1 and 0 <= m and m <= 1:
            return Event(position=p, type=EventType.INTERSECT, intersect_ids=[event_1.segment_id, event_2.segment_id])
        return None


class State:
    def __init__(self, cmp_fun):
        self.cmp_fun = cmp_fun

        self.state = []

    def insert(self, e):
        if e is None:
            return
        if e.type == EventType.INTERSECT and e in self.state:
            return

        self.state = sorted(self.state + [e], key=cmp_to_key(self.cmp_fun))

    def remove(self, e):
        if e is None:
            return

        for i, val in enumerate(self.state):
            if val == e:
                ix = i
                break

        self.state.pop(ix)

    def get_neighbours(self, e):
        if e is None:
            return [None, None]

        for i, val in enumerate(self.state):
            if val == e:
                ix = i
                break

        return [self.state[ix - 1] if ix - 1 >= 0 else None, self.state[ix + 1] if ix + 1 < len(self.state) else None]

    def swap_events(self, e1, e2):
        if e1 is None or e2 is None:
            return

        for i, val in enumerate(self.state):
            if val == e1:
                ix1 = i
                break

        for i, val in enumerate(self.state):
            if val == e2:
                ix2 = i
                break

        self.state[ix1], self.state[ix2] = self.state[ix2], self.state[ix1]


class Sweep(State):
    def __init__(self, cmp_fun):
        super().__init__(cmp_fun)


class EventsState(State):
    def __init__(self, cmp_fun):
        super().__init__(cmp_fun)
        self.current_ix = 0

    def next(self):
        self.current_ix += 1
        return self.state[self.current_ix-1]

    def has_next(self):
        return len(self.state) > self.current_ix

    def get_intersects(self):
        return [(e.position, *e.intersect_ids) for e in self.state if e.type == EventType.INTERSECT]


def find_intersections(sections):
    def swap(coord):
        beg, end = coord
        if beg[0] < end[0]:
            return (beg, end)
        return (end, beg)

    global sweep_x

    sections = [swap(val) for val in sections]

    sections_end = [Event(position=value[1], segment_id=ix, type=EventType.END) for ix, value in enumerate(sections)]
    sections_begin = [Event(position=value[0], segment_id=ix, end_position=value[1], type=EventType.BEGIN) for ix, value in enumerate(sections)]

    sweep = Sweep(Event.cmp_ys)
    events = EventsState(Event.cmp_xs)

    for e in sections_end:
        events.insert(e)
    for e in sections_begin:
        events.insert(e)

    while events.has_next():
        e = events.next()
        sweep_x = e.position[0]

        events_to_check = []

        if e.type == EventType.BEGIN:
            sweep.insert(e)
            prev, nxt = sweep.get_neighbours(e)

            events_to_check = [(e, prev), (e, nxt)]

        if e.type == EventType.END:
            begin_event = Event(position=e.position, end_position=e.end_position, type=EventType.BEGIN, segment_id=e.segment_id)

            prev, nxt = sweep.get_neighbours(begin_event)
            sweep.remove(begin_event)

            events_to_check = [(prev, nxt)]

        if e.type == EventType.INTERSECT:
            prev_ix, nxt_ix = e.intersect_ids
            prev = Event(position = sections[prev_ix][0], end_position=sections[prev_ix][1], type=EventType.BEGIN, segment_id=prev_ix)
            nxt = Event(position = sections[nxt_ix][0], end_position=sections[nxt_ix][1], type=EventType.BEGIN, segment_id=nxt_ix)

            sweep.swap_events(prev, nxt)

            prev_neigh_1, prev_neigh_2 = sweep.get_neighbours(prev)
            nxt_neigh_1, nxt_neigh_2 = sweep.get_neighbours(nxt)

            events_to_check = [(prev, prev_neigh_1), (prev, prev_neigh_2), (nxt, nxt_neigh_1), (nxt, nxt_neigh_2)]

        for e1, e2 in events_to_check:
            p = Event.get_intersect(e1, e2)

            events.insert(p)

    return [(a, b+1, c+1) for a, b, c in events.get_intersects()]
