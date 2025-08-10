# RealtyAI

An intelligent PowerPoint presentation generator that using LLM and web search to create comprehensive presentations on any topic.

## ✨ Features

- **Advanced LLM Integration**: Powered by Google Gemini 2.5-flash with configurable temperature, token limits, and intelligent content generation
- **AI-Powered Content Generation**: Uses Google Gemini LLM to create intelligent, well-structured presentations
- **Web Search Integration**: Incorporates real-time web search results using SerpAPI for up-to-date information
- **Auto-Fit Text Management**: Automatically adjusts text to fit PowerPoint slides perfectly
- **Streamlined Architecture**: Clean, maintainable codebase with minimal dependencies
- **Rich CLI Interface**: Beautiful command-line interface with progress tracking and status updates
- **Customizable Output**: Configurable slide count and output file naming

## Quick Start

- Python 3.8+
- Google AI API key (for Gemini)
- SerpAPI key (for web search)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/sharathkumar-md/RealtyAI.git
cd RealtyAI
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_ai_api_key_here
SERP_API_KEY=your_serp_api_key_here
```

### Usage

Generate a PowerPoint presentation on any topic:

```bash
python main.py "Your Topic Here"
```

**Examples**:
```bash
# Create a 10-slide presentation on Machine Learning
python main.py "Machine Learning Fundamentals" --output ml_basics.pptx --slides 10

# Generate a presentation about Climate Change
python main.py "Climate Change Solutions" --output climate.pptx --slides 12

# Create a business presentation
python main.py "Digital Marketing Strategies 2024" --output marketing.pptx
```

## Architecture

RealtyAI follows a clean, modular architecture:

```
realtyai/
├── core/                    # Core functionality
│   ├── llm_handler.py      # Google Gemini LLM integration
│   └── search_engine.py    # SerpAPI web search
├── ppt/                     # PowerPoint generation
│   ├── pptx_generator.py   # Main PowerPoint generator
│   └── slide_templates.py  # Slide layout templates
└── config.py               # Configuration management
```

### Workflow

1. **Search**: Gathers relevant information from the web using SerpAPI
2. **AI Processing**: Google Gemini processes search results and generates structured content
3. **PowerPoint Generation**: Creates professional presentations with auto-fit text management

## LLM Integration

RealtyAI leverages **Google Gemini** as its core AI engine for intelligent content generation. The LLM integration is designed for optimal performance and reliability.

### Google Gemini Features

- **Model**: Uses `gemini-2.5-flash` for fast, high-quality content generation
- **Context-Aware**: Processes web search results to create relevant, up-to-date content
- **Structured Output**: Generates well-organized presentation outlines with titles, content, and bullet points
- **Configurable Parameters**: Adjustable temperature, token limits, and generation settings

### 🔧 LLM Handler Capabilities

The `LLMHandler` class provides:

```python
# Core content generation
generate_outline(topic, num_slides, search_content)
generate_content(outline, slide_number, search_context)
enhance_content(content, context)
```

### Content Generation Process

1. **Topic Analysis**: Gemini analyzes the input topic and identifies key areas to cover
2. **Search Integration**: Incorporates real-time web search results for current information
3. **Structure Creation**: Generates logical slide progression with titles and detailed content
4. **Content Refinement**: Ensures content fits PowerPoint format with proper bullet points

### LLM Configuration Options

```python
# Available settings in config.py
gemini_model_name: str = "gemini-2.5-flash"
temperature: float = 0.7          # Creativity vs. consistency (0.0-2.0)
max_tokens: int = 2000           # Maximum tokens per request
```

### Content Quality Features

- **Contextual Relevance**: Uses search results to ensure information accuracy
- **Professional Formatting**: Automatically structures content for business presentations
- **Adaptive Length**: Adjusts content depth based on specified slide count
- **Error Handling**: Robust retry mechanisms and fallback content generation

### LLM Best Practices

The integration follows these principles:

- **Efficient Prompting**: Optimized prompts for presentation-specific content
- **Rate Limiting**: Respects API limits with proper request management
- **Content Validation**: Ensures generated content meets quality standards
- **Fallback Handling**: Graceful degradation when API is unavailable

### Advanced LLM Features

- **Multi-Turn Conversations**: Can refine content based on feedback
- **Style Consistency**: Maintains consistent tone across all slides
- **Topic Expansion**: Automatically identifies related subtopics
- **Content Summarization**: Condenses complex information into digestible points

## Configuration

The application uses Pydantic Settings for configuration management. Key settings include:

- **AI Configuration**: Model selection, temperature, token limits
- **Search Settings**: Result limits, search parameters
- **PowerPoint Options**: Default slide counts, formatting preferences

All settings can be configured via environment variables or the `.env` file.

## Requirements

### Core Dependencies
- `google-generativeai`: Google Gemini LLM integration
- `python-pptx`: PowerPoint file generation
- `google-search-results`: SerpAPI integration
- `pydantic-settings`: Configuration management
- `click`: CLI framework
- `rich`: Beautiful terminal output

### Development Dependencies
- `python-dotenv`: Environment variable management


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## API Keys Setup

### Google AI API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GOOGLE_API_KEY`

### SerpAPI Key
1. Sign up at [SerpAPI](https://serpapi.com/)
2. Get your API key from the dashboard
3. Add it to your `.env` file as `SERP_API_KEY`



**PowerPoint Generation Issues**: Check that you have write permissions in the output directory.

## Performance

- **Generation Time**: Typically 30-60 seconds per presentation
- **Slide Capacity**: Supports 1-50 slides per presentation
- **Content Quality**: AI-powered content with web search integration ensures relevant, up-to-date information



**Built with ❤️ by [Sharath Kumar MD](https://github.com/sharathkumar-md)**