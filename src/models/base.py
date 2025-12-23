from datetime import datetime
from config.database import db
import uuid

class BaseModel(db.Model):
    """
    Modelo base con campos comunes
    Equivalente a timestamps: true en Sequelize
    """
    __abstract__ = True
    
    # UUID como primary key (igual que tu Node.js)
    id = db.Column(
        db.String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )
    
    # Timestamps (createdAt, updatedAt en Sequelize)
    created_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    def to_dict(self, exclude=None):
        """
        Convierte modelo a dict
        exclude: lista de campos a excluir
        """
        if exclude is None:
            exclude = []
            
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"