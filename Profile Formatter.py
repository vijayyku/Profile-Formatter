
import streamlit as st
from docx import Document
from io import BytesIO
from openai import AzureOpenAI

# -----------------------------
# Azure OpenAI Configuration
# -----------------------------
client = AzureOpenAI(
    api_key=st.secrets["AZURE_OPENAI_KEY"],
    azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-15-preview"
)

DEPLOYMENT_NAME = st.secrets["DEPLOYMENT_NAME"]
st.write(f"Deployment Name: {DEPLOYMENT_NAME}")


# -----------------------------
# Helper Functions
# -----------------------------
def read_docx(file):
    doc = Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text


def create_word_document(content):
    doc = Document()

    for line in content.split("\n"):
        doc.add_paragraph(line)

    output = BytesIO()
    doc.save(output)
    output.seek(0)

    return output


def generate_profile(profile_text, template_text):

    prompt = f"""
You are an expert profile writer.

TASK:
Convert the profile information provided into the exact format, structure,
headings, and style used in the template.

TEMPLATE:
--------------------
{template_text}
--------------------

PROFILE INFORMATION:
--------------------
{profile_text}
--------------------

RULES:
1. Follow template structure exactly.
2. Preserve all profile information.
3. Rewrite professionally.
4. Create missing sections only if reasonable.
5. Output only the final formatted profile.
"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a professional executive profile formatter."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Profile Formatter")

st.write(
    "Upload a raw profile and a format template. "
    "The tool will generate the profile using the template format."
)

profile_file = st.file_uploader(
    "Upload Profile",
    type=["docx"]
)

template_file = st.file_uploader(
    "Upload Format Template",
    type=["docx"]
)

if st.button("Generate Formatted Profile"):

    if profile_file and template_file:

        with st.spinner("Generating profile..."):

            profile_text = read_docx(profile_file)
            template_text = read_docx(template_file)

            formatted_profile = generate_profile(
                profile_text,
                template_text
            )

        st.success("Profile generated successfully.")

        st.subheader("Generated Profile")

        st.text_area(
            "Output",
            formatted_profile,
            height=500
        )

        word_file = create_word_document(
            formatted_profile
        )

        st.download_button(
            label="Download Word File",
            data=word_file,
            file_name="Formatted_Profile.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    else:
        st.warning(
            "Please upload both Profile and Format Template."
        )
