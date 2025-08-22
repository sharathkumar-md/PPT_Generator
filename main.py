"""
PPT Generator - PowerPoint Generator CLI
=======================================

Generate PowerPoint presentations on any topic using LLMs and web search.
"""

import click
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Rich console for beautiful output
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

# PPT Generator components
from ppt_generator.config import get_settings, Settings
from ppt_generator.core.search_engine import SearchEngine
from ppt_generator.core.llm_handler import LLMHandler
from ppt_generator.ppt.pptx_generator import PowerPointBuilder
from ppt_generator.ppt.slide_templates import DEFAULT_THEME, DARK_THEME, get_theme

# Initialize rich console
console = Console()


def validate_settings() -> Settings:
    """Validate configuration and return settings"""
    try:
        settings = get_settings()
        
        # Check for required API key
        if not settings.google_api_key:
            console.print("Error: GOOGLE_API_KEY is required in .env file", style="red")
            console.print("Please add your Google AI API key to the .env file")
            sys.exit(1)
        
        # Check search configuration
        search_config = settings.validate_search_config()
        if not search_config["any_search_configured"]:
            console.print("Warning: No search APIs configured", style="yellow")
            console.print("Add GOOGLE_SEARCH_API_KEY to .env for better results")
        
        return settings
        
    except Exception as e:
        console.print(f"Configuration error: {str(e)}", style="red")
        sys.exit(1)


