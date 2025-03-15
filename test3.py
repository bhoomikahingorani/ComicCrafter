import streamlit as st
from langchain_groq import ChatGroq
from together import Together
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Check for API keys
groq_api_key = os.getenv("GROQ_API_KEY")
together_api_key = os.getenv("TOGETHER_API_KEY")

if not groq_api_key or not together_api_key:
    st.error("Please set GROQ_API_KEY and TOGETHER_API_KEY in your .env file")
    st.stop()

# Set environment variables
os.environ["GROQ_API_KEY"] = groq_api_key
os.environ["TOGETHER_API_KEY"] = together_api_key

# Initialize models
llm = ChatGroq(
    model_name="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=1000  # Increased for more detailed stories
)
together_client = Together(api_key=os.environ["TOGETHER_API_KEY"])

# Functions for generating manga story and panel descriptions
def generate_manga_story(prompt, genre):
    messages = [
        ("system", f"""You're a manga storytelling AI. Create a {genre} manga with:
        - 5-7 panels
        - Expressive character dialogues (e.g., *shouting*, *gasping*)
        - Action descriptions in [brackets]
        - Maintain manga pacing and page flow.
        
        Format your response as a sequence of panels, with each panel having:
        1. A panel number
        2. A brief description of what's happening in the panel
        3. Any dialogue spoken by characters
        
        Example format:
        Panel 1: Description of scene.
        Character: "Dialogue here."
        
        Panel 2: Another description.
        Character: "*gasps* More dialogue!"
        """),
        ("human", prompt)
    ]
    response = llm.invoke(messages)
    return response.content

def extract_panels(story):
    """Extract individual panels from the generated story"""
    panels = []
    current_panel = ""
    
    for line in story.split('\n'):
        if line.strip().startswith("Panel") and current_panel:
            panels.append(current_panel.strip())
            current_panel = line
        else:
            current_panel += "\n" + line
            
    # Add the last panel
    if current_panel:
        panels.append(current_panel.strip())
        
    return panels

def generate_panel_image(description):
    """Generate manga-style image using Together's FLUX model"""
    try:
        # Crafting a manga-specific prompt
        prompt = (
            f"Manga-style illustration: {description}, "
            "monochrome, clean line art, dynamic pose, expressive facial features, "
            "sharp details, screentone shading, speech bubble with dialogue, "
            "high contrast, professional manga panel style."
        )
        
        # Generate the image
        response = together_client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            steps=4
        )
        
        # Use the URL field from the response
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
        return None

# Set page config
st.set_page_config(page_title="Comic - AI", layout="wide", initial_sidebar_state="collapsed")

