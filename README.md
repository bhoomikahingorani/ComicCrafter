# Comic Crafter
This project focuses on generating Comic stories using LLM models. The model is locally deployed for efficient inference. The project involves setting up the model, optimizing performance for edge deployment, and integrating it into an interactive application for generating dynamic narratives.

# Story Generator - AI Comic Book Creator

## Overview
Story Generator is a Streamlit-based web application that creates detailed comic book stories using AI. The application generates structured stories with panels, character dialogues, and scene descriptions, making it perfect for comic book writers and enthusiasts.

## Features
- **AI-Powered Story Generation**: Creates detailed 4-part comic book stories
- **Genre Selection**: Multiple genres including Superhero, Science Fiction, Fantasy, Mystery, Adventure, Comedy, and Drama
- **Structured Output**: Stories are divided into:
  - Introduction
  - Storyline
  - Climax
  - Moral
- **Panel-Based Format**: Each section contains detailed panels with:
  - Visual descriptions
  - Character dialogues
  - Thought bubbles
  - Narration boxes
- **Interactive UI**: Easy-to-use interface with expandable panels and story sections

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Required Setup
- In the terminal prompt do the following
    - Move to the directory of your file
    - Create a virtual environment
        - python -m venv venv
        - (venv\Scripts\activate)
    - install the following packages
        - pip install streamlit
        - pip install llama-cpp-python --prefer-binary
    
### Model Setup
1. Download the required GGUF model file (LM Studio)
2. Place it in the models folder 
3. Update the model path in the code: model_path=r"path/to/your/model.gguf"


## Usage
1. Start the application: streamlit run Story_generator.py
   
2. In the sidebar:
   - Enter your story concept
   - Select a genre
   - Click "Generate Comic Story"

3. View the generated story with:
   - Expandable panels
   - Character dialogues
   - Scene descriptions
   - Narration boxes

## Code Structure

### Main Components
- `generate_comic_story()`: Generates the initial story using the AI model
- `parse_story()`: Processes the AI output into structured panels and sections
- Streamlit UI components for user interaction and story display

### Story Format
The generated story follows this structure:

  INTRODUCTION:
  Panel 1: [Scene Description]
  Character Dialogues
  Narration Boxes
  STORYLINE:
  Panel 2: [Scene Description]
  ...
  CLIMAX:
  Panel 3: [Scene Description]
  ...
  MORAL:
  Panel 4: [Scene Description]
