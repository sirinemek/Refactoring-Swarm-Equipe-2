"""
Agent de base pour le Refactoring Swarm
Classe abstraite dont héritent tous les agents spécialisés
"""
import json
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from src.utils import config
from src.utils.logger import log_experiment, ActionType


class BaseAgent:
    """Classe de base pour tous les agents"""
    
    def __init__(self, agent_name: str, system_prompt: str):
        """
        Initialise un agent
        
        Args:
            agent_name: Nom de l'agent (ex: "Auditor_Agent")
            system_prompt: Instructions système pour le LLM
        """
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        
        # Configuration de l'API Gemini
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        # Initialisation du modèle
        self.model = genai.GenerativeModel(
            model_name=config.MODEL_NAME,
            system_instruction=self.system_prompt
        )
        
        print(f"✅ {self.agent_name} initialisé avec {config.MODEL_NAME}")
    
    def call_llm(self, user_prompt: str) -> str:
        """
        Appelle le LLM avec un prompt utilisateur
        
        Args:
            user_prompt: Prompt à envoyer au LLM
            
        Returns:
            Réponse du LLM (texte brut)
        """
        try:
            response = self.model.generate_content(user_prompt)
            return response.text
        except Exception as e:
            raise Exception(f"[{self.agent_name}] Erreur LLM: {str(e)}")
    
    def call_llm_with_retry(self, user_prompt: str, max_retries: int = None) -> str:
        """
        Appelle le LLM avec système de retry
        
        Args:
            user_prompt: Prompt utilisateur
            max_retries: Nombre max de tentatives (défaut: config.MAX_RETRIES)
            
        Returns:
            Réponse du LLM
        """
        if max_retries is None:
            max_retries = config.MAX_RETRIES
        
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return self.call_llm(user_prompt)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Backoff exponentiel
                    print(f"⚠️ [{self.agent_name}] Tentative {attempt}/{max_retries} échouée: {e}")
                    time.sleep(wait_time)
        
        raise Exception(f"[{self.agent_name}] Échec après {max_retries} tentatives: {last_error}")
    
    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse une réponse JSON du LLM
        
        Args:
            response_text: Texte de réponse du LLM
            
        Returns:
            Dictionnaire parsé
        """
        try:
            # Nettoyer la réponse (retirer les balises markdown si présentes)
            cleaned = response_text.strip()
            
            # Retirer ```json et ``` si présents
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Parser le JSON
            return json.loads(cleaned)
            
        except json.JSONDecodeError as e:
            raise Exception(
                f"[{self.agent_name}] Erreur parsing JSON: {e}\n"
                f"Réponse reçue: {response_text[:200]}..."
            )
    
    def safe_call_llm_json(self, 
                          user_prompt: str,
                          action_type: ActionType,
                          additional_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Appelle le LLM et parse la réponse JSON avec logging automatique
        
        Args:
            user_prompt: Prompt utilisateur
            action_type: Type d'action pour le logging
            additional_details: Détails supplémentaires à logger
            
        Returns:
            Réponse parsée en JSON
        """
        response_text = None
        status = "FAILURE"
        
        try:
            # Appeler le LLM
            response_text = self.call_llm_with_retry(user_prompt)
            
            # Parser la réponse
            parsed_response = self.parse_json_response(response_text)
            
            status = "SUCCESS"
            
            return parsed_response
            
        except Exception as e:
            # Logger l'erreur
            error_msg = str(e)
            raise e
            
        finally:
            # Logger l'action (succès ou échec)
            details = additional_details or {}
            details["input_prompt"] = user_prompt[:500]  # Limiter la taille
            details["output_response"] = (response_text[:500] if response_text else "NO_RESPONSE")
            
            if status == "FAILURE":
                details["error"] = error_msg if 'error_msg' in locals() else "Unknown error"
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=config.MODEL_NAME,
                action=action_type,
                details=details,
                status=status
            )
    
    def get_agent_name(self) -> str:
        """Retourne le nom de l'agent"""
        return self.agent_name
