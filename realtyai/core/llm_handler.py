"""
LLM Handler module for RealtyAI
Manages interactions with Google Gemini for content generation
"""

import google.generativeai as genai
import json
from typing import List, Dict, Any, Optional
import logging
from ..config import get_settings

logger = logging.getLogger(__name__)


class LLMHandler:
    """Handler for Google Gemini AI interactions"""
    
    def __init__(self, model: str = None, api_key: str = None):
        """
        Initialize LLM Handler
        
        Args:
            model: Model name to use (default from config)
            api_key: Google API key (default from config)
        """
        settings = get_settings()
        self.model = model or settings.gemini_model_name
        self.api_key = api_key or settings.google_api_key
        
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
    
    def generate_outline(self, topic: str, num_slides: int = None, 
                        search_content: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a presentation outline for the given topic
        
        Args:
            topic: Presentation topic
            num_slides: Number of slides (default from config)
            search_content: Optional search results to enhance content
        
        Returns:
            Dictionary containing outline structure
        """
        if num_slides is None:
            settings = get_settings()
            num_slides = settings.default_slide_count
        
        # Prepare search context if available
        search_context = ""
        if search_content:
            search_context = "\n\nSearch Context to incorporate:\n"
            for i, result in enumerate(search_content[:5]):  # Limit to top 5 results
                search_context += f"{i+1}. {result.get('title', '')}: {result.get('snippet', '')}\n"
        
        prompt = f"""
        You are a presentation expert. Create a detailed presentation outline for the topic: "{topic}"
        {search_context}
        
        CRITICAL: You must respond with ONLY valid JSON, no additional text or explanations.
        
        Requirements:
        - Generate exactly {num_slides} slides following this specific structure:
          Slide 1: Title (with topic name and compelling subtitle)
          Slide 2: Overview (introduction and background)
          Slides 3-{num_slides-1}: Key points/trends/arguments (main content)
          Slide {num_slides}: Conclusion/Takeaways (summary and key insights)
        - Use the search context provided to create more accurate and relevant content
        - Incorporate specific facts, data, and insights from the search results
        
        JSON Response Format (respond with ONLY this JSON structure):
        {{
            "title": "{topic}",
            "slides": [
                {{
                    "slide_number": 1,
                    "title": "{topic}",
                    "type": "title",
                    "subtitle": "A Comprehensive Overview",
                    "key_points": []
                }},
                {{
                    "slide_number": 2,
                    "title": "Overview",
                    "type": "content",
                    "key_points": ["Introduction and definition", "Background context", "Why this topic matters", "What we'll explore"]
                }},
                {{
                    "slide_number": 3,
                    "title": "Key Point 1",
                    "type": "content", 
                    "key_points": ["First major aspect", "Supporting details", "Real-world examples"]
                }}
            ]
        }}
        
        Create exactly {num_slides} slides following this structure. Ensure slide titles are clear headlines.
        """
        
        try:
            response = self.client.generate_content(prompt)
            content = response.text.strip()
            
            # Clean the response - remove any text before/after JSON
            content = self._extract_json_from_response(content)
            
            # Try to parse JSON response
            try:
                outline = json.loads(content)
                # Validate the structure
                if self._validate_outline_structure(outline):
                    return outline
                else:
                    logger.error("Invalid outline structure received from AI")
                    raise Exception("AI generated invalid outline structure")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Raw response: {content[:200]}...")
                raise Exception(f"AI generated invalid JSON: {str(e)}")
        
        except Exception as e:
            logger.error(f"Failed to generate outline: {str(e)}")
            raise Exception(f"Failed to generate presentation outline: {str(e)}")
    
    def generate_slide_content(self, slide_title: str, key_points: List[str], 
                             research_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate detailed content for a specific slide
        
        Args:
            slide_title: Title of the slide
            key_points: Key points to cover
            research_data: Additional research data from web search
        
        Returns:
            Dictionary with slide content
        """
        research_context = ""
        if research_data:
            research_context = "\n\nAdditional Research Data:\n"
            for item in research_data[:3]:  # Limit to top 3 results
                research_context += f"- {item.get('title', '')}: {item.get('snippet', '')}\n"
        
        prompt = f"""
        You are an expert content creator. Create detailed content for a presentation slide.
        
        CRITICAL: Respond with ONLY valid JSON, no additional text.
        
        Slide Title: {slide_title}
        Key Points to Cover: {', '.join(key_points) if key_points else 'General information about the topic'}
        {research_context}
        
        JSON Response Format (respond with ONLY this JSON structure):
        {{
            "title": "{slide_title}",
            "bullet_points": [
                {{"point": "First key concept", "details": "Detailed explanation of the concept"}},
                {{"point": "Second important aspect", "details": "Comprehensive details and examples"}},
                {{"point": "Third crucial element", "details": "In-depth explanation with context"}}
            ],
            "statistics": ["Relevant statistic or fact", "Another important data point"],
            "conclusion": "Key takeaway from this slide"
        }}
        
        Provide 3-5 bullet points with meaningful content. Do not include any text outside the JSON.
        """
        
        try:
            response = self.client.generate_content(prompt)
            content = response.text.strip()
            
            # Clean the response
            content = self._extract_json_from_response(content)
            
            try:
                slide_content = json.loads(content)
                if self._validate_slide_content_structure(slide_content):
                    return slide_content
                else:
                    logger.error("Invalid slide content structure received from AI")
                    raise Exception("AI generated invalid slide content structure")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse slide content JSON: {str(e)}")
                raise Exception(f"AI generated invalid JSON: {str(e)}")
        
        except Exception as e:
            logger.error(f"Failed to generate slide content: {str(e)}")
            raise Exception(f"Failed to generate slide content: {str(e)}")
    
    def refine_content(self, content: str, requirements: str = "") -> str:
        """
        Refine and improve existing content
        
        Args:
            content: Content to refine
            requirements: Specific requirements for refinement
        
        Returns:
            Refined content as string
        """
        prompt = f"""
        Please refine and improve the following content for a presentation:
        
        Original Content:
        {content}
        
        Requirements:
        {requirements if requirements else "Make it more engaging, clear, and professional."}
        
        Return only the refined content without additional formatting.
        """
        
        try:
            full_prompt = f"You are an expert editor. Improve content clarity and engagement.\n\n{prompt}"
            response = self.client.generate_content(full_prompt)
            return response.text.strip()
        
        except Exception as e:
            logger.error(f"Failed to refine content: {str(e)}")
            return content  # Return original content if refinement fails
    
    
    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON from a response that might contain additional text"""
        
        # Try to find JSON object boundaries
        start_idx = content.find('{')
        if start_idx == -1:
            return content
        
        # Find the matching closing brace
        brace_count = 0
        end_idx = start_idx
        
        for i, char in enumerate(content[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        return content[start_idx:end_idx]
    
    def _validate_outline_structure(self, outline: Dict[str, Any]) -> bool:
        """Validate that the outline has the required structure"""
        required_keys = ["title", "slides"]
        
        if not all(key in outline for key in required_keys):
            return False
        
        if not isinstance(outline["slides"], list) or len(outline["slides"]) == 0:
            return False
        
        # Validate each slide
        for slide in outline["slides"]:
            slide_keys = ["slide_number", "title", "type"]
            if not all(key in slide for key in slide_keys):
                return False
        
        return True
    
    def _validate_slide_content_structure(self, content: Dict[str, Any]) -> bool:
        """Validate that slide content has the required structure"""
        required_keys = ["title", "bullet_points"]
        
        if not all(key in content for key in required_keys):
            return False
        
        if not isinstance(content["bullet_points"], list):
            return False
        
        return True
    
