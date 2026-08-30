"""
Business context provider.
Loads and provides business information for the AI assistant.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config import get_settings


class BusinessContext:
    """Manages the business context information."""

    def __init__(self, context_file: Optional[Path] = None):
        self.settings = get_settings()
        if context_file is None:
            # Default to data/business.json in the project root
            self.context_file = Path(__file__).parent.parent.parent / "data" / "business.json"
        else:
            self.context_file = Path(context_file) if isinstance(context_file, str) else context_file

        # Load the business context
        self.context = self._load_context()

    def _load_context(self) -> Dict[str, Any]:
        """Load business context from JSON file.
        If the file doesn't exist, return a default context.
        """
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                # If there's an error, we'll log it and return default
                # In a real app, we might want to raise or handle differently
                print(f"Warning: Could not load business context from {self.context_file}: {e}")
                return self._default_context()
        else:
            # If the file doesn't exist, create a default context and save it
            default_context = self._default_context()
            self._save_context(default_context)
            return default_context

    def _default_context(self) -> Dict[str, Any]:
        """Return a default business context."""
        return {
            "business_name": "Our AI Demo Business",
            "description": "We provide innovative AI-powered solutions for businesses of all sizes.",
            "services": [
                {
                    "name": "Website Development",
                    "description": "Custom website design and development",
                    "price_range": "$500 - $5000",
                    "features": ["Responsive design", "SEO optimized", "CMS included"]
                },
                {
                    "name": "AI Consulting",
                    "description": "Expert advice on implementing AI in your business",
                    "price_range": "$150/hour",
                    "features": ["Strategy development", "Implementation roadmap", "Training"]
                },
                {
                    "name": "Chatbot Development",
                    "description": "Custom AI chatbots for customer service and lead generation",
                    "price_range": "$1000 - $10000",
                    "features": ["Natural language processing", "Integration with websites and apps", "Analytics"]
                }
            ],
            "faqs": [
                {
                    "question": "What is your typical project timeline?",
                    "answer": "Project timelines vary based on scope. Simple websites typically take 2-4 weeks, while more complex AI integrations can take 2-3 months."
                },
                {
                    "question": "Do you offer ongoing support and maintenance?",
                    "answer": "Yes, we offer monthly maintenance packages for websites and AI systems to ensure they remain up-to-date and secure."
                },
                {
                    "question": "What industries do you serve?",
                    "answer": "We work with businesses across various industries including retail, healthcare, finance, education, and technology."
                }
            ],
            "contact_information": {
                "email": "hello@ouraidemo.com",
                "phone": "+1 (555) 123-4567",
                "website": "https://ouraidemo.com"
            },
            "tone": "professional yet friendly, helpful and concise",
            "policies": {
                "refund": "We offer a 30-day money-back guarantee on our services if you're not satisfied.",
                "support": "Standard support is available during business hours (9 AM - 5 PM EST)."
            }
        }

    def _save_context(self, context: Dict[str, Any]) -> None:
        """Save the business context to the JSON file."""
        # Ensure the directory exists
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save business context to {self.context_file}: {e}")

    def get_context(self) -> Dict[str, Any]:
        """Get the full business context."""
        return self.context

    def get_business_name(self) -> str:
        """Get the business name."""
        return self.context.get("business_name", "Our Business")

    def get_description(self) -> str:
        """Get the business description."""
        return self.context.get("description", "")

    def get_services(self) -> list:
        """Get the list of services."""
        return self.context.get("services", [])

    def get_faqs(self) -> list:
        """Get the list of FAQs."""
        return self.context.get("faqs", [])

    def get_contact_information(self) -> dict:
        """Get contact information."""
        return self.context.get("contact_information", {})

    def get_tone(self) -> str:
        """Get the tone/style for the AI."""
        return self.context.get("tone", "professional and helpful")

    def get_policies(self) -> dict:
        """Get business policies."""
        return self.context.get("policies", {})

    def format_context_for_prompt(self) -> str:
        """Format the business context as a string for inclusion in AI prompts."""
        context_str = f"""
Business Information:
- Name: {self.get_business_name()}
- Description: {self.get_description()}

Services Offered:
"""
        for service in self.get_services():
            context_str += f"- {service['name']}: {service['description']} (Price: {service.get('price_range', 'N/A')})\n"

        context_str += "\nFrequently Asked Questions:\n"
        for faq in self.get_faqs():
            context_str += f"Q: {faq['question']}\nA: {faq['answer']}\n"

        context_str += f"\nContact Information:\n"
        contact = self.get_contact_information()
        for key, value in contact.items():
            context_str += f"- {key.capitalize()}: {value}\n"

        context_str += f"\nCommunication Tone: {self.get_tone()}\n"

        policies = self.get_policies()
        if policies:
            context_str += "\nPolicies:\n"
            for key, value in policies.items():
                context_str += f"- {key.capitalize()}: {value}\n"

        return context_str.strip()