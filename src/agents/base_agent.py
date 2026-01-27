"""
Classe de base pour tous les agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

from ..utils.logger import log_experiment, ActionType

load_dotenv()

class BaseAgent(ABC):
    """Agent de base avec fonctionnalités communes"""
    
    def __init__(self, name: str, model: str = "gemini-2.5-flash"):
        """
        Initialise l'agent
        
        Args:
            name: Nom de l'agent
            model: Modèle à utiliser
        """
        self.name = name
        self.model_name = model
        
        # Initialiser le LLM
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY non configurée dans .env")
        
        # Gemini ne supporte pas les messages système, on utilise convert_system_message_to_human
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.1,
            max_output_tokens=2048,
            convert_system_message_to_human=True  # Important pour Gemini
        )
        
        self.system_prompt = None
    
    def set_system_prompt(self, prompt: str):
        """Définit le prompt système"""
        self.system_prompt = prompt
    
    def create_messages(self, human_input: str, context: Dict[str, Any] = None) -> List:
        """
        Crée les messages pour le LLM
        
        Args:
            human_input: Input utilisateur
            context: Contexte supplémentaire
            
        Returns:
            Liste des messages
        """
        messages = []
        
        # Pour Gemini, on combine le prompt système avec l'input humain
        if self.system_prompt:
            # Remplacer les variables dans le prompt système
            system_content = self.system_prompt
            if context:
                for key, value in context.items():
                    placeholder = f"{{{key}}}"
                    if placeholder in system_content:
                        system_content = system_content.replace(placeholder, str(value))
            
            # Gemini ne supporte pas SystemMessage, on utilise HumanMessage
            messages.append(HumanMessage(content=system_content))
        
        # Ajouter l'input humain
        messages.append(HumanMessage(content=human_input))
        
        return messages
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une requête (à implémenter par chaque agent)
        
        Args:
            input_data: Données d'entrée
            
        Returns:
            Résultat du traitement
        """
        pass
    
    def call_llm(self, prompt: str, context: Dict[str, Any] = None, action_type: ActionType = None) -> str:
        """
        Appelle le LLM avec logging
        
        Args:
            prompt: Prompt à envoyer
            context: Contexte supplémentaire
            action_type: Type d'action pour le logging
            
        Returns:
            Réponse du LLM
        """
        try:
            # Créer les messages
            messages = self.create_messages(prompt, context)
            
            # Appeler le LLM
            response = self.llm.invoke(messages)
            response_content = response.content
            
            # Logger l'interaction
            if action_type:
                log_experiment(
                    agent_name=self.name,
                    model_used=self.model_name,
                    action=action_type,
                    details={
                        'input_prompt': prompt,
                        'output_response': response_content,
                        'context': context or {},
                        'agent_name': self.name
                    },
                    status="SUCCESS"
                )
            
            return response_content
            
        except Exception as e:
            # Logger l'erreur
            if action_type:
                log_experiment(
                    agent_name=self.name,
                    model_used=self.model_name,
                    action=action_type,
                    details={
                        'input_prompt': prompt,
                        'output_response': f"ERREUR: {str(e)}",
                        'context': context or {},
                        'agent_name': self.name,
                        'error': str(e)
                    },
                    status="ERROR"
                )
            
            raise
    
    def validate_response_format(self, response: str, expected_format: str = "JSON") -> bool:
        """
        Valide le format de la réponse
        
        Args:
            response: Réponse à valider
            expected_format: Format attendu
            
        Returns:
            True si valide
        """
        if expected_format == "JSON":
            try:
                import json
                # Essayer de parser comme JSON
                json.loads(response)
                return True
            except:
                # Vérifier si c'est du JSON partiel
                if response.strip().startswith('{') and response.strip().endswith('}'):
                    return True
                return False
        return True