import streamlit as st
import google.generativeai as genai
import json
import re

# Configure the page
st.set_page_config(page_title="AI Travel Itinerary Planner", page_icon="✈️", layout="wide")

# Inject Custom CSS for styling
st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap');

        /* Apply Fonts globally */
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }
        h1, h2, h3, h4, h5, h6, .st-emotion-cache-10trblm {
            font-family: 'Playfair Display', serif !important;
        }

        /* Sidebar Styling: Dark Gradient */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
        }
        
        /* Sidebar text color overrides for better contrast */
        [data-testid="stSidebar"] .st-emotion-cache-10trblm, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown h2 {
            color: #ffffff !important;
        }
        
        /* Main welcome section centering */
        .welcome-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 70vh;
            text-align: center;
        }
        .welcome-emoji {
            font-size: 6rem;
            margin-bottom: 20px;
        }
        .welcome-title {
            font-family: 'Playfair Display', serif;
            font-size: 3rem;
            color: inherit;
            margin-bottom: 10px;
        }
        .welcome-subtitle {
            font-family: 'DM Sans', sans-serif;
            font-size: 1.2rem;
            color: #888;
        }
    </style>
""", unsafe_allow_html=True)

def call_gemini(api_key, destination, duration, travel_style, budget, interests):
    genai.configure(api_key=api_key)
    
    # Dynamically find available models for this API key to avoid 404 errors
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            
    if not available_models:
        raise Exception("No text generation models found for this API key.")
        
    # Prefer gemini-1.5-flash, then 1.5-pro, otherwise take the first available
    selected_model_name = available_models[0]
    for m_name in available_models:
        if "gemini-1.5-flash" in m_name:
            selected_model_name = m_name
            break
        elif "gemini-1.5-pro" in m_name and "flash" not in selected_model_name:
            selected_model_name = m_name
            
    # Clean the 'models/' prefix if it exists to prevent 'models/models/...' errors
    clean_model_name = selected_model_name.replace("models/", "")
    model = genai.GenerativeModel(clean_model_name)
    
    prompt = f"""
    Act as an expert travel planner. Create a detailed travel itinerary.
    Destination: {destination}
    Duration: {duration} days
    Travel Style: {travel_style}
    Budget Range: {budget}
    Interests: {', '.join(interests)}
    
    Return ONLY a raw valid JSON (no markdown, no ```json fences, no explanation).
    The JSON structure MUST exactly match this format:
    {{
        "destination": "Name of destination",
        "duration_days": {duration},
        "travel_style": "{travel_style}",
        "budget": "{budget}",
        "summary": "A brief overview of the trip",
        "days": [
            {{
                "day": 1,
                "theme": "Day theme",
                "morning": {{"activity": "activity name", "description": "details", "duration": "e.g. 2 hours", "cost_estimate": "$XX"}},
                "afternoon": {{"activity": "activity name", "description": "details", "duration": "e.g. 2 hours", "cost_estimate": "$XX"}},
                "evening": {{"activity": "activity name", "description": "details", "duration": "e.g. 2 hours", "cost_estimate": "$XX"}}
            }}
        ],
        "accommodation": "Suggested accommodation types or areas",
        "daily_tip": "A tip relevant to the destination",
        "general_tips": ["Tip 1", "Tip 2"],
        "estimated_total_budget": "$XXXX"
    }}
    """
    
    response = model.generate_content(prompt)
    raw_text = response.text
    
    # Strip markdown code fences
    cleaned_text = re.sub(r'```json', '', raw_text)
    cleaned_text = re.sub(r'```', '', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return json.loads(cleaned_text), raw_text

def render_text_itinerary(data: dict):
    # 1. HEADER SECTION
    dest = data.get("destination", "Unknown Destination")
    duration = data.get("duration_days", "")
    st.markdown(f"# 📍 {dest} ({duration} Days)")
    
    t_style = data.get("travel_style", "")
    budget = data.get("budget", "")
    st.markdown(f"**Travel Style:** {t_style} &nbsp;|&nbsp; **Budget:** {budget}")
    st.markdown("---")
    
    summary = data.get("summary", "")
    if summary:
        st.info(summary)
        
    # 2. DAY-BY-DAY SECTION
    days = data.get("days", [])
    for day in days:
        day_num = day.get("day", "")
        theme = day.get("theme", "")
        
        # a. HTML Card
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
                border-left: 4px solid #4361ee;
                border-radius: 12px;
                padding: 1.2rem;
                margin-bottom: 1rem;
                color: #1a1a2e;
            ">
                <h3 style="font-family: 'Playfair Display', serif; margin: 0; color: #1a1a2e;">Day {day_num}: {theme}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # b. Columns
        cols = st.columns(3)
        periods = [
            ("Morning 🌅", day.get("morning", {})),
            ("Afternoon ☀️", day.get("afternoon", {})),
            ("Evening 🌙", day.get("evening", {}))
        ]
        
        for col, (label, p_data) in zip(cols, periods):
            with col:
                st.markdown(f"**{label}**")
                if p_data:
                    st.markdown(f"**{p_data.get('activity', '')}**")
                    st.write(p_data.get("description", ""))
                    st.caption(f"⏱️ {p_data.get('duration', '')} | 💰 {p_data.get('cost_estimate', '')}")
                else:
                    st.write("No specific plans.")
                    
        # c. Accommodation
        acc = day.get("accommodation", data.get("accommodation", ""))
        st.markdown(f"**🏨 Accommodation:** {acc}")
        
        # d. Daily tip
        tip = day.get("daily_tip", data.get("daily_tip", ""))
        if tip:
            st.markdown(
                f"""
                <div style="
                    background: #fff8e1;
                    border-left: 4px solid #ffc107;
                    border-radius: 8px;
                    padding: 1rem;
                    margin-top: 1rem;
                    margin-bottom: 1rem;
                    color: #5d4037;
                ">
                    <strong>💡 Tip:</strong> {tip}
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # 4. SPACING
        st.markdown("---")

    # 3. TIPS & BUDGET SECTION
    st.markdown("### 📌 General Travel Tips")
    general_tips = data.get("general_tips", [])
    for gt in general_tips:
        st.markdown(f"- {gt}")
        
    total_budget = data.get("estimated_total_budget", "")
    st.success(f"**💰 Estimated Total Budget:** {total_budget}")

def render_json_tab(data: dict):
    # 1. JSON DISPLAY BLOCK
    json_str = json.dumps(data, indent=2)
    st.markdown(
        f"""
        <div style="
            background: #0d1117;
            color: #c9d1d9;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            border-radius: 10px;
            padding: 1.2rem;
            max-height: 500px;
            overflow-y: auto;
        ">
            <pre style="margin: 0; color: inherit; font-family: inherit;">{json_str}</pre>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 2. DOWNLOAD BUTTONS
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    
    dest_filename = data.get('destination', 'itinerary').replace(' ', '_')
    
    with col1:
        st.download_button(
            label="⬇️ Download JSON",
            data=json_str,
            file_name=f"{dest_filename}_itinerary.json",
            mime="application/json"
        )
        
    with col2:
        text_lines = []
        text_lines.append(f"Travel Itinerary: {data.get('destination', '')}")
        text_lines.append(f"Duration: {data.get('duration_days', '')} days")
        text_lines.append("")
        
        summary = data.get('summary', '')
        if summary:
            text_lines.append(summary)
            text_lines.append("")
            
        for day in data.get('days', []):
            text_lines.append(f"Day {day.get('day', '')} — {day.get('theme', '')}")
            
            for period in ['morning', 'afternoon', 'evening']:
                if period in day and day[period]:
                    p_data = day[period]
                    activity = p_data.get('activity', '')
                    desc = p_data.get('description', '')
                    text_lines.append(f"  {period.capitalize()}: {activity} — {desc}")
            
            acc = day.get('accommodation', data.get('accommodation', ''))
            if acc:
                text_lines.append(f"  Stay: {acc}")
                
            tip = day.get('daily_tip', data.get('daily_tip', ''))
            if tip:
                text_lines.append(f"  Tip: {tip}")
                
            text_lines.append("")
            
        text_lines.append("General Tips:")
        for gt in data.get('general_tips', []):
            text_lines.append(f"- {gt}")
            
        text_lines.append("")
        text_lines.append(f"Estimated Budget: {data.get('estimated_total_budget', '')}")
        
        text_output = "\n".join(text_lines)
        
        st.download_button(
            label="⬇️ Download Text",
            data=text_output,
            file_name=f"{dest_filename}_itinerary.txt",
            mime="text/plain"
        )

# Sidebar UI setup
with st.sidebar:
    st.markdown("## 🧭 Travel Preferences")
    
    with st.form("planner_form"):
        api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key")
        destination_input = st.text_input("Destination", placeholder="e.g., Kyoto, Japan")
        
        duration_input = st.slider("Trip Duration (days)", min_value=1, max_value=14, value=7)
        
        travel_style_input = st.selectbox(
            "Travel Style",
            ["Adventure", "Cultural", "Relaxation", "Family-friendly", "Budget", "Luxury"]
        )
        
        budget_range_input = st.selectbox(
            "Budget Range",
            ["Budget ($)", "Mid-range ($$)", "Premium ($$$)", "Luxury ($$$$)"]
        )
        
        interests_input = st.multiselect(
            "Interests",
            ["Food & Dining", "History & Museums", "Nature & Hiking", "Shopping", "Nightlife", "Art & Architecture"]
        )
        
        submit_button = st.form_submit_button(label="Generate Itinerary")

# Main Area UI setup
if submit_button:
    if not api_key_input:
        st.warning("Please provide your Gemini API Key in the sidebar to generate the itinerary.")
    elif not destination_input:
        st.warning("Please enter a destination to plan your trip.")
    else:
        with st.spinner("Planning your trip..."):
            try:
                itinerary_data, raw_response = call_gemini(
                    api_key=api_key_input,
                    destination=destination_input,
                    duration=duration_input,
                    travel_style=travel_style_input,
                    budget=budget_range_input,
                    interests=interests_input
                )
                
                st.success(f"Itinerary generated for {destination_input}!")
                
                tab1, tab2 = st.tabs(["📋 Itinerary View", "🔧 JSON Output"])
                with tab1:
                    render_text_itinerary(itinerary_data)
                with tab2:
                    render_json_tab(itinerary_data)
                
            except json.JSONDecodeError:
                st.error("Unexpected format returned from AI. Failed to parse JSON.")
                with st.expander("View Raw Output"):
                    try:
                        st.text(raw_response)
                    except NameError:
                        st.text("Could not fetch raw response.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    # Display the centered welcome message with a globe emoji
    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-emoji">🌎</div>
            <div class="welcome-title">Welcome to AI Travel Planner</div>
            <div class="welcome-subtitle">Fill out your preferences in the sidebar to generate a custom itinerary.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
