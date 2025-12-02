"""
Chart Components
Wrappers para Plotly charts con configuración consistente
"""
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional

class ChartConfig:
    """Configuración global de charts"""
    
    THEME = {
        'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial',
        'primary_color': '#007AFF',
        'success_color': '#34C759',
        'warning_color': '#FF9500',
        'danger_color': '#FF3B30',
        'neutral_color': '#6e6e73',
        'background': 'white',
        'grid_color': '#f5f5f7'
    }
    
    @staticmethod
    def get_base_layout(title: str = "") -> dict:
        """Retorna layout base para charts"""
        return {
            'title': {
                'text': title,
                'font': {
                    'family': ChartConfig.THEME['font_family'],
                    'size': 18,
                    'color': '#1d1d1f'
                },
                'x': 0.5,
                'xanchor': 'center'
            },
            'font': {
                'family': ChartConfig.THEME['font_family'],
                'size': 12,
                'color': '#6e6e73'
            },
            'plot_bgcolor': ChartConfig.THEME['background'],
            'paper_bgcolor': ChartConfig.THEME['background'],
            'margin': {'t': 60, 'l': 60, 'r': 40, 'b': 60},
            'hovermode': 'closest'
        }


class LineChart:
    """
    Line chart component
    
    Uso:
        chart = LineChart(title="Tendencia")
        chart.add_line(x=[1,2,3], y=[10,20,30], name="Serie 1")
        fig = chart.get_figure()
    """
    
    def __init__(
        self,
        title: str = "",
        height: int = 400
    ):
        self.title = title
        self.height = height
        self.traces = []
    
    def add_line(
        self,
        x: List,
        y: List,
        name: str = "",
        color: Optional[str] = None,
        mode: str = 'lines+markers'
    ):
        """Añade línea al chart"""
        if not color:
            color = ChartConfig.THEME['primary_color']
        
        trace = go.Scatter(
            x=x,
            y=y,
            name=name,
            mode=mode,
            line={'color': color, 'width': 2},
            marker={'size': 6}
        )
        self.traces.append(trace)
    
    def get_figure(self) -> go.Figure:
        """Retorna figura de Plotly"""
        layout = ChartConfig.get_base_layout(self.title)
        layout['height'] = self.height
        
        fig = go.Figure(data=self.traces, layout=layout)
        return fig


class BarChart:
    """
    Bar chart component
    
    Uso:
        chart = BarChart(title="Comparativa")
        chart.add_bar(x=["A","B","C"], y=[10,20,15], name="Métrica")
        fig = chart.get_figure()
    """
    
    def __init__(
        self,
        title: str = "",
        height: int = 400,
        orientation: str = 'v'
    ):
        self.title = title
        self.height = height
        self.orientation = orientation
        self.traces = []
    
    def add_bar(
        self,
        x: List,
        y: List,
        name: str = "",
        color: Optional[str] = None
    ):
        """Añade barras al chart"""
        if not color:
            color = ChartConfig.THEME['primary_color']
        
        trace = go.Bar(
            x=x if self.orientation == 'v' else y,
            y=y if self.orientation == 'v' else x,
            name=name,
            orientation=self.orientation,
            marker={'color': color}
        )
        self.traces.append(trace)
    
    def get_figure(self) -> go.Figure:
        """Retorna figura de Plotly"""
        layout = ChartConfig.get_base_layout(self.title)
        layout['height'] = self.height
        
        fig = go.Figure(data=self.traces, layout=layout)
        return fig


class BubbleChart:
    """
    Bubble chart component
    
    Uso:
        chart = BubbleChart(title="Topics")
        chart.add_bubble(x=[1,2], y=[10,20], size=[50,100], text=["A","B"])
        fig = chart.get_figure()
    """
    
    def __init__(
        self,
        title: str = "",
        height: int = 500
    ):
        self.title = title
        self.height = height
        self.data = []
    
    def add_bubble(
        self,
        x: List,
        y: List,
        size: List,
        text: List,
        color: Optional[List] = None
    ):
        """Añade bubbles al chart"""
        if color is None:
            color = [ChartConfig.THEME['primary_color']] * len(x)
        
        trace = go.Scatter(
            x=x,
            y=y,
            mode='markers+text',
            marker={
                'size': size,
                'color': color,
                'opacity': 0.6,
                'line': {'width': 2, 'color': 'white'}
            },
            text=text,
            textposition='middle center',
            textfont={'size': 10, 'color': 'white', 'family': ChartConfig.THEME['font_family']}
        )
        self.data.append(trace)
    
    def get_figure(self) -> go.Figure:
        """Retorna figura de Plotly"""
        layout = ChartConfig.get_base_layout(self.title)
        layout['height'] = self.height
        layout['showlegend'] = False
        
        fig = go.Figure(data=self.data, layout=layout)
        return fig


class SparklineChart:
    """
    Sparkline miniature chart
    
    Uso:
        sparkline = SparklineChart()
        html = sparkline.render([10, 15, 13, 18, 20])
    """
    
    def __init__(
        self,
        width: int = 80,
        height: int = 20,
        color: str = '#007AFF'
    ):
        self.width = width
        self.height = height
        self.color = color
    
    def render(self, values: List[float]) -> str:
        """
        Renderiza sparkline como HTML/CSS
        
        Args:
            values: Lista de valores
        
        Returns:
            HTML string
        """
        if not values:
            return ""
        
        max_val = max(values) if values else 1
        max_val = max(max_val, 1)  # Evitar división por 0
        
        # Crear puntos
        points = []
        for val in values:
            height_pct = (val / max_val) * 100 if max_val > 0 else 0
            points.append(f'<div style="height:{height_pct}%; background:{self.color}; width:3px; display:inline-block; margin:0 1px; vertical-align:bottom;"></div>')
        
        return f"""
        <div style="
            display: inline-flex;
            align-items: flex-end;
            height: {self.height}px;
            width: {self.width}px;
            gap: 1px;
        ">
            {"".join(points)}
        </div>
        """


class ProgressBar:
    """
    Progress bar component
    
    Uso:
        bar = ProgressBar(value=75, max_value=100)
        html = bar.render()
    """
    
    def __init__(
        self,
        value: float,
        max_value: float = 100,
        color: str = '#007AFF',
        height: str = '8px',
        show_label: bool = True
    ):
        self.value = value
        self.max_value = max_value
        self.color = color
        self.height = height
        self.show_label = show_label
    
    def render(self) -> str:
        """Renderiza progress bar"""
        import html
        
        percentage = (self.value / self.max_value * 100) if self.max_value > 0 else 0
        percentage = min(percentage, 100)
        
        label_html = ""
        if self.show_label:
            label_html = f"""
            <div style="
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.25rem;
                font-size: 0.85rem;
                color: #6e6e73;
            ">
                <span>{html.escape(str(self.value))}</span>
                <span>{percentage:.0f}%</span>
            </div>
            """
        
        return f"""
        <div style="margin: 0.5rem 0;">
            {label_html}
            <div style="
                background: #f5f5f7;
                border-radius: 999px;
                height: {self.height};
                overflow: hidden;
            ">
                <div style="
                    background: {self.color};
                    height: 100%;
                    width: {percentage}%;
                    transition: width 0.3s ease;
                    border-radius: 999px;
                "></div>
            </div>
        </div>
        """
