
from templates.templates import GridMapBuilder, TemplateIO
import models.Floyd_Warshall

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
draw, cars = temp.load_template('map6')
draw.ctrl.scale = 500
draw.ctrl.name = 'map6'
draw.ctrl.speed = 5 
draw.Start(observation_time=5000)
