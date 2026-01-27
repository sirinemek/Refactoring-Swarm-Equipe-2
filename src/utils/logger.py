"""
Module de logging standardisé pour l'expérience
"""
import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import hashlib

class ActionType(Enum):
    """Types d'actions standardisés pour les agents"""
    ANALYSIS = "ANALYSIS"
    GENERATION = "GENERATION"
    DEBUG = "DEBUG"
    FIX = "FIX"

@dataclass
class LogEntry:
    """Structure d'une entrée de log"""
    timestamp: str
    agent_name: str
    model_used: str
    action: ActionType
    details: Dict[str, Any]
    status: str
    execution_id: str
    iteration: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON"""
        data = asdict(self)
        data['action'] = self.action.value
        return data

class ExperimentLogger:
    """Logger principal pour l'expérience"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "experiment_data.json")
        self.execution_id = self._generate_execution_id()
        self.iteration = 0
        
        # Créer le dossier logs s'il n'existe pas
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialiser le fichier de log avec encodage UTF-8
        if not os.path.exists(self.log_file):
            self._initialize_log_file()
        else:
            # Si le fichier existe, vérifier son contenu
            self._ensure_valid_json()
    
    def _initialize_log_file(self):
        """Initialise le fichier de log avec une liste vide"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)
    
    def _ensure_valid_json(self):
        """S'assure que le fichier JSON est valide et contient une liste"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Si le fichier est vide, l'initialiser
            if not content.strip():
                self._initialize_log_file()
                return
                
            # Essayer de parser le JSON
            data = json.loads(content)
            
            # Vérifier que c'est une liste
            if not isinstance(data, list):
                print(f"⚠️  Le fichier de logs n'est pas une liste, réinitialisation...")
                self._initialize_log_file()
                
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"⚠️  Erreur de décodage JSON: {str(e)}. Réinitialisation du fichier de logs.")
            self._initialize_log_file()
        except Exception as e:
            print(f"⚠️  Erreur inattendue: {str(e)}. Réinitialisation du fichier de logs.")
            self._initialize_log_file()
    
    def _generate_execution_id(self) -> str:
        """Génère un ID unique pour l'exécution"""
        timestamp = datetime.now().isoformat()
        unique_str = f"{timestamp}_{os.urandom(8).hex()}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]
    
    def _validate_details(self, details: Dict[str, Any]) -> bool:
        """Valide que les champs obligatoires sont présents"""
        required_fields = ['input_prompt', 'output_response']
        
        for field in required_fields:
            if field not in details:
                raise ValueError(f"Champ obligatoire manquant: {field}")
        
        return True
    
    def log(self, 
            agent_name: str, 
            model_used: str, 
            action: ActionType, 
            details: Dict[str, Any], 
            status: str = "SUCCESS") -> None:
        """
        Enregistre une interaction dans le log
        
        Args:
            agent_name: Nom de l'agent
            model_used: Modèle LLM utilisé
            action: Type d'action (enum ActionType)
            details: Détails de l'interaction (doit contenir input_prompt et output_response)
            status: Statut de l'action (SUCCESS, ERROR, etc.)
        """
        try:
            # Valider les détails
            self._validate_details(details)
            
            # Nettoyer les chaînes de caractères pour éviter les problèmes d'encodage
            cleaned_details = self._clean_unicode(details)
            
            # Créer l'entrée de log
            entry = LogEntry(
                timestamp=datetime.now().isoformat(),
                agent_name=agent_name,
                model_used=model_used,
                action=action,
                details=cleaned_details,
                status=status,
                execution_id=self.execution_id,
                iteration=self.iteration
            )
            
            # Lire les logs existants avec encodage UTF-8
            logs = self._load_logs()
            
            # Ajouter la nouvelle entrée
            logs.append(entry.to_dict())
            
            # Écrire dans le fichier avec encodage UTF-8 et ensure_ascii=False
            self._save_logs(logs)
            
        except Exception as e:
            print(f"❌ Erreur lors du logging: {str(e)}")
            raise
    
    def _load_logs(self) -> List[Dict[str, Any]]:
        """Charge les logs depuis le fichier"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                
            # S'assurer que logs est une liste
            if not isinstance(logs, list):
                print("⚠️  Les logs ne sont pas une liste, réinitialisation...")
                logs = []
                self._save_logs(logs)
                
            return logs
            
        except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError) as e:
            print(f"⚠️  Erreur lors du chargement des logs: {str(e)}. Retour d'une liste vide.")
            return []
    
    def _save_logs(self, logs: List[Dict[str, Any]]):
        """Sauvegarde les logs dans le fichier"""
        try:
            # Sauvegarder d'abord dans un fichier temporaire
            temp_file = self.log_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            
            # Remplacer le fichier original
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
            os.rename(temp_file, self.log_file)
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde des logs: {str(e)}")
            raise
    
    def _clean_unicode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie les chaînes de caractères pour éviter les problèmes d'encodage"""
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Nettoyer les caractères non-ASCII problématiques
                cleaned[key] = value.encode('ascii', 'ignore').decode('ascii')
            elif isinstance(value, dict):
                cleaned[key] = self._clean_unicode(value)
            elif isinstance(value, list):
                cleaned[key] = [self._clean_unicode(item) if isinstance(item, dict) else item for item in value]
            else:
                cleaned[key] = value
        return cleaned
    
    def increment_iteration(self):
        """Incrémente le compteur d'itération"""
        self.iteration += 1
    
    def get_execution_id(self) -> str:
        """Retourne l'ID d'exécution"""
        return self.execution_id
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des logs"""
        try:
            logs = self._load_logs()
            
            return {
                "total_entries": len(logs),
                "execution_id": self.execution_id,
                "current_iteration": self.iteration,
                "agents_used": list(set(log['agent_name'] for log in logs)),
                "actions_performed": {
                    action_type.value: sum(1 for log in logs if log['action'] == action_type.value)
                    for action_type in ActionType
                }
            }
        except Exception as e:
            return {"error": f"Impossible de lire les logs: {str(e)}"}

# Instance globale pour faciliter l'import
logger = ExperimentLogger()

def log_experiment(agent_name: str, 
                  model_used: str, 
                  action: ActionType, 
                  details: Dict[str, Any], 
                  status: str = "SUCCESS") -> None:
    """
    Fonction d'interface pour logger une expérience
    
    Args:
        agent_name: Nom de l'agent
        model_used: Modèle LLM utilisé
        action: Type d'action
        details: Détails de l'interaction
        status: Statut de l'action
    """
    logger.log(agent_name, model_used, action, details, status)