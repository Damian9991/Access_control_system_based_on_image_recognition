#!/usr/bin/env python3

import boto3
import datetime
import logging
import os
from utils import *


logger = logging.getLogger("face_recognition")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '') + "/face_recognition.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class CollectionNotCreatedException(Exception):
    pass


class CollectionNotDeletedException(Exception):
    pass


class FaceRecognition:
    """ The class is responsible for face recognition with the use of AWS rekognition cloud system
        -- check whether the recognised face exists in collection; similarity should be above 80%
    """

    def __init__(self):
        self.faces_bucket = 'access-control-system-based-on-image-recognition-faces-eu-west'
        self.collection_id_faces = 'access-control-system-based-on-image-recognition-faces'
        self.client = boto3.client('rekognition')

    def create_collection(self, collection_id):
        response = self.client.create_collection(CollectionId=collection_id)
        if response['StatusCode'] is not 200:
            raise CollectionNotCreatedException("An error occured. Collection has not been created!")

    def list_collections(self):
        collections_dict = self.client.list_collections()

        while True:
            collection_ids = collections_dict['CollectionIds']
            for collection in collection_ids:
                logger.info(collection)
            if 'NextToken' in collections_dict:
                next_token = collections_dict['NextToken']
                collections_dict = self.client.list_collections(NextToken=next_token)
            else:
                break

    def delete_collection(self, collection_id):
        response = self.client.delete_collection(CollectionId=collection_id)
        if response['StatusCode'] is not 200:
            raise CollectionNotDeletedException("An error occured. Collection has not been deleted!")

    def list_faces_in_collection(self):
        tokens = True
        response_dict = self.client.list_faces(CollectionId=self.collection_id_faces)
        names = []
        logger.info('Faces in collection ' + self.collection_id_faces + ':')

        while tokens:
            faces_list = response_dict['Faces']
            for face in faces_list:
                logger.info(face['ExternalImageId'].replace('_', ' '))
                names.append(face['ExternalImageId'].replace('_', ' '))
            if 'NextToken' in response_dict:
                next_token = response_dict['NextToken']
                response_dict = self.client.list_faces(CollectionId=self.collection_id_faces, NextToken=next_token)
            else:
                tokens = False
        return names

    def add_face_to_collection(self, image_path, name):
        name = name.replace(' ', '_')
        upload_image_to_s3_bucket(image_path, self.faces_bucket, name)
        response = self.client.index_faces(CollectionId=self.collection_id_faces,
                                           Image={'S3Object': {'Bucket': self.faces_bucket, 'Name': name}},
                                           ExternalImageId=name,
                                           MaxFaces=1,
                                           QualityFilter="AUTO",
                                           DetectionAttributes=['ALL'])

        if 'FaceRecords' not in response:
            logger.error('An error occured. Face has not been added to collection!')
        else:
            return True

    def remove_face_from_collection(self, name):
        tokens = True
        response_dict = self.client.list_faces(CollectionId=self.collection_id_faces)

        while tokens:
            faces_list = response_dict['Faces']
            for face in faces_list:
                if face['ExternalImageId'] == name.replace(' ', '_'):
                    face_id = face['FaceId']
            if 'NextToken' in response_dict:
                next_token = response_dict['NextToken']
                response_dict = self.client.list_faces(CollectionId=self.collection_id_faces, NextToken=next_token)
            else:
                tokens = False
        try:
            self.client.delete_faces(CollectionId=self.collection_id_faces, FaceIds=[face_id])
            return True
        except UnboundLocalError:
            logger.error('Face does not exist in collection!')

    def search_for_face_in_collection(self, image_path):
        image_name = datetime.datetime.now().strftime("face_%d%m%Y_%H%M%S.jpg")
        upload_image_to_s3_bucket(image_path, self.faces_bucket, image_name)
        threshold = 80
        response_dict = self.client.search_faces_by_image(CollectionId=self.collection_id_faces,
                                                          Image={'S3Object': {'Bucket': self.faces_bucket,
                                                                              'Name': image_name}},
                                                          FaceMatchThreshold=threshold)

        delete_image_from_s3_bucket(self.faces_bucket, image_name)
        face_matches = response_dict['FaceMatches']
        if face_matches:
            for match in face_matches:
                logger.info(match)
                logger.info('FaceId:' + match['Face']['FaceId'])
                logger.info('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                if match["Similarity"] > 80:
                    return match['Face']['ExternalImageId'].replace('_', ' ')
        else:
            return None
