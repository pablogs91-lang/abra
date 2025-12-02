"""
Widget Components
Componentes reutilizables para dashboard widgets
"""
import html
from typing import List, Dict, Optional
from abra.components.cards.base import Card
from abra.components.layouts.grids import Grid, FlexLayout

class MiniWidget:
    """
    Base mini widget para dashboard
    
    Uso:
        widget = MiniWidget(title="Noticias", icon="📰")
        widget.add_item("Título 1", "Descripción 1")
        html = widget.render()
    """
    
    def __init__(
        self,
        title: str,
        icon: str = "",
        max_items: int = 3,
        show_more_link: bool = True,
        more_text: str = "Ver más →"
    ):
        self.title = title
        self.icon = icon
        self.max_items = max_items
        self.show_more_link = show_more_link
        self.more_text = more_text
        self.items = []
    
    def add_item(
        self,
        title: str,
        subtitle: str = "",
        thumbnail: str = "",
        link: str = "#",
        badge: str = "",
        badge_color: str = "#007AFF"
    ):
        """Añade item al widget"""
        self.items.append({
            'title': title,
            'subtitle': subtitle,
            'thumbnail': thumbnail,
            'link': link,
            'badge': badge,
            'badge_color': badge_color
        })
    
    def render(self) -> str:
        """Renderiza el widget"""
        if not self.items:
            return ""
        
        icon_html = f"<span style='margin-right: 0.5rem;'>{self.icon}</span>" if self.icon else ""
        
        items_html = ""
        for item in self.items[:self.max_items]:
            safe_title = html.escape(item['title'][:100] + '...' if len(item['title']) > 100 else item['title'])
            safe_subtitle = html.escape(item['subtitle']) if item['subtitle'] else ""
            
            # Thumbnail
            thumbnail_html = ""
            if item['thumbnail']:
                thumbnail_html = f"""
                <img src="{item['thumbnail']}" 
                     style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover; flex-shrink: 0;"
                     onerror="this.style.display='none'">
                """
            
            # Badge
            badge_html = ""
            if item['badge']:
                badge_html = f"""
                <span style="
                    background: {item['badge_color']}20;
                    color: {item['badge_color']};
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.7rem;
                    font-weight: 600;
                    white-space: nowrap;
                ">{html.escape(item['badge'])}</span>
                """
            
            items_html += f"""
            <a href="{item['link']}" target="_blank" style="
                display: flex;
                gap: 0.75rem;
                align-items: center;
                padding: 0.75rem;
                margin-bottom: 0.5rem;
                border-radius: 8px;
                text-decoration: none;
                transition: background 0.2s ease;
            " onmouseover="this.style.background='#f5f5f7'" 
               onmouseout="this.style.background='transparent'">
                {thumbnail_html}
                <div style="flex: 1; min-width: 0;">
                    <div style="
                        color: #1d1d1f;
                        font-weight: 500;
                        font-size: 0.9rem;
                        line-height: 1.3;
                        margin-bottom: 0.25rem;
                    ">
                        {safe_title}
                    </div>
                    {f'<div style="font-size: 0.8rem; color: #86868b;">{safe_subtitle}</div>' if safe_subtitle else ''}
                </div>
                {badge_html}
            </a>
            """
        
        # More link
        more_link_html = ""
        if self.show_more_link:
            more_link_html = f"""
            <div style="
                text-align: center;
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(0,0,0,0.08);
            ">
                <span style="
                    color: #007AFF;
                    font-size: 0.9rem;
                    font-weight: 500;
                    cursor: pointer;
                ">
                    {html.escape(self.more_text)}
                </span>
            </div>
            """
        
        return f"""
        <div style="
            background: white;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        ">
            <h4 style="margin: 0 0 1rem 0; color: #1d1d1f; display: flex; align-items: center;">
                {icon_html}{html.escape(self.title)}
            </h4>
            {items_html}
            {more_link_html}
        </div>
        """


