"""
Core LLM judge evaluation logic.
"""
import json
import time
from typing import Dict, List, Any
from openai import OpenAI
from src.config import (
    OPENAI_API_KEY,
    MODEL_NAME,
    CONVERSATIONS_FILE,
    RUBRIC_FILE,
    MAX_RETRIES,
    RETRY_DELAY,
    JSON_SCHEMA,
)


class LLMJudge:
    """LLM Judge for evaluating conversations."""
    
    def __init__(self, prompt_template: str):
        """
        Initialize LLM Judge.
        
        Args:
            prompt_template: The prompt template to use for evaluation
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.prompt_template = prompt_template
        self.rubric = self._load_rubric()
    
    def _load_rubric(self) -> str:
        """Load the rubric from file."""
        with open(RUBRIC_FILE, 'r') as f:
            return f.read()
    
    def load_conversations(self) -> List[Dict[str, Any]]:
        """Load conversations from JSON file."""
        with open(CONVERSATIONS_FILE, 'r') as f:
            data = json.load(f)
        
        # Flatten the conversation structure
        conversations = []
        for item in data:
            set_id = item['set_id']
            for conv in item['conversations']:
                conversation_text = self._format_conversation(conv['exchanges'])
                conversations.append({
                    'conversation_id': set_id,
                    'exchanges': conv['exchanges'],
                    'conversation_text': conversation_text
                })
        
        return conversations
    
    def _format_conversation(self, exchanges: List[Dict[str, str]]) -> str:
        """
        Format conversation exchanges into a readable string.
        
        Args:
            exchanges: List of exchanges with 'role' and 'content'
        
        Returns:
            Formatted conversation string
        """
        formatted = []
        for i, exchange in enumerate(exchanges, 1):
            role = exchange['role']
            content = exchange['content']
            
            if role == 'user':
                formatted.append(f"Q{(i+1)//2}: {content}")
            else:
                formatted.append(f"A{(i+1)//2}: {content}")
        
        return "\n\n".join(formatted)
    
    def create_system_prompt(self) -> str:
        """
        Create the system prompt from template and rubric.
        
        Returns:
            System prompt string
        """
        system_prompt = f"""{self.prompt_template}

# RUBRIC

{self.rubric}"""
        
        return system_prompt
    
    def create_user_message(self, conversation_text: str) -> str:
        """
        Create the user message with conversation to evaluate.
        
        Args:
            conversation_text: The formatted conversation text
        
        Returns:
            User message string
        """
        user_message = f"""# CONVERSATION TO EVALUATE

{conversation_text}

# YOUR EVALUATION

Please evaluate the above conversation according to the rubric and provide your analysis."""
        
        return user_message
    
    def evaluate_conversation(self, conversation: Dict[str, Any], 
                            retry_count: int = 0) -> Dict[str, Any]:
        """
        Evaluate a single conversation.
        
        Args:
            conversation: Conversation dict with 'conversation_id' and 'conversation_text'
            retry_count: Current retry attempt
        
        Returns:
            Dict with conversation_id and LLM response
        """
        system_prompt = self.create_system_prompt()
        user_message = self.create_user_message(conversation['conversation_text'])
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_completion_tokens=4000,
                response_format={
                    "type": "json_schema",
                    "json_schema": JSON_SCHEMA
                }
            )
            
            result = {
                'conversation_id': conversation['conversation_id'],
                'llm_response': response.choices[0].message.content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens,
                }
            }
            
            return result
            
        except Exception as e:
            if retry_count < MAX_RETRIES:
                print(f"Error evaluating conversation {conversation['conversation_id']}: {e}")
                print(f"Retrying... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY * (retry_count + 1))
                return self.evaluate_conversation(conversation, retry_count + 1)
            else:
                print(f"Failed to evaluate conversation {conversation['conversation_id']} after {MAX_RETRIES} retries")
                return {
                    'conversation_id': conversation['conversation_id'],
                    'llm_response': None,
                    'error': str(e)
                }
    
    def prepare_batch_input(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare conversations for batch API format.
        
        Args:
            conversations: List of conversation dicts
        
        Returns:
            List of batch API request objects
        """
        batch_requests = []
        system_prompt = self.create_system_prompt()
        
        for conversation in conversations:
            user_message = self.create_user_message(conversation['conversation_text'])
            
            request = {
                "custom_id": f"eval-{conversation['conversation_id']}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_completion_tokens": 4000,
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": JSON_SCHEMA
                    }
                }
            }
            
            batch_requests.append(request)
        
        return batch_requests

