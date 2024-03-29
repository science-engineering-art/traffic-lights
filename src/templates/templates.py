import math
import heapq
import random
from typing import Tuple
from copy import deepcopy
import dictdatabase as ddb
from models.metaheuristic_control import metaeh_control
from models.road import Road
from abc import abstractmethod
from scipy.spatial import distance
from models.new_control import new_draw
from models.navigation import navigation
from templates.visitor import NodeVisitor
from templates.models import Template, Vehicle
from templates.models import CurveEdge, Edge, IntersectionNode, Map, RoadEdge
     

class BasicMapBuilder:

    def __init__(self):
        self.map = Map(
            width_roads=0,
            lanes=[],
            roads=[],
            intersections={},
            curves=[],
            extremes_lanes=[]
        )

    @abstractmethod
    def build_map(self) -> Map:
        pass

    def __build_roads(self, start, end, inN, outN, width):
        x0, y0 = start
        x1, y1 = end

        if x0**2 + y0**2 > x1**2 + y1**2:
            x0, y0 = end
            x1, y1 = start

        vX, vY = x1-x0, y1-y0
        nX, nY = vY, -vX

        # normalize
        n = (nX**2 + nY**2)**0.5
        nX, nY = width/n*nX, width/n*nY

        n = (vX**2 + vY**2)**0.5
        x0, y0 = x0 + vX * width / n, y0 + vY * width / n
        x1, y1 = x1 - vX * width / n, y1 - vY * width / n

        n = int((inN + outN) / 2)
        rX, rY = n * -nX, n * -nY

        if (inN + outN) % 2 == 0:
            rX, rY = rX + nX / 2, rY + nY / 2

        x0, y0 = x0 + rX, y0 + rY
        x1, y1 = x1 + rX, y1 + rY

        if start not in self.map.intersections:
            self.map.intersections[start] = IntersectionNode(
                input_lanes=[],
                out_lanes=[],
                follows=[]
            )
        if end not in self.map.intersections:
            self.map.intersections[end] = IntersectionNode(
                input_lanes=[],
                out_lanes=[],
                follows=[]
            )

        road = RoadEdge(
            lanes=[]
        )

        for _ in range(inN):
            # create road
            lane_id = len(self.map.lanes)
            lane = Edge(
                lambda_=0,
                start=(x0, y0),
                end=(x1, y1)
            )
            self.map.lanes.append(lane)
            road.lanes.append(lane_id)

            x0, y0 = x0 + nX, y0 + nY
            x1, y1 = x1 + nX, y1 + nY

            self.map.intersections[end].input_lanes.append(lane_id)
            self.map.intersections[start].out_lanes.append(lane_id)
            self.map.extremes_lanes.append(lane_id)

        for _ in range(outN):
            # create road
            lane_id = len(self.map.lanes)
            lane = Edge(
                lambda_=0,
                start=(x1, y1),
                end=(x0, y0)
            )
            self.map.lanes.append(lane)
            road.lanes.append(lane_id)

            x0, y0 = x0 + nX, y0 + nY
            x1, y1 = x1 + nX, y1 + nY

            self.map.intersections[start].input_lanes.append(lane_id)
            self.map.intersections[end].out_lanes.append(lane_id)
            self.map.extremes_lanes.append(lane_id)

        self.map.roads.append(road)

    def __build_intersections(self):

        def is_turning_left(road_in: Edge, road_out: Edge):            
            if road_in.end[1] < road_in.start[1]:
                if road_out.end[0] < road_out.start[0]:
                    return True
            elif road_in.end[1] > road_in.start[1]:
                if road_out.end[0] > road_out.start[0]:
                    return True
            elif road_in.start[0] < road_in.end[0]:
                if road_out.end[1] < road_out.start[1]:
                    return True
            elif road_in.start[0] > road_in.end[0]:
                if road_out.end[1] > road_out.start[1]:
                    return True
            return False
        
        def is_turning_right(road_in: Edge, road_out: Edge):
            if road_in.end[1] < road_in.start[1]:
                if road_out.end[0] > road_out.start[0]:
                    return True
            elif road_in.end[1] > road_in.start[1]:
                if road_out.end[0] < road_out.start[0]:
                    return True
            elif road_in.start[0] < road_in.end[0]:
                if road_out.end[1] > road_out.start[1]:
                    return True
            elif road_in.start[0] > road_in.end[0]:
                if road_out.end[1] < road_out.start[1]:
                    return True
            return False

        for x, y in self.map.intersections:
            i = 0
            follows = {}

            for in_lane_id in self.map.intersections[(x, y)].input_lanes:
                for out_lane_id in self.map.intersections[(x, y)].out_lanes:

                    road_in : Edge = self.map.lanes[in_lane_id]
                    road_out: Edge = self.map.lanes[out_lane_id]
                    
                    # check if road_in and road_out are in the same road
                    if distance.euclidean(road_in.start, road_out.end) == \
                        distance.euclidean(road_in.end, road_out.start):
                        continue
                    
                    if abs(BasicMapBuilder.__calculate_angle(road_in) - 
                    BasicMapBuilder.__calculate_angle(road_out)) < 5:
                        curve_pt = (
                            (road_in.end[0] + road_out.start[0]) / 2, 
                            (road_in.end[1] + road_out.start[1]) / 2
                        )
                    else:
                        curve_pt = BasicMapBuilder.__calculate_curve_point(road_in, road_out)

                    curve = CurveEdge(
                        input_lane_id=in_lane_id,
                        output_lane_id=out_lane_id,
                        curve_point=curve_pt
                    )
                    curve_id = len(self.map.curves)
                    self.map.curves.append(curve)

                    try:
                        self.map.extremes_lanes.remove(out_lane_id)
                    except:
                        print(f'road_out_id {out_lane_id} not in extremeRoads')

                    angle = BasicMapBuilder.__calculate_angle(road_in)

                    if i not in follows:
                        follows[i] = []

                    follows[i].append((angle, curve_id))
                i += 1

            tmp = follows
            follows = {}
            # print(f'TEMP: {tmp}')
            for i in tmp:
                angle, _ = tmp[i][0]

                for j in tmp:
                    if i == j: continue
                    
                    angle2, _ = tmp[j][0]

                    if angle > 180 and angle2 < 180:
                        angle %= 180
                    if angle < 180 and angle2 > 180:
                        angle2 %= 180                    
                    
                    if abs(angle - angle2) < 1e-8:
                        if angle not in follows:
                            follows[angle] = []
                        follows[angle] += [(
                            self.map.curves[curve_id].input_lane_id,
                            self.map.curves[curve_id].output_lane_id, i) 
                            for _, curve_id in tmp[j]]

                if angle not in follows:
                    follows[angle] = []
                follows[angle] += [(
                    self.map.curves[curve_id].input_lane_id,
                    self.map.curves[curve_id].output_lane_id, i) 
                    for _, curve_id in tmp[i]]
            
            j = 0
            tmp = follows
            follows = set()
            turning_left  = {}
            turning_right = {}
            for _, tuples in tmp.items():
                for in_id, out_id, sect in tuples:
                    road_in  = self.map.lanes[in_id]
                    road_out = self.map.lanes[out_id]
                    if is_turning_left(road_in, road_out):
                        if j not in turning_left:
                            turning_left[j] = []
                        turning_left[j].append((in_id, out_id))
                    elif is_turning_right(road_in, road_out):
                        if j not in turning_right:
                            turning_right[j] = []
                        turning_right[j].append((in_id, out_id, j))
                    else:
                        follows.add((in_id, out_id, j))
                j += 1

            for _, tuples in turning_left.items():
                extreme_left00 = extreme_left01 = extreme_left10 = extreme_left11 = None
                min_distance = maxsize

                for in_id0, out_id0 in tuples:
                    for in_id1, out_id1 in tuples:

                        road_in0 = self.map.lanes[in_id0]
                        road_in1 = self.map.lanes[in_id1]
                        
                        if distance.euclidean(road_in0.start, road_in1.start) == \
                           distance.euclidean(road_in0.end, road_in1.end):  continue

                        if distance.euclidean(road_in0.end, road_in1.end) \
                            < min_distance:
                            extreme_left00 = (in_id0, out_id0)
                            extreme_left01 = (in_id1, out_id1)
                            min_distance = distance.euclidean(road_in0.end, road_in1.end) 
                        elif distance.euclidean(road_in0.end, road_in1.end) \
                            == min_distance:
                            extreme_left10 = (in_id0, out_id0)
                            extreme_left11 = (in_id1, out_id1)         
                
                in_id0, _ = extreme_left00
                in_id1, _ = extreme_left01
                
                rm = [(x, y, z) for x,y,z in follows if x == in_id0 or x == in_id1]
                for item in rm:
                    follows.remove(item)

                follows.add((*extreme_left00, j))
                follows.add((*extreme_left01, j))
                follows.add((*extreme_left10, j))
                follows.add((*extreme_left11, j))
                j += 1

            for _, tuples in turning_right.items():
                extreme_right00 = extreme_right01 = extreme_right10 = extreme_right11 = None
                max_distance = -maxsize
                for in_id0, out_id0, sect0 in tuples:
                    for in_id1, out_id1, sect1 in tuples:
                        
                        road_in0  = self.map.lanes[in_id0]
                        road_in1  = self.map.lanes[in_id1]
                        
                        if distance.euclidean(road_in0.start, road_in1.start) == \
                           distance.euclidean(road_in0.end, road_in1.end):  continue

                        if distance.euclidean(road_in0.end, road_in1.end) \
                            > max_distance:
                            extreme_right00 = (in_id0, out_id0, sect0)
                            extreme_right01 = (in_id1, out_id1, sect1)
                            max_distance = distance.euclidean(road_in0.end, road_in1.end)
                        elif distance.euclidean(road_in0.end, road_in1.end) \
                            == max_distance:
                            extreme_right10 = (in_id0, out_id0, sect0)
                            extreme_right11 = (in_id1, out_id1, sect1)

                follows.add(extreme_right00)
                follows.add(extreme_right01)
                follows.add(extreme_right10)
                follows.add(extreme_right11)
                j += 1

            if len(follows) > 0:
                self.map.intersections[(x, y)].follows = [sect for sect in follows]            

    def __calculate_angle(road_in: Road) -> float:
        x0, y0 = road_in.start
        x1, y1 = road_in.end

        if (x0**2 + y0**2) > (x1**2 + y1**2):
            tmp = x0, y0
            x0, y0 = x1, y1
            x1, y1 = tmp

        # print(f'x0: {x0}, y0: {y0}, x1: {x1}, y1: {y1}')

        co = y1 - y0
        ca = x1 - x0

        if ca == 0 and co != 0:
            return 90.0

        h = (co**2 + ca**2)**0.5
        
        # print(f'co: {co}, ca: {ca}, h: {h}')
        try: 
            angle = math.acos((co**2 + ca**2 - h**2) / (2 * co * ca))
            angle = math.degrees(angle)
        except:
            pass
            # print('error 1')

        try: 
            angle = math.acos((co**2 + h**2 - ca**2) / (2 * co * h))
            angle = math.degrees(angle)
        except:
            pass
            # print('error 2')

        try:
            angle = math.acos((h**2 + ca**2 - co**2) / (2 * h * ca))
            angle = math.degrees(angle)
        except:
            pass
            # print('error 3')

        return angle

    def __calculate_curve_point(road_a: Road, road_b: Road):
        '''calculates the point where the curve should be created'''
        xa_0, ya_0 = road_a.start
        xa_1, ya_1 = road_a.end
        xb_0, yb_0 = road_b.start
        xb_1, yb_1 = road_b.end
        print(road_a.__dict__, road_b.__dict__)

        try:
            m_a = (ya_1 - ya_0) / (xa_1 - xa_0)
        except ZeroDivisionError:
            ...

        try:
            m_b = (yb_1 - yb_0) / (xb_1 - xb_0)
        except ZeroDivisionError:
            ...

        n_a = 0
        if xa_1 - xa_0 == 0:
            x = xa_0
            m_a = 0
        elif xb_1 - xb_0 == 0:
            x = xb_0
            m_a = 0
        else:
            n_a = ya_0 - xa_0*m_a
            n_b = yb_0 - xb_0*m_b
            try:
                x = (n_b - n_a) / (m_a - m_b)
            except ZeroDivisionError:
                x = (xa_1 + xb_0) / 2

        y = 0
        if ya_1 - ya_0 == 0:
            y = ya_0
        elif yb_1 - yb_0 == 0:
            y = yb_0
        else:
            y = m_a * x + n_a

        return (x, y) 


