"""
Versão corrigida — checkboxes por REUNIÃO do FOMC (evento_id), com
rótulo legível (mês/ano da reunião), começando tudo desmarcado.

Uso:
    python3 visualizar.py

Requer: pandas, pyarrow, plotly
"""

import pandas as pd
import plotly.graph_objects as go

MESES_PT = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

# --- Carrega os dados ---
fed = pd.read_parquet('data/polymarket_fed_probabilities.parquet')
fed['data'] = pd.to_datetime(fed['data'])

eventos = sorted(fed['evento_id'].unique())
print(f"Total de eventos (reuniões) encontrados: {len(eventos)}")

# --- Para cada evento, monta um rótulo legível: "Mar/2024 — 3 mercados" ---
rotulos = {}
for evento in eventos:
    sub = fed[fed['evento_id'] == evento]
    # Usamos a ÚLTIMA data (mais próxima da resolução/reunião real),
    # não a primeira (que é só quando o mercado começou a ser negociado
    # e pode ser meses antes da reunião de fato).
    ultima_data = sub['data'].max()
    n_mercados = sub['mercado'].nunique()
    rotulo = f"{MESES_PT[ultima_data.month]}/{ultima_data.year} ({n_mercados} mercado{'s' if n_mercados > 1 else ''}) [id:{evento}]"
    rotulos[evento] = rotulo

# --- Monta UMA trace por (evento, mercado) — várias traces podem
#     pertencer ao mesmo evento (ex: "25bps cut", "no change", etc) ---
fig = go.Figure()
trace_para_evento = []  # índice da trace -> evento_id, para o toggle em grupo

for evento in eventos:
    sub_evento = fed[fed['evento_id'] == evento]
    for mercado in sub_evento['mercado'].unique():
        sub = sub_evento[sub_evento['mercado'] == mercado].sort_values('data')
        fig.add_trace(go.Scatter(
            x=sub['data'],
            y=sub['probabilidade'],
            mode='lines',
            name=mercado[:60],
            visible=False,   # tudo começa OCULTO — você escolhe o que ver
            showlegend=False,  # a legenda nativa fica desligada;
                               # quem controla é a lista de checkboxes
        ))
        trace_para_evento.append(evento)

fig.update_layout(
    title='Probabilidades Fed/FOMC (Polymarket) — marque as reuniões que quer ver',
    yaxis_title='Probabilidade',
    xaxis_title='Data',
    height=650,
    showlegend=False,
)

plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='grafico')

# --- Checkboxes: um por REUNIÃO (evento_id), não por mercado individual ---
checkboxes_html = ""
for evento in eventos:
    # índices de todas as traces que pertencem a este evento
    indices = [i for i, e in enumerate(trace_para_evento) if e == evento]
    indices_js = ",".join(str(i) for i in indices)
    checkboxes_html += f'''
    <label style="display:block; font-size:13px; margin:3px 0; cursor:pointer;">
        <input type="checkbox"
               onchange="toggleEvento([{indices_js}], this.checked)">
        {rotulos[evento]}
    </label>
    '''

botoes_html = '''
<div style="margin-bottom:10px;">
    <button onclick="toggleTudo(true)">Marcar todos</button>
    <button onclick="toggleTudo(false)">Desmarcar todos</button>
</div>
'''

script = f'''
<script>
function toggleEvento(indices, visivel) {{
    var updates = {{visible: indices.map(() => visivel)}};
    Plotly.restyle('grafico', updates, indices);
}}
function toggleTudo(visivel) {{
    var total = {len(trace_para_evento)};
    var indices = Array.from({{length: total}}, (_, i) => i);
    var visibles = Array(total).fill(visivel);
    Plotly.restyle('grafico', {{visible: visibles}}, indices);
    document.querySelectorAll('#checkboxes input[type=checkbox]').forEach(
        cb => cb.checked = visivel
    );
}}
</script>
'''

html_final = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        html, body {{ margin:0; padding:0; height:100%; font-family: sans-serif; }}
        .container {{ display:flex; height:100vh; }}
        .grafico-area {{ flex:1; min-width:0; overflow:hidden; }}
        #checkboxes {{
            width:320px;
            flex-shrink:0;
            overflow-y:scroll;
            height:100vh;
            padding:15px;
            box-sizing:border-box;
            border-left:1px solid #ccc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="grafico-area">
            {plot_html}
        </div>
        <div id="checkboxes">
            <h4>Reuniões do FOMC</h4>
            {botoes_html}
            {checkboxes_html}
        </div>
    </div>
    {script}
</body>
</html>
'''

with open('data/preview_fed_interativo.html', 'w') as f:
    f.write(html_final)

print("Salvo: data/preview_fed_interativo.html")