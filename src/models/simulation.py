from abc import ABC
import models.Floyd_Warshall
from models.metaheuristic_control import metaeh_control
from templates.templates import GridMapBuilder, TemplateIO


#classes used to create different simulations given certain characteristics
#of the map, given by the class that inherit from Simulation. 

class Simulation(ABC):
    def get_new_control_object(self):
        pass
    
class Simulation_test_5(Simulation):
        
    def get_new_control_object(self):
        temp = GridMapBuilder(
            center_point=(700, 400), 
            len_roads=100, 
            lower_limit_x=0,
            lower_limit_y= 0, 
            upper_limit_x= 1400,
            upper_limit_y= 800,
            in_roads= 2,
            out_roads= 2,
            width_roads= 4
        )

        models.Floyd_Warshall.big = True
        temp = TemplateIO(temp)
        
        temp.generate_template('map5')
        draw, _ = temp.load_template('map5')
        ctrl = draw.ctrl
        
        ctrl.scale = 100
        ctrl.name = 'map5'
        ctrl.speed = 30 
        
        return ctrl

class Simulation_test_6(Simulation):
        
    def get_new_control_object(self):
        temp = GridMapBuilder(
            center_point=(700, 400), 
            len_roads=350, 
            lower_limit_x=0,
            lower_limit_y= 0, 
            upper_limit_x= 1400,
            upper_limit_y= 800,
            in_roads= 2,
            out_roads= 2,
            width_roads= 4
        )

        models.Floyd_Warshall.big = True
        temp = TemplateIO(temp)
        
        temp.generate_template('map6')
        draw, _ = temp.load_template('map6')
        ctrl = draw.ctrl
        
        ctrl.scale = 350
        ctrl.name = 'map6'
        ctrl.speed = 30 
        
        return ctrl


