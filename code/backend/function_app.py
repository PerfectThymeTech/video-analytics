import json
import logging

import azure.durable_functions as df
import azure.functions as func
from models.error import ErrorModel
from models.health import HeartbeatResponse
from models.startworkflow import StartWorkflowRequest
from newstagextraction.orchestration import bp as bp_newstagextraction
from pydantic import ValidationError

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)
app.register_functions(bp_videoextraction)
app.register_functions(bp_newstagextraction)


# An HTTP-Triggered Function with a Durable Functions Client binding
@app.function_name("StartWorkflow")
@app.route(route="startWorkflow")
@app.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    try:
        # Parse body
        payload = json.loads(req.get_body().decode())
        payload_obj: StartWorkflowRequest = StartWorkflowRequest.model_validate(payload)

        # Start orchestrator
        instance_id = await client.start_new(
            payload_obj.orchestrator_workflow_name.value, client_input=payload
        )
        response = client.create_check_status_response(req, instance_id)
    except ValidationError as e:
        logging.error(f"Validation Error occured for task hub payload: {e}")
        return func.HttpResponse(
            body=ErrorModel(
                error_code=10,
                error_message="Provided input is not following the expected data model",
                error_details=json.loads(e.json()),
            ).model_dump_json(),
            status_code=422,
        )
    return response


@app.function_name("Health")
@app.route(route="heartbeat")
@app.http_type(http_type=func.HttpMethod.GET)
async def heartbeat(req: func.HttpRequest) -> func.HttpResponse:
    response = HeartbeatResponse(is_alive=True).model_dump_json()
    return func.HttpResponse(
        body=response, status_code=200, mimetype="application/json"
    )
