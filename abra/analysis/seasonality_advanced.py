"""
Análisis Avanzado de Estacionalidad
- Por país
- Líneas de tendencia (linear, exponencial, logarítmica)
- Análisis logarítmico
- Predicciones
"""
import numpy as np
from scipy import stats
from datetime import datetime
import math

def calculate_seasonality_by_country(timeline_data, country_code):
    """
    Calcula estacionalidad específica por país con análisis avanzado
    
    Args:
        timeline_data: Datos temporales
        country_code: Código de país (ES, PT, etc)
    
    Returns:
        dict con análisis completo
    """
    if not timeline_data or 'interest_over_time' not in timeline_data:
        return None
    
    try:
        values = timeline_data['interest_over_time']['timeline_data']
        
        # Extraer valores y fechas
        dates = []
        vals = []
        monthly_values = {}
        
        for item in values:
            if item.get('values'):
                date_str = item['date']
                value = item['values'][0].get('extracted_value', 0)
                
                # Parsear fecha
                try:
                    date = datetime.strptime(date_str, "%b %d, %Y")
                    dates.append(date)
                    vals.append(value)
                    
                    # Agrupar por mes
                    month_name = date.strftime("%B")
                    if month_name not in monthly_values:
                        monthly_values[month_name] = []
                    monthly_values[month_name].append(value)
                except:
                    pass
        
        if not vals:
            return None
        
        # Convertir a numpy arrays
        x_vals = np.arange(len(vals))
        y_vals = np.array(vals)
        
        # 1. TENDENCIA LINEAR
        slope_linear, intercept_linear, r_value_linear, _, _ = stats.linregress(x_vals, y_vals)
        trend_linear = slope_linear * x_vals + intercept_linear
        r_squared_linear = r_value_linear ** 2
        
        # 2. TENDENCIA EXPONENCIAL
        # y = a * e^(bx)
        # log(y) = log(a) + bx
        y_positive = np.maximum(y_vals, 0.1)  # Evitar log(0)
        log_y = np.log(y_positive)
        slope_exp, intercept_exp, r_value_exp, _, _ = stats.linregress(x_vals, log_y)
        a_exp = np.exp(intercept_exp)
        b_exp = slope_exp
        trend_exponential = a_exp * np.exp(b_exp * x_vals)
        r_squared_exp = r_value_exp ** 2
        
        # 3. TENDENCIA LOGARÍTMICA
        # y = a + b*log(x)
        x_positive = np.maximum(x_vals + 1, 1)  # Evitar log(0)
        log_x = np.log(x_positive)
        slope_log, intercept_log, r_value_log, _, _ = stats.linregress(log_x, y_vals)
        trend_logarithmic = slope_log * log_x + intercept_log
        r_squared_log = r_value_log ** 2
        
        # 4. ANÁLISIS LOGARÍTMICO DE VOLATILIDAD
        # Usar log-returns para medir volatilidad
        log_returns = []
        for i in range(1, len(y_positive)):
            if y_positive[i-1] > 0:
                log_return = math.log(y_positive[i] / y_positive[i-1])
                log_returns.append(log_return)
        
        volatility = np.std(log_returns) if log_returns else 0
        mean_log_return = np.mean(log_returns) if log_returns else 0
        
        # 5. SELECCIONAR MEJOR TENDENCIA
        best_model = 'linear'
        best_r_squared = r_squared_linear
        best_trend = trend_linear
        
        if r_squared_exp > best_r_squared:
            best_model = 'exponential'
            best_r_squared = r_squared_exp
            best_trend = trend_exponential
        
        if r_squared_log > best_r_squared:
            best_model = 'logarithmic'
            best_r_squared = r_squared_log
            best_trend = trend_logarithmic
        
        # 6. PREDICCIÓN (3 meses)
        future_x = np.arange(len(vals), len(vals) + 3)
        if best_model == 'linear':
            predictions = slope_linear * future_x + intercept_linear
        elif best_model == 'exponential':
            predictions = a_exp * np.exp(b_exp * future_x)
        else:  # logarithmic
            predictions = slope_log * np.log(future_x + 1) + intercept_log
        
        # 7. PROMEDIOS MENSUALES
        monthly_avg = {}
        for month, values_list in monthly_values.items():
            monthly_avg[month] = sum(values_list) / len(values_list)
        
        overall_avg = np.mean(vals)
        
        # 8. SCORE DE ESTACIONALIDAD
        if overall_avg > 0:
            std_dev = np.std(list(monthly_avg.values()))
            seasonality_score = min((std_dev / overall_avg) * 100, 100)
        else:
            seasonality_score = 0
        
        return {
            'country': country_code,
            'monthly_avg': monthly_avg,
            'overall_avg': float(overall_avg),
            'seasonality_score': float(seasonality_score),
            
            # Tendencias
            'trends': {
                'linear': {
                    'values': trend_linear.tolist(),
                    'r_squared': float(r_squared_linear),
                    'slope': float(slope_linear),
                    'equation': f'y = {slope_linear:.2f}x + {intercept_linear:.2f}'
                },
                'exponential': {
                    'values': trend_exponential.tolist(),
                    'r_squared': float(r_squared_exp),
                    'equation': f'y = {a_exp:.2f} * e^({b_exp:.4f}x)'
                },
                'logarithmic': {
                    'values': trend_logarithmic.tolist(),
                    'r_squared': float(r_squared_log),
                    'equation': f'y = {slope_log:.2f} * ln(x) + {intercept_log:.2f}'
                },
                'best_model': best_model,
                'best_r_squared': float(best_r_squared)
            },
            
            # Análisis logarítmico
            'log_analysis': {
                'volatility': float(volatility),
                'mean_log_return': float(mean_log_return),
                'risk_level': 'High' if volatility > 0.5 else 'Medium' if volatility > 0.2 else 'Low'
            },
            
            # Predicciones
            'predictions': {
                'next_3_months': predictions.tolist(),
                'confidence': float(best_r_squared)
            },
            
            # Raw data para gráficos
            'raw_data': {
                'dates': [d.strftime("%Y-%m-%d") for d in dates],
                'values': vals
            }
        }
    
    except Exception as e:
        print(f"Error in seasonality calculation: {e}")
        return None


