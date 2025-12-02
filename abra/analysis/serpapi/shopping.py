"""
Shopping Results - SerpAPI
Productos en venta con precios, ratings y reviews
"""
from typing import List, Dict, Optional
import html
import re

def extract_shopping_results(serpapi_data: Dict) -> List[Dict]:
    """
    Extrae productos del shopping results
    
    Args:
        serpapi_data: Respuesta de SerpAPI (google_shopping)
    
    Returns:
        Lista de productos con precios, ratings, etc
    """
    products = []
    
    if not serpapi_data:
        return []
    
    # Shopping results
    if 'shopping_results' in serpapi_data:
        for item in serpapi_data['shopping_results']:
            product = {
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'product_link': item.get('product_link', ''),
                'product_id': item.get('product_id', ''),
                'serpapi_product_link': item.get('serpapi_product_api', ''),
                'source': item.get('source', 'Unknown'),
                'price': item.get('price', ''),
                'extracted_price': item.get('extracted_price', 0),
                'rating': item.get('rating', 0),
                'reviews': item.get('reviews', 0),
                'extensions': item.get('extensions', []),
                'thumbnail': item.get('thumbnail', ''),
                'delivery': item.get('delivery', ''),
                'tag': item.get('tag', ''),
                'position': item.get('position', 0)
            }
            
            products.append(product)
    
    # Inline shopping results (en organic)
    if 'inline_shopping_results' in serpapi_data:
        for item in serpapi_data['inline_shopping_results']:
            product = {
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'source': item.get('source', 'Unknown'),
                'price': item.get('price', ''),
                'extracted_price': item.get('extracted_price', 0),
                'rating': item.get('rating', 0),
                'reviews': item.get('reviews', 0),
                'thumbnail': item.get('thumbnail', ''),
                'position': item.get('position', 0)
            }
            
            products.append(product)
    
    return products


def analyze_shopping_results(products: List[Dict]) -> Dict:
    """
    Analiza productos para obtener métricas
    
    Args:
        products: Lista de productos
    
    Returns:
        Dict con análisis
    """
    if not products:
        return {}
    
    prices = [p['extracted_price'] for p in products if p.get('extracted_price', 0) > 0]
    ratings = [p['rating'] for p in products if p.get('rating', 0) > 0]
    reviews = [p['reviews'] for p in products if p.get('reviews', 0) > 0]
    
    analysis = {
        'total_products': len(products),
        'avg_price': sum(prices) / len(prices) if prices else 0,
        'min_price': min(prices) if prices else 0,
        'max_price': max(prices) if prices else 0,
        'avg_rating': sum(ratings) / len(ratings) if ratings else 0,
        'total_reviews': sum(reviews),
        'top_rated': sorted(
            [p for p in products if p.get('rating', 0) > 0],
            key=lambda x: (x['rating'], x.get('reviews', 0)),
            reverse=True
        )[:5],
        'best_value': sorted(
            [p for p in products if p.get('extracted_price', 0) > 0 and p.get('rating', 0) > 0],
            key=lambda x: x['rating'] / (x['extracted_price'] / 100 + 1),  # Rating per $100
            reverse=True
        )[:5]
    }
    
    return analysis


