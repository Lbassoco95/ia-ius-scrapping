#!/usr/bin/env python3
"""
🎯 Script de Decisión: AWS vs Google Cloud para SCJN Scraper

Este script ayuda a elegir la mejor plataforma cloud basándose en tus necesidades específicas.
"""

import sys
import os

def print_header():
    """Imprime el encabezado del script"""
    print("=" * 60)
    print("🎯 ELIGE TU PLATAFORMA CLOUD - SCJN SCRAPER")
    print("=" * 60)
    print()

def print_question(question, options):
    """Imprime una pregunta con opciones numeradas"""
    print(f"❓ {question}")
    for i, option in enumerate(options, 1):
        print(f"   {i}. {option}")
    print()

def get_user_choice(max_options):
    """Obtiene la elección del usuario"""
    while True:
        try:
            choice = int(input("👉 Tu elección (número): "))
            if 1 <= choice <= max_options:
                return choice
            else:
                print("❌ Por favor, elige un número válido.")
        except ValueError:
            print("❌ Por favor, ingresa un número.")

def calculate_score(answers):
    """Calcula el puntaje para cada plataforma basado en las respuestas"""
    aws_score = 0
    gcp_score = 0
    
    # Pregunta 1: Experiencia previa
    if answers[0] == 1:  # AWS
        aws_score += 3
    elif answers[0] == 2:  # Google Cloud
        gcp_score += 3
    elif answers[0] == 3:  # Ninguna
        gcp_score += 2  # GCP es más fácil para principiantes
    
    # Pregunta 2: Presupuesto
    if answers[1] == 1:  # Menos de $50/mes
        gcp_score += 2  # GCP es más barato
    elif answers[1] == 2:  # $50-100/mes
        aws_score += 1
        gcp_score += 1
    elif answers[1] == 3:  # Más de $100/mes
        aws_score += 2  # AWS tiene más opciones premium
    
    # Pregunta 3: Escalabilidad
    if answers[2] == 1:  # Básica (1-3 instancias)
        gcp_score += 2
    elif answers[2] == 2:  # Media (3-10 instancias)
        aws_score += 1
        gcp_score += 1
    elif answers[2] == 3:  # Alta (10+ instancias)
        aws_score += 3  # AWS es mejor para escalabilidad
    
    # Pregunta 4: Soporte
    if answers[3] == 1:  # Básico (documentación)
        gcp_score += 2
    elif answers[3] == 2:  # Medio (comunidad)
        aws_score += 1
        gcp_score += 1
    elif answers[3] == 3:  # Premium (24/7)
        aws_score += 3  # AWS tiene mejor soporte empresarial
    
    # Pregunta 5: Tiempo de configuración
    if answers[4] == 1:  # Rápido (1-2 horas)
        gcp_score += 2
    elif answers[4] == 2:  # Medio (2-4 horas)
        aws_score += 1
        gcp_score += 1
    elif answers[4] == 3:  # No importa
        aws_score += 1
        gcp_score += 1
    
    return aws_score, gcp_score