class GridMapBuilder(BasicMapBuilder):

    def __init__(self, 
        center_point: Tuple[float, float], 
        len_roads: float, 
        lower_limit_x: float = 0, 
        lower_limit_y: float = 0, 
        upper_limit_x: float = 1400, 
        upper_limit_y: float = 800,
        in_roads: int = 2,
        out_roads: int = 2,
        width_roads: float = 0.5
    ):
        super().__init__()

        self.center_point = center_point
        self.len_roads = len_roads
        self.lower_limit_x = lower_limit_x
        self.lower_limit_y = lower_limit_y
        self.upper_limit_x = upper_limit_x
        self.upper_limit_y = upper_limit_y
        self.in_roads = in_roads
        self.out_roads = out_roads
        self.map.width_roads = width_roads

        self.__recalculate_limits()

    def build_map(self) -> Map:

        edges = set()
        stack = [self.center_point]

        while len(stack) > 0:
            
            vX, vY = heapq.heappop(stack)
            pts = [
                (vX + self.len_roads, vY), 
                (vX - self.len_roads, vY), 
                (vX, vY + self.len_roads), 
                (vX, vY - self.len_roads)
            ]
            
            for pt in pts:
                if ((vX, vY), pt) not in edges and (pt, (vX, vY)) not in edges \
                    and self.__is_valid(pt):
                    
                    pt0 = (vX, vY)
                    pt1 = pt
        
                    if (pt0[0]**2 + pt0[1]**2)**0.5 > (pt1[0]**2 + pt1[1]**2)**0.5:
                        pt0 = pt
                        pt1 = (vX, vY)

                    if ((pt0[0] <= self.lower_limit_x or pt0[0] >= self.upper_limit_x) and \
                        (pt1[0] <= self.lower_limit_x or pt1[0] >= self.upper_limit_x)) or \
                       ((pt0[1] <= self.lower_limit_y or pt0[1] >= self.upper_limit_y) and \
                        (pt1[1] <= self.lower_limit_y or pt1[1] >= self.upper_limit_y)): 
                        continue

                    self._BasicMapBuilder__build_roads(
                        pt0, pt1, self.in_roads, self.out_roads, self.map.width_roads)
                    
                    heapq.heappush(stack, pt)
                    edges.add((pt0, pt1))

        self._BasicMapBuilder__build_intersections()

        # add the frequency of vehicles in each road
        for road in self.map.roads:
            for i in road.lanes:
                horizontal = abs(self.map.lanes[i].end[1] - self.map.lanes[i].start[1]) < \
                                abs(self.map.lanes[i].end[0] - self.map.lanes[i].start[0]) 
                if horizontal:
                    self.map.lanes[i].lambda_ = random.uniform(0.03, 0.05)
                else:
                    self.map.lanes[i].lambda_ = random.uniform(0, 0.04)
                # print(f'\n{self.map.lanes[i]}\n')


        return deepcopy(self.map) , edges
    
    def __recalculate_limits(self):
            x, y = self.center_point
            X, Y = self.center_point

            while x > self.lower_limit_x or \
                y > self.lower_limit_y or \
                X < self.upper_limit_x or \
                Y < self.upper_limit_y:
                if x > self.lower_limit_x: x -= self.len_roads
                if y > self.lower_limit_y: y -= self.len_roads
                if X < self.upper_limit_x: X += self.len_roads
                if Y < self.upper_limit_y: Y += self.len_roads
            else:
                x += self.len_roads
                X -= self.len_roads
                y += self.len_roads
                Y -= self.len_roads
            
            self.lower_limit_x = x
            self.lower_limit_y = y
            self.upper_limit_x = X
            self.upper_limit_y = Y

    def __is_valid(self, pt):
            return pt[0] >= self.lower_limit_x and \
                pt[0] <= self.upper_limit_x and \
                pt[1] >= self.lower_limit_y and \
                pt[1] <= self.upper_limit_y


