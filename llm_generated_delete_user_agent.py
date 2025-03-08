from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, constr
from comms_api.authentication.authentication import JWTBearer

router = APIRouter(prefix="/api/v1", tags=["users"])

class DeleteUserAgentsRequest(BaseModel):
    """Request model for deleting user agents."""
    user_agent_ids: list[constr(min_length=1)]  # List of user agent IDs to delete

@router.delete("/user_agents", response_model=dict)
async def delete_user_agents(request_body: DeleteUserAgentsRequest, token: str = Depends(JWTBearer())):
    """
    Delete specified user agents from all devices.

    Parameters
    ----------
    request_body : DeleteUserAgentsRequest
        The request body containing user agent IDs to delete.
    token : str
        JWT token for authentication and authorization.

    Raises
    ------
    HTTPException
        If the user agent IDs are invalid or if the operation fails.

    Returns
    -------
    dict
        A success message indicating deletion of user agents.
    """
    try:
        # Simulate the deletion process
        user_agent_ids = request_body.user_agent_ids

        for agent_id in user_agent_ids:
            # Logic for deleting the user agent (pseudo code)
            # delete_user_agent(agent_id)

            pass  # Replace with actual deletion logic

        return {"message": "User agents deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user agents: {str(e)}")
