from elasticsearch import Elasticsearch
from termcolor import colored
from PIL import Image

# Connect to Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# Index some sample documents
def index_documents():
    documents = [
        {
            'title': 'Document 1',
            'content': 'This is the content of document 1.',
            'image_path': 'path_to_image1.jpg'
        },
        {
            'title': 'Document 2',
            'content': 'This is the content of document 2.',
            'image_path': 'path_to_image2.jpg'
        },
        {
            'title': 'Another Document',
            'content': 'This is another document.',
            'image_path': 'path_to_image3.jpg'
        }
    ]

    # Create index with custom analyzer for text preprocessing
    index_settings = {
        'settings': {
            'analysis': {
                'analyzer': {
                    'custom_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'stop', 'snowball']
                    }
                }
            }
        },
        'mappings': {
            'properties': {
                'title': {'type': 'text', 'analyzer': 'custom_analyzer'},
                'content': {'type': 'text', 'analyzer': 'custom_analyzer'},
                'image_path': {'type': 'keyword'}
            }
        }
    }

    es.indices.create(index='documents', body=index_settings)

    # Index the documents
    for idx, doc in enumerate(documents):
        es.index(index='documents', id=idx, body=doc)

# Search for documents
def search_documents(query):
    search_body = {
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['title^2', 'content'],
                'type': 'best_fields'
            }
        },
        'highlight': {
            'fields': {
                'title': {},
                'content': {}
            }
        }
    }

    response = es.search(index='documents', body=search_body)
    hits = response['hits']['hits']

    if len(hits) == 0:
        print(colored('No results found.', 'red'))
    else:
        print(colored('Search Results:', 'green'))
        for hit in hits:
            print(colored('Title:', 'cyan'), hit['_source']['title'])
            print(colored('Content:', 'cyan'), hit['_source']['content'])
            print()

            # Print highlights
            if 'highlight' in hit:
                highlights = hit['highlight']
                if 'title' in highlights:
                    print(colored('Title Highlight:', 'cyan'), ' '.join(highlights['title']))
                if 'content' in highlights:
                    print(colored('Content Highlight:', 'cyan'), ' '.join(highlights['content']))
            print()

            # Display image
            image_path = hit['_source']['image_path']
            display_image(image_path)

def display_image(image_path):
    try:
        image = Image.open(image_path)
        image.show()
    except Exception as e:
        print(colored('Error displaying image:', 'red'), str(e))

# Index some sample documents
index_documents()

# Perform a search
search_query = input(colored('Enter your search query: ', 'yellow'))
search_documents(search_query)
