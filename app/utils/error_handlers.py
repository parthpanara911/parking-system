from flask import render_template, jsonify, request

def register_error_handlers(app):
    """Register error handlers for the Flask application."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Resource not found"}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Forbidden"}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Internal server error"}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Bad request"}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Unauthorized"}), 401
        return render_template('errors/401.html'), 401 