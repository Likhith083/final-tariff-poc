from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
import datetime

# User CRUD

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str) -> models.User:
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Product CRUD

def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()

# Tariff CRUD

def create_tariff(db: Session, tariff: schemas.TariffCreate) -> models.Tariff:
    db_tariff = models.Tariff(**tariff.dict())
    db.add(db_tariff)
    db.commit()
    db.refresh(db_tariff)
    return db_tariff

def get_tariff_by_code_and_country(db: Session, hts_code: str, country: str) -> Optional[models.Tariff]:
    return db.query(models.Tariff).filter(models.Tariff.hts_code == hts_code, models.Tariff.country == country).first()

# Alert CRUD

def create_alert(db: Session, alert: schemas.AlertCreate) -> models.Alert:
    db_alert = models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_alerts_for_user(db: Session, user_id: int) -> List[models.Alert]:
    return db.query(models.Alert).filter(models.Alert.user_id == user_id).all()

# Scenario CRUD

def create_scenario(db: Session, scenario: schemas.ScenarioCreate) -> models.Scenario:
    db_scenario = models.Scenario(**scenario.dict())
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

def get_scenarios_for_user(db: Session, user_id: int) -> List[models.Scenario]:
    return db.query(models.Scenario).filter(models.Scenario.user_id == user_id).all()

# Report CRUD

def create_report(db: Session, report: schemas.ReportCreate) -> models.Report:
    db_report = models.Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports_for_user(db: Session, user_id: int) -> List[models.Report]:
    return db.query(models.Report).filter(models.Report.user_id == user_id).all() 