class Simulation_test_3(Simulation):
    
    def get_new_control_object(self):
        pos_x = [100, 450, 800, 1150]
        pos_y = [100, 300, 500, 700]
        h_diff = 20
        v_diff = 20
        road_width = 10
        
        ctrl = metaeh_control()

        AB = ctrl.AddRoad((pos_x[0], pos_y[2]), (pos_x[1], pos_y[2]))
        LJ = ctrl.AddRoad((pos_x[0], pos_y[1]), (pos_x[1], pos_y[1]))
        BA = ctrl.AddRoad((pos_x[1], pos_y[2] - road_width), (pos_x[0], pos_y[2] - road_width))

        BC = ctrl.AddRoad((pos_x[1] + h_diff, pos_y[2]), (pos_x[2], pos_y[2]))
        CB = ctrl.AddRoad((pos_x[2], pos_y[2] - road_width), (pos_x[1] + h_diff, pos_y[2] - road_width))

        JI = ctrl.AddRoad((pos_x[1] + h_diff, pos_y[1]), (pos_x[2], pos_y[1]))
        IJ = ctrl.AddRoad((pos_x[2], pos_y[1] - road_width), (pos_x[1] + h_diff, pos_y[1] - road_width))

        CD = ctrl.AddRoad((pos_x[2] + h_diff, pos_y[2]), (pos_x[3], pos_y[2]))
        DC = ctrl.AddRoad((pos_x[3], pos_y[2] - road_width), (pos_x[2] + h_diff, pos_y[2] - road_width))
        IG = ctrl.AddRoad((pos_x[2] + h_diff, pos_y[1]), (pos_x[3], pos_y[1]))

        KJ = ctrl.AddRoad((pos_x[1] + h_diff / 2, pos_y[0]), (pos_x[1] + h_diff / 2, pos_y[1] - v_diff))
        JB = ctrl.AddRoad((pos_x[1] + h_diff / 2, pos_y[1] + v_diff / 2), (pos_x[1] + h_diff / 2, pos_y[2] - v_diff))
        BE = ctrl.AddRoad((pos_x[1] + h_diff / 2, pos_y[2] + v_diff / 2), (pos_x[1] + h_diff / 2, pos_y[3]))

        IH = ctrl.AddRoad((pos_x[2] + h_diff / 2, pos_y[1] - v_diff), (pos_x[2] + h_diff / 2, pos_y[0]))
        CI = ctrl.AddRoad((pos_x[2] + h_diff / 2, pos_y[2] - v_diff), (pos_x[2] + h_diff / 2, pos_y[1] + v_diff / 2))
        FC = ctrl.AddRoad((pos_x[2] + h_diff / 2, pos_y[3]), (pos_x[2] + h_diff / 2, pos_y[2] + v_diff / 2))

        normal = 1/50
        factor = 20
        ctrl.AddExtremeRoads([AB, DC, FC, KJ, LJ], [normal * factor, normal * factor, normal, normal, normal])

        #curvas desde la izquiera
        ctrl.connect_roads(AB, BE, (pos_x[1] + h_diff / 2, pos_y[2]))
        ctrl.connect_roads(LJ, JB, (pos_x[1] + h_diff / 2, pos_y[1]))
        ctrl.connect_roads(BC, CI, (pos_x[2] + h_diff / 2, pos_y[2]))
        ctrl.connect_roads(JI, IH, (pos_x[2] + h_diff / 2, pos_y[1]))

        #curvas desde arriba
        ctrl.connect_roads(KJ, JI, (pos_x[1] + h_diff / 2, pos_y[1]))
        ctrl.connect_roads(JB, BA, (pos_x[1] + h_diff / 2, pos_y[2] - road_width))
        ctrl.connect_roads(JB, BC, (pos_x[1] + h_diff / 2, pos_y[2]))

        #curvas desde abajo
        ctrl.connect_roads(FC, CD, (pos_x[2] + h_diff / 2, pos_y[2]))
        ctrl.connect_roads(FC, CB, (pos_x[2] + h_diff / 2, pos_y[2] - road_width))
        ctrl.connect_roads(CI, IG, (pos_x[2] + h_diff / 2, pos_y[1]))
        ctrl.connect_roads(CI, IJ, (pos_x[2] + h_diff / 2, pos_y[1] - road_width))

        #curvas desde la derecha
        ctrl.connect_roads(DC, CI, (pos_x[2] + h_diff / 2, pos_y[2] - road_width))
        ctrl.connect_roads(CB, BE, (pos_x[1] + h_diff / 2, pos_y[2] - road_width))
        ctrl.connect_roads(IJ, JB, (pos_x[1] + h_diff / 2, pos_y[1] - road_width))

        #uniones rectas hortizontales
        ctrl.connect_roads(AB, BC, (pos_x[1], pos_y[2]))
        ctrl.connect_roads(LJ, JI, (pos_x[1], pos_y[1]))
        ctrl.connect_roads(JI, IG, (pos_x[2], pos_y[1]))
        ctrl.connect_roads(BC, CD, (pos_x[2], pos_y[2]))
        ctrl.connect_roads(CB, BA, (pos_x[1], pos_y[2] - road_width))
        ctrl.connect_roads(DC, CB, (pos_x[2], pos_y[2] - road_width))

        #uniones rectas verticales
        ctrl.connect_roads(KJ, JB, (pos_x[1] + h_diff / 2, pos_y[1]))
        ctrl.connect_roads(JB, BE, (pos_x[1] + h_diff / 2, pos_y[2]))
        ctrl.connect_roads(CI, IH, (pos_x[2] + h_diff / 2, pos_y[1]))
        ctrl.connect_roads(FC, CI, (pos_x[2] + h_diff / 2, pos_y[2]))


        ctrl.CreateCorner([(AB, BE, 0), (AB, BC, 0),\
            (CB, BE, 1), (CB, BA, 1),\
            (JB, BC, 2), (JB, BA, 2), (JB, BE, 2)])

        ctrl.CreateCorner([(BC, CD, 0), (BC, CI, 0),\
            (DC, CI, 1), (DC, CB, 1),\
            (FC, CD, 2), (FC, CB, 2), (FC, CI, 2)])

        ctrl.CreateCorner([(LJ, JI, 0), (LJ, JB, 0),\
            (IJ, JB, 1),\
            (KJ, JI, 2), (KJ, JB, 2)])

        ctrl.CreateCorner([(JI, IG, 0), (JI, IH, 0),\
            (CI, IH, 1), (CI, IG, 1), (CI, IJ, 1)])
        
        return ctrl