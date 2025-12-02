"""
Funciones de análisis e insights
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re
import json
import html
from urllib.parse import urlparse


def extract_brand_from_url(url):
    """
    Extract brand name from URL.
    
    Args:
        url: URL string to extract brand from
        
    Returns:
        Extracted brand name or empty string
    """
    try:
        # Parse URL
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        # Remove www. prefix
        domain = domain.replace('www.', '')
        
        # Get main domain name (before TLD)
        parts = domain.split('.')
        if len(parts) >= 2:
            brand = parts[0]
            # Capitalize first letter
            return brand.capitalize()
        
        return domain
    except Exception:
        return ""



def detect_products_in_titles(titles, brand):
    """
    Detecta productos específicos mencionados en títulos.
    SECURITY: Regex optimizado para prevenir ReDoS
    """
    import re
    from collections import defaultdict
    
    products = defaultdict(lambda: {'count': 0, 'recent': 0})
    
    brand_lower = brand.lower()
    # SECURITY: Escape special regex characters in brand
    brand_escaped = re.escape(brand_lower)
    
    for title in titles:
        title_lower = title.lower()
        
        if brand_lower not in title_lower:
            continue
        
        # SECURITY: More specific pattern to prevent ReDoS
        # Limitar a palabras razonables (max 30 chars)
        pattern1 = rf'{brand_escaped}\s+([\w\s]{{0,30}}(?:pro|master|keys|wireless|gaming)?[\w\s]{{0,20}}?)'
        try:
            matches = re.findall(pattern1, title_lower, re.IGNORECASE)
        except:
            continue  # Si regex falla, skip
        
        for match in matches:
            product_name = f"{brand_lower} {match.strip()}"
            product_name = ' '.join(product_name.split()[:4])
            
            if len(product_name) > len(brand_lower) + 2:
                products[product_name]['count'] += 1
    
    filtered = {k: v for k, v in products.items() if v['count'] >= 2}
    sorted_products = dict(sorted(filtered.items(), key=lambda x: x[1]['count'], reverse=True))
    
    return sorted_products


def calculate_changes(timeline_data):
    if not timeline_data or 'interest_over_time' not in timeline_data:
        return None, None, None, None
    
    try:
        values = timeline_data['interest_over_time']['timeline_data']
        if len(values) < 12:
            return None, None, None, None
        
        all_values = [p['values'][0].get('extracted_value', 0) 
                     for p in values if p.get('values')]
        
        if len(all_values) < 12:
            return None, None, None, None
        
        current = all_values[-1]
        month_ago = all_values[-5] if len(all_values) >= 5 else all_values[0]
        quarter_ago = all_values[-13] if len(all_values) >= 13 else all_values[0]
        year_ago = all_values[-52] if len(all_values) >= 52 else all_values[0]
        
        month_change = ((current - month_ago) / month_ago * 100) if month_ago > 0 else 0
        quarter_change = ((current - quarter_ago) / quarter_ago * 100) if quarter_ago > 0 else 0
        year_change = ((current - year_ago) / year_ago * 100) if year_ago > 0 else 0
        avg_value = sum(all_values) / len(all_values) if all_values else 0
        
        return month_change, quarter_change, year_change, avg_value
    except:
        return None, None, None, None


def calculate_relevance(query, categories):
    """Calcula relevancia de query vs categorías seleccionadas"""
    if not categories:
        return 100, [], "N/A"
    
    query_lower = query.lower()
    max_score = 0
    best_matches = []
    best_category = ""
    
    for category in categories:
        keywords = PRODUCT_CATEGORIES[category]["keywords"]
        matches = [kw for kw in keywords if kw.lower() in query_lower]
        
        if matches:
            score = (len(matches) / len(keywords)) * 100
            important_matches = [kw for kw in keywords[:5] if kw.lower() in query_lower]
            if important_matches:
                score += 20
            score = min(score, 100)
            
            if score > max_score:
                max_score = score
                best_matches = matches
                best_category = category
    
    return max_score, best_matches, best_category


def filter_queries_by_categories(queries_data, categories, threshold):
    """
    Filtra related queries basándose en las categorías seleccionadas.
    
    Args:
        queries_data (dict): Datos de queries de pytrends
        categories (list): Categorías seleccionadas
        threshold (int): Umbral de relevancia mínimo
        
    Returns:
        dict: Queries filtradas con información de categoría
    """
    if not queries_data or not categories:
        return queries_data
    
    filtered_data = {
        'related_queries': {
            'top': [],
            'rising': []
        }
    }
    
    # Filtrar queries TOP
    if 'related_queries' in queries_data and 'top' in queries_data['related_queries']:
        for query_item in queries_data['related_queries']['top']:
            query_text = query_item.get('query', '')
            if not query_text:
                continue
                
            relevance, matches, category = calculate_relevance(query_text, categories)
            
            if relevance >= threshold:
                # Añadir metadata de categoría
                query_item['category'] = category
                query_item['relevance'] = relevance
                query_item['matched_keywords'] = matches
                filtered_data['related_queries']['top'].append(query_item)
    
    # Filtrar queries RISING
    if 'related_queries' in queries_data and 'rising' in queries_data['related_queries']:
        for query_item in queries_data['related_queries']['rising']:
            query_text = query_item.get('query', '')
            if not query_text:
                continue
                
            relevance, matches, category = calculate_relevance(query_text, categories)
            
            if relevance >= threshold:
                # Añadir metadata de categoría
                query_item['category'] = category
                query_item['relevance'] = relevance
                query_item['matched_keywords'] = matches
                filtered_data['related_queries']['rising'].append(query_item)
    
    return filtered_data


def filter_topics_by_categories(topics_data, categories, threshold):
    """
    Filtra related topics basándose en las categorías seleccionadas.
    
    Args:
        topics_data (dict): Datos de topics de pytrends
        categories (list): Categorías seleccionadas
        threshold (int): Umbral de relevancia mínimo
        
    Returns:
        dict: Topics filtrados con información de categoría
    """
    if not topics_data or not categories:
        return topics_data
    
    filtered_data = {
        'related_topics': {
            'top': [],
            'rising': []
        }
    }
    
    # Filtrar topics TOP
    if 'related_topics' in topics_data and 'top' in topics_data['related_topics']:
        for topic_item in topics_data['related_topics']['top']:
            topic_title = topic_item.get('topic', {}).get('title', '')
            if not topic_title:
                continue
                
            relevance, matches, category = calculate_relevance(topic_title, categories)
            
            if relevance >= threshold:
                # Añadir metadata de categoría
                topic_item['category'] = category
                topic_item['relevance'] = relevance
                topic_item['matched_keywords'] = matches
                filtered_data['related_topics']['top'].append(topic_item)
    
    # Filtrar topics RISING
    if 'related_topics' in topics_data and 'rising' in topics_data['related_topics']:
        for topic_item in topics_data['related_topics']['rising']:
            topic_title = topic_item.get('topic', {}).get('title', '')
            if not topic_title:
                continue
                
            relevance, matches, category = calculate_relevance(topic_title, categories)
            
            if relevance >= threshold:
                # Añadir metadata de categoría
                topic_item['category'] = category
                topic_item['relevance'] = relevance
                topic_item['matched_keywords'] = matches
                filtered_data['related_topics']['rising'].append(topic_item)
    
    return filtered_data


def classify_query_type(query):
    """Clasifica si es pregunta o atributo"""
    question_words = ["qué", "cuál", "cómo", "dónde", "cuándo", "quién", "por qué",
                     "what", "how", "where", "when", "why", "which", "who"]
    
    query_lower = query.lower()
    is_question = any(word in query_lower for word in question_words)
    
    return "❓ Pregunta" if is_question else "🏷️ Atributo"


def calculate_seasonality(timeline_data):
    """
    Calcula la estacionalidad mensual desde datos de timeline.
    Retorna dict con valores mensuales y score de estacionalidad.
    """
    if not timeline_data or 'interest_over_time' not in timeline_data:
        return None
    
    try:
        values = timeline_data['interest_over_time']['timeline_data']
        
        # Agrupar por mes
        monthly_values = {}
        for item in values:
            if item.get('values'):
                date_str = item['date']
                # Formato: "Nov 24, 2024" -> extraer mes (3 letras capitalizadas)
                month = date_str.split()[0][:3].title()  # FIX: Normalizar a 3 chars
                value = item['values'][0].get('extracted_value', 0)
                
                if month not in monthly_values:
                    monthly_values[month] = []
                monthly_values[month].append(value)
        
        # Calcular promedio por mes
        monthly_avg = {}
        for month, vals in monthly_values.items():
            monthly_avg[month] = sum(vals) / len(vals) if vals else 0
        
        # Calcular promedio general
        overall_avg = sum(monthly_avg.values()) / len(monthly_avg) if monthly_avg else 0
        
        # Calcular desviación estándar para score de estacionalidad
        if overall_avg > 0:
            variance = sum((v - overall_avg) ** 2 for v in monthly_avg.values()) / len(monthly_avg)
            std_dev = variance ** 0.5
            seasonality_score = min((std_dev / overall_avg) * 100, 100)
        else:
            seasonality_score = 0
        
        return {
            'monthly_avg': monthly_avg,
            'overall_avg': overall_avg,
            'seasonality_score': seasonality_score
        }
    except:
        return None


def detect_seasonal_patterns(monthly_data, overall_avg):
    """
    Detecta patrones estacionales automáticamente.
    Retorna lista de patrones identificados.
    """
    if not monthly_data or overall_avg == 0:
        return []
    
    patterns = []
    
    # Definir umbrales
    HIGH_THRESHOLD = 1.4  # 40% por encima del promedio
    MODERATE_THRESHOLD = 1.2  # 20% por encima
    
    # PATRÓN 1: Black Friday / Navidad (Nov-Dec)
    nov_value = monthly_data.get('Nov', 0)
    dec_value = monthly_data.get('Dec', 0)
    
    if nov_value > overall_avg * HIGH_THRESHOLD or dec_value > overall_avg * HIGH_THRESHOLD:
        nov_increase = ((nov_value / overall_avg) - 1) * 100 if overall_avg > 0 else 0
        dec_increase = ((dec_value / overall_avg) - 1) * 100 if overall_avg > 0 else 0
        
        patterns.append({
            'name': 'Black Friday / Navidad',
            'emoji': '🎄',
            'months': ['Noviembre', 'Diciembre'],
            'peak_month': 'Diciembre' if dec_value > nov_value else 'Noviembre',
            'increase': max(nov_increase, dec_increase),
            'type': 'shopping',
            'explanation': 'Pico típico de compras navideñas y ofertas de fin de año'
        })
    
    # PATRÓN 2: Verano (Jun-Jul-Aug)
    jun_value = monthly_data.get('Jun', 0)
    jul_value = monthly_data.get('Jul', 0)
    aug_value = monthly_data.get('Aug', 0)
    summer_avg = (jun_value + jul_value + aug_value) / 3
    
    if summer_avg > overall_avg * MODERATE_THRESHOLD:
        summer_increase = ((summer_avg / overall_avg) - 1) * 100 if overall_avg > 0 else 0
        
        patterns.append({
            'name': 'Temporada de Verano',
            'emoji': '☀️',
            'months': ['Junio', 'Julio', 'Agosto'],
            'peak_month': max([('Jun', jun_value), ('Jul', jul_value), ('Aug', aug_value)], key=lambda x: x[1])[0],
            'increase': summer_increase,
            'type': 'seasonal',
            'explanation': 'Incremento típico durante los meses de verano'
        })
    
    # PATRÓN 3: Regreso a clases (Aug-Sep)
    sep_value = monthly_data.get('Sep', 0)
    
    if aug_value > overall_avg * MODERATE_THRESHOLD or sep_value > overall_avg * MODERATE_THRESHOLD:
        back_to_school_increase = max(
            ((aug_value / overall_avg) - 1) * 100 if overall_avg > 0 else 0,
            ((sep_value / overall_avg) - 1) * 100 if overall_avg > 0 else 0
        )
        
        patterns.append({
            'name': 'Regreso a Clases',
            'emoji': '📚',
            'months': ['Agosto', 'Septiembre'],
            'peak_month': 'Septiembre' if sep_value > aug_value else 'Agosto',
            'increase': back_to_school_increase,
            'type': 'education',
            'explanation': 'Pico relacionado con el inicio del curso escolar'
        })
    
    # PATRÓN 4: Enero (Nuevos propósitos / Rebajas)
    jan_value = monthly_data.get('Jan', 0)
    
    if jan_value > overall_avg * HIGH_THRESHOLD:
        jan_increase = ((jan_value / overall_avg) - 1) * 100 if overall_avg > 0 else 0
        
        patterns.append({
            'name': 'Enero - Propósitos de Año Nuevo',
            'emoji': '🎯',
            'months': ['Enero'],
            'peak_month': 'Enero',
            'increase': jan_increase,
            'type': 'new_year',
            'explanation': 'Incremento típico asociado a propósitos de año nuevo y rebajas'
        })
    
    # PATRÓN 5: San Valentín (Feb)
    feb_value = monthly_data.get('Feb', 0)
    
    if feb_value > overall_avg * MODERATE_THRESHOLD:
        feb_increase = ((feb_value / overall_avg) - 1) * 100 if overall_avg > 0 else 0
        
        patterns.append({
            'name': 'San Valentín',
            'emoji': '💝',
            'months': ['Febrero'],
            'peak_month': 'Febrero',
            'increase': feb_increase,
            'type': 'holiday',
            'explanation': 'Pico relacionado con San Valentín'
        })
    
    # PATRÓN 6: Primavera (Mar-Apr-May)
    mar_value = monthly_data.get('Mar', 0)
    apr_value = monthly_data.get('Apr', 0)
    may_value = monthly_data.get('May', 0)
    spring_avg = (mar_value + apr_value + may_value) / 3
    
    if spring_avg > overall_avg * MODERATE_THRESHOLD:
        spring_increase = ((spring_avg / overall_avg) - 1) * 100 if overall_avg > 0 else 0
        
        patterns.append({
            'name': 'Primavera',
            'emoji': '🌸',
            'months': ['Marzo', 'Abril', 'Mayo'],
            'peak_month': max([('Mar', mar_value), ('Apr', apr_value), ('May', may_value)], key=lambda x: x[1])[0],
            'increase': spring_increase,
            'type': 'seasonal',
            'explanation': 'Incremento durante la temporada primaveral'
        })
    
    # Ordenar por aumento (mayor primero)
    patterns.sort(key=lambda x: x['increase'], reverse=True)
    
    return patterns


def generate_seasonality_explanation(patterns, monthly_data, overall_avg):
    """
    Genera explicación en lenguaje natural basada en patrones detectados.
    """
    if not patterns:
        return """
        <div style="margin-top: 1rem; padding: 1rem; background: #f5f5f7; border-radius: 12px;">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">📊 Análisis:</div>
            <div style="color: #6e6e73; line-height: 1.6;">
                No se detectaron patrones estacionales significativos. Las búsquedas se mantienen 
                relativamente constantes a lo largo del año.
            </div>
        </div>
        """
    
    # Generar análisis
    analysis = '<div style="margin-top: 1rem; padding: 1rem; background: #f5f5f7; border-radius: 12px;">'
    analysis += '<div style="font-weight: 600; margin-bottom: 0.5rem; color: #1d1d1f;">📊 Análisis de Patrones:</div>'
    analysis += '<div style="color: #1d1d1f; line-height: 1.8;">'
    
    if len(patterns) == 1:
        p = patterns[0]
        analysis += f"""
        Las búsquedas muestran un patrón estacional claro: <b>{p['emoji']} {p['name']}</b>. 
        Durante {', '.join(p['months'])}, se observa un incremento de aproximadamente 
        <span style="color: #34C759; font-weight: 600;">+{p['increase']:.0f}%</span> 
        respecto al promedio anual. {p['explanation']}.
        """
    else:
        analysis += f"Las búsquedas muestran <b>{len(patterns)} patrones estacionales</b> distintos:<br><br>"
        
        for i, p in enumerate(patterns[:3], 1):  # Mostrar top 3
            analysis += f"""
            <div style="margin-bottom: 0.75rem;">
                {i}. {p['emoji']} <b>{p['name']}</b> ({', '.join(p['months'])}): 
                <span style="color: #34C759; font-weight: 600;">+{p['increase']:.0f}%</span>
                <br>
                <span style="font-size: 0.9rem; color: #6e6e73; margin-left: 1.5rem;">
                    → {p['explanation']}
                </span>
            </div>
            """
    
    analysis += '</div></div>'
    
    # Generar recomendación
    recommendation = generate_seasonality_recommendation(patterns, monthly_data, overall_avg)
    
    return analysis + recommendation


def generate_seasonality_recommendation(patterns, monthly_data, overall_avg):
    """
    Genera recomendaciones basadas en patrones detectados.
    """
    if not patterns:
        return ""
    
    rec = '<div style="margin-top: 1rem; padding: 1rem; background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); border-radius: 12px; border-left: 4px solid #007AFF;">'
    rec += '<div style="font-weight: 600; margin-bottom: 0.5rem; color: #1d1d1f;">💡 Recomendaciones:</div>'
    rec += '<div style="color: #1d1d1f; line-height: 1.8;">'
    
    top_pattern = patterns[0]
    
    # Recomendaciones específicas por tipo de patrón
    if top_pattern['type'] == 'shopping':
        rec += f"""
        <b>Estrategia de Marketing:</b><br>
        • Incrementar presupuesto de publicidad en <b>Octubre-Noviembre</b> (1-2 meses antes del pico)<br>
        • Preparar campañas específicas para Black Friday y Navidad<br>
        • Anticipar stock y logística para el periodo de mayor demanda<br>
        • Considerar promociones pre-navideñas para captar demanda temprana
        """
    elif top_pattern['type'] == 'seasonal':
        rec += f"""
        <b>Planificación Estacional:</b><br>
        • Ajustar inventario 1-2 meses antes de {top_pattern['peak_month']}<br>
        • Lanzar campañas temáticas alineadas con la temporada<br>
        • Aprovechar el interés natural del periodo para maximizar conversiones
        """
    elif top_pattern['type'] == 'education':
        rec += f"""
        <b>Estrategia Back-to-School:</b><br>
        • Iniciar campañas a mediados de <b>Julio</b><br>
        • Destacar productos relacionados con educación y organización<br>
        • Ofrecer packs o bundles especiales para el regreso a clases
        """
    elif top_pattern['type'] == 'new_year':
        rec += f"""
        <b>Estrategia Año Nuevo:</b><br>
        • Capitalizar los propósitos de año nuevo con mensajes motivacionales<br>
        • Aprovechar el tráfico de rebajas de Enero<br>
        • Mantener momentum post-navideño
        """
    else:
        rec += f"""
        <b>Optimización General:</b><br>
        • Aumentar presupuesto publicitario durante los meses pico identificados<br>
        • Reducir inversión en meses de baja demanda<br>
        • Planificar lanzamientos de productos alineados con picos estacionales
        """
    
    rec += '</div></div>'
    
    return rec


def analyze_brand(brand, countries, categories, threshold, channel="web"):
    """
    Análisis completo con todas las APIs
    SPRINT 5: Añadido parámetro channel para multi-canal
    """
    results = {}
    gprop = CHANNELS[channel]["gprop"]
    
    for geo in countries:
        channel_name = CHANNELS[channel]["name"]
        with st.spinner(f'🔎 Analizando {brand} en {COUNTRIES[geo]["name"]} ({channel_name})...'):
            timeline = get_interest_over_time(brand, geo, gprop)
            time.sleep(1)
            
            queries = get_related_queries(brand, geo, gprop)
            time.sleep(1)
            
            topics = get_related_topics(brand, geo, gprop)
            time.sleep(1)
            
            month_change, quarter_change, year_change, avg_value = calculate_changes(timeline)
            
            results[geo] = {
                'country': COUNTRIES[geo]['name'],
                'channel': channel_name,
                'timeline': timeline,
                'queries': queries,
                'topics': topics,
                'month_change': month_change,
                'quarter_change': quarter_change,
                'year_change': year_change,
                'avg_value': avg_value
            }
    
    return results


def analyze_all_channels(brand, countries, categories, threshold):
    """
    Analiza la marca en TODOS los canales simultáneamente.
    Consolida y estructura todos los datos de forma unificada.
    AHORA con filtrado por categorías.
    
    Args:
        brand (str): Marca a analizar
        countries (list): Países a analizar
        categories (list): Categorías seleccionadas para filtrar
        threshold (int): Umbral de relevancia (0-100)
    
    Returns:
        dict: Datos estructurados y consolidados de todos los canales
    """
    all_channels_data = {}
    
    # Canales a analizar
    channels_to_analyze = ['web', 'images', 'news', 'youtube', 'shopping']
    
    for geo in countries:
        country_name = COUNTRIES[geo]['name']
        with st.spinner(f'🌐 Analizando {brand} en {country_name} - Todos los canales...'):
            
            channel_results = {}
            
            # Iterar por cada canal
            for channel_key in channels_to_analyze:
                channel_name = CHANNELS[channel_key]["name"]
                gprop = CHANNELS[channel_key]["gprop"]
                
                try:
                    # Obtener datos de este canal
                    timeline = get_interest_over_time(brand, geo, gprop)
                    time.sleep(0.5)
                    
                    queries = get_related_queries(brand, geo, gprop)
                    time.sleep(0.5)
                    
                    topics = get_related_topics(brand, geo, gprop)
                    time.sleep(0.5)
                    
                    # NUEVO: Filtrar queries y topics por categorías
                    if categories:
                        queries = filter_queries_by_categories(queries, categories, threshold)
                        topics = filter_topics_by_categories(topics, categories, threshold)
                    
                    # Calcular cambios
                    month_change, quarter_change, year_change, avg_value = calculate_changes(timeline)
                    
                    # Guardar resultados del canal
                    channel_results[channel_key] = {
                        'name': channel_name,
                        'timeline': timeline,
                        'queries': queries,
                        'topics': topics,
                        'month_change': month_change,
                        'quarter_change': quarter_change,
                        'year_change': year_change,
                        'avg_value': avg_value
                    }
                    
                except Exception as e:
                    # Si un canal falla, registrar pero continuar
                    channel_results[channel_key] = {
                        'name': channel_name,
                        'error': str(e),
                        'timeline': None,
                        'queries': None,
                        'topics': None,
                        'month_change': 0,
                        'quarter_change': 0,
                        'year_change': 0,
                        'avg_value': 0
                    }
            
            # Consolidar datos del país
            all_channels_data[geo] = {
                'country': country_name,
                'channels': channel_results,
                'consolidated': consolidate_channel_data(channel_results, brand, geo)
            }
    
    return all_channels_data


def consolidate_channel_data(channel_results, brand, geo):
    """
    Consolida datos de múltiples canales en un análisis unificado.
    
    Args:
        channel_results (dict): Resultados de cada canal
        brand (str): Marca analizada
        geo (str): País
    
    Returns:
        dict: Datos consolidados y análisis cross-channel
    """
    consolidated = {
        'total_channels': len(channel_results),
        'channels_with_data': 0,
        'all_queries': [],
        'all_topics': [],
        'channel_volumes': {},
        'dominant_channel': None,
        'insights': []
    }
    
    # Recopilar datos de todos los canales
    total_volume = 0
    channel_volumes = {}
    
    for channel_key, data in channel_results.items():
        if 'error' not in data and data.get('avg_value', 0) > 0:
            consolidated['channels_with_data'] += 1
            
            # Volumen promedio del canal
            avg_val = data.get('avg_value', 0)
            channel_volumes[channel_key] = avg_val
            total_volume += avg_val
            
            # Consolidar queries
            if data.get('queries') and 'related_queries' in data['queries']:
                if 'top' in data['queries']['related_queries']:
                    for q in data['queries']['related_queries']['top']:
                        consolidated['all_queries'].append({
                            'query': q.get('query', ''),
                            'value': q.get('value', 0),
                            'channel': channel_key,
                            'channel_name': data['name'],
                            'category': q.get('category', 'N/A'),
                            'relevance': q.get('relevance', 100),
                            'matched_keywords': q.get('matched_keywords', [])
                        })
            
            # Consolidar topics
            if data.get('topics') and 'related_topics' in data['topics']:
                if 'top' in data['topics']['related_topics']:
                    for t in data['topics']['related_topics']['top'][:10]:
                        consolidated['all_topics'].append({
                            'title': t.get('topic', {}).get('title', ''),
                            'type': t.get('topic', {}).get('type', ''),
                            'value': t.get('value', 0),
                            'channel': channel_key,
                            'channel_name': data['name'],
                            'category': t.get('category', 'N/A'),
                            'relevance': t.get('relevance', 100),
                            'matched_keywords': t.get('matched_keywords', [])
                        })
    
    consolidated['channel_volumes'] = channel_volumes
    
    # Determinar canal dominante
    if channel_volumes:
        dominant = max(channel_volumes.items(), key=lambda x: x[1])
        consolidated['dominant_channel'] = {
            'key': dominant[0],
            'name': channel_results[dominant[0]]['name'],
            'volume': dominant[1],
            'percentage': (dominant[1] / total_volume * 100) if total_volume > 0 else 0
        }
    
    # Generar insights cross-channel
    consolidated['insights'] = generate_cross_channel_insights(
        channel_results, 
        channel_volumes, 
        consolidated['dominant_channel']
    )
    
    return consolidated


def generate_cross_channel_insights(channel_results, channel_volumes, dominant_channel):
    """
    Genera insights analizando datos de múltiples canales.
    
    Args:
        channel_results (dict): Resultados de cada canal
        channel_volumes (dict): Volúmenes por canal
        dominant_channel (dict): Canal dominante
    
    Returns:
        list: Lista de insights
    """
    insights = []
    
    # Insight 1: Canal dominante
    if dominant_channel:
        insights.append({
            'type': 'dominant_channel',
            'icon': '🏆',
            'title': f"Canal dominante: {dominant_channel['name']}",
            'description': f"{dominant_channel['percentage']:.1f}% del volumen total de búsquedas",
            'severity': 'info'
        })
    
    # Insight 2: Distribución de canales
    if len(channel_volumes) > 0:
        # Calcular si hay equilibrio o concentración
        volumes = list(channel_volumes.values())
        max_vol = max(volumes)
        min_vol = min(volumes)
        
        if max_vol > 0 and (max_vol / sum(volumes)) > 0.6:
            insights.append({
                'type': 'concentration',
                'icon': '⚠️',
                'title': 'Concentración alta en un canal',
                'description': 'Más del 60% del interés está en un solo canal',
                'severity': 'warning'
            })
        else:
            insights.append({
                'type': 'balanced',
                'icon': '✅',
                'title': 'Distribución equilibrada',
                'description': 'El interés está distribuido entre varios canales',
                'severity': 'success'
            })
    
    # Insight 3: Canales con crecimiento
    growing_channels = []
    for channel_key, data in channel_results.items():
        if 'error' not in data and data.get('month_change', 0) > 10:
            growing_channels.append({
                'name': data['name'],
                'growth': data['month_change']
            })
    
    if growing_channels:
        top_growth = max(growing_channels, key=lambda x: x['growth'])
        insights.append({
            'type': 'growth',
            'icon': '📈',
            'title': f"Crecimiento destacado en {top_growth['name']}",
            'description': f"+{top_growth['growth']:.1f}% en el último mes",
            'severity': 'success'
        })
    
    # Insight 4: Oportunidades de canal
    low_volume_channels = []
    for channel_key, volume in channel_volumes.items():
        if volume > 0 and volume < sum(channel_volumes.values()) * 0.15:  # Menos del 15%
            low_volume_channels.append(channel_results[channel_key]['name'])
    
    if low_volume_channels:
        insights.append({
            'type': 'opportunity',
            'icon': '💡',
            'title': f"Oportunidad en {', '.join(low_volume_channels[:2])}",
            'description': 'Canales con bajo volumen pero potencial de crecimiento',
            'severity': 'info'
        })
    
    return insights


def compare_brands(brands, countries, categories, threshold, channel="web"):
    """
    Compara múltiples marcas (2-4) simultáneamente.
    
    Args:
        brands (list): Lista de marcas a comparar (2-4)
        countries (list): Países a analizar
        categories (list): Categorías de productos
        threshold (int): Umbral de relevancia
        channel (str): Canal de búsqueda
    
    Returns:
        dict: Resultados comparativos por marca y país
    """
    comparison_results = {}
    gprop = CHANNELS[channel]["gprop"]
    
    for brand in brands:
        brand_results = {}
        
        for geo in countries:
            channel_name = CHANNELS[channel]["name"]
            with st.spinner(f'🔎 Analizando {brand} en {COUNTRIES[geo]["name"]} ({channel_name})...'):
                timeline = get_interest_over_time(brand, geo, gprop)
                time.sleep(1)
                
                queries = get_related_queries(brand, geo, gprop)
                time.sleep(1)
                
                topics = get_related_topics(brand, geo, gprop)
                time.sleep(1)
                
                month_change, quarter_change, year_change, avg_value = calculate_changes(timeline)
                
                brand_results[geo] = {
                    'country': COUNTRIES[geo]['name'],
                    'channel': channel_name,
                    'timeline': timeline,
                    'queries': queries,
                    'topics': topics,
                    'month_change': month_change,
                    'quarter_change': quarter_change,
                    'year_change': year_change,
                    'avg_value': avg_value
                }
        
        comparison_results[brand] = brand_results
    
    return comparison_results


def detect_alerts(current_data, threshold_spike=30, threshold_drop=-20):
    """
    Detecta alertas basadas en cambios significativos.
    
    Args:
        current_data (dict): Datos actuales del análisis
        threshold_spike (int): Umbral de crecimiento significativo (%)
        threshold_drop (int): Umbral de caída significativa (%)
    
    Returns:
        list: Lista de alertas detectadas
    """
    alerts = []
    
    # Verificar cambio mensual
    month_change = current_data.get('month_change')
    if month_change is not None:
        if month_change >= threshold_spike:
            alerts.append({
                'type': 'spike',
                'severity': 'high',
                'metric': 'month_change',
                'value': month_change,
                'message': f"🚀 Crecimiento significativo del {month_change:+.1f}% en el último mes",
                'icon': '🚀',
                'color': '#34C759'
            })
        elif month_change <= threshold_drop:
            alerts.append({
                'type': 'drop',
                'severity': 'high',
                'metric': 'month_change',
                'value': month_change,
                'message': f"⚠️ Caída significativa del {month_change:.1f}% en el último mes",
                'icon': '⚠️',
                'color': '#FF3B30'
            })
    
    # Verificar cambio trimestral
    quarter_change = current_data.get('quarter_change')
    if quarter_change is not None:
        if quarter_change >= threshold_spike * 1.5:  # Mayor umbral para trimestre
            alerts.append({
                'type': 'spike',
                'severity': 'medium',
                'metric': 'quarter_change',
                'value': quarter_change,
                'message': f"📈 Tendencia alcista sostenida: {quarter_change:+.1f}% trimestral",
                'icon': '📈',
                'color': '#34C759'
            })
        elif quarter_change <= threshold_drop * 1.5:
            alerts.append({
                'type': 'drop',
                'severity': 'medium',
                'metric': 'quarter_change',
                'value': quarter_change,
                'message': f"📉 Tendencia bajista sostenida: {quarter_change:.1f}% trimestral",
                'icon': '📉',
                'color': '#FF9500'
            })
    
    # Verificar cambio anual
    year_change = current_data.get('year_change')
    if year_change is not None:
        if year_change >= threshold_spike * 2:  # Mayor umbral para anual
            alerts.append({
                'type': 'spike',
                'severity': 'low',
                'metric': 'year_change',
                'value': year_change,
                'message': f"🌟 Crecimiento anual extraordinario: {year_change:+.1f}%",
                'icon': '🌟',
                'color': '#007AFF'
            })
        elif year_change <= threshold_drop * 2:
            alerts.append({
                'type': 'drop',
                'severity': 'low',
                'metric': 'year_change',
                'value': year_change,
                'message': f"⚡ Declive anual preocupante: {year_change:.1f}%",
                'icon': '⚡',
                'color': '#FF3B30'
            })
    
    # Verificar promedio bajo
    avg_value = current_data.get('avg_value')
    if avg_value is not None and avg_value < 20:
        alerts.append({
            'type': 'low_interest',
            'severity': 'medium',
            'metric': 'avg_value',
            'value': avg_value,
            'message': f"⚡ Interés muy bajo: promedio de {avg_value:.0f}/100",
            'icon': '⚡',
            'color': '#FF9500'
        })
    elif avg_value is not None and avg_value > 80:
        alerts.append({
            'type': 'high_interest',
            'severity': 'low',
            'metric': 'avg_value',
            'value': avg_value,
            'message': f"🔥 Interés muy alto: promedio de {avg_value:.0f}/100",
            'icon': '🔥',
            'color': '#34C759'
        })
    
    return alerts

