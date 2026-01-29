"""
Outils pour l'analyse et les tests de code Python
"""
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional
import re


def run_pylint(file_path: str) -> str:
    """
    Exécute Pylint sur un fichier Python
    
    Args:
        file_path: Chemin du fichier à analyser
        
    Returns:
        Sortie complète de Pylint
    """
    try:
        result = subprocess.run(
            ["pylint", file_path, "--output-format=text"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Error: Pylint timeout"
    except FileNotFoundError:
        return "Error: Pylint not installed. Run: pip install pylint"
    except Exception as e:
        return f"Error running Pylint: {str(e)}"


def parse_pylint_output(pylint_output: str) -> Tuple[float, str]:
    """
    Parse la sortie de Pylint pour extraire le score et le rapport
    
    Args:
        pylint_output: Sortie brute de Pylint
        
    Returns:
        (score, rapport_formaté)
    """
    # Chercher le score dans la sortie
    score_match = re.search(r"Your code has been rated at ([\d\.-]+)/10", pylint_output)
    
    if score_match:
        score = float(score_match.group(1))
    else:
        # Pas de score trouvé (probablement erreur)
        score = 0.0
    
    # Nettoyer le rapport
    lines = pylint_output.split("\n")
    
    # Garder seulement les lignes importantes
    important_lines = []
    skip_section = False
    
    for line in lines:
        # Ignorer les sections de statistiques détaillées
        if "---" in line or "=====" in line:
            skip_section = True
            continue
        
        if line.startswith("Your code has been rated"):
            skip_section = False
            important_lines.append(line)
            continue
        
        if not skip_section and line.strip():
            # Garder les lignes avec des messages d'erreur/warning
            if any(x in line for x in [":", "****", "Your code", "rated"]):
                important_lines.append(line)
    
    report = "\n".join(important_lines[:50])  # Limiter à 50 lignes
    
    return score, report


def run_pytest(test_file_or_dir: str) -> str:
    """
    Exécute pytest sur un fichier ou répertoire de tests
    
    Args:
        test_file_or_dir: Chemin du fichier/répertoire de test
        
    Returns:
        Sortie de pytest
    """
    try:
        result = subprocess.run(
            ["pytest", test_file_or_dir, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Pytest timeout"
    except FileNotFoundError:
        return "Error: Pytest not installed. Run: pip install pytest"
    except Exception as e:
        return f"Error running Pytest: {str(e)}"


def check_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """
    Vérifie la syntaxe Python d'un code
    
    Args:
        code: Code Python à vérifier
        
    Returns:
        (est_valide, message_erreur)
    """
    try:
        compile(code, "<string>", "exec")
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError ligne {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def read_file_safe(file_path: Path) -> Optional[str]:
    """
    Lit un fichier de manière sécurisée
    
    Args:
        file_path: Chemin du fichier
        
    Returns:
        Contenu du fichier ou None si erreur
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Essayer avec une autre encodage
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return None
    except Exception as e:
        print(f"⚠️ Erreur lecture {file_path}: {e}")
        return None


def write_file_safe(file_path: Path, content: str) -> bool:
    """
    Écrit dans un fichier de manière sécurisée
    
    Args:
        file_path: Chemin du fichier
        content: Contenu à écrire
        
    Returns:
        True si succès
    """
    try:
        # Créer le répertoire parent si nécessaire
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ Erreur écriture {file_path}: {e}")
        return False


def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """
    Vérifie qu'un chemin est dans le répertoire autorisé (sécurité)
    
    Args:
        base_dir: Répertoire de base autorisé
        target_path: Chemin à vérifier
        
    Returns:
        True si le chemin est sûr
    """
    try:
        # Résoudre les chemins absolus
        base = base_dir.resolve()
        target = target_path.resolve()
        
        # Vérifier que target est un sous-chemin de base
        return str(target).startswith(str(base))
    except Exception:
        return False


def create_test_file(file_path: Path, test_content: str) -> bool:
    """
    Crée un fichier de test temporaire
    
    Args:
        file_path: Chemin du fichier de test
        test_content: Contenu du test
        
    Returns:
        True si succès
    """
    return write_file_safe(file_path, test_content)


def execute_python_safe(code: str, timeout: int = 5) -> Tuple[bool, str]:
    """
    Exécute du code Python dans un environnement isolé
    
    Args:
        code: Code à exécuter
        timeout: Timeout en secondes
        
    Returns:
        (succès, output_ou_erreur)
    """
    try:
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Exécuter
        result = subprocess.run(
            ["python", temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Nettoyer
        Path(temp_file).unlink()
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "Timeout: code execution took too long"
    except Exception as e:
        return False, f"Execution error: {str(e)}"


def count_lines(code: str) -> int:
    """Compte le nombre de lignes de code (hors commentaires et lignes vides)"""
    lines = code.split("\n")
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            count += 1
    return count


def extract_functions(code: str) -> list:
    """
    Extrait les noms des fonctions définies dans le code
    
    Returns:
        Liste des noms de fonctions
    """
    import ast
    
    try:
        tree = ast.parse(code)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        return functions
    except:
        return []
