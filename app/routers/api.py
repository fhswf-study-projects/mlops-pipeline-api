import os
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import UserInputRequest, AsyncTaskResponse
from app.constants import EnvConfig
from app.core.data_factory import DataFactory
from app.core.celery_client import CeleryClient
from app.core.dvc_client import DVCClient


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

BUCKET = os.environ[EnvConfig.S3_BUCKET_NAME.value]
FILEPATH = "data.joblib"


@router.post("/data-management/upload", tags=["Data Management"])
async def file_upload(file: UploadFile = File(...), append: bool = False):
    dvc_client = DVCClient()
    try:
        contents = await file.read()
        filename = str(file.filename)
        if (df := DataFactory.from_bytes(filename, contents)) is None:
            raise HTTPException(
                status_code=422,
                detail="Provided file is corrupt and can't be processed",
            )
        logger.warning(f"Data read {str(type(df))}")

        if not dvc_client.save_data_to(obj=df, destination=FILEPATH):
            logger.exception("Data upload to s3-bucket storage failed")
            raise HTTPException(status_code=504, detail="File upload failed")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Something went wrong")
    finally:
        await file.close()

    return {"status": "Upload successful", "reference_data_filename": FILEPATH}


# @router.get("/data-management/metadata/get", tags=["Data Management"])
# def get_metadata(filename: str) -> FileMetadataResponse:
#     dvc_client = DVCClient()
#     metadata = dvc_client.get_metadata(bucket=BUCKET, object_name=filename)
#     return FileMetadataResponse(metadata)


# Do we really need async here?
@router.post("/models/train", tags=["Machine Learning"])
async def train_model(optimize_hyperparams: bool = False):
    celery_client = CeleryClient()
    task = celery_client.get_task(
        name="workflows.model_training",
        queue="tasks",
        kwargs={
            "body": {
                "optimize": optimize_hyperparams,
                "filepath": FILEPATH,
                "bucket": BUCKET,
            }
        },
    )
    res = task.apply_async()
    return AsyncTaskResponse(id=res.id, status=str(res.state))


# Do we really need async here?
@router.post("/models/predict", tags=["Machine Learning"])
async def predict(user_input: UserInputRequest):
    celery_client = CeleryClient()
    task = celery_client.get_task(
        name="workflows.make_prediction",
        queue="tasks",
        kwargs={"body": {"data": user_input.model_dump(by_alias=True)}},
    )
    workflow_start = task.apply_async()

    res_id = workflow_start.get()["result_task_id"]
    res_state = celery_client.get_status(res_id)

    return AsyncTaskResponse(id=res_id, status=str(res_state))


@router.get("/tasks/check/{task_id}", tags=["Task Check"])
def check_task(task_id: str) -> AsyncTaskResponse:
    result = None
    celery_client = CeleryClient()
    status = str(celery_client.get_status(task_id))

    if status.upper() == "SUCCESS":
        result = celery_client.get_result(task_id)

    return AsyncTaskResponse(id=task_id, status=str(status), result=result)
