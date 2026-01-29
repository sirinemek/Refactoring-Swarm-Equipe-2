import os
from typing import List, Optional, Union

# Constantes pour les nombres magiques
PASSING_GRADE: float = 10.0
TOP_STUDENTS_COUNT: int = 3

"""
Système de Gestion d'Étudiants - Version Corrigée
Ce code corrige les bugs et améliore la qualité du code original.
"""

class Student:
    """
    Représente un étudiant avec son nom, son âge et ses notes.
    """
    def __init__(self, name: str, age: int, grades: List[float]):
        """
        Initialise un nouvel étudiant.

        Args:
            name (str): Le nom de l'étudiant.
            age (int): L'âge de l'étudiant.
            grades (List[float]): Une liste des notes de l'étudiant.

        Raises:
            ValueError: Si le nom est vide, l'âge est négatif/non-numérique
                        ou si les notes ne sont pas valides (entre 0 et 20).
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Le nom de l'étudiant doit être une chaîne non vide.")
        if not isinstance(age, int) or age <= 0:
            raise ValueError("L'âge de l'étudiant doit être un entier positif.")
        if not isinstance(grades, list) or \
           not all(isinstance(g, (int, float)) and 0 <= g <= 20 for g in grades):
            raise ValueError("Les notes doivent être une liste de nombres entre 0 et 20.")

        self.name: str = name.strip()
        self.age: int = age
        self.grades: List[float] = [float(g) for g in grades] # Assure que toutes les notes sont des floats

    def calculate_average(self) -> float:
        """
        Calcule la moyenne des notes de l'étudiant.

        Returns:
            float: La moyenne des notes. Retourne 0.0 si aucune note n'est présente.
        """
        if not self.grades:
            return 0.0
        return sum(self.grades) / len(self.grades)

    def add_grade(self, grade: float) -> None:
        """
        Ajoute une note à la liste des notes de l'étudiant.

        Args:
            grade (float): La note à ajouter.

        Raises:
            ValueError: Si la note n'est pas valide (entre 0 et 20).
        """
        if not isinstance(grade, (int, float)) or not (0 <= grade <= 20):
            raise ValueError("La note doit être un nombre entre 0 et 20.")
        self.grades.append(grade)

    def is_passing(self) -> bool:
        """
        Vérifie si l'étudiant a une moyenne de passage.

        Returns:
            bool: True si la moyenne est supérieure ou égale à la note de passage, False sinon.
        """
        return self.calculate_average() >= PASSING_GRADE


class StudentManager:
    """
    Gère une collection d'objets Student.
    """
    def __init__(self):
        """
        Initialise un nouveau gestionnaire d'étudiants avec une liste vide d'étudiants.
        """
        self.students: List[Student] = []

    def add_student(self, student: Student) -> None:
        """
        Ajoute un étudiant au gestionnaire.

        Args:
            student (Student): L'objet Student à ajouter.
        """
        if not isinstance(student, Student):
            raise TypeError("Seuls les objets Student peuvent être ajoutés.")
        self.students.append(student)

    def remove_student(self, name: str) -> None:
        """
        Supprime un étudiant du gestionnaire par son nom.
        Cette méthode recrée la liste des étudiants pour éviter les problèmes
        de modification de liste pendant l'itération.

        Args:
            name (str): Le nom de l'étudiant à supprimer.
        """
        initial_len = len(self.students)
        self.students = [student for student in self.students if student.name != name]
        if len(self.students) == initial_len:
            print(f"Avertissement: L'étudiant '{name}' n'a pas été trouvé pour suppression.")

    def find_student(self, name: str) -> Optional[Student]:
        """
        Recherche un étudiant par son nom.

        Args:
            name (str): Le nom de l'étudiant à rechercher.

        Returns:
            Optional[Student]: L'objet Student si trouvé, None sinon.
        """
        for student in self.students:
            if student.name == name:
                return student
        return None

    def get_top_students(self, n: int) -> List[Student]:
        """
        Retourne les 'n' meilleurs étudiants basés sur leur moyenne.

        Args:
            n (int): Le nombre d'étudiants à retourner.

        Returns:
            List[Student]: Une liste des 'n' meilleurs étudiants, triés par ordre
                           décroissant de moyenne. Retourne une liste vide si aucun étudiant.
        """
        if not self.students:
            return []
        sorted_students: List[Student] = sorted(
            self.students, 
            key=lambda x: x.calculate_average(), 
            reverse=True
        )
        return sorted_students[:n]

    def calculate_class_average(self) -> float:
        """
        Calcule la moyenne de la classe.

        Returns:
            float: La moyenne de toutes les notes des étudiants.
                   Retourne 0.0 si aucun étudiant n'est présent.
        """
        if not self.students:
            return 0.0
        total: float = sum(student.calculate_average() for student in self.students)
        return total / len(self.students)

    def print_all_students(self) -> None:
        """
        Affiche le nom et la moyenne de tous les étudiants gérés.
        """
        if not self.students:
            print("Aucun étudiant à afficher.")
            return
        for student in self.students:
            print(f"{student.name}: {student.calculate_average():.2f}")


def load_students_from_file(filename: str) -> StudentManager:
    """
    Charge les informations des étudiants à partir d'un fichier CSV.

    Le format attendu pour chaque ligne est: "nom,âge,note1,note2,..."

    Args:
        filename (str): Le chemin du fichier à lire.

    Returns:
        StudentManager: Une nouvelle instance de StudentManager populée avec les données du fichier.
    """
    manager = StudentManager()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()
                if not clean_line:
                    continue # Ignorer les lignes vides
                try:
                    data = clean_line.split(',')
                    if len(data) < 2:
                        print(f"Ligne {line_num}: Format de données insuffisant. "
                              f"Attendu 'nom,âge,notes...', trouvé '{clean_line}'. Ignorée.")
                        continue

                    name = data[0].strip()
                    age = int(data[1].strip())
                    # Gérer le cas où il n'y a pas de notes après l'âge
                    grades = [float(x.strip()) for x in data[2:]] if len(data) > 2 else []
                    
                    student = Student(name, age, grades)
                    manager.add_student(student)
                except (ValueError, IndexError) as e:
                    print(f"Erreur de parsing des données à la ligne {line_num}: "
                          f"'{clean_line}' - {e}. "
                          "Vérifiez le format (nom,âge,note1,note2,...). "
                          "L'âge doit être un entier et les notes des nombres.")
                except TypeError as e: # Pour la validation de Student.add_student
                    print(f"Erreur lors de l'ajout de l'étudiant à la ligne {line_num}: "
                          f"'{clean_line}' - {e}.")
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{filename}' n'a pas été trouvé.")
        return StudentManager() # Retourne un gestionnaire vide en cas d'erreur
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors de la lecture du fichier '{filename}': {e}")
        return StudentManager() # Retourne un gestionnaire vide en cas d'erreur
    return manager


def save_students_to_file(manager: StudentManager, filename: str) -> None:
    """
    Sauvegarde les informations des étudiants dans un fichier CSV.

    Args:
        manager (StudentManager): L'instance de StudentManager contenant les étudiants.
        filename (str): Le chemin du fichier où sauvegarder les données.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for student in manager.students:
                grades_str = ','.join([str(g) for g in student.grades])
                f.write(f"{student.name},{student.age},{grades_str}\n")
        print(f"Données des étudiants sauvegardées avec succès dans '{filename}'.")
    except IOError as e:
        print(f"Erreur d'écriture dans le fichier '{filename}': {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors de la sauvegarde du fichier '{filename}': {e}")


