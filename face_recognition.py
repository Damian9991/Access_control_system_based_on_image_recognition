import boto3
import datetime
from utils import upload_image_to_s3_bucket


class FaceNotAddedToCollectionException(Exception):
    pass


class FaceRecognition:

    def __init__(self):
        self.faces_bucket = 'access-control-system-based-on-image-recognition-faces-eu-west'
        self.collection_id_faces = 'access-control-system-based-on-image-recognition-faces'
        self.client = boto3.client('rekognition')

    def list_faces_in_collection(self):
        tokens = True
        response_dict = self.client.list_faces(CollectionId=self.collection_id_faces)
        print('Faces in collection ' + self.collection_id_faces)

        while tokens:
            faces_list = response_dict['Faces']
            for face in faces_list:
                print(face)
            if 'NextToken' in response_dict:
                next_token = response_dict['NextToken']
                response_dict = self.client.list_faces(CollectionId=self.collection_id_faces, NextToken=next_token)
            else:
                tokens = False

    def add_face_to_collection(self, image_name):
        response = self.client.index_faces(CollectionId=self.collection_id_faces,
                                           Image={'S3Object': {'Bucket': self.faces_bucket, 'Name': image_name}},
                                           ExternalImageId=image_name,
                                           MaxFaces=1,
                                           QualityFilter="AUTO",
                                           DetectionAttributes=['ALL'])

        if 'FaceRecords' not in response:
            raise FaceNotAddedToCollectionException('An error occured. Face has not been added to collection!')

    def remove_face_from_collection(self, face_id):
        self.client.delete_faces(CollectionId=self.collection_id_faces, FaceIds=[face_id])

    def check_if_face_in_collection(self, image_path):
        image_name = datetime.datetime.now().strftime("face_%d%m%Y_%H%M%S.jpg")
        upload_image_to_s3_bucket(image_path, self.faces_bucket, image_name)
        threshold = 80
        response_dict = self.client.search_faces_by_image(CollectionId=self.collection_id_faces,
                                                          Image={'S3Object': {'Bucket': self.faces_bucket, 'Name': image_name}},
                                                          FaceMatchThreshold=threshold)

        face_matches = response_dict['FaceMatches']
        if face_matches:
            for match in face_matches:
                print(image_path)
                print('FaceId:' + match['Face']['FaceId'])
                print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                if match["Similarity"] > 80:
                    return True
        else:
            return False
