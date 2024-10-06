import streamlit as st
import requests
import json
import re

# Configuración de la página
st.set_page_config(
    page_title="Generador de Problemas e Instrucciones para Streamlit",
    page_icon="💡",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("Generador de 10 Problemas e Instrucciones para Streamlit")
st.write("Ingresa un tema y te proponemos 10 problemas junto con instrucciones para desarrollar aplicaciones de Streamlit que los resuelvan.")

# Campo de entrada para el tema
tema = st.text_input("Ingrese un tema:", "")

# Botón para generar los problemas y las instrucciones
if st.button("Generar Problemas e Instrucciones") and tema:
    with st.spinner("Generando problemas e instrucciones..."):
        try:
            # Obtener la clave de la API desde los Secrets
            api_key = st.secrets["together"]["api_key"]

            # Definir la URL de la API
            url = "https://api.together.xyz/v1/chat/completions"

            # Configurar los encabezados de la solicitud
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Crear el mensaje de entrada para la API en español
            mensaje = {
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Dado el tema '{tema}', realiza lo siguiente:\n"
                            f"1. Propón 10 problemas que puedan ser resueltos mediante una aplicación de Streamlit.\n"
                            f"2. Para cada problema, proporciona instrucciones detalladas para desarrollar una aplicación de Streamlit que lo resuelva.\n"
                            f"Presenta los resultados en un formato estructurado, donde cada problema esté numerado y seguido de sus instrucciones correspondientes."
                        )
                    }
                ],
                "max_tokens": 4000,  # Aumentado para manejar respuestas más largas
                "temperature": 0.7,
                "top_p": 0.7,
                "top_k": 50,
                "repetition_penalty": 1,
                "stop": ["<|eot_id|>"],
                "stream": False
            }

            # Realizar la solicitud POST a la API
            response = requests.post(url, headers=headers, data=json.dumps(mensaje))

            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                respuesta = response.json()
                # Extraer el contenido generado
                contenido = respuesta.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if contenido:
                    # Procesar el contenido para extraer los problemas y las instrucciones
                    # Suponiendo que el formato es:
                    # 1. Problema 1
                    # Instrucciones para la aplicación 1
                    # 2. Problema 2
                    # Instrucciones para la aplicación 2
                    # ...

                    # Dividir el contenido por números que indican cada problema
                    problemas = re.split(r'\n*\d+\.\s+', contenido)
                    # El primer elemento puede estar vacío si el texto comienza con '1. '
                    if problemas[0].strip() == "":
                        problemas = problemas[1:]

                    if len(problemas) >= 10:
                        st.success("Aquí tienes 10 problemas sugeridos junto con las instrucciones para sus aplicaciones:")
                        for idx, problema in enumerate(problemas[:10], 1):
                            # Separar el problema y las instrucciones
                            # Asumimos que las instrucciones siguen después de una línea en blanco
                            partes = problema.split('\n\n', 1)
                            descripcion = partes[0].strip()
                            instrucciones = partes[1].strip() if len(partes) > 1 else "No se proporcionaron instrucciones."

                            st.markdown(f"### **{idx}. {descripcion}**")
                            st.markdown(f"**Instrucciones para la aplicación de Streamlit:**\n{instrucciones}")

                            # Botón para descargar las instrucciones
                            st.download_button(
                                label=f"Descargar Instrucciones de la Aplicación {idx}",
                                data=instrucciones,
                                file_name=f"instrucciones_problema_{idx}.txt",
                                mime="text/plain"
                            )
                    else:
                        st.warning("La API no retornó suficientes problemas. Intenta con otro tema.")
                else:
                    st.error("No se recibió contenido de la API.")
            else:
                st.error(f"Error en la solicitud: {response.status_code} - {response.text}")
        
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
