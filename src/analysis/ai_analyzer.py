import openai
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

from src.config import Config

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """Analizador de documentos usando OpenAI"""
    
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.model = "gpt-4"  # o "gpt-3.5-turbo" para costos menores
        
    def analyze_tesis(self, tesis_data: Dict) -> Dict:
        """Analizar una tesis completa"""
        try:
            # Preparar contenido para análisis
            content = self._prepare_content(tesis_data)
            
            # Realizar análisis
            analysis = {
                'resumen': self._generate_summary(content),
                'categorias': self._categorize_document(content),
                'conceptos_clave': self._extract_key_concepts(content),
                'sentimiento': self._analyze_sentiment(content),
                'relevancia': self._assess_relevance(content),
                'fecha_analisis': datetime.now().isoformat()
            }
            
            logger.info(f"Análisis completado para tesis: {tesis_data.get('titulo', 'Sin título')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando tesis: {e}")
            return {}
    
    def _prepare_content(self, tesis_data: Dict) -> str:
        """Preparar contenido para análisis"""
        content_parts = []
        
        if tesis_data.get('titulo'):
            content_parts.append(f"Título: {tesis_data['titulo']}")
        
        if tesis_data.get('rubro'):
            content_parts.append(f"Rubro: {tesis_data['rubro']}")
        
        if tesis_data.get('texto'):
            content_parts.append(f"Texto: {tesis_data['texto']}")
        
        if tesis_data.get('precedente'):
            content_parts.append(f"Precedente: {tesis_data['precedente']}")
        
        if tesis_data.get('metadata'):
            metadata = tesis_data['metadata']
            if metadata.get('materia'):
                content_parts.append(f"Materia: {metadata['materia']}")
            if metadata.get('epoca'):
                content_parts.append(f"Época: {metadata['epoca']}")
            if metadata.get('sala'):
                content_parts.append(f"Sala: {metadata['sala']}")
        
        return "\n\n".join(content_parts)
    
    def _generate_summary(self, content: str) -> str:
        """Generar resumen del documento"""
        try:
            prompt = f"""
            Analiza el siguiente documento legal y genera un resumen conciso pero completo en español:
            
            {content[:4000]}  # Limitar contenido para evitar tokens excesivos
            
            El resumen debe incluir:
            - Puntos principales del fallo
            - Criterio jurídico establecido
            - Relevancia práctica
            - Máximo 200 palabras
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis legal y jurisprudencia mexicana."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return "Error generando resumen"
    
    def _categorize_document(self, content: str) -> List[str]:
        """Categorizar el documento"""
        try:
            prompt = f"""
            Analiza el siguiente documento legal y categorízalo en las siguientes áreas:
            
            {content[:3000]}
            
            Categorías disponibles:
            - Derecho Constitucional
            - Derecho Civil
            - Derecho Penal
            - Derecho Administrativo
            - Derecho Laboral
            - Derecho Mercantil
            - Derecho Fiscal
            - Derecho Procesal
            - Derechos Humanos
            - Amparo
            - Otros
            
            Responde solo con las categorías aplicables, separadas por comas.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en clasificación legal."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.2
            )
            
            categories = response.choices[0].message.content.strip().split(',')
            return [cat.strip() for cat in categories if cat.strip()]
            
        except Exception as e:
            logger.error(f"Error categorizando documento: {e}")
            return ["Sin categorizar"]
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extraer conceptos clave"""
        try:
            prompt = f"""
            Extrae los conceptos jurídicos clave del siguiente documento:
            
            {content[:3000]}
            
            Responde con una lista de conceptos clave, uno por línea.
            Máximo 10 conceptos.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en terminología jurídica mexicana."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            concepts = response.choices[0].message.content.strip().split('\n')
            return [concept.strip() for concept in concepts if concept.strip()]
            
        except Exception as e:
            logger.error(f"Error extrayendo conceptos clave: {e}")
            return []
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analizar sentimiento del documento"""
        try:
            prompt = f"""
            Analiza el sentimiento del siguiente documento legal:
            
            {content[:2000]}
            
            Clasifica como:
            - POSITIVO: Si establece derechos o protecciones
            - NEGATIVO: Si restringe derechos o establece limitaciones
            - NEUTRO: Si es meramente interpretativo o descriptivo
            
            Responde solo con una palabra: POSITIVO, NEGATIVO o NEUTRO
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de sentimiento legal."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            sentiment = response.choices[0].message.content.strip().upper()
            return sentiment if sentiment in ['POSITIVO', 'NEGATIVO', 'NEUTRO'] else 'NEUTRO'
            
        except Exception as e:
            logger.error(f"Error analizando sentimiento: {e}")
            return 'NEUTRO'
    
    def _assess_relevance(self, content: str) -> float:
        """Evaluar relevancia del documento (0-1)"""
        try:
            prompt = f"""
            Evalúa la relevancia del siguiente documento legal en una escala del 0 al 1:
            
            {content[:2000]}
            
            Considera:
            - Impacto en la jurisprudencia
            - Aplicabilidad práctica
            - Claridad del criterio
            - Precedente establecido
            
            Responde solo con un número entre 0 y 1 (ej: 0.85)
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en evaluación de relevancia jurídica."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            relevance_text = response.choices[0].message.content.strip()
            try:
                relevance = float(relevance_text)
                return max(0.0, min(1.0, relevance))  # Asegurar rango 0-1
            except ValueError:
                return 0.5
            
        except Exception as e:
            logger.error(f"Error evaluando relevancia: {e}")
            return 0.5
    
    def answer_question(self, question: str, context_documents: List[Dict]) -> str:
        """Responder pregunta basada en documentos"""
        try:
            # Preparar contexto
            context = self._prepare_context_for_question(context_documents)
            
            prompt = f"""
            Basándote en los siguientes documentos jurídicos, responde la pregunta:
            
            Contexto:
            {context}
            
            Pregunta: {question}
            
            Responde de manera clara y precisa, citando los documentos relevantes cuando sea apropiado.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en derecho mexicano y jurisprudencia de la SCJN."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error respondiendo pregunta: {e}")
            return "Error procesando la pregunta"
    
    def _prepare_context_for_question(self, documents: List[Dict]) -> str:
        """Preparar contexto para preguntas"""
        context_parts = []
        
        for i, doc in enumerate(documents[:5]):  # Limitar a 5 documentos
            doc_context = f"Documento {i+1}:\n"
            
            if doc.get('titulo'):
                doc_context += f"Título: {doc['titulo']}\n"
            
            if doc.get('resumen'):
                doc_context += f"Resumen: {doc['resumen']}\n"
            elif doc.get('texto'):
                doc_context += f"Texto: {doc['texto'][:500]}...\n"
            
            context_parts.append(doc_context)
        
        return "\n\n".join(context_parts)
    
    def find_similar_documents(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Encontrar documentos similares"""
        try:
            # Crear embeddings para la consulta y documentos
            query_embedding = self._get_embedding(query)
            
            similarities = []
            for doc in documents:
                doc_text = f"{doc.get('titulo', '')} {doc.get('resumen', '')} {doc.get('texto', '')}"
                doc_embedding = self._get_embedding(doc_text)
                
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((similarity, doc))
            
            # Ordenar por similitud
            similarities.sort(reverse=True)
            
            # Retornar documentos más similares
            return [doc for similarity, doc in similarities[:5]]
            
        except Exception as e:
            logger.error(f"Error encontrando documentos similares: {e}")
            return []
    
    def _get_embedding(self, text: str) -> List[float]:
        """Obtener embedding de texto"""
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error obteniendo embedding: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcular similitud coseno"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2) 