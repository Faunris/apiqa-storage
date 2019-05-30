import logging

from django.core.files import File
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from apiqa_storage.minio_storage import storage

logger = logging.getLogger(__name__)


def get_file_response(model, file_uid: str, user=None):
    user_filter = {'user': user} if user else {}

    obj = get_object_or_404(
        model,
        attachments__contains=[{'uid': str(file_uid)}],
        **user_filter,
    )

    attachments = [
        file for file in obj.attachments if file['uid'] == str(file_uid)
    ]

    if len(attachments) > 1:
        logger.warning("Few files with uid %s", file_uid)

    file = attachments[0]

    minio_file_resp = storage.file_get(file['path'], file['bucket_name'])

    resp = FileResponse(File(
        name=file['name'],
        file=minio_file_resp,
    ), as_attachment=True)
    resp['Content-Length'] = file['size']

    return resp
