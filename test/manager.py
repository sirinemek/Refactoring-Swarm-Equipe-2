"""
Système de Gestion d'Étudiants - Version Buguée
Ce code contient intentionnellement des bugs pour tester le Refactoring Swarm
"""

class Student:
    def __init__(self,name,age,grades):
        self.name=name
        self.age=age
        self.grades=grades
    
    def calculate_average(self):
        return sum(self.grades)/len(self.grades)
    
    def add_grade(self,grade):
        self.grades.append(grade)
    
    def is_passing(self):
        if self.calculate_average()>=10:
            return True
        else:
            return False

class StudentManager:
    def __init__(self):
        self.students=[]
    
    def add_student(self,student):
        self.students.append(student)
    
    def remove_student(self,name):
        for i in range(len(self.students)):
            if self.students[i].name==name:
                del self.students[i]
                break
    
    def find_student(self,name):
        for student in self.students:
            if student.name==name:
                return student
        return None
    
    def get_top_students(self,n):
        sorted_students=sorted(self.students,key=lambda x:x.calculate_average(),reverse=True)
        return sorted_students[:n]
    
    def calculate_class_average(self):
        total=0
        for student in self.students:
            total+=student.calculate_average()
        return total/len(self.students)
    
    def print_all_students(self):
        for i in range(len(self.students)):
            print(f"{self.students[i].name}: {self.students[i].calculate_average()}")

def load_students_from_file(filename):
    manager=StudentManager()
    try:
        f=open(filename,'r')
        for line in f:
            data=line.strip().split(',')
            name=data[0]
            age=int(data[1])
            grades=[float(x) for x in data[2:]]
            student=Student(name,age,grades)
            manager.add_student(student)
        f.close()
    except:
        print("Erreur de lecture")
    return manager

def save_students_to_file(manager,filename):
    f=open(filename,'w')
    for student in manager.students:
        grades_str=','.join([str(g) for g in student.grades])
        f.write(f"{student.name},{student.age},{grades_str}\n")
    f.close()

def display_statistics(manager):
    print("=== Statistiques de la classe ===")
    print(f"Nombre d'étudiants: {len(manager.students)}")
    print(f"Moyenne de classe: {manager.calculate_class_average():.2f}")
    
    passing=0
    for student in manager.students:
        if student.is_passing():
            passing+=1
    
    print(f"Étudiants réussissant: {passing}/{len(manager.students)}")
    
    top3=manager.get_top_students(3)
    print("\nTop 3 étudiants:")
    for i in range(len(top3)):
        print(f"{i+1}. {top3[i].name}: {top3[i].calculate_average():.2f}")

# Point d'entrée
if __name__=="__main__":
    # Création du gestionnaire
    manager=StudentManager()
    
    # Ajout d'étudiants
    s1=Student("Alice",20,[15,16,14,17])
    s2=Student("Bob",21,[12,13,11,14])
    s3=Student("Charlie",19,[8,9,7,10])
    s4=Student("Diana",20,[18,17,19,18])
    s5=Student("Eve",22,[10,11,9,12])
    
    manager.add_student(s1)
    manager.add_student(s2)
    manager.add_student(s3)
    manager.add_student(s4)
    manager.add_student(s5)
    
    # Affichage des statistiques
    display_statistics(manager)
    
    # Test de recherche
    print("\n=== Recherche d'étudiant ===")
    found=manager.find_student("Alice")
    if found:
        print(f"Trouvé: {found.name}, Moyenne: {found.calculate_average():.2f}")
    
    # Test d'ajout de note
    print("\n=== Ajout de note ===")
    found.add_grade(20)
    print(f"Nouvelle moyenne de {found.name}: {found.calculate_average():.2f}")
    
    # Affichage de tous les étudiants
    print("\n=== Liste complète ===")
    manager.print_all_students()