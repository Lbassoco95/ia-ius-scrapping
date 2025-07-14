#!/usr/bin/env python3
"""
API REST para consultar tesis de la SCJN
"""

import sys
import os
import json
from typing import List, Dict, Optional
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.models import get_session, Tesis, Consulta
from src.analysis.ai_analyzer import AIAnalyzer
from src.config import Config

# Crear aplicación FastAPI
app = FastAPI(
    title="API de Tesis SCJN",
    description="API para consultar y analizar tesis y jurisprudencia de la SCJN",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class TesisResponse(BaseModel):
    id: int
    scjn_id: str
    titulo: str
    rubro: Optional[str] = None
    texto: Optional[str] = None
    precedente: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    tipo_documento: Optional[str] = None
    materia: Optional[str] = None
    epoca: Optional[str] = None
    sala: Optional[str] = None
    registro: Optional[str] = None
    resumen: Optional[str] = None
    categorias: List[str] = []
    conceptos_clave: List[str] = []
    sentimiento: Optional[str] = None
    relevancia: Optional[float] = None
    pdf_url: Optional[str] = None
    google_drive_id: Optional[str] = None

class ConsultaRequest(BaseModel):
    pregunta: str
    usuario: Optional[str] = "api_user"

class ConsultaResponse(BaseModel):
    pregunta: str
    respuesta: str
    documentos_referenciados: List[str]
    fecha_consulta: datetime

class EstadisticasResponse(BaseModel):
    total_tesis: int
    tesis_analizadas: int
    total_consultas: int
    top_categorias: List[Dict[str, int]]

# Dependencias
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

# Rutas
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "API de Tesis SCJN",
        "version": "1.0.0",
        "endpoints": {
            "tesis": "/api/tesis",
            "consulta": "/api/consulta",
            "estadisticas": "/api/estadisticas",
            "docs": "/docs"
        }
    }

@app.get("/api/tesis", response_model=List[TesisResponse])
async def get_tesis(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    materia: Optional[str] = Query(None, description="Filtrar por materia"),
    sala: Optional[str] = Query(None, description="Filtrar por sala"),
    db: Session = Depends(get_db)
):
    """Obtener lista de tesis con filtros opcionales"""
    try:
        query = db.query(Tesis)
        
        # Aplicar filtros
        if categoria:
            query = query.filter(Tesis.categorias.contains(categoria))
        
        if materia:
            query = query.filter(Tesis.materia.contains(materia))
        
        if sala:
            query = query.filter(Tesis.sala.contains(sala))
        
        # Obtener resultados
        tesis_list = query.offset(skip).limit(limit).all()
        
        # Convertir a respuesta
        response = []
        for tesis in tesis_list:
            tesis_dict = {
                'id': tesis.id,
                'scjn_id': tesis.scjn_id,
                'titulo': tesis.titulo,
                'rubro': tesis.rubro,
                'texto': tesis.texto,
                'precedente': tesis.precedente,
                'fecha_publicacion': tesis.fecha_publicacion,
                'tipo_documento': tesis.tipo_documento,
                'materia': tesis.materia,
                'epoca': tesis.epoca,
                'sala': tesis.sala,
                'registro': tesis.registro,
                'resumen': tesis.resumen,
                'categorias': json.loads(tesis.categorias) if tesis.categorias else [],
                'conceptos_clave': json.loads(tesis.conceptos_clave) if tesis.conceptos_clave else [],
                'sentimiento': tesis.sentimiento,
                'relevancia': tesis.relevancia,
                'pdf_url': tesis.pdf_url,
                'google_drive_id': tesis.google_drive_id
            }
            response.append(tesis_dict)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tesis: {str(e)}")

