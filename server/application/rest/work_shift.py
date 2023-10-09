"""
This module contains the RESTful route handlers
for work shifts in the server application.
"""
import json
from flask import Blueprint, Response, request
from flask_cors import cross_origin
from repository.memrepo import MemRepo
from use_cases.list_workshifts import workshift_list_use_case
from use_cases.add_workshifts import workshift_add_multiple_use_case
from use_cases.delete_workshifts import delete_shift_use_case
from serializers.work_shift import WorkShiftJsonEncoder
from errors.responses import ResponseFailure, ResponseTypes

blueprint = Blueprint("work_shift", __name__)

shifts = [
    {
        "code": "f853578c-fc0f-4e65-81b8-566c5dffa35a",
        "worker": "volunteer@slu.edu",
        "shelter": "shelter-id-for-st-patric-center",
        "start_time": 1696168800000,
        "end_time": 1696179600000,
    },
    {
        "code": "f853578c-fc0f-4e65-81b8-566c5dffa35b",
        "worker": "volunteer2@slu.edu",
        "shelter": "shelter-id-for-st-patric-center",
        "start_time": 1696255200000,
        "end_time": 1696269600000,
    },
]

HTTP_STATUS_CODES_MAPPING = {
    ResponseTypes.NOT_FOUND: 404,
    ResponseTypes.SYSTEM_ERROR: 500,
    ResponseTypes.AUTHORIZATION_ERROR: 403,
    ResponseTypes.PARAMETER_ERROR: 400,
    ResponseTypes.SUCCESS: 200
}



@blueprint.route("/shifts", methods=["GET", "POST"])
@cross_origin()
def work_shifts():
    """
    On GET: The function returns a list of all work shifts in the system.
    On POST: The function adds shifts to the system.
    """
    if request.method == "GET":
        repo = MemRepo(shifts)
        result = workshift_list_use_case(repo)
        return Response(
            json.dumps(result, cls=WorkShiftJsonEncoder),
            mimetype="application/json",
            status=200,
        )
    elif request.method == "POST":
        user = get_user_from_token(request.headers)
        data = request.get_json()
        for shift in data:
            shift["worker"] = user
        repo = MemRepo(shifts)
        workshift_add_multiple_use_case(repo, data)
        return Response(
            json.dumps(data, cls=WorkShiftJsonEncoder),
            mimetype="application/json",
            status=200,
        )

def get_user_from_token(headers):
    return headers["Authorization"]

@blueprint.route("/shifts/<shift_id>", methods=["DELETE"])
@cross_origin()
def delete_work_shift(shift_id):
    try:
        shift_id = str(shift_id)
        user_email = get_user_from_token(request.headers)
        repo = MemRepo(shifts)

        response = delete_shift_use_case(repo, shift_id, user_email)
        status_code = HTTP_STATUS_CODES_MAPPING.get(response.response_type, 500)
        if isinstance(response, ResponseFailure):
            return response.message, status_code

        return response.value, status_code

    except ValueError as exc:
        response_failure = ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
        error_message = response_failure.message
        e_code = HTTP_STATUS_CODES_MAPPING.get(ResponseTypes.SYSTEM_ERROR, 500)
        return error_message, e_code







