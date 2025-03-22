"""Define all needed Request/Response endpoints schemas here."""

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class UserInputRequest(BaseModel):
    age: float = Field(..., ge=16, le=91, description="How old are you? Accepted age: 16-91")
    workclass: Literal[
        'Private',
        'Local-gov',
        'Self-emp-not-inc',
        'Federal-gov',
        'State-gov'
        'Self-emp-inc',
        'Without-pay',
        'Never-worked'
    ] = Field(
        ..., description="Select your workclass to represent your employment status."
    )
    fnlwgt: float = Field(..., ge=10000, le=1500000,
                          description="Insert your final weight. In other words, the number of people the census believes the entry represents. 10.000-1.500.000")
    education: Literal[
        '11th',
        'HS-grad',
        'Assoc-acdm',
        'Some-college',
        '10th',
        'Prof-school'
        '7th-8th',
        'Bachelors',
        'Masters',
        'Doctorate',
        '5th-6th',
        'Assoc-voc',
        '9th',
        '12th',
        '1st-4th',
        'Preschool'
    ] = Field(
        ..., description="Select your highest education-level archieved."
    )
    educational_num: float = Field(
        ...,
        ge=1,
        le=16,
        description="The highest level of education achieved in numerical form. 1-16",
        serialization_alias="educational-num",
    )
    marital_status: Literal[
        'Never-married',
        'Married-civ-spouse',
        'Widowed',
        'Divorced',
        'Separated',
        'Married-spouse-absent',
        'Married-AF-spouse'
    ] = Field(
        ...,
        description="Select your marital status.",
        serialization_alias="marital-status",
    )
    occupation: Literal[
        'Machine-op-inspct',
        'Farming-fishing',
        'Protective-serv',
        'Other-service',
        'Prof-specialty',
        'Craft-repair',
        'Adm-clerical',
        'Exec-managerial',
        'Tech-support',
        'Sales',
        'Priv-house-serv',
        'Transport-moving',
        'Handlers-cleaners',
        'Armed-Forces'
    ] = Field(
        ..., description="Select your general type of occupation."
    )
    relationship: Literal[
        'Own-child',
        'Husband',
        'Not-in-family',
        'Unmarried',
        'Wife',
        'Other-relative'
    ] = Field(
        ..., description="Select your relationship."
    )
    race: Literal[
        'Black',
        'White',
        'Asian-Pac-Islander',
        'Other',
        'Amer-Indian-Eskimo'
    ] = Field(..., description="Select your race.")
    gender: Literal["Male", "Female"] = Field(..., description="Select your gender.")
    capital_gain: float = Field(..., ge=0, le=100000, description="Insert your capital gain.0-100.000",
                                serialization_alias="capital-gain")
    capital_loss: float = Field(..., ge=0, le=5000, description="Insert your capital loss. 0-5.000",
                                serialization_alias="capital-loss")
    hours_per_week: int = Field(..., ge=0, le=65, description="Insert your hours per week you work at. 1-65",
                                serialization_alias="hours-per-week")
    native_country: Literal[
        'United-States',
        'Peru',
        'Guatemala',
        'Mexico',
        'Dominican-Republic',
        'Ireland',
        'Germany',
        'Philippines',
        'Thailand',
        'Haiti',
        'El-Salvador',
        'Puerto-Rico',
        'Vietnam',
        'South',
        'Columbia',
        'Japan',
        'India',
        'Cambodia',
        'Poland',
        'Laos',
        'England',
        'Cuba',
        'Taiwan',
        'Italy',
        'Canada',
        'Portugal',
        'China',
        'Nicaragua',
        'Honduras',
        'Iran',
        'Scotland',
        'Jamaica',
        'Ecuador',
        'Yugoslavia',
        'Hungary',
        'Hong',
        'Greece',
        'Trinadad&Tobago',
        'Outlying-US(Guam-USVI-etc)',
        'France',
        'Holand-Netherlands'
    ] = Field(..., description="Insert your country of origin.", serialization_alias="native-country")


class FeedbackInputRequest(UserInputRequest):
    task_id: str
    income: Literal["<=50K", ">50K"] = Field(+
                                             ..., description="Income class (true label)"
                                             )


class FileMetadataResponse(BaseModel):
    columns: List[str]


class AsyncTaskResponse(BaseModel):
    id: str
    status: str
    result: Optional[Any] = None
