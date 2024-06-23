import streamlit as st
import requests
import json
import random

# Configuración de la API de OpenAI
api_url = "https://api.openai.com/v1/chat/completions"
api_key = "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"  # Reemplaza con tu clave de API
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# --- Funciones para interactuar con ChatGPT ---

def get_questions():
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "Basado en textos de ultrasonido Desarrollarás preguntas en inglés sobre ultrasonido diagnóstico sobre sistema urinario de mediana a alta complejidad tipo ARDMS."},
            {"role": "user", "content": "Provide me with 25 quiz questions in the format: {\"question\": \"Your question?\", \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\", \"Option E\"], \"answer\": \"Correct Option\"}"}
        ],
        "max_tokens": 1500
    }

    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error(f"Error: No se pudieron obtener las preguntas de ChatGPT. Código de estado: {response.status_code}")
        st.error(response.text)  # Mostrar el mensaje de error de la API
        return None

# --- Funciones para la lógica del examen en Streamlit ---

def mostrar_pregunta(pregunta, opciones, respuesta_correcta):
    st.write(pregunta)
    respuesta_usuario = st.radio("Selecciona una opción:", opciones, key=pregunta)  # Clave única para evitar conflictos

    if respuesta_usuario == respuesta_correcta:
        st.success("¡Correcto!")
        return True
    else:
        st.error(f"Incorrecto. La respuesta correcta es: {respuesta_correcta}")
        return False

# --- Interfaz de usuario de Streamlit ---

st.title("Examen de Ultrasonido")

if st.button("Comenzar Examen"):
    st.session_state.aciertos = 0
    st.session_state.preguntas_respondidas = 0
    st.session_state.mostrar_resultados = False

    # Obtener preguntas de ChatGPT
    questions_data = get_questions()

    if questions_data:
        try:
            questions_list = questions_data.split('\n')
            st.session_state.questions = [json.loads(q.split('. ', 1)[1]) for q in questions_list if q]

            # Mostrar preguntas
            for i, question_data in enumerate(st.session_state.questions):
                if st.session_state.preguntas_respondidas < len(st.session_state.questions):
                    st.write("---")
                    resultado = mostrar_pregunta(
                        question_data['question'],
                        question_data['options'],
                        question_data['answer']
                    )
                    st.session_state.preguntas_respondidas += 1
                    if resultado:
                        st.session_state.aciertos += 1
                else:
                    break
            
            if st.session_state.preguntas_respondidas == len(st.session_state.questions):
                st.session_state.mostrar_resultados = True

        except json.JSONDecodeError as e:
            st.error(f"Error al procesar las preguntas de ChatGPT: {str(e)}")

# Mostrar resultados al final
if st.session_state.get("mostrar_resultados", False):
    st.write("---")
    st.write("## Resultados del Examen")
    st.write(f"Respuestas correctas: {st.session_state.aciertos} de {len(st.session_state.questions)}")
    porcentaje = (st.session_state.aciertos / len(st.session_state.questions)) * 100
    st.write(f"Tu calificación: {porcentaje:.2f}%")
