from matplotlib.hatch import HorizontalHatch
from models.control import control


RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (127, 127, 127)


pos_x = [0, 350, 700, 1050]
pos_y = [0, 200, 400, 600]
h_diff = 20
v_diff = 20
road_width = 10
ctrl = control()
# pos_x, pos_y, end_y, start_x, curv = 700, 410, 900, 0, 5

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

IH = ctrl.AddRoad( (pos_x[2] + h_diff / 2, pos_y[1] - v_diff), (pos_x[2] + h_diff / 2, pos_y[0]))
CI = ctrl.AddRoad( (pos_x[2] + h_diff / 2, pos_y[2] - v_diff), (pos_x[2] + h_diff / 2, pos_y[1] + v_diff / 2))
FC = ctrl.AddRoad( (pos_x[2] + h_diff / 2, pos_y[3]), (pos_x[2] + h_diff / 2, pos_y[2] + v_diff / 2))

ctrl.AddExtremeRoads([AB, DC, FC, KJ, LJ])

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
    
# road_WC_id = ctrl.AddRoad((start_x, pos_y), (pos_x, pos_y))


# road_CS_id = ctrl.AddRoad((pos_x + curv, pos_y + curv), (pos_x + curv, end_y))
# road_curWCS_ids = ctrl.connect_roads(road_WC_id, road_CS_id, (pos_x + curv, pos_y))


# pos_x, pos_y, end_y, start_x, curv = 720, 400, 200, 1400, -5
# road_EC_id = ctrl.AddRoad((start_x, pos_y), (pos_x, pos_y))
# road_CE_id = ctrl.AddRoad((pos_x, pos_y + 10), (start_x, pos_y + 10))
# road_CN_id = ctrl.AddRoad((pos_x + curv, pos_y + curv), (pos_x + curv, end_y))

# pos_x, pos_y, end_y, start_x, curv = 720, 400, 200, 1400, -5
# road_EC_id = ctrl.AddRoad((start_x, pos_y), (pos_x, pos_y))


# road_curvECN_ids = ctrl.connect_roads(road_EC_id, road_CN_id, (pos_x + curv, pos_y))
# road_curvECW_ids = ctrl.connect_roads(road_EC_id, road_CW_id, (pos_x, pos_y))
# road_curvWCE_ids = ctrl.connect_roads(road_WC_id, road_CE_id, (pos_x, pos_y + 10))
# road_curvWCN_ids = ctrl.connect_roads(road_WC_id, road_CN_id, (pos_x - curv, pos_y))
# road_curvECS_ids = ctrl.connect_roads(road_EC_id, road_CS_id, (pos_x + curv, pos_y))


# curv_x = -5; curv_y = -5; 
# road_NE_id = ctrl.AddRoad((pos_x, end_y + curv_y), (start_x, end_y + curv_y))
# road_curvCNE_ids = ctrl.connect_roads(road_CN_id, road_NE_id, (pos_x + curv_x, end_y + curv_y))



# ctrl.CreateCorner([(road_WC_id, road_CS_id, 0), (road_EC_id, road_CN_id, 1), (road_EC_id, road_CW_id, 1),\
#     (road_WC_id, road_CN_id, 0), (road_EC_id, road_CS_id,1), (road_WC_id, road_CE_id, 0)])
# ctrl.roads[road_CN_id].end_conn = ctrl.roads[road_NE_id]
# ctrl.curves[(road_NE_id, road_NE_id)] = road_curvCNE_ids
ctrl.Start()
