# AI Travel Itinerary Planner 🌎✈️

A Streamlit web application that acts as an expert travel planner, generating detailed, customized daily itineraries using the Google Gemini AI.

## Features
- **Customizable Inputs**: Specify destination, trip duration, travel style, budget range, and specific interests.
- **AI-Powered Generation**: Utilizes Google's Gemini models to create well-structured travel plans.
- **Beautiful UI**: Built with Streamlit featuring a responsive design, modern Google Fonts (DM Sans & Playfair Display), and customized CSS styling.
- **Detailed Itinerary View**: View your trip broken down day-by-day (morning, afternoon, evening), including activity descriptions, estimated durations, and cost estimates.
- **Export Options**: Download the generated itinerary as a structured JSON file or a plain text summary.

## Prerequisites
- Python 3.8+
- Google Gemini API Key (Get one from [Google AI Studio](https://aistudio.google.com/))

## Installation
1. Clone the repository or navigate to the project directory:
   ```bash
   cd path/to/project
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
2. Open the provided local URL in your web browser (typically `http://localhost:8501`).
3. Enter your Gemini API Key in the sidebar.
4. Fill out your travel preferences (Destination, Duration, Travel Style, etc.).
5. Click **Generate Itinerary** and let the AI plan your perfect trip!

## Technologies Used
- [Streamlit](https://streamlit.io/) - Frontend framework
- [Google Generative AI (Gemini)](https://ai.google.dev/) - LLM for content generation
- Python - Core logic
# ai-travel-itinerary-planner
