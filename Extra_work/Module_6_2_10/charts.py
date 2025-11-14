import pandas as pd
import plotly.express as px

def show_histogram(df, column):
    if column not in df.columns:
        return None
    d = df[[column]].dropna()
    if d.empty:
        return None

    d = d.assign(**{column: d[column].astype(str)})
    return px.histogram(
        d,
        x=column,
        category_orders={column: sorted(d[column].unique(), key=lambda x: float(x))},
        title=f"Histogram of {column}"
    )

def show_stacked_bar_chart(df, x_col, color_col):
    if x_col not in df.columns or color_col not in df.columns:
        return None
    d = df[[x_col, color_col]].dropna()
    if d.empty:
        return None
    counts = d.groupby([x_col, color_col]).size().reset_index(name="count")
    return px.bar(counts, x=x_col, y="count", color=color_col, barmode="stack",
                  title=f"Stacked Bar: {x_col} vs {color_col}")

def pie_chart(df, category_col):
    if category_col not in df.columns:
        return None
    counts = df[category_col].value_counts().reset_index()
    counts.columns = [category_col, "count"]
    return px.pie(counts, names=category_col, values="count", title=f"Distribution of {category_col}", hole=0.3)

def bar_chart_grouped_mean(df, category_col, value_col):
    if category_col not in df.columns or value_col not in df.columns:
        return None
    d = df[[category_col, value_col]].dropna()
    if d.empty:
        return None
    agg = d.groupby(category_col)[value_col].mean().reset_index()
    return px.bar(agg, x=category_col, y=value_col, title=f"Average {value_col} by {category_col}")

def box_plot(df, category_col, value_col):
    if category_col not in df.columns or value_col not in df.columns:
        return None
    d = df[[category_col, value_col]].dropna()
    if d.empty:
        return None
    return px.box(d, x=category_col, y=value_col, points="outliers",
                  title=f"Box Plot: {value_col} by {category_col}")
