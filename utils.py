import boto3


class CollectionNotCreatedException(Exception):
    pass


class CollectionNotDeletedException(Exception):
    pass


def create_collection(aws_client, collection_id):
    response = aws_client.create_collection(CollectionId=collection_id)
    if response['StatusCode'] is not 200:
        raise CollectionNotCreatedException("An error occured. Collection has not been created!")


def list_collections(aws_client):
    collections_dict = aws_client.list_collections()

    while True:
        collection_ids = collections_dict['CollectionIds']
        for collection in collection_ids:
            print(collection)
        if 'NextToken' in collections_dict:
            next_token = collections_dict['NextToken']
            collections_dict = aws_client.list_collections(NextToken=next_token)
        else:
            break


def delete_collection(aws_client, collection_id):
    response = aws_client.delete_collection(CollectionId=collection_id)
    if response['StatusCode'] is not 200:
        raise CollectionNotDeletedException("An error occured. Collection has not been deleted!")


def upload_image_to_s3_bucket(path, bucket, image_name):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(path, bucket, image_name)
