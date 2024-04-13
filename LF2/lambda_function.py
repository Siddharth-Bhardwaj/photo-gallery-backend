import json
import boto3
import requests
from requests.auth import HTTPBasicAuth

def lambda_handler(event, context):
    lex = boto3.client('lex-runtime')
    query_text = event['queryStringParameters']['keyword']
    lex_response = lex.post_text(
        botName='PhotoAlbumBot',
        botAlias='dev',
        userId='test',
        inputText= query_text
    )
    
    keywordA = lex_response['slots']['keywordA']
    keywordB = lex_response['slots']['keywordB']
    print(keywordA)
    print(keywordB)
    if (keywordA is None):
        return {'statusCode': 404, 'body': 'Keyword not found'}
    
    es_query = {
      "query": {
        "match": {
          "labels": keywordA,
        }
      }
    }
    if (keywordB is not None):    
      es_query = {
        "query": {
          "match": {
            "labels": {
              "query": keywordA + " " + keywordB,
              "operator": "and"
            }
          }
        }
      }
    
    headers: dict = {"Content-Type": "application/json"}
    url: str = "https://search-ccphotoalbum-okobqcqxaiuu5do2ujtwm3o6iu.aos.us-east-1.on.aws" + "/" + "photos" + "/" + "_search"

    auth = HTTPBasicAuth("ccphotoalbum","Ccphotoalbum@2024")
    response = requests.get(url, headers=headers, json=es_query, auth=auth)
    response.raise_for_status()
    print(response.json())
    
    response = response.json()
    result_count = response['hits']['total']['value']
    if (result_count < 1):
      return {
        'statusCode': 404,
        'body': 'No images found'
    }
    image_set = set()
    for doc in response['hits']['hits']:
      image_set.add('https://ccphotoalbum.s3.amazonaws.com/'+ doc['_source']['object_key'])
      
    print(image_set)
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(list(image_set))
    }