def display_banner():
    """Display application banner"""
    banner = Text("PPT Generator - AI PowerPoint Creator", style="bold blue")
    subtitle = Text("Generate presentations using AI and web search", style="italic")
    
    panel = Panel.fit(
        Text.assemble(banner, "\n", subtitle),
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()


@click.command()
@click.argument('topic', required=True)
@click.option('--output', '-o', 
              default='presentation.pptx',
              help='Output filename for the presentation')
@click.option('--theme', '-t',
              type=click.Choice(['default', 'dark', 'modern', 'corporate', 'minimalist']),
              default='default',
              help='Theme for the presentation')
@click.option('--slides', '-s',
              default=10,
              type=int,
              help='Number of slides to generate')
@click.option('--search-results',
              default=10,
              type=int,
              help='Number of search results to process')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Enable verbose output')
def main(topic: str, output: str, theme: str, slides: int, search_results: int, verbose: bool):
    """
    Generate a PowerPoint presentation on any TOPIC using AI and web search.
    
    TOPIC: The subject for your presentation (e.g., "Artificial Intelligence")
    """
    
    # Display banner
    display_banner()
    
    # Validate configuration
    console.print("Validating configuration...", style="blue")
    settings = validate_settings()
    
    if verbose:
        console.print("Configuration loaded successfully", style="green")
        console.print(f"   Model: {settings.gemini_model_name}")
        console.print(f"   Max tokens: {settings.max_tokens}")
        console.print(f"   Temperature: {settings.temperature}")
        console.print()
    
    # Initialize services
    console.print("Initializing services...", style="blue")
    
    try:
        search_engine = SearchEngine()
        llm_handler = LLMHandler()
        
        if verbose:
            console.print("All services initialized successfully", style="green")
            console.print()
        
    except Exception as e:
        console.print(f"Failed to initialize services: {str(e)}", style="red")
        sys.exit(1)
    
    # Select theme
    console.print(f"Applying theme: {theme}", style="blue")
    try:
        if theme == 'default':
            selected_theme = get_theme('modern')  # Use modern as default
        elif theme == 'dark':
            selected_theme = get_theme('minimalist')  # Use minimalist for dark
        else:
            selected_theme = get_theme(theme)
        
        if verbose:
            console.print(f"Theme '{theme}' loaded successfully", style="green")
            console.print()
            
    except Exception as e:
        console.print(f"Theme error, using default: {str(e)}", style="yellow")
        selected_theme = get_theme('modern')
    
    # Start the workflow
    console.print(f"Generating presentation on: '{topic}'", style="green")
    console.print(f"Target slides: {slides}")
    console.print(f"Search results: {search_results}")
    console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        
        # Step 1: Search for content
        search_task = progress.add_task("Searching for content...", total=None)
        try:
            search_results_data = search_engine.search(topic, num_results=search_results)
            
            if not search_results_data:
                console.print("No search results found. Proceeding with topic analysis only.", style="yellow")
                search_results_data = []
            
            progress.update(search_task, description=f"Found {len(search_results_data)} search results")
            progress.advance(search_task)
            
            if verbose:
                console.print(f"Search results: {len(search_results_data)} items found")
                for i, result in enumerate(search_results_data[:3]):
                    console.print(f"  {i+1}. {result.title[:60]}...")
                console.print()
                
        except Exception as e:
            console.print(f"Search failed: {str(e)}. Continuing without search results.", style="yellow")
            search_results_data = []
        
        # Step 2: Generate presentation with LLM (simplified approach)
        llm_task = progress.add_task("Generating slides with Gemini...", total=None)
        try:
            # Convert search results to simple format for LLM
            search_content = []
            for result in search_results_data:
                search_content.append({
                    'title': result.title,
                    'snippet': result.snippet,
                    'url': result.url,
                    'source': result.source
                })
            
            # Generate complete presentation directly from topic and search results
            presentation_outline = llm_handler.generate_outline(topic, slides, search_content)
            
            # Generate detailed content for each slide
            enhanced_slides = []
            for slide_info in presentation_outline.get('slides', []):
                enhanced_slide = {
                    'type': slide_info.get('type', 'content'),
                    'title': slide_info.get('title', f'Slide {len(enhanced_slides)+1}'),
                    'slide_number': slide_info.get('slide_number', len(enhanced_slides)+1)
                }
                
                # Add subtitle for title slides
                if slide_info.get('type') == 'title':
                    enhanced_slide['subtitle'] = slide_info.get('subtitle', 'A Comprehensive Overview')
                
                # Generate detailed content for non-title slides
                if slide_info.get('type') != 'title' and slide_info.get('key_points'):
                    slide_content = llm_handler.generate_slide_content(
                        enhanced_slide['title'],
                        slide_info['key_points'],
                        search_content[:3]  # Provide some search context
                    )
                    # Merge the generated content
                    enhanced_slide.update(slide_content)
                elif slide_info.get('key_points'):
                    # For title slides or slides without detailed content generation
                    enhanced_slide['key_points'] = slide_info['key_points']
                
                enhanced_slides.append(enhanced_slide)
            
            progress.update(llm_task, description=f"Generated {len(enhanced_slides)} slides")
            progress.advance(llm_task)
            
            if verbose:
                console.print(f"Presentation title: {presentation_outline.get('title', topic)}")
                console.print(f"Generated slides: {len(enhanced_slides)}")
                console.print()
                
        except Exception as e:
            console.print(f"LLM generation failed: {str(e)}", style="red")
            # Create basic outline from search content
            presentation_outline = {
                'title': topic,
                'slides': [
                    {'type': 'title', 'title': topic, 'subtitle': 'Generated Presentation'}
                ]
            }
            # Create basic slides from search results
            enhanced_slides = []
            for i, result in enumerate(search_content[:slides-1]):
                enhanced_slides.append({
                    'type': 'content',
                    'title': result.get('title', f'Topic {i+1}'),
                    'content': result.get('snippet', 'Content from search results')
                })
            console.print("Using basic search content", style="yellow")
        
        # Step 4: Create PowerPoint presentation
        ppt_task = progress.add_task("Building PowerPoint presentation...", total=None)
        try:
            # Initialize PowerPoint builder
            builder = PowerPointBuilder(selected_theme)
            
            # Add title slide - check if first slide in outline is title slide
            first_slide = presentation_outline.get('slides', [{}])[0] if presentation_outline.get('slides') else {}
            if first_slide.get('type') == 'title':
                # Use the title slide from the outline
                title_slide_data = {
                    'type': 'title',
                    'title': first_slide.get('title', topic),
                    'subtitle': first_slide.get('subtitle', f'A Comprehensive Overview')
                }
                builder.add_slide(title_slide_data)
                
                # Add remaining slides (skip first since it's title)
                for slide_data in enhanced_slides[1:]:
                    builder.add_slide(slide_data)
            else:
                # Create a manual title slide
                title_slide_data = {
                    'type': 'title',
                    'title': presentation_outline.get('title', topic),
                    'subtitle': 'A Comprehensive Overview'
                }
                builder.add_slide(title_slide_data)
                
                # Add all content slides
                for slide_data in enhanced_slides:
                    if slide_data.get('type') != 'title':  # Skip duplicate title slides
                        builder.add_slide(slide_data)
            
            progress.update(ppt_task, description="PowerPoint presentation created")
            progress.advance(ppt_task)
            
        except Exception as e:
            console.print(f"PowerPoint creation failed: {str(e)}", style="red")
            sys.exit(1)
        
        # Step 5: Save the presentation
        save_task = progress.add_task("Saving presentation...", total=None)
        try:
            # Ensure output directory exists
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the presentation
            builder.save(str(output_path))
            
            progress.update(save_task, description=f"Saved as {output}")
            progress.advance(save_task)
            
        except Exception as e:
            console.print(f"Failed to save presentation: {str(e)}", style="red")
            sys.exit(1)
    
    # Success message
    console.print()
    success_panel = Panel.fit(
        Text.assemble(
            ("Presentation Generated Successfully!", "bold green"), "\n",
            f"File: {output}\n",
            f"Slides: {builder.get_slide_count()}\n",
            f"Theme: {theme}\n",
            f"Topic: {topic}"
        ),
        border_style="green",
        title="Complete",
        padding=(1, 2)
    )
    console.print(success_panel)
    
    # Additional information
    if verbose:
        console.print()
        console.print("Generation Statistics:", style="blue")
        console.print(f"  Search results processed: {len(search_results_data)}")
        console.print(f"  Search sources found: {len(search_content)}")
        console.print(f"  Total slides created: {builder.get_slide_count()}")
        console.print()
        console.print("Tips:", style="blue")
        console.print("  • Use --verbose (-v) for detailed output")
        console.print("  • Try different themes: modern, corporate, minimalist")
        console.print("  • Adjust slide count with --slides option")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\nGeneration cancelled by user", style="yellow")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n\nUnexpected error: {str(e)}", style="red")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback
            console.print("\nFull traceback:", style="red")
            console.print(traceback.format_exc())
        sys.exit(1)