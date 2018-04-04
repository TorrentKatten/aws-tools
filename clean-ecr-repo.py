#!/usr/bin/env python

import datetime
import json
from io import StringIO
from sys import argv

import sh


def delete_all_images_older_than_days_form_repo(repo, days_to_keep):
    image_details = get_all_images_in_ecr_repo(repo)

    images_to_delete = get_images_older_than_number_of_days(image_details, days_to_keep)

    print repo + " contains " + str(len(image_details)) + " images, of which " + str(len(
        images_to_delete)) + " are older than " + str(days_to_keep) + " and will be deleted"

    remove_images(repo, images_to_delete)


# query AWS for all images in ECR repo
def get_all_images_in_ecr_repo(repo):
    buf = StringIO()
    sh.aws("ecr", "describe-images", "--repository-name", repo, _out=buf)

    aws_response = json.loads(buf.getvalue())

    return aws_response["imageDetails"]


# filter out all images uploaded before the number of days sent in
def get_images_older_than_number_of_days(images, days):
    images_older_than_days = []
    for image in images:
        upload_date = datetime.datetime.fromtimestamp(
            int(int(image["imagePushedAt"]))
        )

        if upload_date < datetime.datetime.now() - datetime.timedelta(days=int(days)):
            images_older_than_days.append(image["imageDigest"])

    return images_older_than_days


def delete_images_with_digest(repo, image_digests):
    if len(image_digests) != 0:
        sh.aws("ecr", "batch-delete-image", "--repository-name", repo, "--image-ids",
               image_digests)


# removes all images sent in, in batches of 10.
# can possibly be tuned more, but AWS API only accepts
# <100 characters in the arguments
def remove_images(repo, images):
    limit = 10
    num = 0
    image_digest_to_delete = []

    for image in images:
        image_digest_to_delete.append("imageDigest=" + image)
        num += 1
        if num >= limit:
            delete_images_with_digest(repo, image_digest_to_delete)
            num = 0
            image_digest_to_delete = []

    if len(image_digest_to_delete) != 0:
        delete_images_with_digest(repo, image_digest_to_delete)


def print_help():
    print "usage:"
    print "clean_ecr_repo <repository> <days_to_keep>"
    print "requires aws-cli installed and configured"


if __name__ == '__main__':
    if len(argv) < 3:
        print_help()
    if argv[1] == "--help":
        print_help()

    delete_all_images_older_than_days_form_repo(argv[1], argv[2])
