import streamlit as st
import google.generativeai as genai
import PyPDF2
from dotenv import load_dotenv
import os
import json

# Load API key and configure Gemini
load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")  # Using gemini-pro instead of gemini-1.0-pro

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def process_with_gemini(text):
    try:
        prompt = f"""
        Extract the following information from this text and format it as JSON:
        - Name
        - Phone Number
        - Address

        Text: {text}

        Format the response exactly like this example:
        {{
            "Name": "John Doe",
            "Phone": "123-456-7890",
            "Address": "123 Main St, City, State"
        }}
        """
        
        response = model.generate_content(prompt)
        
        if response.text:
            # Clean the response text to ensure it's valid JSON
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:-3]  # Remove ```json and ``` markers
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:-3]  # Remove ``` markers
                
            cleaned_text = cleaned_text.strip()
            data = json.loads(cleaned_text)
            return data
        else:
            return {"Name": "", "Phone": "", "Address": ""}
            
    except Exception as e:
        st.error(f"Error processing text: {e}")
        return {"Name": "", "Phone": "", "Address": ""}

def main():
    st.title("PDF Information Extractor")
    
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Extract text from PDF
        text = extract_text_from_pdf(uploaded_file)
        
        if text:
            # Process with Gemini
            with st.spinner("Extracting information..."):
                data = process_with_gemini(text)
            
            # Display form
            st.subheader("Extracted Information")
            name = st.text_input("Name", value=data.get("Name", ""))
            phone = st.text_input("Phone Number", value=data.get("Phone", ""))
            address = st.text_area("Address", value=data.get("Address", ""))
            
            if st.button("Save Information"):
                st.success("Information saved successfully!")
                st.json({
                    "Name": name,
                    "Phone": phone,
                    "Address": address
                })

if __name__ == "__main__":
    main()