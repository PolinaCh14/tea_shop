from app.extensions import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="disable")
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    description = db.Column(db.String(100), nullable=False)
    
    depends_on_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)
    dependencies = relationship("Service", backref=db.backref('dependent_on', remote_side=[id]), lazy='dynamic')

    def __init__(self, name, endpoint, status="disable", description="", depends_on_id=None):
        self.name = name
        self.endpoint = endpoint
        self.status = status
        self.description = description
        self.depends_on_id = depends_on_id

    @classmethod
    def create(cls, name, endpoint, description, status="disable", depends_on_id=None):
        """Create and save a new service."""
        service = cls(name=name, endpoint=endpoint, description=description, status=status, depends_on_id=depends_on_id)
        db.session.add(service)
        db.session.commit()
        return service

    @classmethod
    def get_by_id(cls, service_id):
        """Get a service by its ID."""
        return cls.query.get(service_id)

    @classmethod
    def get_by_name(cls, name):
        """Get a service by its name."""
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_all(cls):
        """Get all services."""
        return cls.query.all()

    def update_status(self, new_status):
        """Update the status of the service."""
        self.status = new_status
        db.session.commit()

    @classmethod
    def register_service(cls, name, endpoint, description, depends_on_id=None):
        """Register or update a service."""
        service = cls.get_by_name(name)
        if service:
            service.endpoint = endpoint
            service.status = "active"
            service.depends_on_id = depends_on_id
            service.updated_at = func.now()
        else:
            service = cls.create(name=name, endpoint=endpoint, description=description, status="active", depends_on_id=depends_on_id)
        db.session.commit()
        print(f"Service '{name}' registered and set to active.")
        return service

    @classmethod
    def unregister_service(cls, name):
        """Set the service status to 'disable'."""
        service = cls.get_by_name(name)
        if service:
            service.status = "disable"
            service.updated_at = func.now()
            db.session.commit()
            print(f"Service '{name}' set to disable.")

    def get_dependencies(self):
        """Get all services that depend on this service."""
        return self.dependencies.all()

    def get_dependent_service(self):
        """Get the service this service depends on."""
        return self.depends_on_id

    def __repr__(self):
        return f"<Service id={self.id} name={self.name} status={self.status} depends_on_id={self.depends_on_id}>"