def compare_seasonality_countries(results_by_country):
    """
    Compara estacionalidad entre países
    
    Args:
        results_by_country: Dict {country_code: seasonality_data}
    
    Returns:
        Análisis comparativo
    """
    comparison = {
        'countries': [],
        'most_seasonal': None,
        'least_seasonal': None,
        'most_volatile': None,
        'best_trend': None
    }
    
    for country, data in results_by_country.items():
        if not data:
            continue
        
        comparison['countries'].append({
            'country': country,
            'seasonality_score': data['seasonality_score'],
            'volatility': data['log_analysis']['volatility'],
            'best_model': data['trends']['best_model'],
            'r_squared': data['trends']['best_r_squared']
        })
    
    if comparison['countries']:
        # Ordenar por estacionalidad
        sorted_by_seasonality = sorted(comparison['countries'], 
                                       key=lambda x: x['seasonality_score'], 
                                       reverse=True)
        comparison['most_seasonal'] = sorted_by_seasonality[0]
        comparison['least_seasonal'] = sorted_by_seasonality[-1]
        
        # Más volátil
        sorted_by_volatility = sorted(comparison['countries'], 
                                      key=lambda x: x['volatility'], 
                                      reverse=True)
        comparison['most_volatile'] = sorted_by_volatility[0]
        
        # Mejor ajuste
        sorted_by_fit = sorted(comparison['countries'], 
                              key=lambda x: x['r_squared'], 
                              reverse=True)
        comparison['best_trend'] = sorted_by_fit[0]
    
    return comparison
