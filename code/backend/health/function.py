import azure.functions as func
from models.health import HeartbeatResponse


bp = func.Blueprint()

@bp.function_name("Health")
@bp.route(route="v1/heartbeat")
@bp.http_type(http_type=func.HttpMethod.GET)
async def heartbeat(req: func.HttpRequest) -> func.HttpResponse:
    response = HeartbeatResponse(is_alive=True).model_dump_json()
    return func.HttpResponse(
        body=response, status_code=200, mimetype="application/json"
    )
