import solara
from model import SchellingModel
from mesa.visualization import (  
    SolaraViz,
    make_space_component,
    make_plot_component,
)

## Define agent portrayal: color, shape, and size

def agent_portrayal(agent):
    return {
        "color": "blue" if agent.type == 1 else "red",
        "marker": "s",
        "size": 40,
    }

## Enumerate variable parameters in model: seed, grid dimensions, population density, agent preferences, vision, and relative size of groups.
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": {
        "type": "SliderInt",
        "value": 50,
        "label": "Width",
        "min": 5,
        "max": 100,
        "step": 1,
    },
    "height": {
        "type": "SliderInt",
        "value": 50,
        "label": "Height",
        "min": 5,
        "max": 100,
        "step": 1,
    },
    "density": {
        "type": "SliderFloat",
        "value": 0.6,
        "label": "Population Density",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },
    "group_one_share": {
        "type": "SliderFloat",
        "value": 0.7,
        "label": "Share Type 1 Agents",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },
    "radius": {
        "type": "SliderInt",
        "value": 1,
        "label": "Vision Radius",
        "min": 1,
        "max": 5,
        "step": 1,
    },
    # New heterogeneous tolerance parameters
    "tolerance_mean": {
        "type": "SliderFloat",
        "value": 0.5,
        "label": "Tolerance Floor Mean",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },
    "tolerance_std": {
        "type": "SliderFloat",
        "value": 0.1,
        "label": "Tolerance Floor Std",
        "min": 0,
        "max": 0.5,
        "step": 0.01,
    },
    
    "tolerance_upper": {
        "type": "SliderFloat",
        "value": 0.8,
        "label": "Homogeneity Upper Limit",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },
    # New moving-cost parameter
    "moving_cost": {
        "type": "SliderFloat",
        "value": 0.1,
        "label": "Moving Cost",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },

}
schelling_model = SchellingModel()
HappyPlot = make_plot_component({"share_happy": "tab:green"})
SpaceGraph = make_space_component(agent_portrayal, draw_grid=False)

## Instantiate
page = SolaraViz(
    schelling_model,
    components=[SpaceGraph, HappyPlot],
    model_params=model_params,
    name="Schelling Segregation Model with Heterogeneity",
)

page
