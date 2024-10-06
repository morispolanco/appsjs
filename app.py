import streamlit as st
import requests

st.title("Generador de Apps JavaScript basado en un tema")

# Obtener la API Key de los Secrets de Streamlit
api_key = st.secrets["together_api_key"]
url = "https://api.together.xyz/v1/chat/completions"

topic = st.text_input("Introduce un tema:")

if topic:
    st.write("Generando problemas...")
    # Función para obtener los problemas
    def get_problems(topic):
        prompt = f"Dado el tema '{topic}', proporciona cinco problemas que puedan ser resueltos mediante una app de JavaScript. Lista los problemas en forma de lista numerada."
        messages = [{"role": "user", "content": prompt}]
        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": ["<|eot_id|>"],
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]
            return generated_text
        else:
            st.error("Error al comunicarse con la API.")
            return None

    problems_text = get_problems(topic)
    if problems_text:
        # Analizar los problemas generados
        problems = []
        for line in problems_text.splitlines():
            line = line.strip()
            if line and line[0].isdigit():
                problem = line[line.find('.')+1:].strip()
                problems.append(problem)
        if problems:
            selected_problem = st.selectbox("Elige un problema:", problems)
            if selected_problem:
                st.write("Generando código de la app...")
                # Función para obtener el código JavaScript
                def get_js_code(problem):
                    prompt = f"Genera el código de una página web en HTML y JavaScript que resuelva el siguiente problema: '{problem}'."
                    messages = [{"role": "user", "content": prompt}]
                    data = {
                        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                        "messages": messages,
                        "max_tokens": 1024,
                        "temperature": 0.7,
                        "top_p": 0.7,
                        "top_k": 50,
                        "repetition_penalty": 1,
                        "stop": ["<|eot_id|>"],
                        "stream": False
                    }
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    response = requests.post(url, headers=headers, json=data)
                    if response.status_code == 200:
                        result = response.json()
                        generated_code = result["choices"][0]["message"]["content"]
                        return generated_code
                    else:
                        st.error("Error al comunicarse con la API.")
                        return None

                js_code = get_js_code(selected_problem)
                if js_code:
                    st.subheader("Código de la app generada:")
                    st.code(js_code, language='html')

                    st.subheader("Vista previa de la app:")
                    st.components.v1.html(js_code, height=600, scrolling=True)
        else:
            st.error("No se pudieron extraer los problemas.")
    else:
        st.error("No se pudo generar la lista de problemas.")
