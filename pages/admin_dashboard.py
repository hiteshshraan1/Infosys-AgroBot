import streamlit as st
from utils.model_utils import predict_disease
import json
import os
from utils.chatbot_utils import load_knowledge_base
from utils.db_utils import load_history

from utils.model_utils import predict_disease

st.set_page_config(page_title="Admin Dashboard", page_icon="👨‍🌾", layout="wide")
st.title("👨‍🌾 Admin Dashboard")


if st.session_state.get("role") != "Admin":
    st.warning("You do not have permission to view this page. Please log in as an Admin.")
    st.stop()

kb_path = "data/bilingual_knowledge_base.json"

def save_knowledge_base(data):
    """Saves the entire knowledge base dictionary to the JSON file."""
    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if 'editing_key' not in st.session_state:
    st.session_state.editing_key = None



if st.session_state.editing_key:
    st.subheader("✏️ Edit Disease Entry")
    disease_key = st.session_state.editing_key
    all_diseases = load_knowledge_base()
    details = all_diseases.get(disease_key)

    if details:
        with st.form(key="edit_form"):
            st.info(f"You are editing: **{details.get('name', {}).get('en', 'Unknown')}**")

            edited_name_en = st.text_input("Disease Name (EN)", value=details.get('name', {}).get('en', ''))
            edited_crop_en = st.text_input("Crop Name (EN)", value=details.get('crop', {}).get('en', ''))

            st.markdown("---")
            st.markdown("**Keywords** (comma-separated)")
            edited_keywords_en = st.text_input("Keywords (EN)", value=", ".join(details.get('keywords', {}).get('en', [])))
            edited_keywords_hi = st.text_input("Keywords (HI)", value=", ".join(details.get('keywords', {}).get('hi', [])))
            edited_keywords_pa = st.text_input("Keywords (PA)", value=", ".join(details.get('keywords', {}).get('pa', [])))

            st.markdown("---")
            st.markdown("**Solutions**")
            edited_solution_en = st.text_area("Solution (EN)", value=details.get('solution', {}).get('en', ''), height=100)
            edited_solution_hi = st.text_area("Solution (HI)", value=details.get('solution', {}).get('hi', ''), height=100)
            edited_solution_pa = st.text_area("Solution (PA)", value=details.get('solution', {}).get('pa', ''), height=100)

            st.markdown("---")
            st.markdown("**Disease Image**")
            current_image = details.get("image", "")
            if current_image and os.path.exists(current_image):
                st.image(current_image, caption="Current Image", use_container_width=True)
            new_image = st.file_uploader("Upload new image (optional)", type=["jpg", "jpeg", "png"])

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button(" Save Changes", use_container_width=True):
                    
                    if new_image is not None:
                        image_dir = "data/disease_images"
                        os.makedirs(image_dir, exist_ok=True)
                        new_path = os.path.join(image_dir, new_image.name)
                        with open(new_path, "wb") as f:
                            f.write(new_image.getbuffer())
                        details["image"] = new_path

                    
                    details["name"]["en"] = edited_name_en
                    details["crop"]["en"] = edited_crop_en
                    details["keywords"]["en"] = [k.strip() for k in edited_keywords_en.split(",")]
                    details["keywords"]["hi"] = [k.strip() for k in edited_keywords_hi.split(",")]
                    details["keywords"]["pa"] = [k.strip() for k in edited_keywords_pa.split(",")]
                    details["solution"]["en"] = edited_solution_en
                    details["solution"]["hi"] = edited_solution_hi
                    details["solution"]["pa"] = edited_solution_pa

                    all_diseases[disease_key] = details
                    save_knowledge_base(all_diseases)
                    st.success("✅ Changes saved successfully!")
                    st.session_state.editing_key = None
                    st.rerun()

            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.editing_key = None
                    st.rerun()



