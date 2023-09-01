import sys
import pytest
from io import StringIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from project_and_contract_system import Program, Contract, Project, Base



# Фикстура для создания сессии SQLAlchemy
@pytest.fixture(scope="function")
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Тесты для класса Contract
def test_create_contract(session):
    contract_name = "C001"
    contract = Contract(contract_name=contract_name, project_name='', status="Draft")
    session.add(contract)
    session.commit()
    fetched_contract = session.query(Contract).filter_by(contract_name=contract_name).first()
    assert fetched_contract is not None

def test_confirm_contract(session):
    contract_name = "C001"
    contract = Contract(contract_name=contract_name, project_name='', status="Draft")
    session.add(contract)
    session.commit()

    program = Program(None, session)
    program.confirm_contract(contract_name)

    fetched_contract = session.query(Contract).filter_by(contract_name=contract_name).first()
    assert fetched_contract.status == "Active"
    assert fetched_contract.signing_date is not None

def test_end_contract(session):
    contract_name = "C001"
    contract = Contract(contract_name=contract_name, project_name='', status="Active")
    session.add(contract)
    session.commit()

    program = Program(None, session)
    program.end_contract(contract_name)

    fetched_contract = session.query(Contract).filter_by(contract_name=contract_name).first()
    assert fetched_contract.status == "Ended"
    assert fetched_contract.project_name == ''

def test_list_contracts(session, capsys):
    contract1 = Contract(contract_name="C001", project_name='', status="Draft")
    contract2 = Contract(contract_name="C002", project_name='', status="Active")
    session.add_all([contract1, contract2])
    session.commit()

    program = Program(None, session)
    program.list_contracts()
    captured = capsys.readouterr()
    assert "Contract Name: C001" in captured.out
    assert "Contract Name: C002" in captured.out

# Тесты для класса Project
def test_create_project(session):
    project_name = "P001"
    project = Project(project_name=project_name)
    session.add(project)
    session.commit()
    fetched_project = session.query(Project).filter_by(project_name=project_name).first()
    assert fetched_project is not None

def test_list_projects(session, capsys):
    project1 = Project(project_name="P001")
    project2 = Project(project_name="P002")
    session.add_all([project1, project2])
    session.commit()

    program = Program(None, session)
    program.list_projects()
    captured = capsys.readouterr()
    assert "Project Name: P001" in captured.out
    assert "Project Name: P002" in captured.out

# Тесты для класса Program
def test_create_contract_in_program(session, capsys):
    program = Program(None, session)
    contract_name = "C001"
    program.create_contract(contract_name)
    captured = capsys.readouterr()
    assert "Contract C001 created." in captured.out

def test_create_existing_contract_in_program(session, capsys):
    contract_name = "C001"
    contract = Contract(contract_name=contract_name, project_name='', status="Draft")
    session.add(contract)
    session.commit()

    program = Program(None, session)
    program.create_contract(contract_name)
    captured = capsys.readouterr()
    assert "Contract C001 already exists." in captured.out


def test_create_project_in_program(session, capsys):
    program = Program(None, session)
    project_name = "P001"

    # Вызываем метод create_project
    program.create_project(project_name)

    # Перехватываем вывод и записываем его в captured_output
    captured_output = capsys.readouterr()

    # Проверяем, что предупреждение есть в захваченном выводе
    assert "Warning: You cannot create a project without at least one active contract." in captured_output.out


def test_create_project_without_active_contracts_in_program(session, capsys):
    program = Program(None, session)

    # Создаем объект StringIO для перехвата вывода
    captured_output = StringIO()

    # Перенаправляем стандартный вывод в captured_output
    sys.stdout = captured_output

    program.create_project("P002")

    # Возвращаем stdout в исходное состояние
    sys.stdout = sys.__stdout__

    # Проверяем, что предупреждение есть в захваченном выводе
    captured_output.seek(0)  # Перематываем StringIO к началу
    assert "Warning: You cannot create a project without at least one active contract." in captured_output.read()


if __name__ == "__main__":
    pytest.main()
