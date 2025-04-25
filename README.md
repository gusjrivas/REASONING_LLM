# REASONING_LLM

# 🧠💡 LLM con Cadena de Pensamiento Detallada (PoC)

Este proyecto es una Prueba de Concepto (PoC) desarrollada en el marco del Posgrado de IA de la FIUBA. Demuestra cómo un Modelo de Lenguaje Grande (LLM) como GPT-4o puede ser guiado para "razonar" paso a paso y resolver preguntas complejas, mostrando su proceso de pensamiento al usuario.

**El Problema:** Los LLMs a veces fallan en problemas que requieren múltiples pasos de cálculo o lógica. ¿Cómo podemos hacer que muestren su trabajo y mejorar su precisión?

**La Solución:** Esta aplicación implementa una **cadena de pensamiento simulada**:

1.  **Descomposición:** El LLM recibe la pregunta compleja y la divide en un plan de pasos lógicos.
2.  **Verificación (Opcional):** Otro llamado al LLM revisa si el plan es coherente.
3.  **Ejecución Paso a Paso:** El LLM ejecuta cada paso del plan, mostrando sus cálculos o análisis intermedios. Usa el contexto de los pasos anteriores.
4.  **Síntesis Final:** Un último llamado al LLM revisa todos los resultados intermedios y genera la respuesta final, siguiendo el formato solicitado.

La interfaz, construida con **Streamlit**, muestra dinámicamente cada etapa del proceso, permitiendo al usuario ver cómo el LLM "piensa" para llegar a la solución. Además, calcula y muestra el uso de tokens y un costo estimado en USD para la ejecución.

## Tecnologías

*   **Python**
*   **Streamlit:** Para la interfaz web interactiva.
*   **OpenAI API:** Para acceder a modelos como GPT-4o.
*   **Biblioteca `openai` de Python:** Para interactuar con la API.

## Requisitos Previos

*   Python 3.9 o superior.
*   Una clave API de OpenAI.

## Instalación

1.  **Clona el repositorio (si aplica) o guarda el código:** Guarda el código principal como `reasoning_app.py` (o el nombre que prefieras).
2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # Windows: venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate
    ```
3.  **Instala las dependencias:**
    ```bash
    pip install streamlit openai
    ```

## Configuración

1.  **Configura tu API Key de OpenAI:** La forma más segura es establecer una variable de entorno llamada `OPENAI_API_KEY` con tu clave secreta.
    *   **Linux/macOS:** `export OPENAI_API_KEY="tu_sk-..."`
    *   **Windows (cmd):** `set OPENAI_API_KEY=tu_sk-...`
    *   **Windows (PowerShell):** `$env:OPENAI_API_KEY="tu_sk-..."`

## Cómo Ejecutar la Aplicación

1.  Abre tu terminal o línea de comandos.
2.  Navega hasta el directorio donde guardaste el archivo `.py`.
3.  Asegúrate de que la variable de entorno `OPENAI_API_KEY` esté configurada en esa sesión.
4.  Ejecuta el siguiente comando:
    ```bash
    streamlit run reasoning_app.py
    ```
    *(Reemplaza `reasoning_app.py` si guardaste el archivo con otro nombre)*.
5.  Se abrirá automáticamente una pestaña en tu navegador web con la aplicación.

## Cómo Usar la Interfaz

1.  Verás un área de texto con una pregunta compleja de ejemplo (cálculo de construcción). Puedes modificarla o escribir la tuya.
2.  Haz clic en el botón "**🚀 Iniciar Razonamiento**".
3.  Observa la sección "**🤔 Cadena de Pensamiento**":
    *   Aparecerá el plan generado por el LLM.
    *   Luego, los resultados de cada paso se irán mostrando uno por uno a medida que el LLM los calcula.
    *   Finalmente, se mostrará la respuesta final sintetizada.
    *   Podrás expandir la sección "**📊 Ver Reporte de Tokens y Costo Estimado**" para ver el detalle del uso de la API.
4.  Una vez terminado, puedes hacer clic en "**🔄 Nueva Consulta**" para limpiar los resultados y empezar de nuevo.

¡Explora cómo el LLM aborda diferentes problemas complejos!