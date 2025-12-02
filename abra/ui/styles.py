"""
Estilos CSS Apple-style para Abra
"""
import streamlit as st

def apply_custom_css():
    """Aplica CSS personalizado Apple-style"""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-bg: #ffffff;
        --secondary-bg: #f5f5f7;
        --card-bg: #ffffff;
        --card-border: rgba(0, 0, 0, 0.08);
        --text-primary: #1d1d1f;
        --text-secondary: #6e6e73;
        --text-tertiary: #86868b;
        --accent-orange: #FF6B00;
        --accent-blue: #007AFF;
        --accent-green: #34C759;
        --accent-red: #FF3B30;
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f7 100%);
    }
    
    .main-header {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 24px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B00 0%, #FF8533 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .main-header p {
        color: var(--text-secondary);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--accent-orange);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-delta {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-delta.positive { color: var(--accent-green); }
    .metric-delta.negative { color: var(--accent-red); }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #ff8533 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(255, 107, 0, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(255, 107, 0, 0.4);
    }
    
    .stTextInput > div > div > input {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        color: var(--text-primary);
        padding: 0.75rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-orange);
        box-shadow: 0 0 0 3px rgba(255, 107, 0, 0.1);
        outline: none;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-tertiary);
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* FLOATING FOOTER - Barra de herramientas flotante abajo */
    .floating-toolbar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-top: 1px solid var(--card-border);
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.12);
        padding: 1rem 2rem;
        z-index: 9999;
        animation: slideUp 0.3s ease-out;
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    /* Ajustar padding del contenido para que no quede tapado */
    .main .block-container {
        padding-bottom: 140px !important;
    }
    
    /* Compact multiselect tags */
    .stMultiSelect [data-baseweb="tag"] {
        margin: 2px;
        font-size: 0.8rem;
        padding: 0.2rem 0.5rem;
    }
    
    /* Compact selectbox */
    .stSelectbox select {
        font-size: 0.9rem;
        padding: 0.5rem;
    }
    
    /* Slider más compacto */
    .stSlider {
        padding-top: 0.25rem;
    }
    
    /* Labels más pequeños en toolbar */
    .stSelectbox label,
    .stMultiSelect label,
    .stSlider label {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* ========================================= */
    /* NUEVOS ESTILOS SPRINT 1 - GLIMPSE-STYLE */
    /* ========================================= */
    
    /* Query bars - Barras horizontales para volumen */
    .query-bar-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--card-border);
        transition: background 0.2s ease;
    }
    
    .query-bar-container:hover {
        background: var(--secondary-bg);
    }
    
    .query-text {
        flex: 0 0 300px;
        font-weight: 500;
        color: var(--text-primary);
        font-size: 0.95rem;
    }
    
    .query-bar-wrapper {
        flex: 1;
        position: relative;
        height: 28px;
        background: var(--secondary-bg);
        border-radius: 6px;
        overflow: hidden;
    }
    
    .query-bar {
        height: 100%;
        background: linear-gradient(90deg, #007AFF 0%, #0051D5 100%);
        border-radius: 6px;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 0.75rem;
        box-shadow: 0 2px 4px rgba(0, 122, 255, 0.2);
    }
    
    .query-bar:hover {
        filter: brightness(1.1);
    }
    
    .query-value {
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* Seasonality bars */
    .seasonality-container {
        display: flex;
        align-items: flex-end;
        justify-content: space-around;
        height: 200px;
        padding: 1rem;
        gap: 0.5rem;
    }
    
    .seasonality-month {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    .seasonality-bar {
        width: 100%;
        border-radius: 4px 4px 0 0;
        transition: all 0.2s ease;
        min-height: 4px;
    }
    
    .seasonality-bar.positive {
        background: linear-gradient(180deg, #34C759 0%, #248A3D 100%);
    }
    
    .seasonality-bar.negative {
        background: linear-gradient(180deg, #FF6B6B 0%, #C92A2A 100%);
    }
    
    .seasonality-bar:hover {
        opacity: 0.8;
        transform: scaleX(1.05);
    }
    
    .month-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* ========================================= */
    /* SPRINT 2: EXPORT & SPARKLINES STYLES     */
    /* ========================================= */
    
    /* Export button container */
    .export-container {
        position: fixed;
        top: 2rem;
        right: 2rem;
        z-index: 1000;
    }
    
    .export-button {
        background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .export-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0, 122, 255, 0.4);
    }
    
    /* Export modal */
    .export-modal {
        background: white;
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        min-width: 250px;
    }
    
    .export-option {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 0.5rem;
    }
    
    .export-option:hover {
        background: var(--secondary-bg);
    }
    
    .export-icon {
        font-size: 1.5rem;
    }
    
    .export-text {
        font-weight: 500;
        color: var(--text-primary);
    }
    
    /* Sparkline cards */
    .sparkline-card {
        background: white;
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .sparkline-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: #007AFF;
    }
    
    .sparkline-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    .sparkline-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.8rem;
    }
    
    .sparkline-type {
        color: var(--text-secondary);
    }
    
    .sparkline-value {
        font-weight: 600;
        color: var(--accent-green);
    }
    
    /* Pagination */
    .pagination {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.5rem 1rem;
        border-top: 1px solid var(--card-border);
    }
    
    .pagination-info {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .pagination-controls {
        display: flex;
        gap: 0.5rem;
    }
    
    /* Results counter */
    .results-counter {
        display: inline-flex;
        align-items: center;
        background: var(--secondary-bg);
        padding: 0.4rem 0.9rem;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-left: 0.5rem;
    }
    
    /* Sort controls */
    .sort-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding: 0.75rem 1rem;
        background: var(--secondary-bg);
        border-radius: 12px;
    }
    
    .sort-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Chips/Pills para categorías */
    .category-chip {
        display: inline-block;
        background: var(--secondary-bg);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        padding: 0.4rem 0.8rem;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
        margin: 0.25rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .category-chip:hover {
        background: var(--accent-orange);
        color: white;
        border-color: var(--accent-orange);
    }
    
    .category-chip.selected {
        background: var(--accent-orange);
        color: white;
        border-color: var(--accent-orange);
    }
    
    /* Country flags */
    .country-flag {
        font-size: 1.5rem;
        cursor: pointer;
        opacity: 0.3;
        transition: all 0.2s ease;
        margin: 0 0.25rem;
    }
    
    .country-flag:hover {
        opacity: 1;
        transform: scale(1.2);
    }
    
    .country-flag.selected {
        opacity: 1;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 1px solid var(--card-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--secondary-bg);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--secondary-bg);
        color: var(--accent-orange) !important;
        border-bottom: 2px solid var(--accent-orange);
    }
    
    .streamlit-expanderHeader {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        color: var(--text-primary);
        font-weight: 500;
        padding: 1rem 1.5rem;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--secondary-bg);
        border-color: var(--accent-orange);
    }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .badge-high {
        background: rgba(52, 199, 89, 0.15);
        color: #248A3D;
        border: 1px solid rgba(52, 199, 89, 0.3);
    }
    
    .badge-medium {
        background: rgba(255, 204, 0, 0.15);
        color: #B38600;
        border: 1px solid rgba(255, 204, 0, 0.3);
    }
    
    .badge-low {
        background: rgba(255, 149, 0, 0.15);
        color: #C66900;
        border: 1px solid rgba(255, 149, 0, 0.3);
    }
    
    .badge-doubt {
        background: rgba(255, 59, 48, 0.15);
        color: #D70015;
        border: 1px solid rgba(255, 59, 48, 0.3);
    }
    
    /* ================================ */
    /* SPRINT 4: ANIMATIONS & TRANSITIONS */
    /* ================================ */
    
    /* Keyframes */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    @keyframes loading {
        0% {
            background-position: 200% 0;
        }
        100% {
            background-position: -200% 0;
        }
    }
    
    /* Animation Classes */
    .animate-fadeInUp {
        animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        animation-fill-mode: both;
    }
    
    .animate-fadeIn {
        animation: fadeIn 0.5s ease-out;
        animation-fill-mode: both;
    }
    
    .animate-slideInRight {
        animation: slideInRight 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        animation-fill-mode: both;
    }
    
    .animate-scaleIn {
        animation: scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation-fill-mode: both;
    }
    
    /* Staggered Delays */
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .delay-4 { animation-delay: 0.4s; }
    .delay-5 { animation-delay: 0.5s; }
    .delay-6 { animation-delay: 0.6s; }
    
    /* Skeleton Loader */
    .skeleton {
        background: linear-gradient(
            90deg,
            #f0f0f0 25%,
            #e0e0e0 50%,
            #f0f0f0 75%
        );
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: 4px;
    }
    
    /* Enhanced Hover Effects */
    .metric-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .glass-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18);
        border-color: rgba(0, 122, 255, 0.3);
    }
    
    /* Button Hover Effects */
    button {
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Sparkline Card Animations */
    .sparkline-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .sparkline-card:hover {
        transform: translateY(-4px) scale(1.03);
        box-shadow: 0 8px 24px rgba(0, 122, 255, 0.2);
        border-color: var(--accent-blue);
    }
    
    /* Query Bar Animations */
    .query-bar-container {
        transition: all 0.2s ease;
    }
    
    .query-bar-container:hover {
        transform: translateX(4px);
        background: rgba(0, 122, 255, 0.02);
    }
    
    .query-bar {
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Seasonality Bar Animations */
    .seasonality-bar {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .seasonality-bar:hover {
        transform: scaleY(1.1);
        filter: brightness(1.2);
    }
    
    /* Loading Animation */
    .loading-pulse {
        animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Smooth Transitions for All Interactive Elements */
    a, input, select, textarea {
        transition: all 0.2s ease;
    }
    
    input:focus, select:focus, textarea:focus {
        outline: none;
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
    }
    
    /* Tab Transitions */
    .stTabs [data-baseweb="tab-list"] button {
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: rgba(0, 122, 255, 0.05);
    }
    
    /* Export Button Animations */
    .export-button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .export-button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 20px rgba(0, 122, 255, 0.3);
    }
    
    .export-button:active {
        transform: translateY(-1px) scale(1.02);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
