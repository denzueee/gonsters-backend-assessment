"""
Data API Routes
Handles sensor data ingestion and retrieval endpoints
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta
from pydantic import ValidationError
from uuid import UUID
import logging
import json
from app.database import get_db, write_sensor_data, query_sensor_data, get_redis_client
from app.models import MachineMetadata
from app.schemas import IngestRequest, ErrorResponse, CreateMachineRequest, MachineListResponse, MachineInfo
from app.auth.middleware import require_auth, require_permission
from app.utils import cache_response, invalidate_cache

bp = Blueprint('data', __name__, url_prefix='/api/v1/data')
logger = logging.getLogger(__name__)


def get_cached_machine_metadata(db, machine_id):
    """
    Mengambil metadata mesin dengan Cache-Aside pattern (Redis + DB)
    """
    redis_client = get_redis_client()
    cache_key = f"machine_metadata:{machine_id}"
    
    # Coba ambil dari cache
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                # Rekonstruksi objek dari dictionary untuk penggunaan sederhana
                machine = MachineMetadata.from_dict(data)
                machine.id = UUID(data['id'])
                machine.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
                machine.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
                return machine
        except Exception as e:
            logger.warning(f"Gagal membaca cache Redis: {e}")

    # Ambil dari Database
    machine = db.query(MachineMetadata).filter(
        MachineMetadata.id == machine_id
    ).first()
    
    # Simpan ke cache
    if machine and redis_client:
        try:
            redis_client.set(
                cache_key,
                json.dumps(machine.to_dict()),
                ex=3600  # Expire 1 jam
            )
        except Exception as e:
            logger.warning(f"Gagal menulis cache Redis: {e}")
            
    return machine
@bp.route('/ingest', methods=['POST'])
@require_auth
@require_permission('write:sensor_data')
def ingest_data():
    """
    POST /api/v1/data/ingest
    
    Ingest data sensor secara batch dari industrial gateways.
    
    Request Body:
        {
            "gateway_id": "gateway-001",
            "timestamp": "2025-12-13T03:38:52Z",
            "batch": [
                {
                    "machine_id": "uuid",
                    "sensor_type": "Temperature",
                    "location": "Floor 1",
                    "readings": [
                        {
                            "timestamp": "2025-12-13T03:38:50Z",
                            "temperature": 72.5,
                            "pressure": 101.3,
                            "speed": 1450.0
                        }
                    ]
                }
            ]
        }
    
    Returns:
        201: Batch ingestion berhasil
        207: Partial success (beberapa gagal)
        400: Error validasi
        500: Server error
    """

    try:
        # Validasi request body
        try:
            data = request.get_json(force=False, silent=False)
            if data is None:
                return jsonify({
                    'status': 'error',
                    'message': 'Request body is required'
                }), 400
            
            # Validasi struktur data
            ingest_request = IngestRequest(**data)
            
        except ValidationError as e:
            errors = []
            for error in e.errors():
                errors.append({
                    'field': '.'.join(str(loc) for loc in error['loc']),
                    'error': error['msg'],
                    'value': str(error.get('input', ''))
                })
            
            return jsonify({
                'status': 'error',
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # Proses batch data
        gateway_id = ingest_request.gateway_id
        batch = ingest_request.batch
        
        total_machines = len(batch)
        total_readings = 0
        errors = []
        details = []
        
        with get_db() as db:
            for idx, machine_data in enumerate(batch):
                try:
                    machine_id = str(machine_data.machine_id)
                    sensor_type = machine_data.sensor_type
                    location = machine_data.location
                    readings = machine_data.readings
                    
                    # Validasi keberadaan mesin (Cache & DB)
                    machine = get_cached_machine_metadata(db, machine_data.machine_id)
                    
                    if not machine:
                        errors.append({
                            'field': f'batch[{idx}].machine_id',
                            'error': 'Machine ID not found in database',
                            'value': machine_id
                        })
                        details.append({
                            'machine_id': machine_id,
                            'readings_count': 0,
                            'status': 'failed'
                        })
                        continue
                    
                    # Tulis setiap pembacaan ke InfluxDB
                    readings_written = 0
                    for reading in readings:
                        try:
                            # Tulis ke InfluxDB
                            success = write_sensor_data(
                                machine_id=machine_id,
                                sensor_type=sensor_type,
                                location=location,
                                temperature=reading.temperature,
                                pressure=reading.pressure,
                                speed=reading.speed,
                                timestamp=reading.timestamp
                            )
                            
                            if success:
                                readings_written += 1
                                total_readings += 1
                            else:
                                logger.error(
                                    f"Failed to write reading for machine {machine_id}"
                                )
                        
                        except Exception as e:
                            logger.error(
                                f"Error writing reading for machine {machine_id}: {str(e)}"
                            )
                    
                    # Tambahkan detail hasil
                    details.append({
                        'machine_id': machine_id,
                        'readings_count': readings_written,
                        'status': 'success' if readings_written > 0 else 'failed'
                    })
                
                except Exception as e:
                    logger.error(
                        f"Error processing machine data at index {idx}: {str(e)}"
                    )
                    errors.append({
                        'field': f'batch[{idx}]',
                        'error': str(e),
                        'value': None
                    })
        
        # Kirim respons
        if errors and total_readings == 0:
            # All failed
            return jsonify({
                'status': 'error',
                'message': 'Batch ingestion failed',
                'errors': errors
            }), 400
        
        elif errors or total_readings < len(batch):
            # Partial success or silent failures (readings_written=0 but no validation errors)
            if not errors and total_readings == 0:
                 return jsonify({
                    'status': 'error',
                    'message': 'Batch ingestion failed - No readings could be written to database',
                    'details': details
                }), 500

            return jsonify({
                'status': 'partial_success',
                'message': 'Batch ingestion completed with errors',
                'summary': {
                    'total_machines': total_machines,
                    'total_readings': total_readings,
                    'processed_at': datetime.utcnow().isoformat() + 'Z',
                    'gateway_id': gateway_id
                },
                'details': details,
                'errors': errors
            }), 207  # Multi-Status
        
        else:
            # Berhasil total
            return jsonify({
                'status': 'success',
                'message': 'Batch ingestion completed',
                'summary': {
                    'total_machines': total_machines,
                    'total_readings': total_readings,
                    'processed_at': datetime.utcnow().isoformat() + 'Z',
                    'gateway_id': gateway_id
                },
                'details': details
            }), 201
    
    except Exception as e:
        # Handle BadRequest (400) from Flask before falling back to 500
        from werkzeug.exceptions import BadRequest
        if isinstance(e, BadRequest):
            return jsonify({
                'status': 'error',
                'message': 'Invalid request format'
            }), 400
        
        logger.error(f"Unexpected error in ingest_data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@bp.route('/machine/<machine_id>', methods=['GET'])
@require_auth
@require_permission('read:sensor_data')
@cache_response(timeout=30, key_prefix='machine_data')
def get_machine_data(machine_id):
    """
    GET /api/v1/data/machine/{machine_id}
    
    Mengambil data sensor historis untuk mesin tertentu.
    
    Query Parameters:
        start_time (required): Waktu mulai (ISO 8601)
        end_time (optional): Waktu akhir (ISO 8601), default: sekarang
        interval (optional): Interval agregasi (raw, 1m, 5m, 1h, 1d), default: raw
        fields (optional): Comma-separated fields (temperature, pressure, speed, all), default: all
        limit (optional): Max records (1-10000), default: 1000
        offset (optional): Pagination offset, default: 0
    
    Returns:
        200: Sukses
        400: Parameter tidak valid
        404: Mesin tidak ditemukan
        500: Server error
    """

    try:
        # Validasi format ID mesin
        try:
            machine_uuid = UUID(machine_id)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid machine ID format',
                'machine_id': machine_id
            }), 400
        
        # Validasi keberadaan mesin (Cache & DB)
        with get_db() as db:
            machine = get_cached_machine_metadata(db, machine_uuid)
            
            if not machine:
                return jsonify({
                    'status': 'error',
                    'message': 'Machine not found',
                    'machine_id': machine_id
                }), 404
            
            # Extract machine data before session closes
            machine_data = {
                'machine_id': str(machine.id),
                'name': machine.name,
                'location': machine.location,
                'sensor_type': machine.sensor_type
            }
        
        # Validasi dan parsing parameter
        errors = []
        
        # start_time (required)
        start_time_str = request.args.get('start_time')
        if not start_time_str:
            errors.append({
                'parameter': 'start_time',
                'error': 'Required parameter missing',
                'value': None
            })
        else:
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            except ValueError:
                errors.append({
                    'parameter': 'start_time',
                    'error': 'Invalid ISO 8601 format',
                    'value': start_time_str
                })
                start_time = None
        
        # end_time (opsional, default: sekarang)
        end_time_str = request.args.get('end_time')
        if end_time_str:
            try:
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            except ValueError:
                errors.append({
                    'parameter': 'end_time',
                    'error': 'Invalid ISO 8601 format',
                    'value': end_time_str
                })
                end_time = datetime.utcnow()
        else:
            end_time = datetime.utcnow()
        
        # interval (opsional, default: 'raw')
        interval = request.args.get('interval', 'raw')
        valid_intervals = ['raw', '1m', '5m', '1h', '1d']
        if interval not in valid_intervals:
            errors.append({
                'parameter': 'interval',
                'error': f'Invalid interval value. Must be one of: {", ".join(valid_intervals)}',
                'value': interval
            })
        
        # fields (opsional, default: 'all')
        fields_str = request.args.get('fields', 'all')
        if fields_str == 'all':
            fields = ['temperature', 'pressure', 'speed']
        else:
            fields = [f.strip() for f in fields_str.split(',')]
            valid_fields = ['temperature', 'pressure', 'speed']
            invalid_fields = [f for f in fields if f not in valid_fields]
            if invalid_fields:
                errors.append({
                    'parameter': 'fields',
                    'error': f'Invalid fields: {", ".join(invalid_fields)}. Must be one of: {", ".join(valid_fields)}',
                    'value': fields_str
                })
        
        # limit (opsional, default: 1000)
        limit_str = request.args.get('limit', '1000')
        try:
            limit = int(limit_str)
            if limit < 1 or limit > 10000:
                errors.append({
                    'parameter': 'limit',
                    'error': 'Limit must be between 1 and 10000',
                    'value': limit_str
                })
        except ValueError:
            errors.append({
                'parameter': 'limit',
                'error': 'Limit must be an integer',
                'value': limit_str
            })
            limit = 1000
        
        # offset (opsional, default: 0)
        offset_str = request.args.get('offset', '0')
        try:
            offset = int(offset_str)
            if offset < 0:
                errors.append({
                    'parameter': 'offset',
                    'error': 'Offset must be non-negative',
                    'value': offset_str
                })
        except ValueError:
            errors.append({
                'parameter': 'offset',
                'error': 'Offset must be an integer',
                'value': offset_str
            })
            offset = 0
        
        # Kembalikan error jika ada
        if errors:
            return jsonify({
                'status': 'error',
                'message': 'Invalid query parameters',
                'errors': errors
            }), 400
        
        # Query ke InfluxDB
        aggregation_window = None if interval == 'raw' else interval
        
        records = query_sensor_data(
            machine_id=machine_id,
            start_time=start_time,
            end_time=end_time,
            aggregation_window=aggregation_window
        )
        
        # Filter fields dan paginasi
        filtered_data = []
        for record in records:
            if record['field'] in fields:
                filtered_data.append(record)
        
        # Group by timestamp
        data_points = {}
        for record in filtered_data:
            timestamp = record['time'].isoformat()
            if timestamp not in data_points:
                data_points[timestamp] = {'timestamp': record['time']}
            data_points[timestamp][record['field']] = record['value']
        
        # Convert to list and sort by timestamp
        data_list = sorted(data_points.values(), key=lambda x: x['timestamp'])
        
        # Apply pagination
        total_records = len(data_list)
        paginated_data = data_list[offset:offset + limit]
        
        #  Format respons
        return jsonify({
            'status': 'success',
            'machine': machine_data,
            'query': {
                'start_time': start_time.isoformat() + 'Z',
                'end_time': end_time.isoformat() + 'Z',
                'interval': interval,
                'fields': fields
            },
            'data': [
                {
                    'timestamp': dp['timestamp'].isoformat() + 'Z',
                    **{k: v for k, v in dp.items() if k != 'timestamp'}
                }
                for dp in paginated_data
            ],
            'pagination': {
                'total_records': total_records,
                'returned_records': len(paginated_data),
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_records
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Unexpected error in get_machine_data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@bp.route('/machine', methods=['POST'])
@require_auth
@require_permission('write:machines')
def create_machine():
    """
    POST /api/v1/data/machine
    Menambahkan mesin baru.
    
    Required Permission: write:machines
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request body is required'}), 400
        
        try:
            req_data = CreateMachineRequest(**data)
        except ValidationError as e:
            return jsonify({'status': 'error', 'message': 'Validation failed', 'errors': e.errors()}), 400
            
        with get_db() as db:
            # Check existing name
            existing = db.query(MachineMetadata).filter(MachineMetadata.name == req_data.name).first()
            if existing:
                return jsonify({'status': 'error', 'message': f'Machine with name {req_data.name} already exists'}), 409
                
            new_machine = MachineMetadata(
                name=req_data.name,
                location=req_data.location,
                sensor_type=req_data.sensor_type,
                status=req_data.status
            )
            db.add(new_machine)
            db.commit()
            
            # Invalidate machines list cache
            invalidate_cache("cache:machines_list:*")
            
            return jsonify({
                'status': 'success',
                'message': 'Machine created successfully',
                'machine_id': str(new_machine.id)
            }), 201
            
    except Exception as e:
        logger.error(f"Create machine error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@bp.route('/machines', methods=['GET'])
@require_auth
@require_permission('read:machines')
@cache_response(timeout=60, key_prefix='machines_list')
def list_machines():
    """
    GET /api/v1/data/machines
    Melihat daftar semua mesin.
    
    Required Permission: read:machines
    """
    try:
        # Query params for filtering
        location = request.args.get('location')
        status = request.args.get('status')
        sensor_type = request.args.get('sensor_type')
        
        with get_db() as db:
            query = db.query(MachineMetadata)
            
            if location:
                query = query.filter(MachineMetadata.location == location)
            if status:
                query = query.filter(MachineMetadata.status == status)
            if sensor_type:
                query = query.filter(MachineMetadata.sensor_type == sensor_type)
                
            machines = query.all()
            
            result = []
            for m in machines:
                result.append({
                    'machine_id': str(m.id),
                    'name': m.name,
                    'location': m.location,
                    'sensor_type': m.sensor_type
                })
                
            return jsonify({
                'status': 'success',
                'count': len(result),
                'machines': result
            }), 200
            
    except Exception as e:
        logger.error(f"List machines error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