import heapq
from sys import maxsize

def get_nearest_lane(map: Map, start, end):
    return random.choice( 
        [ lane 
            for lane in map.intersections[start].out_lanes
                for lane2 in map.intersections[end].input_lanes
                    if lane == lane2
        ]
    )

def get_nearest_nodes(map: Map, edges, visited, lane_id):

    def get_point(pt):
        for x, y in visited:
            if x == pt[0] and y == pt[1]:
                return visited[(x,y)]
        return -1

    start = map.lanes[lane_id].start
    end   = map.lanes[lane_id].end

    for (x0, y0), (x1, y1) in edges:
        # print(x0, x1, y0, y1)
        if (x0, y0) != (x1, y1): 
            lane_id = get_nearest_lane(map, (x0,y0), (x1,y1))
            lane = map.lanes[lane_id]
            if lane.start == start and lane.end == end:
                return get_point((x0,y0)), get_point((x1,y1))

        # print(x0, x1, y0, y1)

    return -1

def a(map: Map, edges, visited, paths, i, j, k):

    def get_point(pt):
        for x, y in visited:
            if visited[(x,y)] == pt:
                return x, y
        return -1

    s0 = e0 = s1 = e1 = 0

    if len(paths[i][k]) == 0 or len(paths[k][j]) == 0:
        return False
    
    s0, e0 = paths[i][k][len(paths[i][k]) - 1], k
    s1, e1 = k, paths[k][j][0]
    
    s0 = get_nearest_nodes(map, edges, visited, s0)
    e1 = get_nearest_nodes(map, edges, visited, e1)

    if s0 == -1 or e1 == -1: return False
    
    s0, _ = s0
    _, e1 = e1

    # print(visited)
    # print(paths)
    s0 = get_point(s0)
    e0 = get_point(e0)
    s1 = get_point(s1)
    e1 = get_point(e1)

    # print(paths[k][j])
    # print(s0, e0, s1, e1)
    # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    
    lane_in_id  = get_nearest_lane(map, s0, e0)
    lane_out_id = get_nearest_lane(map, s1, e1)

    k = get_point(k)
    # print(map.intersections.keys())
    # print(k0, k1)

    return len ([follows for follows in map.intersections[k].follows
        if map.lanes[follows[0]] == lane_in_id and \
           map.lanes[follows[1]] == lane_out_id ]) > 0

