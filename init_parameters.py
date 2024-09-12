import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from math import factorial
import pandas as pd


init_data = pd.DataFrame([
        {'xi': 0.0, 'dv*EI': 0.0,  'dφ*EI': 56.0/3,     'dM': 0.0, 'dQ': 5.0, 'q': 0},
        {'xi': 2.0, 'dv*EI': 0.0,  'dφ*EI': 0.0,        'dM': 0.0, 'dQ': -6.0, 'q': 4},
        {'xi': 4.0, 'dv*EI': 0.0,  'dφ*EI': -58.0/3,    'dM': 0.0, 'dQ': 0.0, 'q': 4},
        ])


st.write('Ниже записано общее решение уравнения изгиба балки с применением метода начальных параметров')
st.write(
    '''$EI \\cdot v_i(x) = EI \\cdot v_{i-1}(x) +EI \\cdot \\Delta v  + EI \\cdot \\Delta \\varphi \\cdot (x - x_i) - \\dfrac{\\Delta M \\ cdot (x - x_i)^2}{2!} - \\dfrac{\\Delta Q \\cdot (x - x_i)^3}{3!} +  \\dfrac{(q_i - q_{i-1}) \\cdot (x - x_i)^4}{4!} $''')

column_conf = {
        'xi': st.column_config.NumberColumn('xi', help='Координата начала участка', format='%.2f', required=True, default=0),
        'dv*EI': st.column_config.NumberColumn('dv*EI', help='Дополнительный прогиб в начале участка', format='%.2f', required=True, default=0),
        'dφ*EI': st.column_config.NumberColumn('dφ*EI', help='Дополнительный угол поворота в начале участка', format='%.2f', required=True, default=0),
        'dM': st.column_config.NumberColumn('dM', help='Дополнительный момент в начале участка', format='%.2f', required=True, default=0),
        'dQ': st.column_config.NumberColumn('dQ', help='Дополнительная сосредоточенная сила в начале участка', format='%.2f', required=True, default=0),
        'q': st.column_config.NumberColumn('q', help='Интенсивность распределенной нагрузки на участке', format='%.2f', required=True, default=0),
        }

st.write('Для построения графиков введите в таблицу ниже значения начальных параметров для каждого из участков балки, а также общую длину балки в поле под таблицей.')
data = st.data_editor(init_data, hide_index=False, use_container_width=True, num_rows='dynamic', column_config=column_conf)
L = st.number_input(label=r'Полная длина балки', value=6.0, step=0.1, format='%.1f', min_value=1.0)

#Общее решение методом начальных параметров для произвольного участка
def EJvi(EJdv, EJdf, dM, dQ, qi, qp, xi):
    return lambda x: EJdv + EJdf*(x-xi) - dM*(x-xi)**2/factorial(2) - dQ*(x-xi)**3/factorial(3) + (qi-qp)*(x-xi)**4/factorial(4)

def EJfi(EJdv, EJdf, dM, dQ, qi, qp, xi):
    return lambda x: EJdf - dM*(x-xi) - dQ*(x-xi)**2/factorial(2) + (qi-qp)*(x-xi)**3/factorial(3)

def Mi(EJdv, EJdf, dM, dQ, qi, qp, xi):
    return lambda x: dM + dQ*(x-xi) - (qi-qp)*(x-xi)**2/factorial(2)

def Qi(EJdv, EJdf, dM, dQ, qi, qp, xi):
    return lambda x: dQ - (qi-qp)*(x-xi)



xi_arr = data['xi'].tolist()
num_of_elements = len(xi_arr)
xi_arr.append(L)
EJdv_arr = data['dv*EI'].tolist()
EJdf_arr = data['dφ*EI'].tolist()
dM_arr = data['dM'].tolist()
dQ_arr = data['dQ'].tolist()
qi_arr = data['q'].tolist()
#Значение распределенной нагрузки на предыдущем участке
qp_arr = [0]
for i in range(1, len(qi_arr)):
    qp_arr.append(qi_arr[i-1])

v_arr = []
f_arr = []
M_arr = []
Q_arr = []
for k in range(num_of_elements):
    v_arr.append(EJvi(EJdv_arr[k], EJdf_arr[k], dM_arr[k], dQ_arr[k], qi_arr[k], qp_arr[k], xi_arr[k]))
    f_arr.append(EJfi(EJdv_arr[k], EJdf_arr[k], dM_arr[k], dQ_arr[k], qi_arr[k], qp_arr[k], xi_arr[k]))
    M_arr.append(Mi(EJdv_arr[k], EJdf_arr[k], dM_arr[k], dQ_arr[k], qi_arr[k], qp_arr[k], xi_arr[k]))
    Q_arr.append(Qi(EJdv_arr[k], EJdf_arr[k], dM_arr[k], dQ_arr[k], qi_arr[k], qp_arr[k], xi_arr[k]))


num_points = 9
points = []
for i in range(num_of_elements):
    points.append(np.linspace(xi_arr[i], xi_arr[i+1], num_points).tolist())

v = [[0 for k in points[i]] for i in range(num_of_elements)]
f = [[0 for k in points[i]] for i in range(num_of_elements)]
M = [[0 for k in points[i]] for i in range(num_of_elements)]
Q = [[0 for k in points[i]] for i in range(num_of_elements)]

for i in range(num_of_elements):
    for p in range(len(points[i])):
        for k in range(0,i+1):
            v[i][p] = v[i][p] + v_arr[k](points[i][p])
            f[i][p] = f[i][p] + f_arr[k](points[i][p])
            M[i][p] = M[i][p] + M_arr[k](points[i][p])
            Q[i][p] = Q[i][p] + Q_arr[k](points[i][p]) 
    

##def plots():
fig = make_subplots(rows = 2,cols = 2, subplot_titles=['Перемещения v*EI', 'Углы поворота φ*EI', 'Момент Mz', 'Поперечная сила Qy'])
for i in range(num_of_elements):
    fig.add_trace(go.Scatter(x=points[i], y=v[i], showlegend=False, line=dict(color = "LightSkyBlue")), row = 1, col = 1)
    fig.add_trace(go.Scatter(x=points[i], y=f[i], showlegend=False, line=dict(color = "LightSkyBlue")), row = 1, col = 2)
    fig.add_trace(go.Scatter(x=points[i], y=M[i], showlegend=False, line=dict(color = "LightSkyBlue")), row = 2, col = 1)
    fig.add_trace(go.Scatter(x=points[i], y=Q[i], showlegend=False, line=dict(color = "LightSkyBlue")), row = 2, col = 2)

fig.update_yaxes(autorange="reversed", row=1, col=1)
fig.update_yaxes(autorange="reversed", row=1, col=2)
fig.update_yaxes(autorange="reversed", row=2, col=1)
fig.update_yaxes(autorange="reversed", row=2, col=2)
fig.update_layout(height=500)
##    fig.show(config={ 'modeBarButtonsToRemove': ['zoom', 'pan'] })
##    return fig

##st.components.v1.html(fig.to_html(include_mathjax='cdn'), height=500)
##st.write(1)

st.plotly_chart(fig)









