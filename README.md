# REASONING_LLM

# Proyecto Procesamiento del Lenguaje Natural 2 (FIUBA): LLM con Cadena de Pensamiento Simulada para Resolución de Problemas Complejos

**Curso:** Procesamiento del Lenguaje Natural 2
**Institución:** Facultad de Ingeniería, Universidad de Buenos Aires (FIUBA)
**Autor/a:** Gustavo Julián Rivas
**Fecha:** 25 de abril de 2025

---

## 1. Resumen del Proyecto

Este proyecto consiste en una Prueba de Concepto (PoC) que explora la implementación de una **cadena de pensamiento (Chain of Thought - CoT)** simulada utilizando un Modelo de Lenguaje Grande (LLM) para abordar la resolución de problemas complejos que requieren múltiples pasos lógicos o de cálculo.

El sistema recibe una pregunta compleja en lenguaje natural, la descompone en sub-tareas, ejecuta cada una de ellas secuencialmente (utilizando el LLM para el razonamiento y cálculo intermedio), y finalmente sintetiza una respuesta final. La aplicación, desarrollada con Streamlit, visualiza dinámicamente este proceso paso a paso, ofreciendo transparencia sobre el "razonamiento" simulado del modelo. Adicionalmente, se realiza un seguimiento del consumo de tokens y se estima el costo asociado al uso de la API de OpenAI.

## 2. Objetivos

*   Implementar un marco de trabajo para simular una cadena de pensamiento (CoT) utilizando llamadas secuenciales a un LLM (GPT-4o).
*   Demostrar la capacidad de un LLM para descomponer un problema complejo en sub-tareas manejables (planificación).
*   Evaluar la habilidad del LLM para ejecutar pasos de cálculo intermedios siguiendo instrucciones precisas y utilizando contexto de pasos anteriores.
*   Desarrollar un "agente" sintetizador (basado en LLM) capaz de consolidar resultados parciales en una respuesta final coherente y formateada.
*   Proporcionar una interfaz de usuario interactiva (Streamlit) que visualice el proceso de razonamiento paso a paso.
*   Cuantificar el uso de recursos computacionales (tokens) y estimar el costo asociado a este enfoque de razonamiento simulado.

## 3. Metodología y Enfoque Técnico

La solución se basa en un **enfoque de agentes simulados**, donde diferentes instancias de llamadas al LLM, guiadas por prompts específicos (ingeniería de prompts), desempeñan roles distintos dentro de un flujo orquestado:

1.  **Agente Descompositor:** Recibe la pregunta compleja inicial y genera un plan detallado, numerado y secuencial, indicando las operaciones y variables clave para cada paso.
2.  **Agente Verificador del Plan:** Evalúa la lógica, completitud y corrección del plan generado por el descomponitor.
3.  **Agente Solucionador:** Ejecuta cada paso individual del plan. Recibe la descripción del paso actual y el contexto acumulado (pregunta original, plan, resultados de pasos anteriores). Se le instruye explícitamente para mostrar su trabajo de cálculo y mantener alta precisión. *En esta implementación, el LLM realiza los cálculos intermedios.*
4.  **Agente Sintetizador (Auditor Final):** Recibe la pregunta original, el plan y todos los resultados parciales detallados. Su función es extraer la información relevante, realizar los cálculos finales (ej. aplicación de descuentos, redondeo) y formatear la respuesta final de acuerdo a los requerimientos explícitos de la pregunta original.

Este flujo secuencial simula una cadena de pensamiento, donde la salida de una etapa alimenta la siguiente. La interfaz de Streamlit se actualiza después de cada etapa para reflejar el progreso.

## 4. Arquitectura y Tecnologías

*   **Lenguaje:** Python 3.x
*   **Interfaz de Usuario:** Streamlit (`streamlit`)
*   **Modelo de Lenguaje:** OpenAI GPT-4o (accedido vía API)
*   **Cliente API:** Biblioteca oficial `openai`
*   **Bibliotecas Auxiliares:** `os`, `re`, `json`, `traceback`, `math`

## 5. Recursos Adicionales

*   **Video Demostrativo:** Se incluye una breve demostración en video del funcionamiento de la aplicación en la carpeta `/video`.
*   **Casos de Prueba:** La carpeta `/test_cases` contiene el archivo `prompts_ejemplo.txt` con ejemplos de preguntas complejas utilizadas durante las pruebas y el desarrollo.

