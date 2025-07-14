#!/usr/bin/env python3
"""
Interfaz de chat para consultas sobre tesis de la SCJN
"""

import sys
import os
import json
import logging
from typing import List, Dict, Optional

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.models import get_session, Tesis, Consulta
from src.analysis.ai_analyzer import AIAnalyzer
from src.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatInterface:
    """Interfaz de chat para consultas sobre tesis"""
    
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        self.session = get_session()
        
    def __del__(self):
        if self.session:
            self.session.close()
    
    def start_chat(self):
        """Iniciar interfaz de chat"""
        print("=" * 60)
        print("🤖 CHAT DE CONSULTAS - TESIS SCJN")
        print("=" * 60)
        print("Escribe 'salir' para terminar")
        print("Escribe 'ayuda' para ver comandos disponibles")
        print("=" * 60)
        
        while True:
            try:
                # Obtener pregunta del usuario
                user_input = input("\n💬 Tú: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print("👋 ¡Hasta luego!")
                    break
                
                if user_input.lower() == 'ayuda':
                    self.show_help()
                    continue
                
                # Procesar pregunta
                response = self.process_question(user_input)
                print(f"\n🤖 Asistente: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                logger.error(f"Error en chat: {e}")
                print(f"\n❌ Error: {e}")
    
    def process_question(self, question: str) -> str:
        """Procesar pregunta del usuario"""
        try:
            # Buscar documentos relevantes
            relevant_docs = self.find_relevant_documents(question)
            
            if not relevant_docs:
                return "No encontré documentos relevantes para tu pregunta. ¿Podrías reformularla?"
            
            # Generar respuesta usando IA
            response = self.ai_analyzer.answer_question(question, relevant_docs)
            
            # Guardar consulta en base de datos
            self.save_consultation(question, response, relevant_docs)
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando pregunta: {e}")
            return f"Error procesando tu pregunta: {e}"
    
    def find_relevant_documents(self, question: str, limit: int = 5) -> List[Dict]:
        """Encontrar documentos relevantes para la pregunta"""
        try:
            # Buscar en base de datos
            query = self.session.query(Tesis)
            
            # Búsqueda por palabras clave en título y texto
            keywords = question.lower().split()
            for keyword in keywords:
                if len(keyword) > 3:  # Solo palabras significativas
                    query = query.filter(
                        (Tesis.titulo.contains(keyword)) |
                        (Tesis.texto.contains(keyword)) |
                        (Tesis.resumen.contains(keyword))
                    )
            
            # Obtener resultados
            results = query.limit(limit).all()
            
            # Convertir a diccionarios
            documents = []
            for tesis in results:
                doc = {
                    'id': tesis.id,
                    'scjn_id': tesis.scjn_id,
                    'titulo': tesis.titulo,
                    'texto': tesis.texto,
                    'resumen': tesis.resumen,
                    'categorias': json.loads(tesis.categorias) if tesis.categorias else [],
                    'conceptos_clave': json.loads(tesis.conceptos_clave) if tesis.conceptos_clave else [],
                    'relevancia': tesis.relevancia
                }
                documents.append(doc)
            
            # Si no hay resultados, buscar por similitud semántica
            if not documents:
                all_tesis = self.session.query(Tesis).limit(100).all()
                all_docs = []
                for tesis in all_tesis:
                    all_docs.append({
                        'id': tesis.id,
                        'scjn_id': tesis.scjn_id,
                        'titulo': tesis.titulo,
                        'texto': tesis.texto,
                        'resumen': tesis.resumen
                    })
                
                documents = self.ai_analyzer.find_similar_documents(question, all_docs)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error buscando documentos relevantes: {e}")
            return []
    
    def save_consultation(self, question: str, response: str, documents: List[Dict]):
        """Guardar consulta en base de datos"""
        try:
            consultation = Consulta(
                pregunta=question,
                respuesta=response,
                documentos_referenciados=json.dumps([doc.get('scjn_id') for doc in documents], ensure_ascii=False),
                usuario="usuario_chat"
            )
            
            self.session.add(consultation)
            self.session.commit()
            
        except Exception as e:
            logger.error(f"Error guardando consulta: {e}")
            self.session.rollback()
    
    def show_help(self):
        """Mostrar ayuda"""
        help_text = """
📋 COMANDOS DISPONIBLES:

• Preguntas generales:
  - "¿Qué dice la jurisprudencia sobre amparo?"
  - "¿Cuáles son los criterios sobre derechos humanos?"
  - "¿Qué establece la SCJN sobre propiedad?"

• Búsquedas específicas:
  - "Busca tesis sobre derecho laboral"
  - "Encuentra jurisprudencia sobre procedimiento penal"
  - "¿Hay tesis sobre responsabilidad civil?"

• Consultas por categoría:
  - "Muestra tesis de derecho constitucional"
  - "¿Qué hay sobre derecho administrativo?"

• Información del sistema:
  - "¿Cuántas tesis tienes?"
  - "¿Cuáles son las más relevantes?"

💡 TIPS:
• Sé específico en tus preguntas
• Usa términos jurídicos cuando sea posible
• Puedes preguntar sobre conceptos específicos
        """
        print(help_text)
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas del sistema"""
        try:
            total_tesis = self.session.query(Tesis).count()
            tesis_analizadas = self.session.query(Tesis).filter_by(analizado=True).count()
            total_consultas = self.session.query(Consulta).count()
            
            # Categorías más comunes
            categorias_query = self.session.query(Tesis.categorias).filter(Tesis.categorias.isnot(None))
            categorias = []
            for result in categorias_query:
                if result[0]:
                    categorias.extend(json.loads(result[0]))
            
            from collections import Counter
            categorias_count = Counter(categorias)
            top_categorias = categorias_count.most_common(5)
            
            return {
                'total_tesis': total_tesis,
                'tesis_analizadas': tesis_analizadas,
                'total_consultas': total_consultas,
                'top_categorias': top_categorias
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

def main():
    """Función principal"""
    try:
        # Validar configuración
        Config.validate()
        
        # Crear interfaz de chat
        chat = ChatInterface()
        
        # Mostrar estadísticas iniciales
        stats = chat.get_statistics()
        if stats:
            print(f"📊 Estadísticas del sistema:")
            print(f"   • Total de tesis: {stats.get('total_tesis', 0)}")
            print(f"   • Tesis analizadas: {stats.get('tesis_analizadas', 0)}")
            print(f"   • Consultas realizadas: {stats.get('total_consultas', 0)}")
            print()
        
        # Iniciar chat
        chat.start_chat()
        
    except Exception as e:
        logger.error(f"Error iniciando chat: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 