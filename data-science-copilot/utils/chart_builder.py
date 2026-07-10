"""
Step 6b: Chart building.

The agent's `analyze(df)` function returns "chart_type" and
"chart_data" (a pandas Series or small DataFrame). This converts
that into an actual interactive Plotly figure for the UI.
"""

import pandas as pd
import plotly.express as px


def build_chart(chart_type: str, chart_data):
    """
    Returns a Plotly figure, or None if there's nothing sensible to plot.

    Handles two shapes of chart_data, matching what the agent's
    generated code typically produces:
    - pd.Series: index is the category, values are the numbers
    - pd.DataFrame: first column is the category, second is the value
    """
    if chart_data is None or chart_type == "none":
        return None

    if isinstance(chart_data, pd.Series):
        plot_df = chart_data.reset_index()
        plot_df.columns = ["category", "value"]

    elif isinstance(chart_data, pd.DataFrame):
        if chart_data.shape[1] < 2:
            return None
        plot_df = chart_data.iloc[:, :2].copy()
        plot_df.columns = ["category", "value"]

    else:
        # Not a shape we know how to plot (e.g. a plain number or string)
        return None

    if chart_type == "line":
        fig = px.line(plot_df, x="category", y="value", markers=True)
    else:
        # default to bar for "bar" and any unrecognized type
        fig = px.bar(plot_df, x="category", y="value")

    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=380,
    )

    return fig