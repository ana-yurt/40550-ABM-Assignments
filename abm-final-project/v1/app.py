from model import EthnicViolenceModel
from mesa.visualization import Slider, SolaraViz, make_plot_component, make_space_component

def agent_portrayal(agent):
    return {"color":"red" if agent.ethnicity=="majority" else "blue","marker":"s","size":2}

model_params = {
    "width":        Slider("Grid Width",    60,20,300,1),
    "height":       Slider("Grid Height",   60,20,300,1),
    "majority_pct": Slider("Majority %",    0.7,0.0,1.0,0.01),
    "density":      Slider("Density",       0.6,0.0,1.0,0.01),
    "alpha":        Slider("Alpha",         0.2,0.0,0.5,0.01),
    "beta":         Slider("Beta",          0.05,0.0,0.5,0.01),
    "decay":        Slider("Decay",         0.8,0.7,1.0,0.01),
    "vision":       Slider("Vision",        2,  1,  5,  1),
}

# pull defaults
default_kwargs = {k:v.value for k,v in model_params.items()}
print("Default model parameters:", default_kwargs)
eth_model = EthnicViolenceModel(**default_kwargs)

SpaceGraph = make_space_component(agent_portrayal=agent_portrayal)
MajPlot    = make_plot_component("Avg_Maj_Grievance")
MinPlot    = make_plot_component("Avg_Min_Grievance")
ThrPlot    = make_plot_component("Avg_Maj_Threshold")
VioPlot = make_plot_component("Overall_Violence_Level")
InteractionsPlot = make_plot_component("Overall_Interactions")

# chart options to force one tick per x-step and show data‐labels
chart_options = {
    "plugins": {
        "datalabels": {
            "display": True,
            "anchor": "end",
            "align": "top",
            # format value to two decimals
            "formatter": "function(value){return value.toFixed(3);}"
        }
    }
}

page = SolaraViz(
    model=eth_model,
    components=[SpaceGraph, MajPlot, MinPlot, ThrPlot, VioPlot, InteractionsPlot],
    model_params=model_params,
    name="Ethnic Violence ABM",
    chart_opts=chart_options,   # <-- pass your Chart.js config here
)
