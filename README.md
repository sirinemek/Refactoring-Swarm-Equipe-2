# 🐝 The Refactoring Swarm

Système Multi-Agents de Refactoring Automatique  
**École Nationale Supérieure d'Informatique - 2025-2026**  
**Enseignant:** BATATA Sofiane

---

## 📋 Description

The Refactoring Swarm est un système multi-agents utilisant des LLM (Large Language Models) pour analyser, corriger et valider automatiquement du code Python de mauvaise qualité.

### Les 3 Agents

1. **🔍 Auditor Agent** - Analyse le code et détecte les bugs
2. **🔧 Fixer Agent** - Corrige les bugs et améliore le code
3. **⚖️ Judge Agent** - Valide les corrections et décide d'accepter ou de réessayer

---

## 🚀 Installation

### Prérequis

- Python 3.10 ou 3.11
- Git
- Clé API Google Gemini (gratuite)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd refactoring-swarm
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la clé API**
```bash
# Dupliquer .env.example en .env
cp .env.example .env

# Éditer .env et ajouter votre clé
# GOOGLE_API_KEY=AIzaSy...votre_clé
```

**Obtenir une clé gratuite:** https://aistudio.google.com/app/apikey

5. **Vérifier l'installation**
```bash
python check_setup.py
```

---

## 💻 Utilisation

### Usage basique

```bash
python main.py --target_dir ./test
```

### Options disponibles

```bash
python main.py --target_dir ./mon_code --max_iterations 5 --verbose
```

**Arguments:**
- `--target_dir` : Répertoire contenant le code à refactorer (OBLIGATOIRE)
- `--max_iterations` : Nombre max d'itérations (défaut: 10)
- `--verbose` : Activer les logs détaillés

### Exemple complet

```bash
# 1. Créer un répertoire de test avec du code buggé
mkdir my_messy_code
echo "def calc(x,y): return x/y" > my_messy_code/test.py

# 2. Lancer le refactoring
python main.py --target_dir ./my_messy_code

# 3. Vérifier les résultats
cat sandbox/my_messy_code/test.py
cat logs/experiment_data.json
```

---

## 📁 Structure du Projet

```
refactoring-swarm/
├── main.py                    # Point d'entrée principal 🔒
├── requirements.txt           # Dépendances 🔒
├── check_setup.py            # Script de vérification 🔒
├── .env                      # Clés API (ne pas commiter!) 🔒
├── .gitignore
├── README.md
│
├── src/
│   ├── orchestrator.py       # Coordonne les agents
│   ├── agents/
│   │   ├── base_agent.py     # Classe de base
│   │   ├── auditor_agent.py  # Agent d'analyse
│   │   ├── fixer_agent.py    # Agent de correction
│   │   └── judge_agent.py    # Agent de validation
│   │
│   ├── prompts/
│   │   ├── auditor_prompts.py
│   │   ├── fixer_prompts.py
│   │   └── tester_prompts.py
│   │
│   └── utils/
│       ├── config.py         # Configuration
│       ├── logger.py         # Système de logging
│       └── tools.py          # Outils (pylint, pytest)
│
├── logs/                     # Logs d'exécution 🔒
│   ├── experiment_data.json
│   └── refactoring_summary.json
│
├── sandbox/                  # Zone de travail temporaire
└── test/                     # Fichiers de test
    └── calculator.py
```

**🔒 = Fichiers obligatoires (ne pas modifier les noms)**

---

## 🔧 Configuration

### Fichier `src/utils/config.py`

```python
# Modèle Gemini à utiliser
MODEL_NAME = "gemini-2.5-flash"  # OU "gemini-1.5-flash"

# Nombre max d'itérations
MAX_ITERATIONS = 10

# Activer les logs détaillés
VERBOSE = True
```

### Changer de modèle

Si un modèle ne fonctionne pas, testez les alternatives :

```python
# Testé et fonctionnel
MODEL_NAME = "gemini-2.5-flash"      # ✅ Recommandé
MODEL_NAME = "gemini-2.0-flash-exp"  # ✅ Alternative
MODEL_NAME = "gemini-1.5-flash"      # ✅ Stable
MODEL_NAME = "gemini-1.5-flash-8b"   # ✅ Ultra rapide
```

---

## 📊 Comprendre les Résultats

### Logs d'expérimentation

Le fichier `logs/experiment_data.json` contient **toutes** les interactions avec les LLM :

```json
[
  {
    "timestamp": "2025-01-28T10:30:00",
    "agent_name": "Auditor_Agent",
    "model_used": "gemini-2.5-flash",
    "action_type": "analysis",
    "status": "SUCCESS",
    "details": {
      "file_analyzed": "calculator.py",
      "input_prompt": "Analyse ce code...",
      "output_response": "J'ai trouvé 3 bugs...",
      "issues_found": 3
    }
  }
]
```

### Résumé final

Le fichier `logs/refactoring_summary.json` contient un résumé :