def render_shopping_results(products: List[Dict], analysis: Optional[Dict] = None) -> str:
    """
    Renderiza productos con precios y ratings
    
    Args:
        products: Lista de productos
        analysis: Análisis opcional
    
    Returns:
        HTML string
    """
    if not products:
        return """
        <div style="text-align: center; padding: 2rem; color: #6e6e73;">
            <p>🛒 No se encontraron productos en venta</p>
            <small>Intenta con un producto más específico</small>
        </div>
        """
    
    html_content = ""
    
    # Métricas resumen
    if analysis:
        html_content += """
        <div style="
            background: linear-gradient(135deg, #FF9500 20 0%, #FF950010 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        ">
            <h4 style="margin: 0 0 1rem 0; color: #1d1d1f;">📊 Análisis de Mercado</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
        """
        
        metrics = [
            ('🛒', 'Productos', analysis['total_products'], ''),
            ('💰', 'Precio Promedio', f"${analysis['avg_price']:.2f}", ''),
            ('💵', 'Rango', f"${analysis['min_price']:.0f} - ${analysis['max_price']:.0f}", ''),
            ('⭐', 'Rating Promedio', f"{analysis['avg_rating']:.1f}", '/5.0'),
            ('💬', 'Total Reviews', f"{analysis['total_reviews']:,}", '')
        ]
        
        for icon, label, value, suffix in metrics:
            html_content += f"""
            <div style="
                background: white;
                border-radius: 8px;
                padding: 1rem;
                text-align: center;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">{icon}</div>
                <div style="font-size: 0.75rem; color: #6e6e73; margin-bottom: 0.25rem;">{label}</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #1d1d1f;">
                    {value}<span style="font-size: 0.8rem; color: #6e6e73;">{suffix}</span>
                </div>
            </div>
            """
        
        html_content += """
            </div>
        </div>
        """
    
    # Grid de productos
    html_content += """
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;">
    """
    
    for product in products[:20]:  # Top 20
        safe_title = html.escape(product['title'][:80] + '...' if len(product['title']) > 80 else product['title'])
        safe_source = html.escape(product['source'])
        
        # Precio
        price_html = ""
        if product.get('price'):
            price_html = f"""
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: #1d1d1f;
                margin: 0.75rem 0;
            ">{html.escape(product['price'])}</div>
            """
        
        # Rating
        rating_html = ""
        if product.get('rating', 0) > 0:
            rating = product['rating']
            reviews = product.get('reviews', 0)
            stars = '⭐' * int(rating) + '☆' * (5 - int(rating))
            
            rating_html = f"""
            <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.5rem 0;">
                <div style="color: #FF9500; font-size: 0.9rem;">{stars}</div>
                <div style="font-size: 0.85rem; color: #6e6e73;">
                    {rating:.1f} ({reviews:,} reviews)
                </div>
            </div>
            """
        
        # Thumbnail
        thumbnail_html = ""
        if product.get('thumbnail'):
            thumbnail_html = f"""
            <div style="
                width: 100%;
                height: 180px;
                border-radius: 8px;
                overflow: hidden;
                background: #f5f5f7;
                margin-bottom: 1rem;
            ">
                <img src="{product['thumbnail']}" 
                     style="width: 100%; height: 100%; object-fit: contain; padding: 1rem;"
                     onerror="this.style.display='none'">
            </div>
            """
        
        # Extensions (free shipping, etc)
        extensions_html = ""
        if product.get('extensions'):
            extensions_html = '<div style="margin: 0.5rem 0; display: flex; flex-wrap: wrap; gap: 0.25rem;">'
            for ext in product['extensions'][:3]:
                extensions_html += f"""
                <span style="
                    background: #34C75920;
                    color: #34C759;
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.7rem;
                    font-weight: 600;
                ">{html.escape(ext)}</span>
                """
            extensions_html += '</div>'
        
        # Delivery
        delivery_html = ""
        if product.get('delivery'):
            delivery_html = f"""
            <div style="
                font-size: 0.8rem;
                color: #6e6e73;
                margin-top: 0.5rem;
            ">🚚 {html.escape(product['delivery'])}</div>
            """
        
        html_content += f"""
        <a href="{product.get('link', '#')}" target="_blank" style="
            text-decoration: none;
            display: block;
        ">
            <div style="
                background: white;
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
                height: 100%;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                
                {thumbnail_html}
                
                <div style="
                    font-weight: 600;
                    color: #1d1d1f;
                    font-size: 0.95rem;
                    line-height: 1.3;
                    margin-bottom: 0.5rem;
                    min-height: 40px;
                ">{safe_title}</div>
                
                {rating_html}
                
                {price_html}
                
                {extensions_html}
                
                <div style="
                    font-size: 0.85rem;
                    color: #6e6e73;
                    margin-top: 0.75rem;
                    padding-top: 0.75rem;
                    border-top: 1px solid rgba(0,0,0,0.05);
                ">🏪 {safe_source}</div>
                
                {delivery_html}
            </div>
        </a>
        """
    
    html_content += "</div>"
    
    return html_content


def render_shopping_mini_widget(products: List[Dict], max_items: int = 3) -> str:
    """
    Widget compacto de productos para dashboard
    
    Args:
        products: Lista de productos
        max_items: Máximo de productos
    
    Returns:
        HTML compacto
    """
    if not products:
        return ""
    
    # Top rated or best value
    top_products = sorted(
        [p for p in products if p.get('rating', 0) > 0],
        key=lambda x: (x['rating'], x.get('reviews', 0)),
        reverse=True
    )[:max_items]
    
    if not top_products:
        top_products = products[:max_items]
    
    html_content = """
    <div style="
        background: white;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0 0 1rem 0; color: #1d1d1f;">🛒 Productos Destacados</h4>
    """
    
    for product in top_products:
        safe_title = html.escape(product['title'][:60] + '...' if len(product['title']) > 60 else product['title'])
        
        rating_stars = ''
        if product.get('rating', 0) > 0:
            rating = product['rating']
            rating_stars = '⭐' * int(rating)
        
        html_content += f"""
        <a href="{product.get('link', '#')}" target="_blank" style="
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
            
            <img src="{product.get('thumbnail', '')}" 
                 style="width: 60px; height: 60px; border-radius: 8px; object-fit: contain; background: #f5f5f7; padding: 0.5rem;"
                 onerror="this.style.display='none'">
            
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
                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem;">
                    {f'<span style="color: #FF9500;">{rating_stars}</span>' if rating_stars else ''}
                    <span style="color: #1d1d1f; font-weight: 700;">{html.escape(product.get('price', ''))}</span>
                </div>
            </div>
        </a>
        """
    
    html_content += """
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
            ">
                Ver todos los productos →
            </span>
        </div>
    </div>
    """
    
    return html_content
