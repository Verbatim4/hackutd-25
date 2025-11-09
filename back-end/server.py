from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
api = Api(app)

# MongoDB connection
# Default connection to local MongoDB
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client['complaint_database']
complaints_collection = db['complaints']

# Load clustered data (will load with clusters if available)
CLUSTERED_DATA_FILE = 'dfw_complaints_with_clusters.csv'
ORIGINAL_DATA_FILE = 'dfw_complaints.csv'

def load_cluster_data():
    """Load the clustered data from CSV"""
    if os.path.exists(CLUSTERED_DATA_FILE):
        return pd.read_csv(CLUSTERED_DATA_FILE)
    elif os.path.exists(ORIGINAL_DATA_FILE):
        return pd.read_csv(ORIGINAL_DATA_FILE)
    return None

cluster_data = load_cluster_data()


class ComplaintResource(Resource):
    """Resource for handling individual complaint operations"""
    
    def get(self, complaint_id):
        """Get a specific complaint by ID"""
        try:
            complaint = complaints_collection.find_one({'_id': ObjectId(complaint_id)})
            if complaint:
                complaint['_id'] = str(complaint['_id'])
                return jsonify({'success': True, 'data': complaint})
            return jsonify({'success': False, 'message': 'Complaint not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    def put(self, complaint_id):
        """Update a specific complaint"""
        try:
            data = request.get_json()
            
            # Update only provided fields
            update_data = {}
            allowed_fields = ['Downtown Dallas', 'complaint', 'type_of_complaint', 'solution', 'status']
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]
            
            if update_data:
                update_data['updated_at'] = datetime.utcnow()
                result = complaints_collection.update_one(
                    {'_id': ObjectId(complaint_id)},
                    {'$set': update_data}
                )
                
                if result.modified_count > 0:
                    return jsonify({'success': True, 'message': 'Complaint updated successfully'})
                return jsonify({'success': False, 'message': 'No changes made'}), 400
            
            return jsonify({'success': False, 'message': 'No valid fields to update'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    def delete(self, complaint_id):
        """Delete a specific complaint"""
        try:
            result = complaints_collection.delete_one({'_id': ObjectId(complaint_id)})
            if result.deleted_count > 0:
                return jsonify({'success': True, 'message': 'Complaint deleted successfully'})
            return jsonify({'success': False, 'message': 'Complaint not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400


class ComplaintsListResource(Resource):
    """Resource for handling multiple complaints operations"""
    
    def get(self):
        """Get all complaints with optional filtering"""
        try:
            # Get query parameters for filtering
            status = request.args.get('status')
            type_of_complaint = request.args.get('type_of_complaint')
            location = request.args.get('location')
            
            # Build query
            query = {}
            if status:
                query['status'] = status
            if type_of_complaint:
                query['type_of_complaint'] = type_of_complaint
            if location:
                query['Downtown Dallas'] = location
            
            # Get complaints
            complaints = list(complaints_collection.find(query))
            
            # Convert ObjectId to string
            for complaint in complaints:
                complaint['_id'] = str(complaint['_id'])
            
            return jsonify({
                'success': True,
                'count': len(complaints),
                'data': complaints
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    def post(self):
        """Create a new complaint"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['Downtown Dallas', 'complaint', 'type_of_complaint', 'solution', 'status']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }), 400
            
            # Create complaint document
            complaint_doc = {
                'Downtown Dallas': str(data['Downtown Dallas']),
                'complaint': str(data['complaint']),
                'type_of_complaint': str(data['type_of_complaint']),
                'solution': str(data['solution']),
                'status': str(data['status']),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Insert into database
            result = complaints_collection.insert_one(complaint_doc)
            
            return jsonify({
                'success': True,
                'message': 'Complaint created successfully',
                'id': str(result.inserted_id)
            }), 201
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400


class ComplaintStatsResource(Resource):
    """Resource for getting complaint statistics"""
    
    def get(self):
        """Get statistics about complaints"""
        try:
            total_complaints = complaints_collection.count_documents({})
            
            # Group by status
            status_pipeline = [
                {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
            ]
            status_stats = list(complaints_collection.aggregate(status_pipeline))
            
            # Group by type
            type_pipeline = [
                {'$group': {'_id': '$type_of_complaint', 'count': {'$sum': 1}}}
            ]
            type_stats = list(complaints_collection.aggregate(type_pipeline))
            
            # Group by location
            location_pipeline = [
                {'$group': {'_id': '$Downtown Dallas', 'count': {'$sum': 1}}}
            ]
            location_stats = list(complaints_collection.aggregate(location_pipeline))
            
            return jsonify({
                'success': True,
                'data': {
                    'total_complaints': total_complaints,
                    'by_status': status_stats,
                    'by_type': type_stats,
                    'by_location': location_stats
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400


class ClustersListResource(Resource):
    """Resource for getting information about all clusters"""
    
    def get(self):
        """Get list of all clusters with counts"""
        try:
            if cluster_data is None:
                return jsonify({
                    'success': False,
                    'message': 'Clustered data not available. Run clustering first.'
                }), 404
            
            if 'cluster' not in cluster_data.columns:
                return jsonify({
                    'success': False,
                    'message': 'Data does not contain cluster information.'
                }), 404
            
            # Get cluster statistics
            cluster_counts = cluster_data['cluster'].value_counts().sort_index().to_dict()
            
            clusters_info = []
            for cluster_id, count in cluster_counts.items():
                cluster_subset = cluster_data[cluster_data['cluster'] == cluster_id]
                
                cluster_info = {
                    'cluster_id': int(cluster_id),
                    'count': int(count),
                    'is_noise': cluster_id == -1,
                    'center': {
                        'latitude': float(cluster_subset['latitude'].mean()),
                        'longitude': float(cluster_subset['longitude'].mean())
                    }
                }
                clusters_info.append(cluster_info)
            
            return jsonify({
                'success': True,
                'total_clusters': len(clusters_info),
                'data': clusters_info
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400


class ClusterDetailResource(Resource):
    """Resource for getting detailed information about a specific cluster"""
    
    def get(self, cluster_id):
        """Get all data points in a specific cluster"""
        try:
            cluster_id = int(cluster_id)
            
            if cluster_data is None:
                return jsonify({
                    'success': False,
                    'message': 'Clustered data not available.'
                }), 404
            
            if 'cluster' not in cluster_data.columns:
                return jsonify({
                    'success': False,
                    'message': 'Data does not contain cluster information.'
                }), 404
            
            # Filter data for this cluster
            cluster_subset = cluster_data[cluster_data['cluster'] == cluster_id]
            
            if cluster_subset.empty:
                return jsonify({
                    'success': False,
                    'message': f'Cluster {cluster_id} not found.'
                }), 404
            
            # Convert to list of dictionaries
            points = cluster_subset.to_dict('records')
            
            # Clean up NaN values
            for point in points:
                for key, value in point.items():
                    if pd.isna(value):
                        point[key] = None
            
            return jsonify({
                'success': True,
                'cluster_id': cluster_id,
                'count': len(points),
                'is_noise': cluster_id == -1,
                'center': {
                    'latitude': float(cluster_subset['latitude'].mean()),
                    'longitude': float(cluster_subset['longitude'].mean())
                },
                'data': points
            })
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid cluster ID'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400


class ClusterAnalysisResource(Resource):
    """Resource for getting cluster analysis from CSV"""
    
    def get(self):
        """Get cluster analysis data"""
        try:
            analysis_file = 'cluster_analysis_20251109_031626.csv'
            
            if not os.path.exists(analysis_file):
                return jsonify({
                    'success': False,
                    'message': 'Cluster analysis file not found.'
                }), 404
            
            # Load analysis data
            analysis_df = pd.read_csv(analysis_file)
            
            # Convert to list of dictionaries
            analysis_data = analysis_df.to_dict('records')
            
            # Clean up NaN values
            for record in analysis_data:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
            
            return jsonify({
                'success': True,
                'count': len(analysis_data),
                'data': analysis_data
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400


# Add resources to API
api.add_resource(ComplaintsListResource, '/api/complaints')
api.add_resource(ComplaintResource, '/api/complaints/<string:complaint_id>')
api.add_resource(ComplaintStatsResource, '/api/complaints/stats')
api.add_resource(ClustersListResource, '/api/clusters')
api.add_resource(ClusterDetailResource, '/api/clusters/<string:cluster_id>')
api.add_resource(ClusterAnalysisResource, '/api/clusters/analysis')


@app.route('/')
def index():
    cluster_status = 'Available' if cluster_data is not None and 'cluster' in cluster_data.columns else 'Not Available'
    return jsonify({
        'message': 'Complaint Management API',
        'cluster_data_status': cluster_status,
        'endpoints': {
            'GET /api/complaints': 'Get all complaints (supports ?status=, ?type_of_complaint=, ?location= filters)',
            'POST /api/complaints': 'Create a new complaint',
            'GET /api/complaints/<id>': 'Get a specific complaint',
            'PUT /api/complaints/<id>': 'Update a specific complaint',
            'DELETE /api/complaints/<id>': 'Delete a specific complaint',
            'GET /api/complaints/stats': 'Get complaint statistics',
            'GET /api/clusters': 'Get list of all clusters with counts',
            'GET /api/clusters/<cluster_id>': 'Get all data points in a specific cluster',
            'GET /api/clusters/analysis': 'Get AI-generated cluster analysis'
        }
    })


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)