def display_statistics(manager: StudentManager) -> None:
    """
    Affiche diverses statistiques sur les étudiants gérés.

    Args:
        manager (StudentManager): L'instance de StudentManager à partir de laquelle afficher les statistiques.
    """
    print("\n=== Statistiques de la classe ===")
    num_students = len(manager.students)
    print(f"Nombre d'étudiants: {num_students}")

    if num_students == 0:
        print("Aucun étudiant n'est enregistré pour calculer les statistiques.")
        return

    class_average = manager.calculate_class_average()
    print(f"Moyenne de classe: {class_average:.2f}")
    
    # Calcul du nombre d'étudiants réussissant
    passing_students_count = sum(1 for student in manager.students if student.is_passing())
    print(f"Étudiants réussissant: {passing_students_count}/{num_students} "
          f"({(passing_students_count / num_students * 100):.2f} %)")

    top_students = manager.get_top_students(TOP_STUDENTS_COUNT)
    if top_students:
        print(f"\nTop {TOP_STUDENTS_COUNT} étudiants:")
        for i, student in enumerate(top_students, 1):
            print(f"{i}. {student.name}: {student.calculate_average():.2f}")
    else:
        print(f"\nPas assez d'étudiants pour afficher le top {TOP_STUDENTS_COUNT}.")