def floyd_warshall(map: Map, edges: set):
    visited = dict()

    for x, y in map.intersections:
        for (x0, y0), (x1, y1) in edges:
            if (x0, y0) == (x, y) and (x1, y1) not in visited:
                visited[(x1, y1)] = len(visited)
            if (x1, y1) == (x, y) and (x0, y0) not in visited:
                visited[(x0, y0)] = len(visited)

    paths = [[[] for _ in range(len(visited))]      for _ in range(len(visited))]
    costs = [[maxsize for _ in range(len(visited))] for _ in range(len(visited))]

    (x0, y0), (x1, y1) = [t for t in iter(edges)][0]
    len_roads = distance.euclidean((x0, y0), (x1, y1))
    
    for i, ((x0, y0), (x1, y1)) in enumerate(edges):
        i = visited[(x0, y0)]
        j = visited[(x1, y1)]
        costs[i][j] = len_roads
        paths[i][j] = [i]

    for i in range(len(visited)):
        costs[i][i] = 0

    for k in range(len(visited)):
        for i in range(len(visited)):
            for j in range(len(visited)):
                if k == i or k == j or i == j: # or \
                    # not a(map, edges, visited, paths, i, j, k): 
                    continue
                if costs[i][k] + costs[k][j] < costs[i][j]:
                    costs[i][j] = costs[i][k] + costs[k][j]
                    paths[i][j] = paths[i][k] + paths[k][j]

    
    for i in range(len(visited)):
        for j in range(len(visited)):
            if i == j: continue
            path = ""
            for edge_id in paths[i][j]:
                
                edge = None
                for i, edg in enumerate(edges):
                    if i == edge_id:
                        edge = edg
                        break
                
                # s,e = edge
                # path += f"( {s} --> {e} ) ====>"
            if path != "":
                print(path)
    

    # print(f'PATH: {paths}')

    return visited, costs, paths