@app.get("/api/tesis/{tesis_id}", response_model=TesisResponse)
async def get_tesis_by_id(tesis_id: int, db: Session = Depends(get_db)):
    """Obtener una tesis específica por ID"""
    try:
        tesis = db.query(Tesis).filter(Tesis.id == tesis_id).first()
        
        if not tesis:
            raise HTTPException(status_code=404, detail="Tesis no encontrada")
        
        return {
            'id': tesis.id,
            'scjn_id': tesis.scjn_id,
            'titulo': tesis.titulo,
            'rubro': tesis.rubro,
            'texto': tesis.texto,
            'precedente': tesis.precedente,
            'fecha_publicacion': tesis.fecha_publicacion,
            'tipo_documento': tesis.tipo_documento,
            'materia': tesis.materia,
            'epoca': tesis.epoca,
            'sala': tesis.sala,
            'registro': tesis.registro,
            'resumen': tesis.resumen,
            'categorias': json.loads(tesis.categorias) if tesis.categorias else [],
            'conceptos_clave': json.loads(tesis.conceptos_clave) if tesis.conceptos_clave else [],
            'sentimiento': tesis.sentimiento,
            'relevancia': tesis.relevancia,
            'pdf_url': tesis.pdf_url,
            'google_drive_id': tesis.google_drive_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tesis: {str(e)}")

@app.get("/api/tesis/scjn/{scjn_id}", response_model=TesisResponse)
async def get_tesis_by_scjn_id(scjn_id: str, db: Session = Depends(get_db)):
    """Obtener una tesis específica por ID de SCJN"""
    try:
        tesis = db.query(Tesis).filter(Tesis.scjn_id == scjn_id).first()
        
        if not tesis:
            raise HTTPException(status_code=404, detail="Tesis no encontrada")
        
        return {
            'id': tesis.id,
            'scjn_id': tesis.scjn_id,
            'titulo': tesis.titulo,
            'rubro': tesis.rubro,
            'texto': tesis.texto,
            'precedente': tesis.precedente,
            'fecha_publicacion': tesis.fecha_publicacion,
            'tipo_documento': tesis.tipo_documento,
            'materia': tesis.materia,
            'epoca': tesis.epoca,
            'sala': tesis.sala,
            'registro': tesis.registro,
            'resumen': tesis.resumen,
            'categorias': json.loads(tesis.categorias) if tesis.categorias else [],
            'conceptos_clave': json.loads(tesis.conceptos_clave) if tesis.conceptos_clave else [],
            'sentimiento': tesis.sentimiento,
            'relevancia': tesis.relevancia,
            'pdf_url': tesis.pdf_url,
            'google_drive_id': tesis.google_drive_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tesis: {str(e)}")

@app.post("/api/consulta", response_model=ConsultaResponse)
async def consultar_tesis(consulta: ConsultaRequest, db: Session = Depends(get_db)):
    """Realizar consulta sobre tesis usando IA"""
    try:
        ai_analyzer = AIAnalyzer()
        
        # Buscar documentos relevantes
        relevant_docs = []
        query = db.query(Tesis)
        
        # Búsqueda por palabras clave
        keywords = consulta.pregunta.lower().split()
        for keyword in keywords:
            if len(keyword) > 3:
                query = query.filter(
                    (Tesis.titulo.contains(keyword)) |
                    (Tesis.texto.contains(keyword)) |
                    (Tesis.resumen.contains(keyword))
                )
        
        results = query.limit(5).all()
        
        for tesis in results:
            doc = {
                'id': tesis.id,
                'scjn_id': tesis.scjn_id,
                'titulo': tesis.titulo,
                'texto': tesis.texto,
                'resumen': tesis.resumen
            }
            relevant_docs.append(doc)
        
        # Generar respuesta
        if relevant_docs:
            respuesta = ai_analyzer.answer_question(consulta.pregunta, relevant_docs)
        else:
            respuesta = "No encontré documentos relevantes para tu pregunta. ¿Podrías reformularla?"
        
        # Guardar consulta
        consulta_db = Consulta(
            pregunta=consulta.pregunta,
            respuesta=respuesta,
            documentos_referenciados=json.dumps([doc.get('scjn_id') for doc in relevant_docs], ensure_ascii=False),
            usuario=consulta.usuario
        )
        
        db.add(consulta_db)
        db.commit()
        
        return {
            'pregunta': consulta.pregunta,
            'respuesta': respuesta,
            'documentos_referenciados': [doc.get('scjn_id') for doc in relevant_docs],
            'fecha_consulta': consulta_db.fecha_consulta
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")

@app.get("/api/estadisticas", response_model=EstadisticasResponse)
async def get_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas del sistema"""
    try:
        total_tesis = db.query(Tesis).count()
        tesis_analizadas = db.query(Tesis).filter_by(analizado=True).count()
        total_consultas = db.query(Consulta).count()
        
        # Categorías más comunes
        categorias_query = db.query(Tesis.categorias).filter(Tesis.categorias.isnot(None))
        categorias = []
        for result in categorias_query:
            if result[0]:
                categorias.extend(json.loads(result[0]))
        
        from collections import Counter
        categorias_count = Counter(categorias)
        top_categorias = [{'categoria': cat, 'count': count} for cat, count in categorias_count.most_common(5)]
        
        return {
            'total_tesis': total_tesis,
            'tesis_analizadas': tesis_analizadas,
            'total_consultas': total_consultas,
            'top_categorias': top_categorias
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@app.get("/api/buscar")
async def buscar_tesis(
    q: str = Query(..., description="Término de búsqueda"),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de resultados"),
    db: Session = Depends(get_db)
):
    """Buscar tesis por término"""
    try:
        query = db.query(Tesis)
        
        # Búsqueda en múltiples campos
        search_term = f"%{q}%"
        query = query.filter(
            (Tesis.titulo.contains(search_term)) |
            (Tesis.texto.contains(search_term)) |
            (Tesis.resumen.contains(search_term)) |
            (Tesis.rubro.contains(search_term))
        )
        
        results = query.limit(limit).all()
        
        response = []
        for tesis in results:
            tesis_dict = {
                'id': tesis.id,
                'scjn_id': tesis.scjn_id,
                'titulo': tesis.titulo,
                'resumen': tesis.resumen,
                'categorias': json.loads(tesis.categorias) if tesis.categorias else [],
                'relevancia': tesis.relevancia
            }
            response.append(tesis_dict)
        
        return {
            'query': q,
            'total_results': len(response),
            'results': response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

def main():
    """Función principal para ejecutar la API"""
    import uvicorn
    
    try:
        # Validar configuración
        Config.validate()
        
        # Ejecutar servidor
        uvicorn.run(
            "src.api.main:app",
            host=Config.API_HOST,
            port=Config.API_PORT,
            reload=Config.API_DEBUG
        )
        
    except Exception as e:
        print(f"Error iniciando API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 