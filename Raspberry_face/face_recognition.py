#!/usr/bin/env python3

#-----------------------------------------------------------
# Name: Access_control_system_based_on_image_recognition
# Authors: Kamil Kryczka, Damian Osinka
# Thesis supervisor: dr hab. inz. Mikołaj Leszczuk
# Purpose: Engineering Thesis
# Created: 13-10-2018
#-----------------------------------------------------------

import boto3
import datetime
import logging
import os
from utils import upload_image_to_s3_bucket

logger = logging.getLogger("Access_control_system_based_on_image_recognition")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '').replace(' ', '') + "/Access_control_system_based_on_image_recognition.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class CollectionNotCreatedException(Exception):
    pass


class CollectionNotDeletedException(Exception):
    pass


class FaceNotAddedToCollectionException(Exception):
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
                print(collection)
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

    def search_for_face_in_collection(self, image_path):
        image_name = datetime.datetime.now().strftime("face_%d%m%Y_%H%M%S.jpg")
        upload_image_to_s3_bucket(image_path, self.faces_bucket, image_name)
        threshold = 80
        response_dict = self.client.search_faces_by_image(CollectionId=self.collection_id_faces,
                                                          Image={'S3Object': {'Bucket': self.faces_bucket,
                                                                              'Name': image_name}},
                                                          FaceMatchThreshold=threshold)

        face_matches = response_dict['FaceMatches']
        if face_matches:
            for match in face_matches:
                logger.info(match)
                logger.info('FaceId:' + match['Face']['FaceId'])
                logger.info('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                if match["Similarity"] > 80:
                    return match['Face']['ExternalImageId']
        else:
            return None
