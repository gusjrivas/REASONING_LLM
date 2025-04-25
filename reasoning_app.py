# reasoning_app_final_merged_cost.py

import os
import re
import json
import traceback
from typing import Optional, Dict, Tuple, List, Any
import math

import streamlit as st
from openai import OpenAI, BadRequestError, RateLimitError

# --- 1. Configuración Inicial y Constantes ---
MODEL_NAME = "gpt-4o-mini" # Modelo potente recomendado
PI_VALUE = math.pi
PI_DISPLAY = "π"

# --- TARIFAS GPT-4o-mini (USD por 1 Millón de Tokens - Verificar siempre!) ---
RATE_INPUT_GPT4O = 0.15
RATE_OUTPUT_GPT4O = 0.60

# --- FUNCIÓN CACHEADA PARA INICIALIZAR CLIENTE ---
@st.cache_resource(show_spinner="Inicializando conexión con OpenAI...")
def init_openai_client():
    """Inicializa y devuelve el cliente OpenAI."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: raise ValueError("Variable de entorno OPENAI_API_KEY no encontrada.")
    try:
        client = OpenAI(api_key=api_key)
        client.models.list(); print("Cliente OpenAI inicializado.")
        return client
    except Exception as e: raise ConnectionError(f"No se pudo conectar/verificar OpenAI: {e}")

# --- 2. Funciones de Lógica de Razonamiento (AGENTES LLM CON PROMPTS MEJORADOS) ---

def call_llm_with_usage(client: OpenAI, model_name: str, messages: List[Dict], purpose: str = "", temperature: float = 0.1) -> Tuple[Optional[str], Optional[object]]:
    """Realiza una llamada al LLM y devuelve contenido y objeto 'usage'."""
    print(f"\n--- LLM Call ({purpose} | Temp: {temperature}) ---")
    if not client: return "Error: Cliente LLM no proporcionado.", None
    try:
        response = client.chat.completions.create(model=model_name, messages=messages, temperature=temperature)
        content = response.choices[0].message.content
        usage = response.usage
        print(f"Token Usage ({purpose}): Prompt={usage.prompt_tokens}, Completion={usage.completion_tokens}")
        return content, usage
    except RateLimitError as rle: print(f"!!! ERROR RateLimitError: {rle}"); return f"Error Límite Tasa: {rle}", None
    except BadRequestError as bre: print(f"!!! ERROR BadRequest: {bre}"); return f"Error API: {bre}", None
    except Exception as e: print(f"!!! ERROR LLM Call: {e}"); traceback.print_exc(); return f"Error inesperado: {e}", None

# (Las definiciones de agente_descompositor, agente_verificador_plan,
# agente_solucionador, agente_sintetizador permanecen IGUAL que en
# la versión anterior "LLM Calculator" con prompts ultra-detallados)
def agente_descompositor(client: OpenAI, model_name: str, pregunta_compleja: str) -> Tuple[Optional[str], Optional[object]]:
    messages = [
        {"role": "system", "content": f"""Eres un ingeniero de planificación... (Instrucciones Detalladas)... Usa {PI_DISPLAY} ≈ {PI_VALUE}... Responde únicamente con la lista numerada de pasos."""}, # Omitido
        {"role": "user", "content": f"Descompón la siguiente pregunta en pasos de cálculo detallados:\n\n{pregunta_compleja}"}
    ]
    return call_llm_with_usage(client, model_name, messages, purpose="Descomposición Ultra-Detallada", temperature=0.3)

def agente_verificador_plan(client: OpenAI, model_name: str, pregunta_original: str, plan_propuesto: str) -> Tuple[Optional[str], Optional[object]]:
    messages = [
        {"role": "system", "content": "Eres un revisor lógico... Responde brevemente con tu evaluación o 'Plan OK'."}, # Omitido
        {"role": "user", "content": f"Problema Original:\n{pregunta_original}\n\nPlan Propuesto:\n{plan_propuesto}\n\nEvaluación Crítica del Plan:"}
    ]
    return call_llm_with_usage(client, model_name, messages, purpose="Verificación Plan", temperature=0.1)

def agente_solucionador(client: OpenAI, model_name: str, paso_actual: str, contexto_completo: str) -> Tuple[Optional[str], Optional[object]]:
    system_prompt = f"""Eres una calculadora/analista extremadamente preciso... Usa {PI_DISPLAY} ≈ {PI_VALUE}... MUESTRA TU TRABAJO... Responde únicamente con la ejecución detallada y el resultado de ESTE PASO.""" # Omitido
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Contexto Completo (Pregunta, Plan, Resultados Previos):\n{contexto_completo}\n\n--- TAREA ACTUAL ---\nEjecuta y detalla este paso del plan: {paso_actual}"}
    ]
    purpose_id = os.urandom(3).hex()
    return call_llm_with_usage(client, model_name, messages, purpose=f"Solución Paso Detallada {purpose_id}", temperature=0.05)

def agente_sintetizador(client: OpenAI, model_name: str, pregunta_original: str, plan: str, resultados_parciales: dict) -> Tuple[Optional[str], Optional[object]]:
    contexto_respuestas = f"Plan Seguido:\n{plan}\n\nResultados Detallados...\n" + "\n".join([f"- {k}:\n  {v}" for k, v in resultados_parciales.items()])
    final_format_instruction = "Proporciona únicamente el valor numérico final redondeado a 2 decimales, precedido por 'Costo Total:'. Ejemplo: 'Costo Total: 12345.67'"
    if "costo total" not in pregunta_original.lower(): final_format_instruction = "Resume la respuesta final..."
    messages = [
        {"role": "system", "content": f"""Eres un experto sintetizador y auditor final... Realiza cualquier cálculo FINAL necesario... Responde ÚNICAMENTE según el formato solicitado... {final_format_instruction} No añadas explicaciones..."""}, # Omitido
        {"role": "user", "content": f"Pregunta Original:\n{pregunta_original}\n\n{contexto_respuestas}\n\n--- INSTRUCCIÓN FINAL ---\nActúa como Auditor Final: Revisa, extrae, calcula y proporciona la respuesta final EXACTAMENTE como se pide."}
    ]
    return call_llm_with_usage(client, model_name, messages, purpose="Auditoría y Síntesis Final", temperature=0.05)


# --- FUNCIÓN DE ORQUESTACIÓN (MODIFICADA PARA CALCULAR COSTO) ---
def proceso_razonamiento_llm_calculator(client: OpenAI, model_name: str, pregunta_usuario: str) -> Dict[str, Any]:
    """Orquesta flujo LLM y calcula costo."""
    print(f"\n--- Iniciando proceso LLM Calculator ---")
    if not client: return {"error_message": "Error Crítico: Cliente LLM no disponible."}
    # Inicializar diccionario de resultados con campos de costo
    results = {
        "pregunta_original": pregunta_usuario, "plan": "N/A", "plan_revision": "N/A",
        "resultados_parciales": {}, "respuesta_final": "N/A",
        "token_report": {"prompt": 0, "reasoning": 0, "output": 0, "total_calc": 0, "cost_input": 0.0, "cost_output": 0.0, "cost_total": 0.0},
        "error_message": None
    }
    prompt_tokens = 0; reasoning_tokens = 0; output_tokens = 0; error_critico = False

    # --- Ejecución de Etapas (igual que antes, acumulando tokens) ---
    # 1. Descomposición
    plan_str, usage_decomp = agente_descompositor(client, model_name, pregunta_usuario)
    if usage_decomp is None or not plan_str or ("Error" in plan_str): results["error_message"] = f"Fallo Descomp: {plan_str}"; return results
    results["plan"] = plan_str; prompt_tokens = usage_decomp.prompt_tokens; reasoning_tokens += usage_decomp.completion_tokens; print(f"\nPlan:\n{plan_str}")

    # 2. Verificación Plan
    revision_plan, usage_verif = agente_verificador_plan(client, model_name, pregunta_usuario, plan_str)
    if usage_verif: reasoning_tokens += usage_verif.prompt_tokens + usage_verif.completion_tokens; results["plan_revision"] = revision_plan; print(f"Revisión: {revision_plan}")
    if revision_plan and "error" in revision_plan.lower() and "ok" not in revision_plan.lower(): print("Adv: Plan podría ser incorrecto.")

    # 3. Solución Pasos
    pasos = [line.strip() for line in plan_str.split('\n') if re.match(r'^\s*[\d]+[.)]?\s+', line)]
    if not pasos: pasos = [line.strip() for line in plan_str.split('\n') if line.strip()] or [plan_str]
    contexto_acumulado = f"Pregunta Original: {pregunta_usuario}\nPlan General:\n{plan_str}\n\n--- Resultados Pasos Anteriores ---\n"
    results["resultados_parciales"] = {}
    for i, paso in enumerate(pasos):
        if error_critico: break
        print(f"\n--- Ejecutando Paso {i+1}: {paso[:80]}... ---")
        contexto_actual_paso = contexto_acumulado + f"\n---\nTarea Actual: Ejecutar y detallar el paso '{paso}'"
        respuesta_paso, usage_paso = agente_solucionador(client, model_name, paso, contexto_actual_paso)
        paso_key = f"Paso {i+1}: {paso}"
        results["resultados_parciales"][paso_key] = respuesta_paso
        if usage_paso is None or not respuesta_paso or ("Error API" in respuesta_paso or "Error inesperado" in respuesta_paso):
            print(f"!!! Error Crítico Paso {i+1}: {respuesta_paso}"); error_critico = True
            contexto_acumulado += f"{paso_key}: {respuesta_paso} (ERROR)\n"; break
        else:
            reasoning_tokens += usage_paso.prompt_tokens + usage_paso.completion_tokens
            contexto_acumulado += f"{paso_key}:\n{respuesta_paso}\n"

    # 4. Síntesis Final
    if not error_critico:
        print(f"\n--- Sintetizando Respuesta Final ---")
        respuesta_final, usage_sint = agente_sintetizador(
            client, model_name, pregunta_original=pregunta_usuario, plan=results["plan"],
            resultados_parciales=results["resultados_parciales"]
        )
        if usage_sint is None or not respuesta_final or ("Error" in respuesta_final):
             error_critico = True; synthesis_error = f"Fallo en Síntesis: {respuesta_final}"
             print(f"!!! {synthesis_error}"); results["respuesta_final"] = synthesis_error
             if results["error_message"] is None: results["error_message"] = synthesis_error
        else:
             results["respuesta_final"] = respuesta_final
             reasoning_tokens += usage_sint.prompt_tokens
             output_tokens = usage_sint.completion_tokens
    else: results["respuesta_final"] = "No se pudo generar la respuesta final por errores previos."; output_tokens = 0

    # --- 5. Calcular Costos y Poblar Reporte Final ---
    cost_input = prompt_tokens * (RATE_INPUT_GPT4O / 1_000_000)
    cost_output = (reasoning_tokens + output_tokens) * (RATE_OUTPUT_GPT4O / 1_000_000)
    cost_total = cost_input + cost_output

    results["token_report"] = {
        "prompt": prompt_tokens, "reasoning": reasoning_tokens, "output": output_tokens,
        "total_calc": prompt_tokens + reasoning_tokens + output_tokens,
        "cost_input": cost_input, "cost_output": cost_output, "cost_total": cost_total
    }
    print(f"\n--- Proceso Completado ---")
    return results


# --- Función Helper para formato Math ---
def format_math(text: Optional[str]) -> str:
    """Reemplaza delimitadores \( \) por $ $ para renderizado LaTeX en Streamlit."""
    if text is None: return ""
    text = text.replace('\\( ', '$').replace(' \\)', '$')
    text = text.replace('\\(', '$').replace('\\)', '$')
    return text

# --- Interfaz Streamlit (CON LÓGICA DE ETAPAS Y VISUALIZACIÓN MEJORADA) ---
def run_streamlit_app():
    """Ejecuta la interfaz y la lógica de etapas con visualización dinámica."""

    # --- Configuración de Página (PRIMERO) ---
    st.set_page_config(page_title="LLM Razonamiento Experto", layout="wide")

    # --- Inicializar Cliente (DESPUÉS de set_page_config) ---
    try:
        llm_client = init_openai_client()
        if llm_client is None: raise ValueError("Cliente OpenAI no inicializado.")
    except Exception as e:
        st.error(f"Error crítico inicializando OpenAI: {e}")
        st.stop()

    # --- Título y Descripción ---
    model_to_use = MODEL_NAME
    st.title("🧠💡 LLM con Cadena de Pensamiento Experta")
    st.caption(f"Usando {model_to_use}. Observa el proceso paso a paso con fórmulas y cálculos.")

    # --- Inicializar Session State ---
    if "app_state" not in st.session_state:
        st.session_state.app_state = {
            "current_stage": "idle", "question": "", "plan": None, "plan_revision": None,
            "steps": [], "current_step_index": 0, "partial_results": {},
            "final_answer": None,
            "token_report": {"prompt": 0, "reasoning": 0, "output": 0, "total_calc": 0, "cost_input": 0.0, "cost_output": 0.0, "cost_total": 0.0},
            "error_message": None, "processing_lock": False
        }
    # Mantener la pregunta en la caja entre reruns
    if "current_question_in_box" not in st.session_state: st.session_state.current_question_in_box = ""

    # --- Función para Limpiar Estado ---
    def clear_state_for_new_query():
        # Guardar pregunta actual antes de limpiar
        current_q = st.session_state.app_state.get("question", "")
        st.session_state.app_state = {
            "current_stage": "idle", "question": current_q, # Mantener la pregunta
            "plan": None, "plan_revision": None, "steps": [], "current_step_index": 0,
            "partial_results": {}, "final_answer": None,
            "token_report": {"prompt": 0, "reasoning": 0, "output": 0, "total_calc": 0, "cost_input": 0.0, "cost_output": 0.0, "cost_total": 0.0},
            "error_message": None, "processing_lock": False
        }

    # --- Área de Texto ---
    default_question = f"""Calcula el costo total de construcción... (igual que antes)...""" # Omitido
    # Usar valor del estado o el default si está vacío
    st.session_state.current_question_in_box = st.session_state.app_state.get("question", default_question)
    question_input = st.text_area(
        "Introduce tu pregunta compleja aquí:",
        value=st.session_state.current_question_in_box,
        height=300,
        key="user_question_area"
    )
    # Actualizar estado si cambia
    st.session_state.app_state["question"] = question_input

    # --- Botones de Control ---
    col1, col2 = st.columns([1.5, 5])
    with col1:
        start_disabled = st.session_state.app_state["current_stage"] not in ["idle", "done", "error"] or st.session_state.app_state["processing_lock"]
        if st.button("🚀 Iniciar Razonamiento", key="start_btn", disabled=start_disabled):
            if question_input and question_input.strip():
                clear_state_for_new_query() # Limpiar resultados anteriores
                st.session_state.app_state["question"] = question_input # Guardar pregunta actual
                st.session_state.app_state["current_stage"] = "decomposing"
                st.session_state.app_state["processing_lock"] = True
                st.rerun()
            else: st.warning("Introduce una pregunta válida.")
    with col2:
        # Mostrar botón Nueva Consulta solo si el proceso ha terminado (done o error)
        if st.session_state.app_state["current_stage"] in ["done", "error"]:
             if st.button("🔄 Nueva Consulta", key="clear_btn", disabled=st.session_state.app_state["processing_lock"]):
                  clear_state_for_new_query()
                  st.session_state.app_state["question"] = "" # Limpiar área de texto
                  st.rerun()

    # --- Lógica de Ejecución por Etapas ---
    current_stage = st.session_state.app_state["current_stage"]
    print(f"--- Current Stage: {current_stage} ---")

    status_placeholder = st.empty()
    results_container = st.container() # Usar un contenedor principal para resultados
    trigger_next_stage = False # Flag para controlar rerun

    try:
        # Solo ejecutar si está en una etapa de procesamiento activa
        if current_stage not in ["idle", "done", "error"]:
            st.session_state.app_state["processing_lock"] = True # Asegurar bloqueo

            if current_stage == "decomposing":
                status_placeholder.info("📝 Descomponiendo la pregunta...")
                plan_str, usage_decomp = agente_descompositor(llm_client, model_to_use, st.session_state.app_state["question"])
                if usage_decomp and plan_str and not ("Error" in plan_str):
                    st.session_state.app_state["plan"] = plan_str
                    st.session_state.app_state["token_report"]["prompt"] = usage_decomp.prompt_tokens
                    st.session_state.app_state["token_report"]["reasoning"] += usage_decomp.completion_tokens
                    st.session_state.app_state["current_stage"] = "verifying"
                    trigger_next_stage = True
                else: raise ValueError(f"Fallo en Descomposición: {plan_str}")

            elif current_stage == "verifying":
                status_placeholder.info("🧐 Verificando el plan...")
                revision_plan, usage_verif = agente_verificador_plan(llm_client, model_to_use, st.session_state.app_state["question"], st.session_state.app_state["plan"])
                if usage_verif:
                    st.session_state.app_state["plan_revision"] = revision_plan
                    st.session_state.app_state["token_report"]["reasoning"] += usage_verif.prompt_tokens + usage_verif.completion_tokens
                    plan_to_parse = st.session_state.app_state["plan"] or ""
                    pasos = [line.strip() for line in plan_to_parse.split('\n') if re.match(r'^\s*[\d]+[.)]?\s+', line)]
                    if not pasos: pasos = [line.strip() for line in plan_to_parse.split('\n') if line.strip()] or [plan_to_parse]
                    st.session_state.app_state["steps"] = pasos
                    st.session_state.app_state["current_step_index"] = 0
                    st.session_state.app_state["partial_results"] = {}
                    if not pasos: st.session_state.app_state["current_stage"] = "synthesizing"
                    else: st.session_state.app_state["current_stage"] = f"solving_step_0"
                    trigger_next_stage = True
                else: raise ValueError(f"Fallo en Verificación: {revision_plan}")

            elif current_stage.startswith("solving_step_"):
                step_index = st.session_state.app_state["current_step_index"]
                if step_index < len(st.session_state.app_state["steps"]):
                    current_step_desc = st.session_state.app_state["steps"][step_index]
                    status_placeholder.info(f"▶️ Resolviendo Paso {step_index + 1}/{len(st.session_state.app_state['steps'])}...")

                    contexto_acumulado = f"Pregunta Original: {st.session_state.app_state['question']}\nPlan:\n{st.session_state.app_state['plan']}\n\nResultados Previos:\n"
                    contexto_acumulado += "\n".join([f"- {k}:\n  {v}" for k, v in st.session_state.app_state["partial_results"].items()])
                    contexto_actual_paso = contexto_acumulado + f"\n---\nTarea Actual: {current_step_desc}"

                    respuesta_paso, usage_paso = agente_solucionador(llm_client, model_to_use, current_step_desc, contexto_actual_paso)
                    paso_key = f"Paso {step_index + 1}: {current_step_desc}"
                    st.session_state.app_state["partial_results"][paso_key] = respuesta_paso # Guardar resultado

                    if usage_paso and respuesta_paso and not ("Error API" in respuesta_paso or "Error inesperado" in respuesta_paso):
                        st.session_state.app_state["token_report"]["reasoning"] += usage_paso.prompt_tokens + usage_paso.completion_tokens
                        st.session_state.app_state["current_step_index"] += 1
                        next_step_index = st.session_state.app_state["current_step_index"]
                        if next_step_index < len(st.session_state.app_state["steps"]): st.session_state.app_state["current_stage"] = f"solving_step_{next_step_index}"
                        else: st.session_state.app_state["current_stage"] = "synthesizing"
                        trigger_next_stage = True
                    else: raise ValueError(f"Fallo Crítico Paso {step_index+1}: {respuesta_paso}")
                else: # Índice fuera de rango
                     st.session_state.app_state["current_stage"] = "synthesizing"; trigger_next_stage = True

            elif current_stage == "synthesizing":
                status_placeholder.info("✅ Sintetizando respuesta final...")
                respuesta_final, usage_sint = agente_sintetizador(
                    client=llm_client, model_name=model_to_use,
                    pregunta_original=st.session_state.app_state["question"], plan=st.session_state.app_state["plan"],
                    resultados_parciales=st.session_state.app_state["partial_results"]
                )
                if usage_sint and respuesta_final and "Error" not in respuesta_final:
                    st.session_state.app_state["final_answer"] = respuesta_final
                    st.session_state.app_state["token_report"]["reasoning"] += usage_sint.prompt_tokens
                    st.session_state.app_state["token_report"]["output"] = usage_sint.completion_tokens
                    st.session_state.app_state["token_report"]["total_calc"] = (st.session_state.app_state["token_report"]["prompt"] + st.session_state.app_state["token_report"]["reasoning"] + st.session_state.app_state["token_report"]["output"])
                    # --- Calcular Costos ---
                    cost_input = st.session_state.app_state["token_report"]["prompt"] * (RATE_INPUT_GPT4O / 1_000_000)
                    cost_output = (st.session_state.app_state["token_report"]["reasoning"] + st.session_state.app_state["token_report"]["output"]) * (RATE_OUTPUT_GPT4O / 1_000_000)
                    st.session_state.app_state["token_report"]["cost_input"] = cost_input
                    st.session_state.app_state["token_report"]["cost_output"] = cost_output
                    st.session_state.app_state["token_report"]["cost_total"] = cost_input + cost_output
                    # --- Fin Cálculo Costos ---
                    st.session_state.app_state["current_stage"] = "done"
                    status_placeholder.empty()
                    trigger_next_stage = False # Terminamos
                    st.session_state.app_state["processing_lock"] = False
                    st.rerun() # Último rerun para mostrar todo
                else: raise ValueError(f"Fallo en Síntesis Final: {respuesta_final}")

    except Exception as e:
         # Capturar errores en el flujo y actualizar estado
         st.session_state.app_state["error_message"] = f"Error en etapa '{current_stage}': {e}"
         st.session_state.app_state["current_stage"] = "error"
         print(f"!!! Error en Flujo: {e}"); traceback.print_exc()
         status_placeholder.error(f"⚠️ Error inesperado: {e}")
         st.session_state.app_state["processing_lock"] = False
         # No hacer rerun aquí para mostrar el error y detener

    # --- Visualización Acumulada (Siempre se muestra el estado actual) ---
    with results_container:
        # Mostrar la pregunta original siempre que se haya iniciado
        if st.session_state.app_state["current_stage"] != "idle":
            st.divider()
            st.markdown(f"### 💬 Pregunta en Proceso:")
            st.markdown(f"> {st.session_state.app_state['question']}")

            # Mostrar error general si existe
            if st.session_state.app_state["error_message"] and st.session_state.app_state["current_stage"] == 'error':
                 st.error(f"**Error Detenido:** {st.session_state.app_state['error_message']}")

            # Mostrar Cadena de Pensamiento si el plan existe
            if st.session_state.app_state["plan"]:
                st.markdown("---"); st.markdown("### 🤔 Cadena de Pensamiento")
                # Usar expander para Plan y Revisión
                with st.expander("📝 Plan y Revisión", expanded=False): # Empezar colapsado
                    st.markdown("**Plan Generado (LLM):**"); st.markdown(f"```\n{format_math(st.session_state.app_state.get('plan', 'N/A'))}\n```")
                    if st.session_state.app_state.get("plan_revision"):
                        st.markdown("--- \n**Revisión del Plan (LLM):**")
                        rev = st.session_state.app_state["plan_revision"]; fmt_rev = format_math(rev)
                        if "ok" not in rev.lower(): st.warning(fmt_rev)
                        else: st.info(fmt_rev)

                # Mostrar Pasos Intermedios si existen
                if st.session_state.app_state["partial_results"]:
                    st.markdown("--- \n▶️ **Ejecución de Pasos (LLM):**")
                    container_steps = st.container(border=True)
                    for paso_desc, paso_res in st.session_state.app_state["partial_results"].items():
                         paso_texto_solo = re.sub(r'^Paso \d+:\s*', '', paso_desc)
                         container_steps.markdown(f"**{format_math(paso_desc)}**") # Clave completa
                         is_error = paso_res is None or (isinstance(paso_res, str) and ("Error" in paso_res or "Fallo" in paso_res))
                         res_fmt = format_math(paso_res)
                         if is_error: container_steps.error(f"└── Resultado:\n```\n{res_fmt}\n```")
                         else: container_steps.markdown(f"└── Resultado:\n```\n{res_fmt}\n```")
                # Indicar si aún no hay pasos ejecutados pero el plan existe
                elif st.session_state.app_state["current_stage"] not in ["idle", "decomposing"]:
                     st.markdown("--- \n▶️ **Ejecución de Pasos (LLM):**")
                     st.info("Esperando ejecución del primer paso...")


            # Mostrar Respuesta Final si existe
            if st.session_state.app_state["final_answer"]:
                st.markdown("--- \n### ✅ Respuesta Final (LLM Auditor)")
                final_ans = st.session_state.app_state["final_answer"]
                ans_fmt = format_math(final_ans)
                if st.session_state.app_state["error_message"]: st.warning(ans_fmt) # Mostrar como advertencia si hubo error previo
                else: st.success(ans_fmt)

            # Mostrar Reporte de Tokens y Costo al final
            if st.session_state.app_state["current_stage"] in ["done", "error"] and st.session_state.app_state["token_report"]["total_calc"] > 0:
                st.divider()
                tk_rep = st.session_state.app_state["token_report"]
                with st.expander("📊 Ver Reporte de Tokens y Costo Estimado (USD)", expanded=True):
                    st.markdown(f"""
                    | Métrica         | Tokens          | Costo Estimado (USD) |
                    |-----------------|-----------------|----------------------|
                    | Entrada         | {tk_rep['prompt']:<15} | ${tk_rep['cost_input']:.6f}          |
                    | Razonamiento    | {tk_rep['reasoning']:<15} |                      |
                    | Salida          | {tk_rep['output']:<15} |                      |
                    | **Subtotal Salida** | **{tk_rep['reasoning'] + tk_rep['output']:<13}** | **${tk_rep['cost_output']:.6f}**      |
                    | **TOTAL**       | **{tk_rep['total_calc']:<13}** | **${tk_rep['cost_total']:.6f}**      |
                    """)
                    st.caption(f"Tarifas usadas ({MODEL_NAME}): Input ${RATE_INPUT_GPT4O}/M, Output ${RATE_OUTPUT_GPT4O}/M. Razonamiento incluye tokens intermedios (salida+entrada).")
            elif st.session_state.app_state["error_message"]:
                 st.info("No se generó reporte de tokens completo debido a error.")


    # Ejecutar siguiente etapa si es necesario (después de dibujar la UI actual)
    if trigger_next_stage:
         st.rerun()

# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    run_streamlit_app()