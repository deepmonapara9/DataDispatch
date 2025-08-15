import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

from prompts import (
    NEWSLETTER_SYSTEM_PROMPT, 
    NEWSLETTER_CONTENT_PROMPT, 
    HTML_EMAIL_TEMPLATE,
    OLLAMA_SYSTEM_PROMPT,
    SAMPLE_NEWSLETTER_CONTENT
)

load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        # Default to the user's desired model alias; we'll normalize to a valid Ollama tag
        self.ollama_model_input = os.getenv("OLLAMA_MODEL", "llama:3.2:1b")
        self.ollama_model = self._normalize_ollama_model(self.ollama_model_input)
        # Select provider: default to Ollama unless explicitly set to openai
        provider = os.getenv("AI_PROVIDER", "ollama").lower()
        self.use_openai = (provider == "openai") and bool(self.openai_api_key)
        
    def _normalize_ollama_model(self, model: str) -> str:
        """Normalize common aliases to official Ollama tags."""
        alias_map = {
            # User-friendly aliases mapped to common instruct tag
            "llama:3.2:1b": "llama3.2:1b-instruct",
            "llama3.2:1b": "llama3.2:1b-instruct",
            "llama-3.2-1b": "llama3.2:1b-instruct",
            "llama-3.2:1b": "llama3.2:1b-instruct",
            # Fallbacks without instruct
            "llama3.2": "llama3.2:1b-instruct",
        }
        normalized = alias_map.get(model.strip().lower(), model)
        # Keep the original if it already looks like an ollama tag with a colon version
        return normalized
        
    def generate_newsletter_content(self) -> Dict[str, str]:
        """
        Generate newsletter content using AI (OpenAI or Ollama)
        Returns: Dict with 'subject' and 'html' keys
        """
        try:
            if self.use_openai:
                return self._generate_with_openai()
            else:
                return self._generate_with_ollama()
        except Exception as e:
            print(f"❌ AI generation failed: {str(e)}")
            print("📝 Using fallback sample content...")
            return self._get_fallback_content()
    
    def _generate_with_openai(self) -> Dict[str, str]:
        """Generate content using OpenAI API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_api_key)
            
            current_date = datetime.now().strftime("%B %d, %Y")
            prompt = NEWSLETTER_CONTENT_PROMPT.format(current_date=current_date)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": NEWSLETTER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = (response.choices[0].message.content or "").strip()
            
            # Try to parse JSON response
            try:
                result = json.loads(content)
                if "subject" in result and "html" in result:
                    # Wrap HTML content in email template
                    result["html"] = self._wrap_in_email_template(result["subject"], result["html"])
                    return result
                else:
                    raise ValueError("Invalid response format from OpenAI")
            except json.JSONDecodeError:
                # If not JSON, try to extract content
                return self._extract_content_from_text(content)
                
        except ImportError:
            print("❌ OpenAI library not installed. Install with: pip install openai")
            return self._get_fallback_content()
        except Exception as e:
            print(f"❌ OpenAI API error: {str(e)}")
            return self._get_fallback_content()
    
    def _generate_with_ollama(self) -> Dict[str, str]:
        """Generate content using Ollama local LLM"""
        try:
            current_date = datetime.now().strftime("%B %d, %Y")
            user_prompt = f"""
            {OLLAMA_SYSTEM_PROMPT}
            
            Generate a tech newsletter for {current_date}. Include:
            - Latest AI developments
            - New developer tools
            - Programming insights
            - Quick tips for developers
            
            Return only valid JSON with 'subject' and 'html' keys.
            Subject max 60 characters.
            """
            
            payload = {
                "model": self.ollama_model,
                "prompt": user_prompt,
                # Ask Ollama to enforce JSON where supported
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "").strip()
                
                # Try to parse JSON response
                try:
                    parsed = json.loads(content)
                    if "subject" in parsed and "html" in parsed:
                        # Wrap HTML content in email template
                        parsed["html"] = self._wrap_in_email_template(parsed["subject"], parsed["html"])
                        return parsed
                    else:
                        raise ValueError("Invalid response format from Ollama")
                except json.JSONDecodeError:
                    # If not JSON, try to extract content
                    return self._extract_content_from_text(content)
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama connection error: {str(e)}")
            print("💡 Make sure Ollama is running: ollama serve")
            print(f"💡 If model not present, pull it: ollama pull {self.ollama_model}")
            return self._get_fallback_content()
        except Exception as e:
            print(f"❌ Ollama error: {str(e)}")
            return self._get_fallback_content()
    
    def _wrap_in_email_template(self, subject: str, content: str) -> str:
        """Wrap content in HTML email template"""
        return HTML_EMAIL_TEMPLATE.format(
            subject=subject,
            content_sections=content
        )
    
    def _extract_content_from_text(self, text: str) -> Dict[str, str]:
        """Extract content from non-JSON text response"""
        # Simple fallback if AI doesn't return proper JSON
        lines = text.split('\n')
        subject = "🚀 Weekly AI & Tech Update"
        
        # Try to find a subject line
        for line in lines:
            if any(word in line.lower() for word in ['subject:', 'title:', '🚀', '📧']):
                subject = line.replace('Subject:', '').replace('Title:', '').strip()[:60]
                break
        
        # Use the full text as HTML content
        html_content = f"""
        <div class="section">
            <h2 class="section-title">📝 This Week's Update</h2>
            <div class="section-content">
                <div class="item">
                    <div class="item-description">
                        {text.replace('\n', '<br>')}
                    </div>
                </div>
            </div>
        </div>
        """
        
        return {
            "subject": subject,
            "html": self._wrap_in_email_template(subject, html_content)
        }
    
    def _get_fallback_content(self) -> Dict[str, str]:
        """Return fallback content when AI generation fails"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Use sample content with current date
        content = SAMPLE_NEWSLETTER_CONTENT.copy()
        content["subject"] = f"🚀 Tech Update for {current_date}"
        content["html"] = self._wrap_in_email_template(content["subject"], content["html"])
        
        return content
    
    def test_ai_connection(self) -> Dict[str, bool]:
        """Test AI service connections"""
        results = {
            "openai": False,
            "ollama": False
        }
        
        # Test OpenAI
        if self.openai_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                # Simple test request
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                results["openai"] = True
                print("✅ OpenAI connection successful")
            except Exception as e:
                print(f"❌ OpenAI connection failed: {str(e)}")
        
        # Test Ollama
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                if any(self.ollama_model in name or name.startswith(self.ollama_model) for name in model_names):
                    results["ollama"] = True
                    print(f"✅ Ollama connection successful (model: {self.ollama_model})")
                else:
                    print(f"❌ Ollama model '{self.ollama_model}' not found. Available: {', '.join(model_names) or 'none'}")
                    print(f"💡 Pull the model: ollama pull {self.ollama_model}")
            else:
                print(f"❌ Ollama API error: {response.status_code}")
        except Exception as e:
            print(f"❌ Ollama connection failed: {str(e)}")
        
        return results

def main():
    """Test the content generator"""
    print("🤖 Testing AI Content Generator...")
    
    generator = ContentGenerator()
    
    # Test connections
    print("\n📡 Testing AI connections...")
    connections = generator.test_ai_connection()
    
    if not any(connections.values()):
        print("⚠️  No AI services available. Will use fallback content.")
    
    # Generate content
    print("\n📝 Generating newsletter content...")
    start_time = time.time()
    
    content = generator.generate_newsletter_content()
    
    end_time = time.time()
    generation_time = round(end_time - start_time, 2)
    
    print(f"✅ Content generated in {generation_time}s")
    print(f"📧 Subject: {content['subject']}")
    print(f"📄 HTML length: {len(content['html'])} characters")
    
    # Save to file for inspection
    with open("/tmp/sample_newsletter.html", "w", encoding="utf-8") as f:
        f.write(content["html"])
    print("💾 Sample saved to /tmp/sample_newsletter.html")
    
    return content

if __name__ == "__main__":
    main()
