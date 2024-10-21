import azure.functions as func
from models.health import HeartbeatResponse

from videoupload.function import bp as bp_videoupload

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
app.register_functions(bp_videoupload)


@app.function_name("Health")
@app.route(route="heartbeat")
@app.http_type(http_type=func.HttpMethod.GET)
async def heartbeat(req: func.HttpRequest) -> func.HttpResponse:
    response = HeartbeatResponse(is_alive=True).model_dump_json()
    return func.HttpResponse(
        body=response, status_code=200, mimetype="application/json"
    )
