"""
Configuración específica para el scraping de la página de SCJN
"""

# Selectores CSS para diferentes elementos de la página
SELECTORS = {
    # Página de búsqueda
    'search_results': [
        'div.resultado-busqueda',
        'tr.tesis-row',
        'div.tesis-item',
        'div.search-result'
    ],
    
    # Elementos de tesis individual
    'tesis_link': 'a[href*="/detalle/tesis/"]',
    'tesis_title': [
        'h3',
        'h4',
        'strong',
        '.titulo-tesis',
        '.tesis-title'
    ],
    
    # Metadatos
    'metadata': {
        'materia': [
            '.materia',
            '.subject',
            '[data-field="materia"]'
        ],
        'epoca': [
            '.epoca',
            '.epoch',
            '[data-field="epoca"]'
        ],
        'sala': [
            '.sala',
            '.chamber',
            '[data-field="sala"]'
        ],
        'registro': [
            '.registro',
            '.registry',
            '[data-field="registro"]'
        ],
        'fecha': [
            '.fecha',
            '.date',
            '[data-field="fecha"]'
        ]
    },
    
    # Página de detalle
    'detail': {
        'rubro': [
            '.rubro',
            '.rubric',
            '[data-field="rubro"]'
        ],
        'texto': [
            '.texto',
            '.text',
            '.tesis-text',
            '[data-field="texto"]'
        ],
        'precedente': [
            '.precedente',
            '.precedent',
            '[data-field="precedente"]'
        ]
    },
    
    # Enlaces de PDF
    'pdf_links': [
        'a[href*=".pdf"]',
        'a[href*="download"]',
        'a:contains("PDF")',
        'a:contains("Descargar")'
    ]
}

# Patrones de URL
URL_PATTERNS = {
    'base_url': 'https://sjf2.scjn.gob.mx',
    'search_url': 'https://sjf2.scjn.gob.mx/busqueda-principal-tesis',
    'detail_pattern': r'/detalle/tesis/(\d+)',
    'pdf_pattern': r'\.pdf$'
}

# Configuración de paginación
PAGINATION = {
    'param_name': 'page',
    'size_param': 'size',
    'default_size': 20,
    'max_pages': 50
}

# Filtros disponibles
FILTERS = {
    'materia': [
        'Derecho Constitucional',
        'Derecho Civil',
        'Derecho Penal',
        'Derecho Administrativo',
        'Derecho Laboral',
        'Derecho Mercantil',
        'Derecho Fiscal',
        'Derecho Procesal',
        'Derechos Humanos',
        'Amparo'
    ],
    'epoca': [
        'Décima Época',
        'Novena Época',
        'Octava Época',
        'Séptima Época'
    ],
    'sala': [
        'Primera Sala',
        'Segunda Sala',
        'Pleno'
    ],
    'tipo': [
        'Tesis',
        'Jurisprudencia',
        'Voto Particular'
    ]
}

# Configuración de delays y timeouts
TIMING = {
    'request_delay': 1,  # segundos entre requests
    'page_load_timeout': 30,
    'download_timeout': 60,
    'max_retries': 3,
    'retry_delay': 5
}

# Headers para requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Configuración de logging específica
LOGGING = {
    'scraper_logger': 'scjn_scraper',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_level': 'INFO'
}

# Configuración de validación de datos
VALIDATION = {
    'required_fields': ['scjn_id', 'titulo'],
    'min_title_length': 10,
    'max_title_length': 500,
    'min_text_length': 50,
    'max_text_length': 50000
}

# Configuración de procesamiento de PDFs
PDF_CONFIG = {
    'download_dir': 'data/pdfs',
    'filename_template': 'tesis_{scjn_id}.pdf',
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'allowed_extensions': ['.pdf']
}

# Configuración de análisis de contenido
CONTENT_ANALYSIS = {
    'max_content_length': 4000,  # para análisis de IA
    'summary_max_length': 200,
    'keywords_max_count': 10,
    'categories_max_count': 5
}

# Configuración de base de datos
DATABASE_CONFIG = {
    'batch_size': 100,
    'commit_interval': 10,
    'duplicate_check': True
}

# Configuración de monitoreo
MONITORING = {
    'progress_interval': 10,  # mostrar progreso cada N tesis
    'stats_interval': 100,    # mostrar estadísticas cada N tesis
    'save_interval': 50       # guardar resultados cada N tesis
} 