"""
Grid Layout Component
Sistema de grids responsive y flexible
"""
from typing import List, Optional

class Grid:
    """
    Grid layout modular
    
    Uso:
        grid = Grid(columns=3, gap="1rem")
        grid.add_item("<div>Item 1</div>")
        grid.add_item("<div>Item 2</div>")
        html = grid.render()
    """
    
    def __init__(
        self,
        columns: int = 3,
        gap: str = "1rem",
        min_column_width: str = "250px",
        responsive: bool = True
    ):
        """
        Inicializa grid
        
        Args:
            columns: Número de columnas (si no responsive)
            gap: Espacio entre items
            min_column_width: Ancho mínimo por columna (responsive)
            responsive: Si usar auto-fit responsive
        """
        self.columns = columns
        self.gap = gap
        self.min_column_width = min_column_width
        self.responsive = responsive
        self.items = []
    
    def add_item(self, content: str):
        """Añade item al grid"""
        self.items.append(content)
    
    def render(self) -> str:
        """
        Renderiza el grid
        
        Returns:
            HTML string
        """
        if self.responsive:
            grid_template = f"repeat(auto-fill, minmax({self.min_column_width}, 1fr))"
        else:
            grid_template = f"repeat({self.columns}, 1fr)"
        
        items_html = "".join(self.items)
        
        return f"""
        <div style="
            display: grid;
            grid-template-columns: {grid_template};
            gap: {self.gap};
        ">
            {items_html}
        </div>
        """


class FlexLayout:
    """
    Flex layout modular
    
    Uso:
        flex = FlexLayout(direction="row", justify="space-between")
        flex.add_item("<div>Left</div>")
        flex.add_item("<div>Right</div>")
        html = flex.render()
    """
    
    def __init__(
        self,
        direction: str = "row",
        justify: str = "flex-start",
        align: str = "flex-start",
        gap: str = "1rem",
        wrap: bool = False
    ):
        """
        Inicializa flex layout
        
        Args:
            direction: row | column
            justify: flex-start | center | space-between | space-around
            align: flex-start | center | flex-end | stretch
            gap: Espacio entre items
            wrap: Si permitir wrap
        """
        self.direction = direction
        self.justify = justify
        self.align = align
        self.gap = gap
        self.wrap = wrap
        self.items = []
    
    def add_item(self, content: str, flex: Optional[str] = None):
        """
        Añade item al flex
        
        Args:
            content: HTML content
            flex: Propiedad flex CSS (ej: "1" para ocupar espacio)
        """
        if flex:
            wrapped_content = f'<div style="flex: {flex};">{content}</div>'
        else:
            wrapped_content = content
        
        self.items.append(wrapped_content)
    
    def render(self) -> str:
        """Renderiza el flex layout"""
        items_html = "".join(self.items)
        wrap_css = "wrap" if self.wrap else "nowrap"
        
        return f"""
        <div style="
            display: flex;
            flex-direction: {self.direction};
            justify-content: {self.justify};
            align-items: {self.align};
            gap: {self.gap};
            flex-wrap: {wrap_css};
        ">
            {items_html}
        </div>
        """


class Accordion:
    """
    Accordion component
    
    Uso:
        accordion = Accordion()
        accordion.add_item("Título 1", "<p>Contenido 1</p>")
        accordion.add_item("Título 2", "<p>Contenido 2</p>")
        html = accordion.render()
    """
    
    def __init__(self, allow_multiple: bool = False):
        """
        Inicializa accordion
        
        Args:
            allow_multiple: Si permitir múltiples items abiertos
        """
        self.allow_multiple = allow_multiple
        self.items = []
    
    def add_item(
        self,
        title: str,
        content: str,
        expanded: bool = False,
        badge: Optional[str] = None,
        badge_color: str = "#007AFF"
    ):
        """
        Añade item al accordion
        
        Args:
            title: Título del item
            content: Contenido (HTML)
            expanded: Si empieza expandido
            badge: Badge opcional
            badge_color: Color del badge
        """
        self.items.append({
            'title': title,
            'content': content,
            'expanded': expanded,
            'badge': badge,
            'badge_color': badge_color
        })
    
    def render(self) -> str:
        """Renderiza el accordion"""
        import html as html_lib
        
        items_html = ""
        for i, item in enumerate(self.items):
            safe_title = html_lib.escape(item['title'])
            
            badge_html = ""
            if item['badge']:
                badge_html = f"""
                <span style="
                    background: {item['badge_color']}20;
                    color: {item['badge_color']};
                    padding: 0.25rem 0.75rem;
                    border-radius: 12px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    margin-left: auto;
                ">{html_lib.escape(item['badge'])}</span>
                """
            
            open_attr = "open" if item['expanded'] else ""
            
            items_html += f"""
            <details {open_attr} style="
                background: white;
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.75rem;
                cursor: pointer;
            ">
                <summary style="
                    font-weight: 600;
                    color: #1d1d1f;
                    font-size: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                ">
                    <span style="flex: 1;">{safe_title}</span>
                    {badge_html}
                </summary>
                <div style="
                    margin-top: 1rem;
                    padding-top: 1rem;
                    border-top: 1px solid rgba(0,0,0,0.05);
                ">
                    {item['content']}
                </div>
            </details>
            """
        
        return f'<div>{items_html}</div>'


class Tabs:
    """
    Tabs component (simple HTML/CSS)
    
    Uso:
        tabs = Tabs()
        tabs.add_tab("Tab 1", "📊", "<p>Content 1</p>")
        tabs.add_tab("Tab 2", "📈", "<p>Content 2</p>")
        html = tabs.render()
    
    Note: Para tabs reales de Streamlit usar st.tabs()
    """
    
    def __init__(self):
        self.tabs_list = []
    
    def add_tab(self, title: str, icon: str, content: str):
        """Añade tab"""
        self.tabs_list.append({
            'title': title,
            'icon': icon,
            'content': content
        })
    
    def render(self) -> str:
        """Renderiza tabs (visual simple, no interactivo)"""
        import html as html_lib
        
        tabs_nav = []
        for i, tab in enumerate(self.tabs_list):
            safe_title = html_lib.escape(tab['title'])
            active_style = "border-bottom: 3px solid #007AFF; color: #007AFF;" if i == 0 else "color: #6e6e73;"
            
            tabs_nav.append(f"""
            <div style="
                padding: 1rem 1.5rem;
                cursor: pointer;
                font-weight: 600;
                {active_style}
            ">
                {tab['icon']} {safe_title}
            </div>
            """)
        
        # Por simplicidad, mostrar solo primer tab activo
        active_content = self.tabs_list[0]['content'] if self.tabs_list else ""
        
        return f"""
        <div style="border-bottom: 1px solid rgba(0,0,0,0.08); display: flex; gap: 0;">
            {"".join(tabs_nav)}
        </div>
        <div style="padding: 1.5rem 0;">
            {active_content}
        </div>
        """
