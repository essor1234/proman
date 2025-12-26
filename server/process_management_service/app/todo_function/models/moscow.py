from sqlalchemy import Column, String, Boolean, ForeignKey, create_engine, Integer
from sqlalchemy.orm import declarative_base, relationship, Session
from .element import Element
from ..core.database import Base

Base = declarative_base()   

class Moscow(Element):
    """
    Class corresponding to 'Moscow'.
    Inherits attributes from Element.
    """
    __tablename__ = 'moscow'
    
    id = Column(Integer, ForeignKey('elements.id'), primary_key=True)
    
    category = Column(String(100))

    __mapper_args__ = {
        'polymorphic_identity': 'moscow',
    }

    # Method from Class Diagram (Change_category: bool)
    def change_category(self, new_category: str) -> bool:
        try:
            self.category = new_category
            return True
        except:
            return False