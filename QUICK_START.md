# ⚡ DÉMARRAGE RAPIDE - The Refactoring Swarm

**Temps d'installation:** 5-10 minutes

---

## 📦 Installation en 5 Étapes

### 1️⃣ Extraire le Projet

```bash
# Windows (PowerShell)
Expand-Archive refactoring-swarm-complete.zip -DestinationPath .
cd refactoring-swarm-complete

# Mac/Linux
tar -xzf refactoring-swarm-complete.tar.gz
cd refactoring-swarm-complete
```

### 2️⃣ Créer l'Environnement Virtuel

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer la Clé API

```bash
# Créer le fichier .env
# Windows
copy .env.example .env
notepad .env

# Mac/Linux
cp .env.example .env
nano .env
```

**Modifier .env :**
```
GOOGLE_API_KEY=AIzaSy...votre_clé_ici
```

**🔑 Obtenir une clé gratuite:**  
https://aistudio.google.com/app/apikey

### 5️⃣ Vérifier l'Installation

```bash
python check_setup.py
```

**Vous devriez voir:**
```
✅ Python
✅ Packages
✅ Fichier .env
✅ Structure
✅ Fichiers clés
✅ API Gemini
🎉 TOUT EST OK!
```

---

## 🚀 Premier Test

```bash
# Lancer sur le fichier d'exemple
python main.py --target_dir ./test

# Vérifier les résultats
cat sandbox/test/calculator.py
cat logs/experiment_data.json
```

**Résultat attendu:**
```
✅ Validation terminée avec succès!
🎉 MISSION ACCOMPLIE avec succès!
```

---

## 🔧 Configuration du Modèle

Si vous avez une erreur de modèle, éditez `src/utils/config.py` :

```python
# Ligne 15 - Changez le modèle
MODEL_NAME = "gemini-2.5-flash"  # ✅ Testé et fonctionnel
```

**Alternatives si ça ne marche pas:**
```python
MODEL_NAME = "gemini-1.5-flash"      # Stable
MODEL_NAME = "gemini-2.0-flash-exp"  # Expérimental
```

---

## 📝 Tester avec Votre Propre Code

### Créer un fichier de test

```bash
mkdir mon_test
```

**Windows (PowerShell):**
```powershell
@"
def calculate(x, y):
    result = x / y
    return result

def process_list(items):
    for i in range(len(items)):
        print(items[i])
"@ | Out-File -Encoding UTF8 mon_test/test.py
```

**Mac/Linux:**
```bash
cat > mon_test/test.py << 'EOF'
def calculate(x, y):
    result = x / y
    return result

def process_list(items):
    for i in range(len(items)):
        print(items[i])
EOF
```

### Lancer le refactoring

```bash
python main.py --target_dir ./mon_test
```

---

## 📊 Structure du Projet

```
refactoring-swarm-complete/
├── main.py                 ← Point d'entrée principal
├── check_setup.py          ← Script de vérification
├── requirements.txt        ← Dépendances
├── .env                    ← Votre clé API (à créer)
├── README.md               ← Documentation complète
│
├── src/
│   ├── orchestrator.py     ← Coordinateur principal
│   ├── agents/             ← Les 3 agents (Auditor, Fixer, Judge)
│   ├── prompts/            ← Prompts système
│   └── utils/              ← Configuration, logger, outils
│
├── test/                   ← Fichiers d'exemple
│   └── calculator.py
│
├── logs/                   ← Logs générés automatiquement
└── sandbox/                ← Zone de travail temporaire
```

---

## 🎯 Commandes Essentielles

| Commande | Description |
|----------|-------------|
| `python check_setup.py` | Vérifier l'installation |
| `python main.py --target_dir ./test` | Lancer sur le dossier test |
| `python main.py --help` | Voir toutes les options |
| `git status` | Vérifier l'état Git |
| `git add -f logs/experiment_data.json` | Ajouter les logs pour soumission |

---

## ❌ Erreurs Courantes

### 1. "GOOGLE_API_KEY non trouvée"

**Solution:**
```bash
# Vérifier que .env existe
cat .env  # ou: type .env (Windows)

# Si manquant, créer .env avec votre clé
echo "GOOGLE_API_KEY=AIzaSy..." > .env
```

### 2. "404 models/gemini-X not found"

**Solution:** Changez le modèle dans `src/utils/config.py`
```python
MODEL_NAME = "gemini-2.5-flash"  # Sans -exp
```

### 3. "No module named 'google.generativeai'"

**Solution:**
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --upgrade
```

### 4. "experiment_data.json est vide"

**Solution:** Relancez le système, les logs se génèrent automatiquement
```bash
python main.py --target_dir ./test
```

---

## 🤝 Travailler en Équipe (Git)

### Configuration (une seule fois)

```bash
# 1. Créer un repo sur GitHub
# 2. Configurer le remote
git init
git remote add origin https://github.com/USER/Refactoring-Swarm-Equipe-X.git

# 3. Premier commit
git add .
git commit -m "Initial commit: projet complet"
git push -u origin main
```

### Workflow quotidien

```bash
# Matin : récupérer les changements
git pull origin main

# Travailler sur une branche
git checkout -b feature/mon-travail

# Sauvegarder régulièrement
git add .
git commit -m "feat: description du changement"
git push origin feature/mon-travail
```

### Avant soumission

```bash
# IMPORTANT : Ajouter les logs
git add -f logs/experiment_data.json
git commit -m "DATA: Submission of experiment logs"
git push origin main
```

---

## 📚 Ressources

- **Documentation complète:** Voir `README.md`
- **Guide des prompts:** Voir `README_PROMPTS.md` (si inclus)
- **API Gemini:** https://ai.google.dev/docs
- **PEP 8 (style Python):** https://peps.python.org/pep-0008/

---

## 🆘 Besoin d'Aide ?

1. ✅ Lancez `python check_setup.py` pour diagnostiquer
2. ✅ Consultez `README.md` pour la doc complète
3. ✅ Vérifiez les logs dans `logs/experiment_data.json`
4. ✅ Testez avec un fichier simple d'abord

---

## 📞 Support

**En cas de problème:**
1. Vérifiez que vous avez suivi toutes les étapes
2. Testez avec le fichier d'exemple fourni (`./test`)
3. Vérifiez votre connexion Internet
4. Vérifiez que votre clé API est valide

---

**C'est parti ! 🚀**

```bash
# GO!
python main.py --target_dir ./test
```
