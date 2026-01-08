
# ============================================================================
# IMPORTS - Bibliothèques nécessaires
# ============================================================================
import argparse  # Pour lire --target_dir
import sys       # Pour arrêter le programme
from pathlib import Path  # Pour manipuler les chemins
from dotenv import load_dotenv  # Pour charger les clés API
from src.utils.logger import log_experiment, ActionType  # Pour les logs

# Charger les variables d'environnement (GOOGLE_API_KEY, etc.)
load_dotenv()


# ============================================================================
# FONCTION PRINCIPALE : orchestre les 3 agents
# ============================================================================
def main():
    
    # ÉTAPE 1 : LIRE L'ARGUMENT --target_dir
    
    # Créer le lecteur d'arguments
    parser = argparse.ArgumentParser(
        description="Refactoring Swarm - Système multi-agents"
    )
    
    # Définir l'argument obligatoire --target_dir
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Dossier contenant le code Python à corriger"
    )
    
    # Lire les arguments tapés par l'utilisateur
    args = parser.parse_args()
    
    print(f" *Dossier cible : {args.target_dir}")
    
    # ÉTAPE 2 : VÉRIFIER QUE LE DOSSIER EXISTE
    
    # Convertir en objet Path
    target_directory = Path(args.target_dir)
    
    # Vérifier l'existence
    if not target_directory.exists():
        print(f"❌ Erreur : Le dossier {args.target_dir} n'existe pas.")
        
        # Logger l'erreur
        log_experiment(
            agent_name="System",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Vérification dossier {args.target_dir}",
                "output_response": "Dossier introuvable",
                "error": "Directory not found"
            },
            status="FAILED"
        )
        
        # Arrêter avec code d'erreur 1
        sys.exit(1)
    
    print(f" *Dossier trouvé !")
    
 
    # ÉTAPE 3 : LOGGER LE DÉMARRAGE
 
    
    print("\n DEMARRAGE DU REFACTORING SWARM")
    print("=" * 70)
    
    # Enregistrer le démarrage dans les logs
    log_experiment(
        agent_name="System",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Initialisation sur {args.target_dir}",
            "output_response": "Système démarré avec succès",
            "target_directory": str(target_directory)
        },
        status="SUCCESS"
    )
    

    # ÉTAPE 4 : ORCHESTRATION (PROTÉGÉE PAR TRY-EXCEPT) 
    try:
       
        # PHASE 1 : ANALYSE PAR L'AUDITEUR
 
        print("\n📋 ÉTAPE 1 : ANALYSE PAR L'AUDITEUR")
        print("-" * 70)
        
        # TODO: Décommenter ces 2 lignes quand l'agent Auditeur sera créé
        # from src.agents.auditor import analyze
        # audit_result = analyze(target_directory)
        
        # SIMULATION TEMPORAIRE (à supprimer plus tard)
        audit_result = {
            "files_analyzed": [],
            "issues_found": [],
            "pylint_score_before": 0.0
        }
        print("  Agent Auditeur non implémenté (TODO Prompt Engineer)")
        
        # ====================================================================
        # PHASE 2 : BOUCLE DE CORRECTION (MAX 10 ITÉRATIONS)
        # ====================================================================
        
        print("\nDÉMARRAGE DE LA BOUCLE DE CORRECTION")
        print(f"   Limite : 10 itérations")
        print("=" * 70)
        
        # Variables de contrôle de la boucle
        max_iterations = 10          # Limite imposée par l'énoncé
        iteration = 0                # Compteur (commence à 0)
        all_tests_passed = False     # Drapeau de succès
        
        # Boucle : Continue tant que (pas 10 itérations) ET (tests échouent)
        while iteration < max_iterations and not all_tests_passed:
            
            # Incrémenter le compteur
            iteration += 1
            
            # Afficher l'en-tête de l'itération
            print(f"\n{'='*70}")
            print(f" ITÉRATION {iteration}/{max_iterations}")
            print(f"{'='*70}")
            
            # SOUS-ÉTAPE A : CORRECTION PAR LE FIXER 
            
            print(f"\n  Correction par le Fixer...")
            
            # TODO: Décommenter ces 2 lignes quand l'agent Fixer sera créé
            # from src.agents.fixer import fix
            # fix_result = fix(audit_result, target_directory)
            
            # SIMULATION TEMPORAIRE
            fix_result = {
                "files_modified": [],
                "changes_applied": 0,
                "status": "NOT_IMPLEMENTED"
            }
            print("  Agent Fixer non implémenté (TODO Toolsmith)")
            
            # ================================================================
            # SOUS-ÉTAPE B : TEST PAR LE JUDGE
            # ================================================================
            
            print(f"\n Tests par le Judge...")
            
            # TODO: Décommenter ces 2 lignes quand l'agent Judge sera créé
            # from src.agents.judge import test
            # test_result = test(target_directory)
            
            # SIMULATION TEMPORAIRE
            test_result = {
                "all_passed": False,   # Si True → Mission accomplie !
                "total_tests": 0,
                "failed_tests": [],
                "error_logs": ""
            }
            print("  Agent Judge non implémenté (TODO Toolsmith)")
            
            # ================================================================
            # SOUS-ÉTAPE C : DÉCISION - CONTINUER OU ARRÊTER ?
            # ================================================================
            
            # Vérifier si tous les tests sont passés
            if test_result.get("all_passed", False):
                
                #  SUCCÈS : Tous les tests passent !
                all_tests_passed = True
                print(f"\n SUCCÈS en {iteration} itération(s) !")
                
                # Logger le succès
                log_experiment(
                    agent_name="System",
                    model_used="N/A",
                    action=ActionType.FIX,
                    details={
                        "input_prompt": "Vérification finale",
                        "output_response": f"Succès en {iteration} itérations",
                        "iterations_needed": iteration
                    },
                    status="SUCCESS"
                )
                
                # Sortir de la boucle immédiatement
                break
            
            else:
                #  ÉCHEC : Des tests ont encore échoué
                
                # Compter les tests échoués
                failed_count = len(test_result.get("failed_tests", []))
                print(f"\n  {failed_count} test(s) échoué(s)")
                
                # Vérifier si on a atteint la limite
                if iteration >= max_iterations:
                    #  Limite atteinte
                    print(f"\nLIMITE ATTEINTE ({max_iterations} itérations)")
                    
                    # Logger l'échec
                    log_experiment(
                        agent_name="System",
                        model_used="N/A",
                        action=ActionType.DEBUG,
                        details={
                            "input_prompt": "Fin de boucle",
                            "output_response": "Limite d'itérations atteinte",
                            "failed_tests": test_result.get("failed_tests", [])
                        },
                        status="FAILED"
                    )
                else:
                    # On continue
                    print(f"   → Nouvelle tentative...")
        
        # ====================================================================
        # PHASE 3 : RAPPORT FINAL
        # ====================================================================
        
        print("\n" + "=" * 70)
        print(" RAPPORT FINAL")
        print("=" * 70)
        print(f"✓ Itérations : {iteration}/{max_iterations}")
        print(f"✓ Statut : {'SUCCÈS ✅' if all_tests_passed else 'ÉCHEC ❌'}")
        print(f"✓ Dossier : {target_directory}")
        print("=" * 70)
        
        # Sortie avec le bon code
        if all_tests_passed:
            print("\n✅ MISSION_COMPLETE")
            sys.exit(0)  # Code 0 = Succès
        else:
            print("\n❌ MISSION_INCOMPLETE")
            sys.exit(1)  # Code 1 = Échec
    
    # ========================================================================
    # GESTION DES ERREURS CRITIQUES
    # ========================================================================
    
    except Exception as e:
        # Si une erreur survient, on la capture ici
        print(f"\n💥 ERREUR CRITIQUE : {type(e).__name__}")
        print(f"   Message : {str(e)}")
        
        # Logger l'erreur
        log_experiment(
            agent_name="System",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "input_prompt": "Exécution système",
                "output_response": f"Erreur : {str(e)}",
                "error_type": type(e).__name__
            },
            status="FAILED"
        )
        
        # Sortir avec erreur
        sys.exit(1)


# ============================================================================
# POINT D'ENTRÉE DU PROGRAMME
# ============================================================================

# Cette ligne fait en sorte que main() se lance automatiquement
if __name__ == "__main__":
    main()


# ============================================================================
# TODO POUR L'ÉQUIPE (À DÉCOMMENTER PLUS TARD)
# ============================================================================
#
# Quand les agents seront prêts, décommente ces lignes :
#
# Ligne 133-134 : Agent Auditeur
# from src.agents.auditor import analyze
# audit_result = analyze(target_directory)
#
# Ligne 180-181 : Agent Fixer
# from src.agents.fixer import fix
# fix_result = fix(audit_result, target_directory)
#
# Ligne 198-199 : Agent Judge
# from src.agents.judge import test
# test_result = test(target_directory)
#
# ============================================================================