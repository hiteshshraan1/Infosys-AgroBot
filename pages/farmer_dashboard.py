import streamlit as st
from utils.image_utils import predict_disease
from utils.db_utils import save_history
from utils.chatbot_utils import get_disease_info, analyze_symptoms_by_text
import os
import time 

st.set_page_config(page_title="Farmer Dashboard", page_icon="🌿", layout="wide")
st.title("🌿 Farmer Diagnosis Center")


if "username" not in st.session_state:
    st.warning("Please log in to access the dashboard.")
    st.stop()
username = st.session_state["username"]

LANGUAGES = {"English": "en", "हिन्दी (Hindi)": "hi", "ਪੰਜਾਬੀ (Punjabi)": "pa"}
selected_lang_name = st.radio("Choose Your Language", list(LANGUAGES.keys()), horizontal=True)
lang_code = LANGUAGES[selected_lang_name]

tab1, tab2 = st.tabs(["Diagnose by Image 📸", "Diagnose by Text Symptoms 💬"])

with tab1:
    st.header("Upload an Image of the Infected Plant")
    uploaded_file = st.file_uploader("Select an image file", type=["jpg", "png", "jpeg"], key="image_uploader")

    if uploaded_file:
        temp_file_path = os.path.join("data", uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.image(temp_file_path, caption="Uploaded Image", use_container_width=True)

        with st.spinner("Analyzing image with AI..."):
            prediction_index = predict_disease(temp_file_path)

        if isinstance(prediction_index, (int, float)):
            disease_map = {
                0: "apple_apple_scab", 1: "apple_black_rot",
                2: "corn_maize_common_rust", 3: "corn_maize_northern_leaf_blight",
                4: "grape_black_rot", 5: "potato_early_blight",
                6: "potato_late_blight", 7: "tomato_bacterial_spot",
                8: "tomato_early_blight", 9: "tomato_late_blight"
            }
            
            disease_key = disease_map.get(prediction_index)
            
            if disease_key:
                result = get_disease_info(disease_key)
                if result:
                    issue_name = result.get("name", {}).get(lang_code, disease_key)
                    crop_name = result.get("crop", {}).get(lang_code, "N/A")
                    solution = result.get("solution", {}).get(lang_code, "No solution found.")
                    
                    st.success(f"**Diagnosis:** {issue_name} in {crop_name}")
                    st.info(f"**Recommended Solution:**\n{solution}")
                    save_history(username, issue_name, selected_lang_name, solution)
                else:
                    st.error(f"Could not find information for '{disease_key}' in the knowledge base.")
            else:
                st.error("Prediction could not be mapped to a known disease.")
        else:
            st.error(prediction_index)
            
        os.remove(temp_file_path)

with tab2:
    st.header("Describe the Plant's Symptoms")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("e.g., my tomato leaves have white powder spots..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing symptoms..."):
                result = analyze_symptoms_by_text(prompt, lang_code)
                
                if not result:
                    response_text = {
                        "en": "I could not identify the issue. Please try describing with different keywords.",
                        "hi": "मुझे समस्या की पहचान नहीं हो सकी। कृपया अलग-अलग कीवर्ड से वर्णन करने का प्रयास करें।",
                        "pa": "ਮੈਨੂੰ ਮਸਲੇ ਦੀ ਪਛਾਣ ਨਹੀਂ ਹੋ ਸਕੀ। ਕਿਰਪਾ ਕਰਕੇ ਵੱਖ-ਵੱਖ ਕੀਵਰਡਸ ਨਾਲ ਲੱਛਣਾਂ ਦਾ ਵਰਣਨ ਕਰਨ ਦੀ ਕੋਸ਼ਿਸ਼ ਕਰੋ।"
                    }.get(lang_code)
                else:
                    crop_name = result.get("crop", {}).get(lang_code, "N/A")
                    issue_name = result.get("name", {}).get(lang_code, "N/A")
                    solution = result.get("solution", {}).get(lang_code, "No solution found.")
                    
                    response_text = f"""Based on your description, the likely issue is **{issue_name}** in **{crop_name}**.
                    \n\n**Recommended Solution:**\n{solution}"""
                    save_history(username, issue_name, selected_lang_name, solution)

            
            message_placeholder = st.empty()
            full_response = ""
            for word in response_text.split():
                full_response += word + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})