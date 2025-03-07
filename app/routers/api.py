import os
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import UserInputRequest, FileMetadataResponse, AsyncTaskResponse
from app.constants import EnvConfig
from app.core.celery_client import CeleryClient
from app.core.s3_client import S3Client


logger = logging.getLogger()

router = APIRouter(prefix="/api", tags=["PredictionMaker"])

BUCKET = os.environ[EnvConfig.S3_BUCKET_NAME.value]


@router.post("/data-management/upload", tags=["Data Management"])
async def file_upload(file: UploadFile = File(...), append: bool = False):
    s3_client = S3Client()
    try:
        contents = await file.file.read()
        # TODO: capsulate reading depending on the file ext for accessing columns
        # Save the columns as metadata to object which speed ups processing
        upload_success = s3_client.upload_file(
            bucket=BUCKET,
            obj=contents,
            object_name=file.filename,
            extra_args={"Metadata": {"column1": "value1"}},
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Something went wrong")
    finally:
        await file.file.close()

    if not upload_success:
        logger.exception("Upload failed, most likely boto3.ClintError")
        raise HTTPException(status_code=500, detail="Upload failed")

    return {"status": "Upload successful"}


@router.get("/data-management/metadata/get", tags=["Data Management"])
def get_metadata(filename: str) -> FileMetadataResponse:
    s3_client = S3Client()
    metadata = s3_client.get_metadata(bucket=BUCKET, object_name=filename)
    return FileMetadataResponse(metadata)


@router.post("/models/train", tags=["Machine Learning"])
async def train_model(optimize_hyperparams: bool = False):
    celery_client = CeleryClient()
    task = celery_client.get_task(
        name="workflows.model_training",
        queue="tasks",
        kwargs={"body": {"optimize": optimize_hyperparams}},
    )
    res = task.apply_async()
    return AsyncTaskResponse(id=res.id, status=str(res.state))


@router.post("/models/predict", tags=["Machine Learning"])
async def predict(user_input: UserInputRequest):
    celery_client = CeleryClient()
    task = celery_client.get_task(
        name="workflows.make_prediction",
        queue="tasks",
        kwargs={"body": {"data": user_input.model_dump()}},
    )
    res = task.apply_async()
    return AsyncTaskResponse(id=res.id, status=str(res.state))


@router.route("/tasks/check/{task_id}", tags=["Task Check"])
def check_task(task_id: str) -> AsyncTaskResponse:
    status = CeleryClient.get_status(task_id)
    result = (
        CeleryClient.get_result(task_id) if str(status).upper() != "PENDING" else None
    )
    return AsyncTaskResponse(id=task_id, status=str(status), result=result)
