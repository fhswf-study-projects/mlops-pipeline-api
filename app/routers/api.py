import os
import logging
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from app.middleware import get_bearer_token
from app.core.data_factory import DataFactory
from app.core.celery_client import CeleryClient
from app.core.dvc_client import DVCClient
from app.schemas import UserInputRequest, FeedbackInputRequest, AsyncTaskResponse
from app.constants import EnvConfig


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/api")

BUCKET = os.environ[EnvConfig.S3_BUCKET_NAME.value]
FEEDBACK_PATH = "retrain.joblib"
FILEPATH = "data.joblib"


@router.post("/data-management/upload/file", tags=["Data Management"])
async def upload_file(
    _: Annotated[None, Depends(get_bearer_token)],
    file: UploadFile = File(...),
):
    dvc_client = DVCClient()
    try:
        contents = await file.read()
        filename = str(file.filename)
        if (df := DataFactory.from_bytes(filename, contents)) is None:
            raise HTTPException(
                status_code=422,
                detail="Provided file is corrupt and can't be processed",
            )

        if not dvc_client.save_data_to(obj=df, destination=FILEPATH):
            logger.exception("Data upload to s3-bucket storage failed")
            raise HTTPException(status_code=504, detail="File upload failed")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Something went wrong")
    finally:
        await file.close()

    logger.info(f"Uploaded file {filename} under {FILEPATH}")
    return {"status": "Upload successful", "reference_data_filename": FILEPATH}


@router.post("/data-management/upload/feedback", tags=["Data Management"])
async def upload_feedback(
    _: Annotated[None, Depends(get_bearer_token)], feeback_input: FeedbackInputRequest
):
    dvc_client = DVCClient()
    feeback_input_json = feeback_input.model_dump(by_alias=True)
    try:
        if (df := DataFactory.from_dict(feeback_input_json)) is None:
            raise HTTPException(
                status_code=422,
                detail="Provided file is corrupt and can't be processed",
            )

        if (df_feedback := dvc_client.read_data_from(source=FEEDBACK_PATH)) is not None:
            df = DataFactory.merge_dfs(df, df_feedback)

        if dvc_client.save_data_to(obj=df, destination=FEEDBACK_PATH) is False:
            logger.exception("Data upload to s3-bucket storage failed")
            raise HTTPException(status_code=504, detail="File upload failed")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Something went wrong")

    logger.info(
        f"Uploaded feedback with id: {feeback_input_json['task_id']} under {FEEDBACK_PATH}"
    )
    return {"status": "Upload successful", "reference_data_filename": FEEDBACK_PATH}


# Do we really need async here?
@router.post("/models/train", tags=["Machine Learning"])
async def train_model(
    _: Annotated[None, Depends(get_bearer_token)],
    optimize_hyperparams: bool = False,
    include_user_data: bool = False,
):
    celery_client = CeleryClient()
    task = celery_client.get_task(
        name="workflows.model_training",
        queue="tasks",
        kwargs={
            "body": {
                "optimize": optimize_hyperparams,
                "include_user_data": include_user_data,
                "feedback_path": FEEDBACK_PATH,
                "filepath": FILEPATH,
                "bucket": BUCKET,
            }
        },
    )
    workflow_start = task.apply_async()

    res_id = workflow_start.get()["result_task_id"]
    res_state = celery_client.get_status(res_id)

    logger.info(f"Training workflow started with id: {res_id}")
    return AsyncTaskResponse(id=res_id, status=str(res_state))


# Do we really need async here?
@router.post("/models/predict", tags=["Machine Learning"])
async def predict(
    _: Annotated[None, Depends(get_bearer_token)], user_input: UserInputRequest
):
    celery_client = CeleryClient()
    user_input_json = user_input.model_dump(by_alias=True)

    task = celery_client.get_task(
        name="workflows.make_prediction",
        queue="tasks",
        kwargs={"body": {"data": user_input_json}},
    )
    workflow_start = task.apply_async()

    res_id = workflow_start.get()["result_task_id"]
    res_state = celery_client.get_status(res_id)

    logger.info(f"Prediction workflow started with id: {res_id}")
    return AsyncTaskResponse(id=res_id, status=str(res_state))


@router.get("/tasks/check/{task_id}", tags=["Task Check"])
def check_task(
    _: Annotated[None, Depends(get_bearer_token)], task_id: str
) -> AsyncTaskResponse:
    result = None
    celery_client = CeleryClient()
    status = str(celery_client.get_status(task_id))

    if status.upper() == "SUCCESS":
        result = celery_client.get_result(task_id)

    return AsyncTaskResponse(id=task_id, status=str(status), result=result)