if not st.session_state.editing_key:
    with st.expander("➕ Add a New Disease Entry", expanded=True):
        with st.form(key="add_form", clear_on_submit=True):
            st.subheader("New Disease Details")

            disease_name_en = st.text_input("Disease Name (English)", help="This will be auto-filled if you upload an image.")
            crop_name_en = st.text_input("Crop Name (English)")
            uploaded_image = st.file_uploader("Upload a sample photo", type=["jpg", "png", "jpeg"])

            st.markdown("---")
            st.markdown("**Keywords** (comma-separated)")
            keywords_en = st.text_input("Keywords (EN)", placeholder="e.g., white, powder, spots")
            keywords_hi = st.text_input("Keywords (Hindi)", placeholder="e.g., सफ़ेद, पाउडर, धब्बे")
            keywords_pa = st.text_input("Keywords (Punjabi)", placeholder="e.g., ਚਿੱਟਾ, ਪਾਊਡਰ, ਧੱਬੇ")

            st.markdown("---")
            st.markdown("**Solutions**")
            solution_en = st.text_area("Solution (EN)")
            solution_hi = st.text_area("Solution (Hindi)")
            solution_pa = st.text_area("Solution (Punjabi)")

            submitted = st.form_submit_button("Save New Disease")
            if submitted:
                
                if not crop_name_en or not keywords_en or not solution_en:
                    st.error("Please fill in at least Crop Name and all English keyword/solution fields.")
                else:
                    image_path = ""
                    
                    if uploaded_image is not None:
                        image_dir = "data/disease_images"
                        os.makedirs(image_dir, exist_ok=True)
                        image_path = os.path.join(image_dir, uploaded_image.name)
                        with open(image_path, "wb") as f:
                            f.write(uploaded_image.getbuffer())

                        
                        try:
                            predicted_label, confidence = predict_disease(image_path)
                            st.info(f"🧠 Model Prediction: **{predicted_label}** ({confidence * 100:.2f}% confidence)")
                            disease_name_en = predicted_label  # auto-fill from model prediction
                        except Exception as e:
                            st.error(f"Model prediction failed: {e}")
                            # If prediction fails, we rely on the manual input for disease name
                    
                    # Final check to ensure disease name is not empty
                    if not disease_name_en:
                        st.error("Disease Name is missing. Please enter it manually or upload an image for auto-detection.")
                    else:
                        disease_key = f"{crop_name_en.lower().replace(' ', '_')}_{disease_name_en.lower().replace(' ', '_')}"
                        
                        new_entry = {
                            "crop": {"en": crop_name_en, "hi": crop_name_en, "pa": crop_name_en},
                            "name": {"en": disease_name_en, "hi": disease_name_en, "pa": disease_name_en},
                            "keywords": {
                                "en": [k.strip() for k in keywords_en.split(',')],
                                "hi": [k.strip() for k in keywords_hi.split(',')],
                                "pa": [k.strip() for k in keywords_pa.split(',')]
                            },
                            "solution": {
                                "en": solution_en, "hi": solution_hi, "pa": solution_pa
                            },
                            "image": image_path
                        }

                        all_diseases = load_knowledge_base()
                        all_diseases[disease_key] = new_entry
                        save_knowledge_base(all_diseases)
                        st.success(f"Disease '{disease_name_en}' added successfully!")

    st.divider()
    st.subheader("⚙️ Manage Existing Diseases")
    all_diseases = load_knowledge_base()

    if not all_diseases:
        st.info("No diseases have been added yet.")
    else:
        for disease_key, details in all_diseases.items():
            disease_name = details.get('name', {}).get('en', f"!!INVALID ENTRY!!")
            crop_name = details.get('crop', {}).get('en', 'Unknown Crop')
            image_path = details.get("image", "")

            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"{disease_name} ({crop_name})")
                if image_path and os.path.exists(image_path):
                    st.image(image_path, width=100)
            with col2:
                if st.button("✏️ Edit", key=f"edit_{disease_key}", use_container_width=True):
                    st.session_state.editing_key = disease_key
                    st.rerun()
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{disease_key}", use_container_width=True):
                    current_data = load_knowledge_base()
                    if disease_key in current_data:
                        del current_data[disease_key]
                        save_knowledge_base(current_data)
                        st.success(f"Deleted '{disease_name}'.")
                        st.rerun()

    st.divider()
    st.subheader("📊 Farmer Query History")
    history = load_history()
    if history:
        st.dataframe(history)
    else:
        st.info("No farmer query history found yet.")