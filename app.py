import streamlit as st
import requests
import json

# Función para obtener la respuesta de la API de Together con streaming
def get_api_response(messages, max_tokens=2512, temperature=0.7, top_p=0.7, top_k=50, repetition_penalty=1, stop=["<|eot_id|>"], stream=True):
    headers = {
        "Authorization": f"Bearer {st.secrets['TOGETHER_API_KEY']}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "repetition_penalty": repetition_penalty,
        "stop": stop,
        "stream": stream
    }

    try:
        response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, data=json.dumps(data), stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error en la solicitud a la API: {e}")
        return ""

    response_text = ""
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith("data: "):
                json_str = decoded_line.replace("data: ", "")
                if json_str == "[DONE]":
                    break
                try:
                    json_obj = json.loads(json_str)
                    delta = json_obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        response_text += delta
                        yield delta
                except json.JSONDecodeError:
                    continue

# Función para generar 10 problemas basados en el tema
def generar_problemas(tema):
    prompt = f"Dado el tema '{tema}', propone 10 problemas que puedan ser resueltos mediante una aplicación de Streamlit."
    messages = [{"role": "user", "content": prompt}]
    problems = []
    response_placeholder = st.empty()
    with st.spinner("Generando problemas..."):
        for chunk in get_api_response(messages):
            response_placeholder.markdown(response_placeholder.markdown + chunk)
    # Procesar el texto recibido para extraer los problemas
    lines = response_placeholder.markdown
    for line in lines.split('\n'):
        line = line.strip()
        if line:
            # Eliminar numeración o viñetas
            if line[0].isdigit() and line[1] == '.':
                problem = line[2:].strip()
            elif line.startswith('- '):
                problem = line[2:].strip()
            else:
                problem = line
            problems.append(problem)
            if len(problems) == 10:
                break
    return problems

# Función para generar el código de la aplicación basado en el problema seleccionado
def generar_codigo(problema):
    prompt = f"Genera el código para una aplicación de Streamlit que resuelva el siguiente problema: {problema}"
    messages = [{"role": "user", "content": prompt}]
    code = ""
    code_placeholder = st.empty()
    with st.spinner("Generando código de la aplicación..."):
        for chunk in get_api_response(messages):
            code += chunk
            code_placeholder.code(code, language='python')
    return code

# Configuración de la página
st.set_page_config(page_title="Generador de Apps Streamlit", layout="wide")

st.title("Generador de Aplicaciones con Streamlit")
st.write("Esta aplicación te ayudará a generar código para aplicaciones de Streamlit basadas en un tema que elijas.")

# Paso 1: Ingresar el tema
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'problems' not in st.session_state:
    st.session_state.problems = []
if 'codigo' not in st.session_state:
    st.session_state.codigo = ""

if st.session_state.step == 1:
    st.header("Paso 1: Ingresa un Tema")
    tema = st.text_input("Introduce el tema de tu interés:")
    if st.button("Generar Problemas") and tema:
        st.session_state.problems = []
        st.session_state.codigo = ""
        st.session_state.step = 2
        st.session_state.problems = generar_problemas(tema)

# Paso 2: Seleccionar un problema y generar el código
if st.session_state.step == 2 and st.session_state.problems:
    st.header("Paso 2: Selecciona un Problema")
    problema = st.selectbox("Elige uno de los siguientes problemas para resolver:", st.session_state.problems)
    if st.button("Generar Código de la App"):
        st.session_state.codigo = generar_codigo(problema)

# Mostrar el código generado
if st.session_state.codigo:
    st.header("Código Generado para la Aplicación de Streamlit")
    st.code(st.session_state.codigo, language='python')
    st.download_button("Descargar Código", st.session_state.codigo, file_name='app.py')
