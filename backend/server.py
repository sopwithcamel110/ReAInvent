# Import modules
from flask import Flask, jsonify, request
from flask_restful import Resource, Api

# Create Flask App
app = Flask(__name__)
# Create API Object
api = Api(app)

# Create resources
class ValidateURL(Resource):
    def get(self, desc=""):
        # Set valid to 1 if url is valid
        # desc: YouTube url descriptor https://www.youtube.com/watch?v=     ----> cdZZpaB2kDM
        valid = 0
        if len(desc) == 11:
            valid = 1
        
        #END CODE
        return jsonify({'Valid' : valid})
    
class Analyze(Resource):
    def get(self, link):
        return jsonify({'descriptor' : link})

# Add resources to API
api.add_resource(ValidateURL, "/validate/<desc>")
api.add_resource(Analyze, "/analyze/<link>")

# Driver
if __name__ == '__main__':
    app.run(debug=True)
