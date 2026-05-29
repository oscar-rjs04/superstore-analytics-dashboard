import plotly.express as px
import plotly.graph_objects as go

_FONT = "Inter, system-ui, sans-serif"


def apply_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        font_family=_FONT,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=120, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title=dict(side="top center")),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E5E7EB", gridwidth=1)
    return fig


_MONTH_ABBREV = {
    "January": "Jan", "February": "Feb", "March": "Mar",
    "April": "Apr", "May": "May", "June": "Jun",
    "July": "Jul", "August": "Aug", "September": "Sep",
    "October": "Oct", "November": "Nov", "December": "Dec",
}


def line_chart(df, x, y, color=None, title="", **kwargs) -> go.Figure:
    return apply_theme(px.line(df, x=x, y=y, color=color, title=title, **kwargs))


def line_chart_dual(df, x, y, year_col, month_col, color=None, title="", **kwargs) -> go.Figure:
    fig = apply_theme(px.line(df, x=x, y=y, color=color, title=title, **kwargs))

    axis_df = (
        df[[x, year_col, month_col]]
        .drop_duplicates(subset=[x])
        .sort_values([year_col, month_col])
        .reset_index(drop=True)
    )
    periods = axis_df[x].tolist()
    years   = axis_df[year_col].tolist()
    months  = axis_df[month_col].tolist()

    tick_text = [_MONTH_ABBREV.get(m, m[:3]) for m in months]
    fig.update_xaxes(tickmode="array", tickvals=periods, ticktext=tick_text, tickangle=-90, title_standoff=40, tickfont=dict(size=11))

    seen, year_ranges = [], {}
    for i, yr in enumerate(years):
        if yr not in year_ranges:
            year_ranges[yr] = [i, i]
            seen.append(yr)
        else:
            year_ranges[yr][1] = i

    for yr in seen:
        start, end = year_ranges[yr]
        mid = (start + end) // 2
        fig.add_annotation(
            text=str(yr), x=mid, y=-0.2,
            xref="x", yref="paper",
            showarrow=False,
            font=dict(size=11, color="#D1D5DB"),
        )
        if start > 0:
            fig.add_shape(
                type="line",
                x0=start - 0.5, x1=start - 0.5, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="#D1D5DB", width=1, dash="dot"),
            )

    period_to_meta = {p: (str(yr), abbr) for p, yr, abbr in zip(periods, years, tick_text)}
    for trace in fig.data:
        xs = trace.x if trace.x is not None else []
        trace.customdata = [[*period_to_meta.get(p, ("", ""))] for p in xs]
        trace.hovertemplate = (
            "<b>%{customdata[0]} %{customdata[1]}</b><br>"
            "%{y:,.2f}<extra>%{fullData.name}</extra>"
        )

    fig.update_layout(margin=dict(b=100))
    return fig


def bar_chart(df, x, y, color=None, title="", orientation="v", **kwargs) -> go.Figure:
    cdm = kwargs.pop("color_discrete_map", None)
    axis_col = y if orientation == "h" else x

    one_color_per_bar = (
        color is not None
        and cdm is not None
        and df.groupby(axis_col)[color].nunique().max() == 1
    )

    if one_color_per_bar:
        marker_colors = [cdm.get(v, "#3B82F6") for v in df[color]]
        fig = apply_theme(px.bar(df, x=x, y=y, title=title, orientation=orientation, **kwargs))
        fig.update_traces(marker_color=marker_colors)
    else:
        if cdm:
            kwargs["color_discrete_map"] = cdm
        fig = apply_theme(px.bar(df, x=x, y=y, color=color, title=title, orientation=orientation, **kwargs))

    if orientation == "h":
        fig.update_layout(bargap=0.25, height=max(400, len(df) * 38))

    return fig


def pie_chart(df, names, values, title="", **kwargs) -> go.Figure:
    return apply_theme(px.pie(df, names=names, values=values, title=title, **kwargs))


def scatter_chart(df, x, y, color=None, size=None, title="", **kwargs) -> go.Figure:
    return apply_theme(px.scatter(df, x=x, y=y, color=color, size=size, title=title, **kwargs))


def choropleth_us(df, locations, color, title="", **kwargs) -> go.Figure:
    fig = px.choropleth(
        df,
        locations=locations,
        locationmode="USA-states",
        color=color,
        scope="usa",
        title=title,
        **kwargs,
    )
    return apply_theme(fig)
