from sqlalchemy import Column, String, Boolean, ForeignKey, create_engine
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
    
    # The Primary Key is also the Foreign Key to Elements
    id = Column(String(50), ForeignKey('elements.id'), primary_key=True)
    
    # Specific attribute from Class Diagram
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