# Point d'entrée
if __name__ == "__main__":
    # Création du gestionnaire
    manager = StudentManager()

    # Ajout d'étudiants
    s1 = Student("Alice", 20, [15, 16, 14, 17])
    s2 = Student("Bob", 21, [12, 13, 11, 14])
    s3 = Student("Charlie", 19, [8, 9, 7, 10])
    s4 = Student("Diana", 20, [18, 17, 19, 18])
    s5 = Student("Eve", 22, [10, 11, 9, 12])

    manager.add_student(s1)
    manager.add_student(s2)
    manager.add_student(s3)
    manager.add_student(s4)
    manager.add_student(s5)

    # Affichage des statistiques
    display_statistics(manager)

    # Test de recherche
    print("\n=== Recherche d'étudiant ===")
    found_student = manager.find_student("Alice")
    if found_student:
        print(f"Trouvé: {found_student.name}, Moyenne: {found_student.calculate_average():.2f}")
    else:
        print("Alice n'a pas été trouvée.")

    # Test d'ajout de note
    print("\n=== Ajout de note ===")
    if found_student:
        try:
            found_student.add_grade(20)
            print(f"Nouvelle moyenne de {found_student.name}: {found_student.calculate_average():.2f}")
        except ValueError as e:
            print(f"Erreur lors de l'ajout de la note: {e}")
    else:
        print("Impossible d'ajouter une note, étudiant non trouvé.")

    # Affichage de tous les étudiants
    print("\n=== Liste complète ===")
    manager.print_all_students()

    # Test de suppression
    print("\n=== Suppression d'étudiant ===")
    manager.remove_student("Bob")
    print("Bob a été tenté d'être supprimé.") # Le message d'avertissement de remove_student s'affichera si non trouvé
    manager.remove_student("Inconnu") # Test suppression d'un étudiant inexistant
    manager.print_all_students()

    # Test de chargement/sauvegarde
    print("\n=== Test de Fichier ===")
    test_filename = "students_data.csv"
    save_students_to_file(manager, test_filename)

    new_manager = load_students_from_file(test_filename)
    print(f"Étudiants chargés depuis '{test_filename}'.")
    new_manager.print_all_students()

    # Test d'un fichier inexistant
    print("\n=== Test de fichier inexistant ===")
    load_students_from_file("non_existent_file.csv")

    # Test de fichier avec données invalides
    print("\n=== Test de fichier avec données invalides ===")
    invalid_data_filename = "invalid_students.csv"
    with open(invalid_data_filename, 'w', encoding='utf-8') as f:
        f.write("Dave,25,10,12,abc\n") # Invalid grade
        f.write("Frank,-5,10,12\n") # Invalid age
        f.write("Grace,20\n") # Missing grades
        f.write("Helen\n") # Missing age and grades
        f.write("  \n") # Empty line
        f.write("Invalid line, only two values\n")

    loaded_invalid_manager = load_students_from_file(invalid_data_filename)
    print("Étudiants chargés du fichier invalide:")
    loaded_invalid_manager.print_all_students()
    
    # Nettoyage des fichiers de test
    if os.path.exists(invalid_data_filename):
        os.remove(invalid_data_filename)
    if os.path.exists(test_filename):
        os.remove(test_filename)
