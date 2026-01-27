"""
Outils disponibles pour les agents
"""
import os
import subprocess
import ast
import json
from typing import List, Dict, Any, Tuple
import tempfile
import shutil

class CodeTools:
    """Outils pour manipuler le code"""
    
    @staticmethod
    def read_file(filepath: str) -> str:
        """
        Lit le contenu d'un fichier
        
        Args:
            filepath: Chemin vers le fichier
            
        Returns:
            Contenu du fichier
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback pour l'encodage Windows
            with open(filepath, 'r', encoding='cp1252') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Erreur lecture fichier {filepath}: {str(e)}")
    
    @staticmethod
    def write_file(filepath: str, content: str) -> bool:
        """
        Écrit du contenu dans un fichier
        
        Args:
            filepath: Chemin vers le fichier
            content: Contenu à écrire
            
        Returns:
            True si succès
        """
        try:
            # Créer les répertoires parents si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise Exception(f"Erreur écriture fichier {filepath}: {str(e)}")
    
    
    @staticmethod
    def list_files(directory: str, extensions: List[str] = None) -> List[str]:
        """
        Liste les fichiers dans un répertoire
        
        Args:
            directory: Répertoire à scanner
            extensions: Filtre par extensions (optionnel)
            
        Returns:
            Liste des fichiers
        """
        if extensions is None:
            extensions = ['.py']
        
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
        
        return files
    
    @staticmethod
    def run_pylint(filepath: str) -> Dict[str, Any]:
        """
        Exécute pylint sur un fichier
        
        Args:
            filepath: Chemin vers le fichier
            
        Returns:
            Résultats de l'analyse
        """
        try:
            # Exécuter pylint avec format JSON
            result = subprocess.run(
                ['pylint', '--output-format=json', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode in [0, 4, 8, 16, 28]:  # Codes de sortie pylint acceptables
                try:
                    issues = json.loads(result.stdout) if result.stdout else []
                    return {
                        'success': True,
                        'score': 10 - (len(issues) * 0.1 if issues else 0),  # Score simplifié
                        'issues': issues,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': f"Erreur parsing pylint output: {result.stdout[:200]}"
                    }
            else:
                return {
                    'success': False,
                    'error': f"Pylint failed with code {result.returncode}: {result.stderr[:200]}"
                }
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Pylint timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def run_pytest(test_path: str) -> Dict[str, Any]:
        """
        Exécute pytest sur un fichier/répertoire
        
        Args:
            test_path: Chemin vers les tests
            
        Returns:
            Résultats des tests
        """
        try:
            # Exécuter pytest
            result = subprocess.run(
                ['pytest', test_path, '--json-report', '-v'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Essayer de parser le rapport JSON
            report_file = '.report.json'
            if os.path.exists(report_file):
                with open(report_file, 'r') as f:
                    report = json.load(f)
                os.remove(report_file)
                
                tests_passed = report.get('summary', {}).get('passed', 0)
                tests_failed = report.get('summary', {}).get('failed', 0)
                tests_total = report.get('summary', {}).get('total', 0)
                
                return {
                    'success': True,
                    'passed': tests_passed,
                    'failed': tests_failed,
                    'total': tests_total,
                    'passed_ratio': tests_passed / tests_total if tests_total > 0 else 0,
                    'report': report,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                # Fallback: analyser la sortie texte
                lines = result.stdout.split('\n')
                passed = sum(1 for line in lines if 'PASSED' in line)
                failed = sum(1 for line in lines if 'FAILED' in line or 'ERROR' in line)
                
                return {
                    'success': True,
                    'passed': passed,
                    'failed': failed,
                    'total': passed + failed,
                    'passed_ratio': passed / (passed + failed) if (passed + failed) > 0 else 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Pytest timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def analyze_code_structure(filepath: str) -> Dict[str, Any]:
        """
        Analyse la structure du code avec AST
        
        Args:
            filepath: Chemin vers le fichier
            
        Returns:
            Analyse structurelle
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Compter les éléments
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            # Vérifier les docstrings
            has_module_docstring = ast.get_docstring(tree) is not None
            functions_with_docstrings = sum(1 for f in functions if ast.get_docstring(f) is not None)
            
            return {
                'success': True,
                'lines': len(content.split('\n')),
                'functions': len(functions),
                'classes': len(classes),
                'imports': len(imports),
                'has_module_docstring': has_module_docstring,
                'functions_with_docstrings': functions_with_docstrings,
                'functions_total': len(functions),
                'docstring_coverage': functions_with_docstrings / len(functions) if len(functions) > 0 else 1.0
            }
            
        except SyntaxError as e:
            return {'success': False, 'error': f"Erreur syntaxique: {str(e)}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def validate_python_syntax(code: str) -> Tuple[bool, str]:
        """
        Valide la syntaxe Python
        
        Args:
            code: Code à valider
            
        Returns:
            (succès, message)
        """
        try:
            ast.parse(code)
            return True, "Syntaxe Python valide"
        except SyntaxError as e:
            return False, f"Erreur syntaxique: {str(e)}"
        except Exception as e:
            return False, f"Erreur: {str(e)}"

# Instance globale
code_tools = CodeTools()