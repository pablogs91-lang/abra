"""
Base Card Component
Componente reutilizable para todas las cards
"""
import html
from typing import Optional, Dict, List

class Card:
    """
    Card component modular y reutilizable
    
    Uso:
        card = Card(title="Mi Card", border_color="#007AFF")
        card.add_content("<p>Contenido</p>")
        html = card.render()
    """
    
    def __init__(
        self,
        title: Optional[str] = None,
        icon: Optional[str] = None,
        border_color: str = "rgba(0,0,0,0.08)",
        background: str = "white",
        border_width: str = "1px",
        border_radius: str = "12px",
        padding: str = "1.5rem",
        margin: str = "0 0 1rem 0",
        hover_effect: bool = True
    ):
        """
        Inicializa card
        
        Args:
            title: Título opcional
            icon: Emoji/icon opcional
            border_color: Color del borde
            background: Color de fondo
            border_width: Ancho del borde
            border_radius: Radio de esquinas
            padding: Padding interno
            margin: Margin externo
            hover_effect: Si aplicar efecto hover
        """
        self.title = title
        self.icon = icon
        self.border_color = border_color
        self.background = background
        self.border_width = border_width
        self.border_radius = border_radius
        self.padding = padding
        self.margin = margin
        self.hover_effect = hover_effect
        self.content_parts = []
    
    def add_content(self, content: str):
        """Añade contenido a la card"""
        self.content_parts.append(content)
    
    def add_header(self, text: str, level: int = 4):
        """Añade header"""
        self.content_parts.append(f"<h{level} style='margin: 0 0 1rem 0; color: #1d1d1f;'>{html.escape(text)}</h{level}>")
    
    def add_paragraph(self, text: str, color: str = "#6e6e73"):
        """Añade párrafo"""
        self.content_parts.append(f"<p style='color: {color}; line-height: 1.6; margin: 0.5rem 0;'>{html.escape(text)}</p>")
    
    def add_metric(self, label: str, value: str, icon: str = ""):
        """Añade métrica"""
        metric_html = f"""
        <div style="margin: 0.5rem 0;">
            <div style="font-size: 0.85rem; color: #6e6e73; margin-bottom: 0.25rem;">
                {icon} {html.escape(label)}
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #1d1d1f;">
                {html.escape(str(value))}
            </div>
        </div>
        """
        self.content_parts.append(metric_html)
    
    def add_divider(self):
        """Añade línea divisoria"""
        self.content_parts.append("<hr style='border: none; border-top: 1px solid rgba(0,0,0,0.08); margin: 1rem 0;'>")
    
    def render(self) -> str:
        """
        Renderiza la card completa
        
        Returns:
            HTML string
        """
        hover_style = ""
        if self.hover_effect:
            hover_style = """
            onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
            """
        
        title_html = ""
        if self.title:
            icon_html = f"<span style='margin-right: 0.5rem;'>{self.icon}</span>" if self.icon else ""
            title_html = f"""
            <h4 style="margin: 0 0 1rem 0; color: #1d1d1f; display: flex; align-items: center;">
                {icon_html}{html.escape(self.title)}
            </h4>
            """
        
        content_html = "".join(self.content_parts)
        
        return f"""
        <div style="
            background: {self.background};
            border: {self.border_width} solid {self.border_color};
            border-radius: {self.border_radius};
            padding: {self.padding};
            margin: {self.margin};
            transition: all 0.3s ease;
        " {hover_style}>
            {title_html}
            {content_html}
        </div>
        """


class MetricCard(Card):
    """Card especializada en métricas"""
    
    def __init__(
        self,
        label: str,
        value: str,
        icon: str = "",
        change: Optional[str] = None,
        change_color: str = "#34C759",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.icon = icon
        self.change = change
        self.change_color = change_color
    
    def render(self) -> str:
        """Renderiza metric card"""
        change_html = ""
        if self.change:
            change_html = f"""
            <div style="
                font-size: 0.85rem;
                color: {self.change_color};
                font-weight: 600;
                margin-top: 0.25rem;
            ">
                {html.escape(self.change)}
            </div>
            """
        
        return f"""
        <div style="
            background: {self.background};
            border: {self.border_width} solid {self.border_color};
            border-radius: {self.border_radius};
            padding: {self.padding};
            margin: {self.margin};
            text-align: center;
            transition: all 0.3s ease;
        " {('onmouseover="this.style.transform=\'scale(1.05)\'" onmouseout="this.style.transform=\'scale(1)\'"' if self.hover_effect else '')}>
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{self.icon}</div>
            <div style="font-size: 0.85rem; color: #6e6e73; text-transform: uppercase; margin-bottom: 0.5rem;">
                {html.escape(self.label)}
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: #1d1d1f;">
                {html.escape(str(self.value))}
            </div>
            {change_html}
        </div>
        """


class AlertCard(Card):
    """Card especializada en alertas"""
    
    TYPES = {
        'info': {'color': '#007AFF', 'icon': 'ℹ️'},
        'success': {'color': '#34C759', 'icon': '✅'},
        'warning': {'color': '#FF9500', 'icon': '⚠️'},
        'error': {'color': '#FF3B30', 'icon': '❌'}
    }
    
    def __init__(
        self,
        message: str,
        alert_type: str = 'info',
        **kwargs
    ):
        alert_config = self.TYPES.get(alert_type, self.TYPES['info'])
        super().__init__(
            icon=alert_config['icon'],
            border_color=alert_config['color'],
            border_width='4px',
            **kwargs
        )
        self.message = message
        self.alert_type = alert_type
    
    def render(self) -> str:
        """Renderiza alert card"""
        alert_config = self.TYPES[self.alert_type]
        
        return f"""
        <div style="
            background: linear-gradient(135deg, {alert_config['color']}20 0%, {alert_config['color']}10 100%);
            border-left: 4px solid {alert_config['color']};
            border-radius: {self.border_radius};
            padding: {self.padding};
            margin: {self.margin};
        ">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.5rem;">{alert_config['icon']}</span>
                <div style="color: #1d1d1f; line-height: 1.6;">
                    {html.escape(self.message)}
                </div>
            </div>
        </div>
        """
