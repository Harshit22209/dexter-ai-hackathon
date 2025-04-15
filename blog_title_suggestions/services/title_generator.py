import logging
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import numpy as np
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class TitleGenerator:
    """Service for generating blog title suggestions using NLP models"""
    
    def __init__(self, model_name: str = "t5-base"):
        """Initialize the title generator with the specified model"""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
    def _load_model(self):
        """Load the NLP model (lazy loading to save resources)"""
        if self.model is None or self.tokenizer is None:
            logger.info(f"Loading title generation model: {self.model_name}")
            try:
                self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            except Exception as e:
                logger.error(f"Error loading title generation model: {e}")
                raise
    
    def _preprocess_content(self, content: str) -> str:
        """Preprocess the blog content for input to the model"""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # If content is too long, take the beginning and end
        max_length = 1024
        if len(content) > max_length:
            # Extract beginning paragraphs and conclusion
            paragraphs = content.split('\n\n')
            
            if len(paragraphs) >= 3:
                # Take first paragraph, last paragraph, and one from the middle
                selected = [
                    paragraphs[0],
                    paragraphs[len(paragraphs) // 2],
                    paragraphs[-1]
                ]
                content = ' '.join(selected)
            else:
                # Just truncate if not enough paragraphs
                half_length = max_length // 2
                content = content[:half_length] + " ... " + content[-half_length:]
        
        return content
    
    def _extract_keywords(self, content: str, num_keywords: int = 5) -> List[str]:
        """Extract key phrases from the content"""
        # This is a simplified keyword extraction
        # In a production environment, consider using KeyBERT or similar libraries
        
        # Split into sentences and remove punctuation
        sentences = re.split(r'[.!?]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Simple approach: take first sentence as it often contains key information
        first_sentence = sentences[0] if sentences else ""
        
        # Remove common words (simplified stopwords list)
        stopwords = {"the", "a", "an", "and", "or", "but", "is", "are", "was", "were", 
                    "in", "on", "at", "to", "for", "with", "by", "about", "of"}
        
        words = [word.lower() for word in re.findall(r'\b\w+\b', first_sentence) 
                if word.lower() not in stopwords and len(word) > 3]
        
        # Return most frequent words
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)
        return keywords[:num_keywords]
    
    def _generate_title_with_model(self, content: str) -> List[str]:
        """Generate title suggestions using the T5 model"""
        try:
            self._load_model()
            
            # Prepare the prompt
            prompt = f"summarize: {content}"
            
            # Tokenize the prompt
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
            
            # Generate titles with different parameters
            titles = []
            
            # More creative titles
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=30,
                num_return_sequences=2,
                temperature=0.9,
                top_k=50,
                top_p=0.95,
                do_sample=True,
                early_stopping=True
            )
            for output in outputs:
                title = self.tokenizer.decode(output, skip_special_tokens=True)
                titles.append(title)
            
            # More straightforward title
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=30,
                num_return_sequences=1,
                temperature=0.7,
                early_stopping=True
            )
            title = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            titles.append(title)
            
            # Clean up titles
            titles = [t.strip() for t in titles]
            titles = [t[0].upper() + t[1:] if t else "" for t in titles]  # Capitalize first letter
            
            return titles
            
        except Exception as e:
            logger.error(f"Error generating titles with model: {e}")
            # Fall back to rule-based generation if model fails
            return None
    
    def _generate_title_rule_based(self, content: str, keywords: List[str]) -> List[str]:
        """Generate title suggestions using rule-based approaches"""
        templates = [
            "The Ultimate Guide to {0}",
            "How to Master {0} in Simple Steps",
            "{0}: A Comprehensive Analysis",
            "Understanding {0}: Key Insights and Strategies",
            "The Essential Guide to {0} and {1}",
            "Why {0} Matters in Today's World",
            "{0}: Trends and Future Perspectives"
        ]
        
        titles = []
        
        # Get the first sentence to use as a potential title
        first_sentence = content.split('.')[0].strip()
        if len(first_sentence) < 70 and len(first_sentence) > 10:
            titles.append(first_sentence)
        
        # Use templates with keywords
        for template in templates:
            if "{1}" in template:
                if len(keywords) >= 2:
                    title = template.format(keywords[0].capitalize(), keywords[1].capitalize())
                    titles.append(title)
            else:
                if keywords:
                    title = template.format(keywords[0].capitalize())
                    titles.append(title)
        
        return titles[:5]  # Return up to 5 template-based titles
    
    def generate_title_suggestions(self, content: str, num_suggestions: int = 3) -> List[str]:
        """Generate title suggestions for the given blog content"""
        try:
            # Preprocess content
            processed_content = self._preprocess_content(content)
            
            # Extract keywords
            keywords = self._extract_keywords(processed_content)
            
            # Try model-based generation first
            model_titles = self._generate_title_with_model(processed_content)
            
            # Fall back to rule-based if model fails
            rule_based_titles = self._generate_title_rule_based(processed_content, keywords)
            
            # Combine and select the best suggestions
            all_titles = []
            
            if model_titles:
                all_titles.extend(model_titles)
            
            all_titles.extend(rule_based_titles)
            
            # Remove duplicates and select requested number
            unique_titles = list(dict.fromkeys(all_titles))
            
            return unique_titles[:num_suggestions]
            
        except Exception as e:
            logger.error(f"Error generating title suggestions: {e}")
            
            # Provide basic fallback suggestions
            return [
                "My Blog Post",
                "New Article",
                "Interesting Insights"
            ]