class StatWidget:
    """
    Stat widget con métrica principal
    
    Uso:
        widget = StatWidget(label="Total", value="150", icon="📊")
        html = widget.render()
    """
    
    def __init__(
        self,
        label: str,
        value: str,
        icon: str = "",
        change: Optional[str] = None,
        change_positive: bool = True,
        subtitle: str = ""
    ):
        self.label = label
        self.value = value
        self.icon = icon
        self.change = change
        self.change_positive = change_positive
        self.subtitle = subtitle
    
    def render(self) -> str:
        """Renderiza stat widget"""
        change_html = ""
        if self.change:
            change_color = "#34C759" if self.change_positive else "#FF3B30"
            change_icon = "↑" if self.change_positive else "↓"
            
            change_html = f"""
            <div style="
                font-size: 0.85rem;
                color: {change_color};
                font-weight: 600;
                margin-top: 0.25rem;
            ">
                {change_icon} {html.escape(self.change)}
            </div>
            """
        
        subtitle_html = ""
        if self.subtitle:
            subtitle_html = f"""
            <div style="
                font-size: 0.75rem;
                color: #6e6e73;
                margin-top: 0.5rem;
            ">
                {html.escape(self.subtitle)}
            </div>
            """
        
        return f"""
        <div style="
            background: white;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='scale(1.05)'" 
           onmouseout="this.style.transform='scale(1)'">
            {f'<div style="font-size: 2rem; margin-bottom: 0.5rem;">{self.icon}</div>' if self.icon else ''}
            <div style="
                font-size: 0.85rem;
                color: #6e6e73;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
                font-weight: 600;
            ">
                {html.escape(self.label)}
            </div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                color: #1d1d1f;
            ">
                {html.escape(str(self.value))}
            </div>
            {change_html}
            {subtitle_html}
        </div>
        """


class DashboardRow:
    """
    Fila de dashboard con widgets
    
    Uso:
        row = DashboardRow(columns=4)
        row.add_widget(StatWidget("Total", "150").render())
        html = row.render()
    """
    
    def __init__(
        self,
        columns: int = 4,
        gap: str = "1rem"
    ):
        self.grid = Grid(columns=columns, gap=gap, responsive=True, min_column_width="180px")
    
    def add_widget(self, widget_html: str):
        """Añade widget a la fila"""
        self.grid.add_item(widget_html)
    
    def render(self) -> str:
        """Renderiza la fila"""
        return self.grid.render()


class BadgeComponent:
    """
    Badge component reutilizable
    
    Uso:
        badge = BadgeComponent("New", color="#34C759")
        html = badge.render()
    """
    
    def __init__(
        self,
        text: str,
        color: str = "#007AFF",
        size: str = "normal"
    ):
        self.text = text
        self.color = color
        self.size = size
    
    def render(self) -> str:
        """Renderiza badge"""
        sizes = {
            'small': {'padding': '0.2rem 0.5rem', 'font-size': '0.7rem'},
            'normal': {'padding': '0.25rem 0.75rem', 'font-size': '0.75rem'},
            'large': {'padding': '0.5rem 1rem', 'font-size': '0.85rem'}
        }
        
        size_config = sizes.get(self.size, sizes['normal'])
        
        return f"""
        <span style="
            background: {self.color}20;
            color: {self.color};
            padding: {size_config['padding']};
            border-radius: 12px;
            font-size: {size_config['font-size']};
            font-weight: 600;
            display: inline-block;
        ">
            {html.escape(self.text)}
        </span>
        """


class ButtonComponent:
    """
    Button component reutilizable
    
    Uso:
        button = ButtonComponent("Download", icon="📥")
        html = button.render()
    """
    
    def __init__(
        self,
        text: str,
        icon: str = "",
        color: str = "#007AFF",
        style: str = "filled",
        onclick: str = ""
    ):
        self.text = text
        self.icon = icon
        self.color = color
        self.style = style  # filled | outlined | ghost
        self.onclick = onclick
    
    def render(self) -> str:
        """Renderiza button"""
        icon_html = f"{self.icon} " if self.icon else ""
        
        if self.style == "filled":
            bg = self.color
            text_color = "white"
            border = "none"
        elif self.style == "outlined":
            bg = "transparent"
            text_color = self.color
            border = f"2px solid {self.color}"
        else:  # ghost
            bg = f"{self.color}20"
            text_color = self.color
            border = "none"
        
        onclick_attr = f'onclick="{self.onclick}"' if self.onclick else ""
        
        return f"""
        <button {onclick_attr} style="
            background: {bg};
            color: {text_color};
            border: {border};
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
            {icon_html}{html.escape(self.text)}
        </button>
        """
