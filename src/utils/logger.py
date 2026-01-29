"""
Système de logging pour le Refactoring Swarm
Conforme au protocole de logging du TP
"""
import json
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Dict, Any, Optional
from src.utils import config


class ActionType(Enum):
    """Types d'actions standardisés (NE PAS MODIFIER)"""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    DEBUG = "debug"
    FIX = "fix"


class ExperimentLogger:
    """Logger singleton pour les données d'expérimentation"""
    
    _instance = None
    _data = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExperimentLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._data = []
        
        # Charger les données existantes si le fichier existe
        if config.EXPERIMENT_LOG_FILE.exists():
            try:
                with open(config.EXPERIMENT_LOG_FILE, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except json.JSONDecodeError:
                self._data = []
    
    def log_action(self, 
                   agent_name: str,
                   model_used: str,
                   action: ActionType,
                   details: Dict[str, Any],
                   status: str = "SUCCESS") -> None:
        """
        Enregistre une action d'agent (CONFORME AU PROTOCOLE)
        
        Args:
            agent_name: Nom de l'agent (ex: "Auditor_Agent")
            model_used: Modèle LLM utilisé (ex: "gemini-2.5-flash")
            action: Type d'action (utiliser ActionType enum)
            details: Dictionnaire contenant les détails
                     DOIT contenir: "input_prompt" et "output_response"
            status: Statut de l'action ("SUCCESS", "FAILURE", "RETRY")
        """
        # Validation des champs obligatoires
        if "input_prompt" not in details:
            raise ValueError("❌ Le champ 'input_prompt' est OBLIGATOIRE dans details")
        
        if "output_response" not in details:
            raise ValueError("❌ Le champ 'output_response' est OBLIGATOIRE dans details")
        
        # Créer l'entrée de log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "model_used": model_used,
            "action_type": action.value,
            "status": status,
            "details": details
        }
        
        # Ajouter à la liste
        self._data.append(log_entry)
        
        # Sauvegarder immédiatement
        self._save()
        
        # Afficher si verbose
        if config.VERBOSE:
            status_emoji = "✅" if status == "SUCCESS" else "❌" if status == "FAILURE" else "🔄"
            print(f"📝 [LOG] {agent_name} | {action.value} | {status_emoji} {status}")
    
    def _save(self) -> None:
        """Sauvegarde les données dans le fichier JSON"""
        try:
            with open(config.EXPERIMENT_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde des logs: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les actions loggées"""
        if not self._data:
            return {
                "total_actions": 0,
                "success_rate": 0,
                "actions_by_agent": {},
                "actions_by_type": {}
            }
        
        total = len(self._data)
        success = sum(1 for entry in self._data if entry["status"] == "SUCCESS")
        
        # Par agent
        by_agent = {}
        for entry in self._data:
            agent = entry["agent_name"]
            by_agent[agent] = by_agent.get(agent, 0) + 1
        
        # Par type d'action
        by_type = {}
        for entry in self._data:
            action = entry["action_type"]
            by_type[action] = by_type.get(action, 0) + 1
        
        return {
            "total_actions": total,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "actions_by_agent": by_agent,
            "actions_by_type": by_type
        }
    
    def clear(self) -> None:
        """Efface tous les logs (ATTENTION: utiliser avec précaution)"""
        self._data = []
        self._save()


# ============================================================================
# FONCTION GLOBALE (Pour faciliter l'utilisation)
# ============================================================================

_logger = ExperimentLogger()


def log_experiment(agent_name: str,
                   model_used: str,
                   action: ActionType,
                   details: Dict[str, Any],
                   status: str = "SUCCESS") -> None:
    """
    Fonction globale pour logger une action
    
    Usage:
        from src.utils.logger import log_experiment, ActionType
        
        log_experiment(
            agent_name="Auditor_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.ANALYSIS,
            details={
                "file_analyzed": "test.py",
                "input_prompt": "Analyse ce code...",
                "output_response": "J'ai trouvé 3 bugs...",
                "issues_found": 3
            },
            status="SUCCESS"
        )
    """
    _logger.log_action(agent_name, model_used, action, details, status)


def get_logger_stats() -> Dict[str, Any]:
    """Retourne les statistiques du logger"""
    return _logger.get_statistics()


def clear_logs() -> None:
    """Efface tous les logs"""
    _logger.clear()
