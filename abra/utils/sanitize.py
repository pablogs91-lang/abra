"""
Utilidades de sanitización HTML para prevenir XSS
"""
import html
import re

def sanitize_html(text):
    """
    Sanitiza texto para uso seguro en HTML
    
    Args:
        text: Texto a sanitizar
        
    Returns:
        str: Texto escapado y seguro
    """
    if text is None:
        return ""
    
    # Convertir a string
    text = str(text)
    
    # Escapar HTML
    text = html.escape(text)
    
    return text

def sanitize_query(query):
    """
    Sanitiza una query de búsqueda específicamente
    
    Args:
        query: Query a sanitizar
        
    Returns:
        str: Query sanitizada
    """
    if not query:
        return ""
    
    query = str(query)
    
    # Remover caracteres peligrosos
    query = re.sub(r'[<>"\']', '', query)
    
    # Escapar HTML
    query = html.escape(query)
    
    # Limitar longitud
    if len(query) > 200:
        query = query[:200]
    
    return query

def sanitize_url(url):
    """
    Sanitiza una URL
    
    Args:
        url: URL a sanitizar
        
    Returns:
        str: URL sanitizada
    """
    if not url:
        return ""
    
    url = str(url)
    
    # Solo permitir http/https
    if not url.startswith(('http://', 'https://')):
        return ""
    
    # Escapar HTML
    url = html.escape(url)
    
    return url

def build_safe_html(template, **kwargs):
    """
    Construye HTML seguro desde template con variables sanitizadas
    
    Args:
        template: Template HTML con {placeholders}
        **kwargs: Variables a insertar (serán sanitizadas automáticamente)
        
    Returns:
        str: HTML seguro
        
    Example:
        html = build_safe_html(
            '<div class="query">{query}</div>',
            query=user_input  # Se sanitiza automáticamente
        )
    """
    # Sanitizar todas las variables
    safe_vars = {
        key: sanitize_html(value) 
        for key, value in kwargs.items()
    }
    
    # Formatear template
    return template.format(**safe_vars)

# Alias comunes
escape = sanitize_html
safe = sanitize_html
