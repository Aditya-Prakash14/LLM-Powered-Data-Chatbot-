import plotly.graph_objects as go

def render_plotly_chart(chart_info):
    """Generates an interactive Plotly chart tailored to a sleek dark aesthetic."""
    chart_type = chart_info.get("type", "bar").lower()
    title = chart_info.get("title", "Data Visualization")
    labels = chart_info.get("labels", [])
    values = chart_info.get("values", [])
    metric_label = chart_info.get("label", "Value")
    
    fig = go.Figure()
    
    # Sleek harmonious color palette
    color_palette = ["#8A2BE2", "#00D2C4", "#FF5E7E", "#FFBE0B", "#3A86C8", "#FF007F"]
    primary_color = "#8A2BE2" # Neon Violet
    secondary_color = "#00D2C4" # Neon Cyan
    
    if chart_type == "bar":
        fig.add_trace(go.Bar(
            x=labels,
            y=values,
            name=metric_label,
            marker=dict(
                color=values,
                colorscale="Purples" if len(values) > 1 else [[0, primary_color], [1, primary_color]],
                showscale=False,
                line=dict(color="#111622", width=1)
            ),
            hovertemplate="<b>%{x}</b><br>" + metric_label + ": %{y:,.2f}<extra></extra>"
        ))
    elif chart_type == "line":
        fig.add_trace(go.Scatter(
            x=labels,
            y=values,
            mode="lines+markers",
            name=metric_label,
            line=dict(color=secondary_color, width=3.5),
            marker=dict(size=8, color="#FFFFFF", line=dict(color=secondary_color, width=2.5)),
            hovertemplate="<b>%{x}</b><br>" + metric_label + ": %{y:,.2f}<extra></extra>"
        ))
    elif chart_type == "scatter":
        fig.add_trace(go.Scatter(
            x=labels,
            y=values,
            mode="markers",
            name=metric_label,
            marker=dict(size=12, color="#FF5E7E", line=dict(color="#FFFFFF", width=1.5)),
            hovertemplate="<b>%{x}</b><br>" + metric_label + ": %{y:,.2f}<extra></extra>"
        ))
    elif chart_type == "pie":
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            hole=0.45,
            marker=dict(colors=color_palette),
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>" + metric_label + ": %{value:,.2f} (%{percent})<extra></extra>"
        ))
        
    # Styling layout parameters for a premium look
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color="#FFFFFF", family="Outfit, Inter, sans-serif"),
            x=0.5,
            xanchor="center"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            tickfont=dict(color="rgba(255,255,255,0.7)", size=11),
            linecolor="rgba(255,255,255,0.1)",
            title_font=dict(color="#94A3B8")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            tickfont=dict(color="rgba(255,255,255,0.7)", size=11),
            linecolor="rgba(255,255,255,0.1)",
            title_font=dict(color="#94A3B8"),
            tickformat=","
        ),
        legend=dict(
            font=dict(color="#FFFFFF", size=10),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380
    )
    
    return fig