# Add custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #a388ff;
        font-weight: bold;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
    }
    .book-icon {
        font-size: 2.5rem;
        margin-right: 0.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .panel-container {
        background-color: #f9f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .button-primary {
        background-color: #a388ff;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        border: none;
        cursor: pointer;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "manga_story" not in st.session_state:
    st.session_state.manga_story = None
if "panels" not in st.session_state:
    st.session_state.panels = []
if "panel_images" not in st.session_state:
    st.session_state.panel_images = {}
if "generated_images" not in st.session_state:
    st.session_state.generated_images = False
if "current_story" not in st.session_state:
    st.session_state.current_story = None
if "manga_history" not in st.session_state:
    st.session_state.manga_history = []

# Header
st.markdown('<div class="main-header"><span class="book-icon">📖</span> MANGA - AI</div>', unsafe_allow_html=True)

# Main UI
tab1, tab2 = st.tabs(["Create", "History"])

with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### Story Prompt")
        story_prompt = st.text_area(
            "Story Prompt", 
            height=150,
            label_visibility="collapsed",
            placeholder="Enter your comic story idea here..."
        )
    
    with col2:
        st.markdown("#### Genre")
        genre = st.selectbox(
            "Genre", 
            ["Romance", "Action", "Fantasy", "Sci-Fi", "Horror"],
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Create a container for the generate button at the bottom of the column
        with st.container():
            if st.button("Generate Story", use_container_width=True):
                with st.spinner("Generating your comic story..."):
                    story = generate_manga_story(story_prompt, genre)
                    st.session_state.manga_story = story
                    st.session_state.panels = extract_panels(story)
                    st.session_state.panel_images = {}
                    st.session_state.generated_images = False
                    st.session_state.current_story = {"prompt": story_prompt, "genre": genre, "story": story}
                st.success("Story generated!")
                st.rerun()
    
    # Display panels when story is generated
    if st.session_state.manga_story:
        st.markdown("### Story Panels")
        
        # Create rows of 3 panels each
        panel_rows = [st.session_state.panels[i:i+3] for i in range(0, len(st.session_state.panels), 3)]
        
        for row_panels in panel_rows:
            cols = st.columns(3)
            
            for i, (col, panel) in enumerate(zip(cols, row_panels)):
                panel_index = panel_rows.index(row_panels) * 3 + i
                
                with col:
                    # Create a placeholder for the image
                    img_placeholder = st.empty()
                    
                    # Display the panel image if available
                    if panel_index in st.session_state.panel_images:
                        img_placeholder.image(st.session_state.panel_images[panel_index], use_column_width=True)
                    else:
                        img_placeholder.image("https://via.placeholder.com/300x300?text=Panel+Image", use_column_width=True)
                    
                    # Display panel text
                    panel_text = st.text_area(
                        f"Panel {panel_index + 1}",
                        value=panel,
                        height=150,
                        key=f"panel_{panel_index}"
                    )
                    
                    # Generate image button for each panel
                    if st.button("Generate Image", key=f"gen_img_{panel_index}"):
                        with st.spinner(f"Generating image for panel {panel_index + 1}..."):
                            image_url = generate_panel_image(panel_text)
                            if image_url:
                                st.session_state.panel_images[panel_index] = image_url
                                st.success(f"Image for panel {panel_index + 1} generated!")
                                st.rerun()
        
        # Button to generate all images at once
        if not st.session_state.generated_images:
            if st.button("Generate All Images", use_container_width=True):
                with st.spinner("Generating images for all panels..."):
                    for i, panel in enumerate(st.session_state.panels):
                        if i not in st.session_state.panel_images:
                            image_url = generate_panel_image(panel)
                            if image_url:
                                st.session_state.panel_images[i] = image_url
                    st.session_state.generated_images = True
                    
                    # Save to history
                    if st.session_state.current_story:
                        history_item = st.session_state.current_story.copy()
                        history_item["images"] = st.session_state.panel_images.copy()
                        st.session_state.manga_history.append(history_item)
                        
                st.success("All panel images generated!")
                st.rerun()
        
        # Button to save the completed manga
        if st.session_state.generated_images:
            if st.button("Save Manga", use_container_width=True):
                # Save to history if not already saved
                if st.session_state.current_story:
                    history_item = st.session_state.current_story.copy()
                    history_item["images"] = st.session_state.panel_images.copy()
                    
                    # Check if this exact story is already in history
                    if not any(h["prompt"] == history_item["prompt"] and h["story"] == history_item["story"] for h in st.session_state.manga_history):
                        st.session_state.manga_history.append(history_item)
                
                st.success("Manga saved to history!")

# History tab
with tab2:
    st.markdown("### Your Manga History")
    
    if not st.session_state.manga_history:
        st.info("You haven't created any manga yet. Go to the Create tab to get started!")
    else:
        for i, manga in enumerate(st.session_state.manga_history):
            with st.expander(f"Manga #{i+1}: {manga['prompt'][:50]}..."):
                st.markdown(f"**Genre:** {manga['genre']}")
                st.markdown(f"**Prompt:** {manga['prompt']}")
                
                # Display story and images
                st.markdown("**Story:**")
                st.text(manga['story'])
                
                # Display panels with images
                st.markdown("**Panels:**")
                panels = extract_panels(manga['story'])
                
                # Create rows of 3 panels each
                panel_rows = [panels[i:i+3] for i in range(0, len(panels), 3)]
                
                for row_panels in panel_rows:
                    cols = st.columns(3)
                    
                    for j, (col, panel) in enumerate(zip(cols, row_panels)):
                        panel_index = panel_rows.index(row_panels) * 3 + j
                        
                        with col:
                            # Display panel image if available
                            if 'images' in manga and panel_index in manga['images']:
                                st.image(manga['images'][panel_index], use_column_width=True)
                            
                            # Display panel text
                            st.text_area(
                                f"Panel {panel_index + 1}",
                                value=panel,
                                height=150,
                                key=f"history_panel_{i}_{panel_index}",
                                disabled=True
                            )

# Button to start a new manga (always visible at the top right)
col1, col2, col3 = st.sidebar.columns([1, 1, 1])
with col2:
    if st.button("New Manga"):
        st.session_state.manga_story = None
        st.session_state.panels = []
        st.session_state.panel_images = {}
        st.session_state.generated_images = False
        st.session_state.current_story = None
        st.rerun()