import boto3


faces_bucket = 'access-control-system-based-on-image-recognition-faces-eu-west'
collectionId_faces = 'faces_for_access-control-system-based-on-image-recognition'
client = boto3.client('rekognition')


def list_collections():
    collections_dict = client.list_collections()

    while True:
        collection_ids = collections_dict['CollectionIds']
        for collection in collection_ids:
            print(collection)
        if 'NextToken' in collections_dict:
            next_token = collections_dict['NextToken']
            collections_dict = client.list_collections(NextToken=next_token)
        else:
            break


def list_faces_in_collection(collection=collectionId_faces):
    tokens = True
    response_dict = client.list_faces(CollectionId=collection)
    print('Faces in collection ' + collection)

    while tokens:
        faces_list = response_dict['Faces']
        for face in faces_list:
            print(face)
        if 'NextToken' in response_dict:
            next_token = response_dict['NextToken']
            response_dict = client.list_faces(CollectionId=collection, NextToken=next_token)
        else:
            tokens = False


def upload_image_to_s3_bucket(path, file_name):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(path, faces_bucket, file_name)


def check_if_face_in_collection(image_name, collection=collectionId_faces, bucket=faces_bucket):
    threshold = 90
    response_dict = client.search_faces_by_image(CollectionId=collection,
                                                 Image={'S3Object': {'Bucket': bucket, 'Name': image_name}},
                                                 FaceMatchThreshold=threshold)

    face_matches = response_dict['FaceMatches']
    if face_matches:
        for match in face_matches:
            if match["Similarity"] > 90:
                    # print('FaceId:' + match['Face']['FaceId'])
                    # print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                return True
    else:
        return False