## 6. Requisitos Previos

*   Python (versión 3.9 o superior recomendada).
*   Acceso a internet.
*   Una clave API válida de OpenAI.

## 7. Instalación

1.  **Clonar o descargar el repositorio.**
2.  **Navegar al directorio del proyecto** en una terminal.
3.  **Crear un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # Activar:
    #   Windows: venv\Scripts\activate
    #   macOS/Linux: source venv/bin/activate
    ```
4.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Si `requirements.txt` no está presente, instalar manualmente):*
    ```bash
    pip install streamlit openai
    ```

## 8. Configuración

*   **API Key de OpenAI:** Es **obligatorio** configurar su clave API de OpenAI como una variable de entorno llamada `OPENAI_API_KEY`.
    *   **Linux/macOS:** `export OPENAI_API_KEY="tu_sk-..."`
    *   **Windows (cmd):** `set OPENAI_API_KEY=tu_sk-...`
    *   **Windows (PowerShell):** `$env:OPENAI_API_KEY="tu_sk-..."`
    *   *(Asegúrese de ejecutar el comando en la misma sesión de terminal donde ejecutará Streamlit, o configúrela de forma persistente en su sistema operativo).*

## 9. Ejecución

1.  Asegúrese de que el entorno virtual (si usa uno) esté activado.
2.  Verifique que la variable de entorno `OPENAI_API_KEY` esté definida.
3.  Desde el directorio raíz del proyecto, ejecute:
    ```bash
    streamlit run reasoning_app.py
    ```
    *(Reemplace `reasoning_app.py` con el nombre real de su archivo principal si es diferente)*.
4.  La aplicación se abrirá en su navegador web predeterminado.

## 10. Uso de la Interfaz

1.  La aplicación carga con una pregunta compleja de ejemplo en el área de texto. Puede modificarla o ingresar una nueva.
2.  Presione el botón "**🚀 Iniciar Razonamiento**".
3.  La interfaz mostrará un indicador de estado mientras el sistema procesa cada etapa (Descomposición, Verificación, Solución de Pasos, Síntesis).
4.  La sección "**🤔 Cadena de Pensamiento**" se actualizará dinámicamente:
    *   Se mostrará el plan generado y su revisión.
    *   Los resultados detallados de cada paso aparecerán secuencialmente. Observe el formato matemático renderizado.
5.  Una vez completado, se mostrará la "**✅ Respuesta Final Sintetizada**".
6.  El reporte de "**📊 Tokens y Costo Estimado**" estará disponible al final.
7.  Utilice el botón "**🔄 Nueva Consulta**" para limpiar los resultados y realizar otra prueba.

## 11. Limitaciones y Trabajo Futuro

*   **Precisión del LLM:** Aunque se usa GPT-4o y prompts detallados, la precisión de los cálculos intermedios realizados por el LLM no está 100% garantizada. Errores sutiles pueden ocurrir.
*   **Dependencia del Plan:** La calidad de la respuesta final depende fuertemente de la calidad del plan generado en la primera etapa. Un plan incorrecto o incompleto llevará a resultados erróneos.
*   **Manejo de Errores:** La detección y recuperación de errores es básica. Un sistema más robusto podría incluir reintentos o mecanismos de auto-corrección.
*   **Generalización:** Si bien el marco es genérico, la efectividad para problemas muy diferentes al ejemplo dependerá de la capacidad del LLM para generar planes adecuados y ejecutar pasos variados.
*   **Optimización de Costos/Tokens:** El enfoque multi-llamada puede consumir una cantidad significativa de tokens.
*   **Trabajo Futuro:**
    *   Implementar el **Enfoque Híbrido (Calculador Python):** Separar la ejecución de cálculos matemáticos a código Python para garantizar precisión absoluta, usando el LLM solo para planificación y extracción de datos (como se discutió previamente).
    *   **Mecanismos de Re-planificación:** Permitir que el sistema revise y corrija el plan si un paso falla o la revisión inicial es negativa.
    *   **Memoria/Estado Más Avanzado:** Incorporar memoria para manejar conversaciones o problemas que requieran recordar información a más largo plazo.

---