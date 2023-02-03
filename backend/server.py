# Import modules
from flask import Flask, jsonify, request
from flask_restful import Resource, Api

# Create Flask App
app = Flask(__name__)
# Create API Object
api = Api(app)

# Create resources
class Hello(Resource):
    def get(self):
        return jsonify({'message' : 'hello world'})
    def post(self):
        data = request.get_json()
        return jsonify({'data' : data}), 201
    
class Analyze(Resource):
    def get(self, link):
        return jsonify({'descriptor' : link})

# Add resources to API
api.add_resource(Hello, "/")
api.add_resource(Analyze, "/analyze/<link>")

# Driver
if __name__ == '__main__':
    app.run(debug=True)
