import streamlit as st
#from ctransformers import AutoModelForCausalLM 
from llama_cpp import Llama

llm = Llama(
    model_path=r"D:\Intel\models\Mistral-Nemo-Instruct-2407-Q3_K_L.gguf",
    n_ctx=2048,
    n_threads=8
)

def generate_comic_story(prompt, genre):
    system_prompt = f"""You are an expert comic book writer specializing in {genre} stories. 
    Create a compelling 4-part comic book story based on this prompt: "{prompt}"
    
    The story must have these four distinct parts:
    1. INTRODUCTION: Set the scene, introduce main characters and the central conflict
    2. STORYLINE: Develop the plot with rising action and obstacles
    3. CLIMAX: Present the most intense moment where the conflict peaks
    4. MORAL: Conclude with a resolution and the lesson or meaning of the story
    
    Format each part with a clear heading and include vivid descriptions that would work well with comic book illustrations.
    Use comic-style dialogue with speech bubbles, thought bubbles, and narration boxes.
    Include specific image description suggestions for key moments in [PANEL: description] format.
    """
    
    full_prompt = f"{system_prompt}\n\nAssistant:"
    
    response = llm(
        full_prompt,
        max_tokens=1200,  # Increased for a more complete story
        temperature=0.7,
    )
    return response

def parse_story(response):
    try:
        # Get the story text from the response
        story_text = response['choices'][0]['text']
        
        # Dictionary to store all parts and their panels
        story_parts = {}
        current_part = None
        current_panels = []
        
        # Split by lines and process
        lines = story_text.split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and dividers
            if not line or line == '---':
                continue
                
            # Check for section headers
            if '**[' in line and ']**' in line:
                # If we were processing a previous section, save it
                if current_part:
                    story_parts[current_part] = current_panels
                
                # Start new section
                current_part = line.replace('**[', '').replace(']**', '').lower()
                current_panels = []
                continue
            
            # Process panels and their content
            if line.startswith('*PANEL'):
                # Start new panel
                panel_num = line.split(':')[0].replace('*PANEL', '').strip()
                panel_content = {
                    'number': panel_num,
                    'description': '',
                    'dialogues': [],
                    'narration': []
                }
                current_panels.append(panel_content)
            
            # Process different types of content
            elif current_panels:  # Make sure we have a current panel
                current_panel = current_panels[-1]  # Get the last panel
                
                if line.startswith('NARRATION BOX:'):
                    current_panel['narration'].append(line.replace('NARRATION BOX:', '').strip())
                elif 'THOUGHT BUBBLE' in line:
                    current_panel['dialogues'].append({
                        'type': 'thought',
                        'character': line.split('(THOUGHT BUBBLE)')[0].strip(),
                        'text': line.split(':')[-1].strip()
                    })
                elif ':' in line and '(' not in line:  # Regular dialogue
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        current_panel['dialogues'].append({
                            'type': 'speech',
                            'character': parts[0].strip(),
                            'text': parts[1].strip()
                        })
                elif not line.startswith('*'):  # Description text
                    if current_panel['description']:
                        current_panel['description'] += ' ' + line
                    else:
                        current_panel['description'] = line
        
        # Save the last section
        if current_part and current_panels:
            story_parts[current_part] = current_panels
        
        return story_parts
    
    except Exception as e:
        st.error(f"Error parsing story: {str(e)}")
        return None

# Streamlit UI
st.title("ComicCrafter - Story Generator")

# Sidebar for input
with st.sidebar:
    st.header("Story Details")
    story_prompt = st.text_area("Story Concept", "A teenage inventor discovers a portal to a parallel universe...")
    genre = st.selectbox("Genre", ["Superhero", "Science Fiction", "Fantasy", "Mystery", "Adventure", "Comedy", "Drama"])

# Initialize session state
if "comic_story" not in st.session_state:
    st.session_state.comic_story = None
    st.session_state.story_parts = {}

# Generate comic story
if st.button("Generate Comic Story"):
    with st.spinner("Generating your comic book story... (This might take a while on CPU)"):
        story = generate_comic_story(story_prompt, genre)
        st.session_state.comic_story = story

# Display comic story
if st.session_state.comic_story:
    st.subheader("Generated Comic Book Story")
    
# Example usage:
if st.session_state.comic_story:  # Assuming the response is stored in session state
    parsed_story = parse_story(st.session_state.comic_story)
    
    if parsed_story:
        # Display each section
        for section, panels in parsed_story.items():
            st.subheader(section.upper())
            
            # Display each panel in the section
            for panel in panels:
                with st.expander(f"Panel {panel['number']}"):
                    # Description
                    st.markdown("**Description:**")
                    st.write(panel['description'])
                    
                    # Narration
                    if panel['narration']:
                        st.markdown("**Narration:**")
                        for narr in panel['narration']:
                            st.write(narr)
                    
                    # Dialogues
                    if panel['dialogues']:
                        st.markdown("**Dialogues:**")
                        for dialogue in panel['dialogues']:
                            if dialogue['type'] == 'thought':
                                st.write(f"💭 {dialogue['character']}: {dialogue['text']}")
                            else:
                                st.write(f"💬 {dialogue['character']}: {dialogue['text']}")