```json
{
  "workflow_status": "COMPLETED",
  "files_processed": 1,
  "success_rate": 100.0,
  "quality_metrics": {
    "average_score_before": 4.5,
    "average_score_after": 8.2,
    "improvement": 3.7
  }
}
```

---

## 🧪 Tests

### Tester avec un fichier simple

```bash
# Créer un fichier de test
mkdir test_simple
echo 'def add(x,y): return x+y' > test_simple/math.py

# Lancer
python main.py --target_dir ./test_simple
```

### Créer votre propre dataset de test

```bash
# Créer plusieurs fichiers avec bugs
mkdir my_tests
echo 'def calc(x): return x/0' > my_tests/bug1.py
echo 'x = 5\nprint(y)' > my_tests/bug2.py

python main.py --target_dir ./my_tests
```

---

## 📝 Workflow Git (Travail en Équipe)

### Configuration initiale (Chef d'équipe)

```bash
# 1. Créer un repo GitHub (Refactoring-Swarm-Equipe-X)
# 2. Configurer le remote
git remote add origin https://github.com/USER/Refactoring-Swarm-Equipe-X.git
git push -u origin main

# 3. Inviter les membres dans Settings > Collaborators
```

### Workflow quotidien

```bash
# Le matin : récupérer les changements
git pull origin main

# Créer une branche pour votre tâche
git checkout -b feature/mon-travail

# Coder...

# Sauvegarder
git add .
git commit -m "feat: ajout de X"

# Partager
git push origin feature/mon-travail

# Créer une Pull Request sur GitHub
```

### Avant la soumission finale

```bash
# IMPORTANT : Ajouter les logs
git add -f logs/experiment_data.json
git commit -m "DATA: Submission of experiment logs"
git push origin main
```

---

## 🎯 Critères d'Évaluation

| Dimension | Poids | Critères |
|-----------|-------|----------|
| **Performance** | 40% | Tests passent, score Pylint amélioré |
| **Robustesse** | 30% | Pas de crash, limite d'itérations respectée |
| **Qualité Data** | 30% | Fichier experiment_data.json valide et complet |

### Comment maximiser votre note

✅ **Performance (40%):**
- Assurez-vous que le code corrigé passe les tests
- Visez un score Pylint > 8.0/10

✅ **Robustesse (30%):**
- Testez sur plusieurs fichiers
- Gérez les erreurs proprement
- Respectez la limite de 10 itérations

✅ **Qualité Data (30%):**
- Vérifiez que `logs/experiment_data.json` se remplit
- Chaque action doit avoir `input_prompt` et `output_response`
- Commitez les logs avec `git add -f`

---

## 🐛 Dépannage

### Erreur : "404 models/gemini-X not found"

**Solution:** Changez le modèle dans `config.py`

```python
MODEL_NAME = "gemini-2.5-flash"  # Sans le -exp
```

### Erreur : "GOOGLE_API_KEY non trouvée"

**Solution:** 
```bash
# Vérifier que .env existe
cat .env

# Créer .env si manquant
echo "GOOGLE_API_KEY=AIzaSy..." > .env
```

### Erreur : "No module named 'google.generativeai'"

**Solution:**
```bash
pip install google-generativeai
```

### Le fichier experiment_data.json est vide

**Cause:** Les agents ne loggent pas correctement

**Solution:** Vérifiez que chaque agent appelle bien `log_experiment()`

---

## 🤝 Contribution & Rôles

### Les 4 Rôles du Projet

1. **L'Orchestrateur (Lead Dev)** 🧠
   - Fichiers : `main.py`, `orchestrator.py`
   - Gère le flux de contrôle

2. **L'Ingénieur Outils (Toolsmith)** 🛠️
   - Fichiers : `src/utils/tools.py`, `src/utils/config.py`
   - Développe les outils (pylint, pytest)

3. **L'Ingénieur Prompt** 💬
   - Fichiers : `src/prompts/*.py`
   - Optimise les prompts système

4. **Le Responsable Qualité & Data** 📊
   - Fichiers : `src/utils/logger.py`
   - Garantit la télémétrie

---

## 📚 Ressources

- [API Gemini](https://ai.google.dev/docs)
- [Pylint Documentation](https://pylint.readthedocs.io/)
- [Pytest Guide](https://docs.pytest.org/)
- [PEP 8](https://peps.python.org/pep-0008/)

---

## ⚠️ Politique Anti-Plagiat

- ❌ Copier le code d'autres équipes
- ❌ Copier les prompts (similarité > 70%)
- ❌ Commitez tout en un seul commit
- ❌ Copier les logs d'autres équipes

✅ **Faites des commits réguliers**  
✅ **Écrivez vos propres prompts**  
✅ **Générez vos propres logs**

---

## 📞 Support

**Questions sur le projet ?**
1. Consultez d'abord ce README
2. Lancez `python check_setup.py`
3. Vérifiez les logs dans `logs/`
4. Contactez l'enseignant

---

## 📄 Licence

Projet éducatif - ESI 2025-2026

---

**Bon courage ! 🚀**
