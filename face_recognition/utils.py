import boto3
import datetime


class FaceRecognition:

    def __init__(self):
        self.faces_bucket = 'access-control-system-based-on-image-recognition-faces-eu-west'
        self.collectionId_faces = 'faces_for_access-control-system-based-on-image-recognition'
        self.client = boto3.client('rekognition')

    def list_collections(self):
        collections_dict = self.client.list_collections()

        while True:
            collection_ids = collections_dict['CollectionIds']
            for collection in collection_ids:
                print(collection)
            if 'NextToken' in collections_dict:
                next_token = collections_dict['NextToken']
                collections_dict = self.client.list_collections(NextToken=next_token)
            else:
                break

    def list_faces_in_collection(self):
        tokens = True
        response_dict = self.client.list_faces(CollectionId=self.collectionId_faces)
        print('Faces in collection ' + self.collectionId_faces)

        while tokens:
            faces_list = response_dict['Faces']
            for face in faces_list:
                print(face)
            if 'NextToken' in response_dict:
                next_token = response_dict['NextToken']
                response_dict = self.client.list_faces(CollectionId=self.collectionId_faces, NextToken=next_token)
            else:
                tokens = False

    def upload_image_to_s3_bucket(self, path, image_name):
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(path, self.faces_bucket, image_name)

    def check_if_face_in_collection(self, path):
        image_name = datetime.datetime.now().strftime("%d%m%Y_%H%M%S.jpg")
        self.upload_image_to_s3_bucket(path, image_name)
        threshold = 80
        response_dict = self.client.search_faces_by_image(CollectionId=self.collectionId_faces,
                                                          Image={'S3Object': {'Bucket': self.faces_bucket, 'Name': image_name}},
                                                          FaceMatchThreshold=threshold)

        face_matches = response_dict['FaceMatches']
        if face_matches:
            for match in face_matches:
                print(path)
                print('FaceId:' + match['Face']['FaceId'])
                print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                if match["Similarity"] > 90:
                    return True
        else:
            return False
