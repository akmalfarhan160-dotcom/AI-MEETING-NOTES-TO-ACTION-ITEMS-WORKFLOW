import streamlit as st
import google.genai as genai
import pandas as pd
import json

# Page Config
st.set_page_config(page_title="AI Meeting Action Items Generator", page_icon="📝", layout="wide")

st.title("📝 AI Meeting Notes to Action Items Workflow")
st.write("Paste your meeting notes or transcript below. AI will analyze them and extract structured action items.")

st.divider()

# Sidebar for API Key
st.sidebar.header("⚙️ Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

# Input Area
st.subheader("1. Enter Meeting Notes")
meeting_notes = st.text_area(
    "Paste Transcript / Rough Notes here:", 
    height=180, 
    placeholder="Example: John will create the login UI by Friday. Priya needs to complete database design by next Monday."
)

if st.button("🚀 Generate Action Items", type="primary"):
    if not api_key:
        st.error("❌ Please enter your Gemini API Key in the sidebar!")
    elif not meeting_notes.strip():
        st.warning("⚠️ Please enter the meeting notes!")
    else:
        with st.spinner("🤖 AI is analyzing your notes... Please wait..."):
            try:
                # Initialize Gemini Client
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                You are an expert AI project manager.
                Analyze the following meeting transcript/notes and extract clear action items.
                
                Meeting Notes:
                {meeting_notes}
                
                Respond ONLY with a valid JSON array containing objects with the following keys:
                - "Task": Specific action/task to be completed
                - "Assignee": Person responsible (use "Unassigned" if not mentioned)
                - "Deadline": Due date or timeline (use "Not specified" if not mentioned)
                - "Priority": "High", "Medium", or "Low" based on urgency
                
                Do NOT include markdown formatting like ```json. Return ONLY raw JSON text.
                """
                
                # Updated to gemini-3.5-flash
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=prompt
                )
                
                clean_response = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(clean_response)
                
                st.success("✅ Action Items successfully generated!")
                st.subheader("2. Extracted Action Items")
                
                df = pd.DataFrame(data)
                
                # Show Table
                st.dataframe(df, use_container_width=True)
                
                # CSV Download Button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download as CSV File",
                    data=csv,
                    file_name="action_items.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")