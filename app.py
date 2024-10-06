import streamlit as st
import requests
import json
import re

# Configuración de la página
st.set_page_config(
    page_title="Generador de Problemas Detallados con Streamlit",
    page_icon="💡",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("Generador de 10 Problemas Detallados para Aplicaciones de Streamlit")
st.write("Ingresa un tema y te proponemos 10 problemas detallados que pueden ser resueltos mediante una aplicación de Streamlit.")

# Campo de entrada para el tema
tema = st.text_input("Ingrese un tema:", "")

# Botón para generar los problemas
if st.button("Generar Problemas") and tema:
    with st.spinner("Generando problemas detallados..."):
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
                            f"Dado el tema '{tema}', propón 10 problemas detallados que puedan ser resueltos mediante una aplicación de Streamlit. "
                            "Para cada problema, proporciona un título y una descripción completa que incluya el objetivo principal, las funcionalidades clave y cualquier requisito adicional necesario."
                        )
                    }
                ],
                "max_tokens": 3000,  # Aumentado para permitir descripciones más detalladas
                "temperature": 0.7,
                "top_p": 0.7,
                "top_k": 50,
                "repetition_penalty": 1,
                "stop": ["<|eot_id|>"],
                "stream": False  # Mantener en False para simplificar la recopilación de respuestas
            }

            # Realizar la solicitud POST a la API
            response = requests.post(url, headers=headers, data=json.dumps(mensaje))

            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                respuesta = response.json()
                # Extraer el contenido generado
                contenido = respuesta.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if contenido:
                    # Procesar el contenido para extraer los 10 problemas detallados
                    # Suponiendo que cada problema comienza con un número seguido de un título
                    # Por ejemplo:
                    # 1. Título del Problema
                    #    Descripción detallada...
                    patrones = re.compile(r'^\s*\d+\.\s*(.+?)\n\s{2,}(.+)', re.MULTILINE | re.DOTALL)
                    problemas = patrones.findall(contenido)
                    
                    if len(problemas) >= 10:
                        st.success("Aquí tienes 10 problemas detallados sugeridos:")
                        for idx, (titulo, descripcion) in enumerate(problemas[:10], 1):
                            with st.expander(f"**{idx}. {titulo.strip()}**"):
                                st.write(descripcion.strip())
                    else:
                        st.warning("La API no retornó suficientes problemas detallados. Intenta con otro tema.")
                else:
                    st.error("No se recibió contenido de la API.")
            else:
                st.error(f"Error en la solicitud: {response.status_code} - {response.text}")
        
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