def print_recommendation(aws_score, gcp_score):
    """Imprime la recomendación basada en los puntajes"""
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DE LA EVALUACIÓN")
    print("=" * 60)
    print()
    
    print(f"🏆 AWS Score: {aws_score}/12 puntos")
    print(f"☁️ Google Cloud Score: {gcp_score}/12 puntos")
    print()
    
    if aws_score > gcp_score:
        print("🎯 RECOMENDACIÓN: AWS")
        print("=" * 30)
        print("✅ Ventajas de AWS para tu caso:")
        print("   • Mejor para escalabilidad empresarial")
        print("   • Soporte técnico superior")
        print("   • Más servicios maduros")
        print("   • Script de despliegue automatizado")
        print()
        print("📋 Próximos pasos:")
        print("   1. Crear cuenta AWS")
        print("   2. Configurar AWS CLI")
        print("   3. Ejecutar: ./aws_deployment/deploy.sh")
        print("   4. Seguir guía en: aws_deployment/README.md")
        
    elif gcp_score > aws_score:
        print("🎯 RECOMENDACIÓN: GOOGLE CLOUD")
        print("=" * 35)
        print("✅ Ventajas de Google Cloud para tu caso:")
        print("   • Más fácil de configurar")
        print("   • Costo menor")
        print("   • Interfaz más intuitiva")
        print("   • Mejor para principiantes")
        print()
        print("📋 Próximos pasos:")
        print("   1. Crear proyecto GCP")
        print("   2. Configurar gcloud CLI")
        print("   3. Seguir guía en: google_cloud_deployment/README.md")
        print("   4. Configurar paso a paso")
        
    else:
        print("🎯 RECOMENDACIÓN: EMPATE")
        print("=" * 25)
        print("✅ Ambas plataformas son buenas opciones.")
        print("   Considera estos factores adicionales:")
        print()
        print("🔍 Factores adicionales:")
        print("   • ¿Ya usas otros servicios de Google/AWS?")
        print("   • ¿Tienes preferencia por alguna interfaz?")
        print("   • ¿Necesitas integración con servicios específicos?")
        print()
        print("💡 Sugerencia: Prueba Google Cloud si eres nuevo,")
        print("   o AWS si planeas escalar significativamente.")

def print_detailed_comparison():
    """Imprime una comparación detallada"""
    print("\n" + "=" * 60)
    print("📋 COMPARACIÓN DETALLADA")
    print("=" * 60)
    print()
    
    comparison_data = [
        ("Costo mensual", "~$56/mes", "~$46/mes"),
        ("Facilidad de uso", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"),
        ("Documentación", "⭐⭐⭐⭐⭐", "⭐⭐⭐⭐"),
        ("Soporte técnico", "⭐⭐⭐⭐⭐", "⭐⭐⭐⭐"),
        ("Escalabilidad", "⭐⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"),
        ("Tiempo de configuración", "15-20 min", "20-25 min"),
        ("Scripts automatizados", "✅ Completo", "⚠️ Parcial"),
        ("Interfaz web", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"),
    ]
    
    print(f"{'Aspecto':<25} {'AWS':<15} {'Google Cloud':<15}")
    print("-" * 55)
    for aspect, aws, gcp in comparison_data:
        print(f"{aspect:<25} {aws:<15} {gcp:<15}")
    
    print("\n📖 Para más detalles, consulta: CLOUD_COMPARISON.md")

def main():
    """Función principal"""
    print_header()
    
    # Preguntas para evaluar necesidades
    questions = [
        "¿Tienes experiencia previa con alguna plataforma cloud?",
        "¿Cuál es tu presupuesto mensual aproximado?",
        "¿Qué nivel de escalabilidad necesitas?",
        "¿Qué tipo de soporte requieres?",
        "¿Qué tan rápido necesitas tener el sistema funcionando?"
    ]
    
    options = [
        ["AWS", "Google Cloud", "Ninguna experiencia"],
        ["Menos de $50/mes", "$50-100/mes", "Más de $100/mes"],
        ["Básica (1-3 instancias)", "Media (3-10 instancias)", "Alta (10+ instancias)"],
        ["Básico (documentación)", "Medio (comunidad)", "Premium (24/7)"],
        ["Rápido (1-2 horas)", "Medio (2-4 horas)", "No importa"]
    ]
    
    answers = []
    
    print("🤔 Vamos a evaluar tus necesidades específicas...")
    print()
    
    # Obtener respuestas del usuario
    for i, question in enumerate(questions):
        print_question(question, options[i])
        choice = get_user_choice(len(options[i]))
        answers.append(choice)
        print()
    
    # Calcular puntajes
    aws_score, gcp_score = calculate_score(answers)
    
    # Mostrar recomendación
    print_recommendation(aws_score, gcp_score)
    
    # Preguntar si quiere ver comparación detallada
    print("\n" + "=" * 60)
    print("📖 ¿Quieres ver una comparación detallada?")
    print("   1. Sí, mostrar comparación")
    print("   2. No, terminar")
    print()
    
    choice = get_user_choice(2)
    if choice == 1:
        print_detailed_comparison()
    
    print("\n" + "=" * 60)
    print("🎉 ¡Gracias por usar el asistente de decisión!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0) 