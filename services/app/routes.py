from flask import Blueprint, request, jsonify, abort
from app.models import Service
from app.extensions import db
from app.schema import ServiceSchema
from sqlalchemy.exc import SQLAlchemyError

service_blueprint = Blueprint('service_blueprint', __name__)

service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)

@service_blueprint.route('/services', methods=['GET'])
def get_all_services():
    try:
        services = Service.get_all()
        return jsonify(services_schema.dump(services)), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@service_blueprint.route('/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    service = Service.get_by_id(service_id)
    if service:
        return jsonify(service_schema.dump(service)), 200
    else:
        return jsonify({"error": "Service not found"}), 404


@service_blueprint.route('/services', methods=['POST'])
def create_service():
    data = request.get_json()
    if not data or not all(key in data for key in ("name", "endpoint", "description")):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        service = Service.create(
            name=data['name'],
            endpoint=data['endpoint'],
            description=data['description'],
            status=data.get('status', "disable"),
            depends_on_id=data.get('depends_on_id')
        )
        return jsonify(service_schema.dump(service)), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@service_blueprint.route('/services/<int:service_id>/status', methods=['PUT'])
def update_service_status(service_id):
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"error": "Missing status field"}), 400

    service = Service.get_by_id(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    try:
        service.update_status(data['status'])
        return jsonify(service_schema.dump(service)), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@service_blueprint.route('/services/<int:service_id>/unregister', methods=['POST'])
def unregister_service(service_id):
    service = Service.get_by_id(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    try:
        service.unregister_service(service.name)
        return jsonify({"message": f"Service '{service.name}' unregistered successfully."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@service_blueprint.route('/services/<int:service_id>/dependencies', methods=['GET'])
def get_service_dependencies(service_id):
    service = Service.get_by_id(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    dependencies = service.get_dependencies()
    return jsonify(services_schema.dump(dependencies)), 200


@service_blueprint.route('/services/register', methods=['POST'])
def register_service():
    data = request.get_json()

    if not data or not all(key in data for key in ("name", "endpoint", "description")):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        service = Service.register_service(
            name=data['name'],
            endpoint=data['endpoint'],
            description=data['description'],
            depends_on_id=data.get('depends_on_id')
        )
        return jsonify(service_schema.dump(service)), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
