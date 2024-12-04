import pymongo
from flask import Flask, request, json, Response
import logging as log
import json

app = Flask(__name__)

#log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')

#myclient = pymongo.MongoClient("mongodb://localhost:5000/")
myclient = pymongo.MongoClient("mongodb://mongo:27017/")
mydb = myclient["PokeDB"]
mycol = mydb["Pokemons"]

#mydict = { "name": "John", "address": "Highway 37" }
#mycol.insert_one(mydict)

#print(myclient.list_database_names())
#print(mydb.list_collection_names())


def read_data(mycol, name):
    log.info(f"Reading Data for name: {name}")
    try:
        # Define filter criteria
        filter_criteria = {"name": name} if name else {}

        # Query the database for one document
        document = mycol.find_one(filter_criteria)

        # Check if the document was found
        if document:
            # Exclude the '_id' field if necessary
            output = {item: document[item] for item in document if item != '_id'}
            return output
        else:
            log.warning(f"No data found in the DB for the name: {name}")
            return {}
    except Exception as e:
        log.error(f"Error reading data: {e}")
        return {'Error': 'An error occurred while reading data', 'Message': str(e)}

def write_data(mycol, data):
    log.info('Writing Data')
    try:
        response = mycol.insert_one(data)
        output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        return output
    except Exception as e:
        log.error(f"Error writing data: {e}")
        return {'Error': 'An error occurred while writing data', 'Message': str(e)}


@app.route('/')
def base():
    name = request.args.get('name')
    return Response(response=json.dumps({"CRUD API": f"Received a request to find {name}"}),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb', methods=['GET'])
def mongo_read():
    name = request.args.get('name')
    print(name)
    log.info(f"Query parameter 'name': {name}")
    if not name:
        return Response(response=json.dumps({"Error": "Please provide a valid query parameter"}),
                        status=400,
                        mimetype='application/json')
    # Read data from the MongoDB collection using `read_data`
    response = read_data(mycol, name)
    print("Response from the DB", response)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb', methods=['POST'])
def mongo_write():

  data = request.json
  response = write_data(mycol, data)
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')