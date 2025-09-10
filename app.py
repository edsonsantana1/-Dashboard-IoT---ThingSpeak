from flask import Flask, render_template
import requests
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

app = Flask(__name__)

# Configurações do ThingSpeak
THINGSPEAK_CHANNEL_ID = '2943258'
THINGSPEAK_API_KEY = 'G3BDQS6I5PRGFEWR'
NUM_RESULTS = 100
THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"


def get_thingspeak_data():
    params = {'results': NUM_RESULTS}
    if THINGSPEAK_API_KEY:
        params['api_key'] = THINGSPEAK_API_KEY

    response = requests.get(THINGSPEAK_URL, params=params)
    if response.status_code != 200:
        return None, "Erro ao acessar a API do ThingSpeak"

    data = response.json()['feeds']
    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['umidade'] = pd.to_numeric(df['field1'], errors='coerce')
    df['temperatura'] = pd.to_numeric(df['field2'], errors='coerce')
    df.dropna(subset=['umidade', 'temperatura'], inplace=True)
    return df, None


@app.route('/')
def index():
    df, error = get_thingspeak_data()
    if error:
        return f"<h1>{error}</h1>"

    last_temp = df['temperatura'].iloc[-1]
    last_umidade = df['umidade'].iloc[-1]

    # Gráfico de área para temperatura
    temp_trace = go.Scatter(
        x=df['created_at'],
        y=df['temperatura'],
        fill='tozeroy',
        mode='none',
        name='Temperatura (°C)',
        line=dict(color='tomato')
    )

    # Gráfico de barras para umidade
    umidade_trace = go.Bar(
        x=df['created_at'],
        y=df['umidade'],
        name='Umidade (%)',
        marker=dict(color='skyblue')
    )

    # Subplots com os dois gráficos
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("🔥 Temperatura - Gráfico de Área", "💧 Umidade - Gráfico de Barras"))

    fig.add_trace(temp_trace, row=1, col=1)
    fig.add_trace(umidade_trace, row=2, col=1)

    fig.update_layout(
        height=700,
        title_text="📊 Visão Comparativa dos Dados IoT",
        xaxis_title="Data e Hora",
        showlegend=False
    )

    dashboard_html = fig.to_html(full_html=False)

    return render_template("index.html",
                           last_temp=last_temp,
                           last_umidade=last_umidade,
                           dashboard_plot=dashboard_html)


if __name__ == '__main__':
    app.run(debug=True)
