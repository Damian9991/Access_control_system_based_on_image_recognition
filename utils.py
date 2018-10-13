import boto3
import json
import hashlib


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


def add_licence_plate_number_to_database(licence_plate, name_list):
    licence_plate_hash = create_hash(licence_plate)
    name_list_hash = []
    for name in name_list:
        name_list_hash.append(create_hash(name))
    new_entry = {licence_plate_hash: name_list_hash}
    with open('database.json', mode='r', encoding='utf-8') as json_file:
        file_content = json.load(json_file)
    with open('database.json', mode='w', encoding='utf-8') as json_file:
        file_content.append(new_entry)
        json.dump(file_content, json_file)


def create_hash(input_str):
    hash_object = hashlib.sha256(bytes(input_str, encoding='utf-8'))
    output = hash_object.hexdigest()
    return str(output)


def check_if_driver_has_access(licence_plate, name):
    licence_plate_hash = create_hash(licence_plate)
    name_hash = create_hash(name)
    with open('database.json', mode='r', encoding='utf-8') as json_file:
        file_content = json.load(json_file)
    for user_dict in file_content:
        if licence_plate_hash in user_dict.keys() and name_hash in user_dict[licence_plate_hash]:
            # print(licence_plate)
            # print(name)
            return True
    return False

# print(check_if_driver_has_access('RDE 65W5', 'Kamil_Kryczka'))
