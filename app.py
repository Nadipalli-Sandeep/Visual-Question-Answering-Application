import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from transformers import ViltProcessor, ViltForQuestionAnswering

# Set page layout to wide
st.set_page_config(layout="wide")

# Custom CSS to enhance appearance
st.markdown("""
    <style>
    .stApp {
        background: url('https://www.transparenttextures.com/patterns/fancy-deboss.png');
        background-size: cover;
        color: #333333;
    }
    .title {
        font-family: 'Lucida Sans Unicode', 'Lucida Grande', sans-serif;
        text-align: center;
        color: #4CAF50;
        margin-top: 20px;
    }
    .description {
        text-align: center;
        color: #555555;
        margin-bottom: 50px;
    }
    .card {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #FF5722;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #E64A19;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
    }
    .stFileUploader>div>div>button {
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize ViltProcessor and ViltForQuestionAnswering
processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")

def get_answer(image, text):
    try:
        # Load and process the image
        img = Image.open(BytesIO(image)).convert("RGB")

        # Prepare inputs
        encoding = processor(img, text, return_tensors="pt")

        # Forward pass
        outputs = model(**encoding)
        logits = outputs.logits
        idx = logits.argmax(-1).item()
        answer = model.config.id2label[idx]

        return answer

    except Exception as e:
        return str(e)

# Set up the Streamlit app
st.markdown("<h1 class='title'>Visual Question Answering</h1>", unsafe_allow_html=True)
st.markdown("<p class='description'>Upload an image and enter a question to get an answer using advanced AI.</p>", unsafe_allow_html=True)

# Create columns for image upload and input fields
col1, col2 = st.columns(2)

# Default image to display when no image is uploaded
default_image_url = "https://via.placeholder.com/400x300.png?text=Upload+an+image+to+get+started"
default_image = requests.get(default_image_url).content

# Image upload
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, use_column_width=True)
    else:
        st.image(default_image, use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Question input
with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    question = st.text_input("Question")

    # Process the image and question when both are provided
    if uploaded_file is not None and question:
        if st.button("Ask Question"):
            image = Image.open(uploaded_file)
            image_byte_array = BytesIO()
            image.save(image_byte_array, format='JPEG')
            image_bytes = image_byte_array.getvalue()

            # Get the answers
            answer = get_answer(image_bytes, question)

            # Display the answer
            st.success("Answer: " + answer)
    st.markdown("</div>", unsafe_allow_html=True)
