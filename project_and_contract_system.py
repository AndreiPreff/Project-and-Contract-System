from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import OperationalError
from datetime import date

Base = declarative_base()

class Contract(Base):
    __tablename__ = 'contracts'

    contract_name = Column(String, primary_key=True)
    project_name = Column(String, ForeignKey('projects.project_name'))
    status = Column(String)
    creation_date = Column(Date)
    signing_date = Column(Date)

    project = relationship("Project", back_populates="contracts")

    def __init__(self, contract_name, project_name, status, creation_date=None, signing_date=None):
        self.contract_name = contract_name
        self.project_name = project_name
        self.status = status
        self.creation_date = creation_date or date.today()
        self.signing_date = signing_date

class Project(Base):
    __tablename__ = 'projects'

    project_name = Column(String, primary_key=True)
    creation_date = Column(Date)

    contracts = relationship("Contract", back_populates="project")

    def __init__(self, project_name, creation_date=None):
        self.project_name = project_name
        self.creation_date = creation_date or date.today()

class Program:
    def __init__(self, engine, session):
        self.session = session

    def has_active_contracts(self):
        active_contracts = self.session.query(Contract).filter_by(status="Active").count()
        return active_contracts > 0

    def create_contract(self, contract_name):
        contract = self.session.query(Contract).filter_by(contract_name=contract_name).first()
        if not contract:
            contract = Contract(contract_name=contract_name, project_name='', status="Draft")
            self.session.add(contract)
            self.session.commit()
            print(f"Contract {contract_name} created.")
        else:
            print(f"Contract {contract_name} already exists.")

    def create_project(self, project_name):
        # Проверка на наличие активных договоров перед созданием проекта
        if not self.has_active_contracts():
            print("Warning: You cannot create a project without at least one active contract.")
            return

        project = self.session.query(Project).filter_by(project_name=project_name).first()
        if not project:
            project = Project(project_name=project_name)
            self.session.add(project)
            self.session.commit()
            print(f"Project {project_name} created.")
        else:
            print(f"Project {project_name} already exists.")

    def add_contract_to_project(self, contract_name, project_name):
        # Поиск договора по указанному имени
        contract = self.session.query(Contract).filter_by(contract_name=contract_name).first()

        # Поиск проекта по указанному имени
        project = self.session.query(Project).filter_by(project_name=project_name).first()

        # Если договор найден
        if contract:
            # Если договор уже активен
            if contract.status == "Active":
                # Если проект существует
                if project:
                    # Поиск другого активного договора, который уже связан с проектом
                    existing_active_contract = (
                        self.session.query(Contract)
                        .filter_by(project_name=project_name, status="Active")
                        .first()
                    )

                    # Если уже есть активный договор в проекте
                    if existing_active_contract:
                        print(
                            f"Project {project_name} already has an active contract: {existing_active_contract.contract_name}.")
                    else:
                        # Поиск другого проекта, к которому уже привязан этот договор
                        existing_project = (
                            self.session.query(Project)
                            .join(Contract, Project.project_name == Contract.project_name)
                            .filter(Contract.contract_name == contract_name)
                            .filter(Contract.status == "Active")
                            .filter(Project.project_name != project_name)
                            .first()
                        )

                        # Если договор уже добавлен в другой проект
                        if existing_project:
                            print(f"Contract {contract_name} is already active in Project {existing_project.project_name}.")
                        else:
                            # Привязка активного договора к указанному проекту
                            contract.project_name = project_name
                            self.session.commit()
                            print(f"Contract {contract_name} added to Project {project_name}.")
                else:
                    print(f"Project {project_name} not found.")
            # Если договор неактивен
            elif contract.status == "Draft" or "Ended":
                print(f"Contract {contract_name} is inactive. Activate it to add to the project.")
        # Если договор не найден
        else:
            print(f"Contract {contract_name} not found.")

    def confirm_contract(self, contract_name):
        contract = self.session.query(Contract).filter_by(contract_name=contract_name).first()
        if contract:
            contract.status = "Active"
            contract.signing_date = date.today()  # Устанавливает текущую дату при подписании
            self.session.commit()
            print(f"Contract {contract_name} confirmed and signed on {contract.signing_date}.")
        else:
            print(f"Contract {contract_name} not found.")

    def end_contract(self, contract_name):
        contract = self.session.query(Contract).filter_by(contract_name=contract_name).first()
        if contract:
            contract.status = "Ended"
            contract.project_name = ''
            self.session.commit()
            print(f"Contract {contract_name} ended.")
        else:
            print(f"Contract {contract_name} not found.")

    def list_contracts(self):
        contracts = self.session.query(Contract).all()
        if contracts:
            print("Contracts:")
            for contract in contracts:
                print(f"- Contract Name: {contract.contract_name}, Project Name: {contract.project_name}, Status: {contract.status}, Creation Date: {contract.creation_date}, Signing Date: {contract.signing_date}")
        else:
            print("No contracts found.")

    def list_projects(self):
        projects = self.session.query(Project).all()
        if projects:
            print("Projects:")
            for project in projects:
                print(f"- Project Name: {project.project_name}, Creation Date: {project.creation_date}")
        else:
            print("No projects found.")

    def run(self):
        while True:
            print("\n===== Program Menu =====\n")
            # Добавление надписи о необходимости создания и активации договора перед проектом
            if not self.has_active_contracts():
                print("Warning: Before creating a project, you need to create and activate at least one contract.\n")
            print("1. Create Project")
            print("2. Create Contract")
            print("3. Add Contract to Project")
            print("4. Confirm Contract")
            print("5. End Contract")
            print("6. List Contracts")
            print("7. List Projects")
            print("8. Exit Program")



            choice = input("Select an action (1-8): ")

            if choice == "1":
                # Проверка на наличие активных договоров перед созданием проекта
                if not self.has_active_contracts():
                    print("Warning: You cannot create a project without at least one active contract.")
                else:
                    project_name = input("Enter Project Name: ")
                    self.create_project(project_name)

            elif choice == "2":
                contract_name = input("Enter Contract Name: ")
                self.create_contract(contract_name)

            elif choice == "3":
                contract_name = input("Enter Contract Name: ")
                project_name = input("Enter Project Name: ")
                self.add_contract_to_project(contract_name, project_name)

            elif choice == "4":
                contract_name = input("Enter Contract Name: ")
                self.confirm_contract(contract_name)

            elif choice == "5":
                contract_name = input("Enter Contract Name: ")
                self.end_contract(contract_name)

            elif choice == "6":
                self.list_contracts()

            elif choice == "7":
                self.list_projects()

            elif choice == "8":
                print("Exiting the program.")
                break

            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        engine = create_engine('sqlite:///Projects_and_Contracts.db')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        program = Program(engine, session)
        program.run()

    except OperationalError:
        print("Error creating the database.")