class VehicleGeneration:

    def __init__(self, map: Map, edges: set):
        visited, matrix, paths = floyd_warshall(map, edges)
        self.visited = visited
        self.matrix = matrix
        self.edges = edges
        self.paths = paths
        self.map = map

    def generate_cars_round(self, dt, time):
        cars = []

        for lane_id in self.map.extremes_lanes:
            lane = self.map.lanes[lane_id]

            r = random.random()
            if r > navigation._navigation__poisson(lane.lambda_, dt, 1):
                continue

            # get nearest point of `lane.start`
            best = (maxsize, (0,0))
            for x, y in self.visited.keys():
                if distance.euclidean(lane.start, (x, y)) < best[0]:
                    best = (distance.euclidean(lane.start, (x, y)), (x, y))

            u = self.visited[best[1]]
            v = u
            while u == v:
                v = random.randint(0, len(self.visited)-1)

            # get path from U to V intersection node
            # print(f"u: {u} == v: {v} == path: {len(self.paths[u])}")
            path = self.paths[u][v]
            # print('!!!')
            # print(path)
            car: Vehicle = Vehicle(path=path, start=time)
            cars.append(car)

        return cars

    def generate_cars(self, time_generation = 10, step_size = 0.014):
        cars = []
        current = 0

        while current  < time_generation:
            cars += self.generate_cars_round(step_size, current)
            current += step_size

        cars = [car for car in cars if len(car.path) > 0]

        return cars


