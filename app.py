from flask import Flask, request, jsonify
import verifier

app = Flask(__name__)

_verifier = verifier.Verifier()

@app.route('/')
def home():
    return "Flask API is running!"

@app.route('/validate-selfie', methods=['POST'])
def validateSelfie():
    data = request.get_json()  # Get JSON data from the request
    response = { 'valid': False, 'message': '' }
    if data is None:
        response["message"] = "Invalid JSON data"
        return jsonify( response ), 400
    if not data.get( "selfieUri" ):
        response["message"] = "Selfie URI is required"
        return jsonify( response ), 400
    
    return jsonify( _verifier.validateSelfie( data.get( "selfieUri" ) ) )

@app.route('/extract-data', methods=['POST'])
def extractData():
    data = request.get_json()  # Get JSON data from the request
    response = { 'success': False, 'message': '', 'data': None }
    if data is None:
        response["message"] = "Invalid JSON data"
        return jsonify( response ), 400
    if not data.get( "idImageUri" ):
        response["message"] = "ID image URI is required"
        return jsonify( response ), 400

    idImageUri = data.get( "idImageUri" )
    countryCode = data.get( "countryCode" )
    docType = data.get( "docType" )
    
    return jsonify( _verifier.extractData( idImageUri, countryCode, docType ) )

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()  # Get JSON data from the request
    response = { 'verified': False, 'message': '' }
    if data is None:
        response["message"] = "Invalid JSON data"
        return jsonify( response ), 400
    if not data.get( "idImageUri" ) or not data.get( "selfieUri" ):
        response["message"] = "ID image URI and selfie URI are required"
        return jsonify( response ), 400

    idImageUri = data.get( "idImageUri" )
    selfieUri = data.get( "selfieUri" )
    
    return jsonify( _verifier.verify( idImageUri, selfieUri ) )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