class TemplateIO:

    def __init__(self, builder: BasicMapBuilder):
        self.builder = builder

    def generate_template(self, name: str):

        ddb.config.storage_directory = '../ddb_storage'
        s = ddb.at(name)
        if not s.exists():
            map, edges = self.builder.build_map()            
            cars = []# cars = VehicleGeneration(map, edges).generate_cars()
            temp = Template(map=map, vehicles=cars)

            s.create(
                NodeVisitor().visit(temp)
            )

    def load_template(self, name: str):
        
        ddb.config.storage_directory = '../ddb_storage'
        s = ddb.at(name)
        if s.exists():
            json = s.read()
            draw = new_draw()
            draw.ctrl = metaeh_control()
            ctrl = draw.ctrl

            # add roads
            print(f"AMOUNT OF LANES: {len(json['map']['lanes'])}")
            for lane in json['map']['lanes']:
                ctrl.AddRoad(
                    road_init_point=lane['start'],
                    road_end_point=lane['end'],
                    lambda_=lane['lambda_'],
                )

            # add connections between roads            
            for curve in json['map']['curves']:
                ctrl.connect_roads(
                    road_1_id=curve['input_lane_id'],
                    road_2_id=curve['output_lane_id'],
                    curve_point=curve['curve_point']
                )
            
            i = 0
            # create intersections
            for x in json['map']['intersections']:
                for y in json['map']['intersections'][x]:
                    follows = json['map']['intersections'][x][y]['follows']
                    follows = [ tuple(f) for f in follows ] 
                    
                    if i % 2 != 0:
                        ctrl.CreateCorner(follows, ligth_controled=False)
                    else:
                        ctrl.CreateCorner(follows)
                    i += 1

            # add extremes roads
            ctrl.AddExtremeRoads(json['map']['extremes_lanes'])

            ctrl.speed = 5

            cars = []
            # for car in json['vehicles']:
            #     path, start = car['path'], car['start']
            #     start, car = ctrl.AddRoutedVehicle(path, start)
            #     cars.append((start, car))

            return draw, cars
