from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.ai import get_gemini_service

from app.config import get_settings

from app.database import (
    get_all_users,
    get_db,
    get_user,
    save_user,
    update_plan,
)

from app.schemas import (
    FeedbackRequest,
    UserInput,
)


router = APIRouter()


templates = Jinja2Templates(
    directory="app/templates"
)


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "error": None,
        },
    )


# ---------------------------------------------------------
# GENERATE WORKOUT - HTML FORM
# ---------------------------------------------------------

@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(
    request: Request,

    user_id: str = Form(...),

    username: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = UserInput(
            user_id=user_id,
            username=username,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        ai = get_gemini_service()

        workout_plan = ai.generate_workout(
            name=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )

        nutrition_tip = ai.generate_nutrition_tip(
            goal=data.goal
        )

        user = save_user(
            db,

            user_id=data.user_id,

            username=data.username,

            age=data.age,

            weight=data.weight,

            goal=data.goal,

            intensity=data.intensity,

            original_plan=workout_plan,

            nutrition_tip=nutrition_tip,
        )

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "user": user,
                "plan": workout_plan,
                "tip": nutrition_tip,
                "message": None,
            },
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(exc),
            },
        )


# ---------------------------------------------------------
# SUBMIT FEEDBACK - HTML FORM
# ---------------------------------------------------------

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(
    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        user = get_user(
            db,
            data.user_id,
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User ID not found.",
            )

        ai = get_gemini_service()

        revised_plan = ai.update_workout(
            original_plan=user.original_plan,
            feedback=data.feedback,
            goal=user.goal,
            intensity=user.intensity,
        )

        nutrition_tip = ai.generate_nutrition_tip(
            goal=user.goal
        )

        user = update_plan(
            db,
            user,
            revised_plan,
            nutrition_tip,
        )

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,

                "user": user,

                "plan": revised_plan,

                "tip": nutrition_tip,

                "message":
                    "Your workout plan was successfully updated using your feedback.",
            },
        )

    except HTTPException:

        raise

    except Exception as exc:

        user = get_user(
            db,
            user_id,
        )

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,

                "user": user,

                "plan": None,

                "tip": None,

                "message":
                    f"Could not update the plan: {exc}",
            },
        )


# ---------------------------------------------------------
# ADMIN HTML PAGE
# ---------------------------------------------------------

@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,

    token: str | None = None,

    db: Session = Depends(get_db),
):

    settings = get_settings()

    if token != settings.admin_token:

        raise HTTPException(
            status_code=401,
            detail="Valid admin token required.",
        )

    users = get_all_users(
        db
    )

    return templates.TemplateResponse(
        "all_users.html",
        {
            "request": request,
            "users": users,
        },
    )


# ---------------------------------------------------------
# JSON API - GENERATE WORKOUT
# ---------------------------------------------------------

@router.post(
    "/api/generate-workout"
)
def api_generate_workout(
    payload: UserInput,

    db: Session = Depends(get_db),
):

    try:

        ai = get_gemini_service()

        workout_plan = ai.generate_workout(
            name=payload.username,
            age=payload.age,
            weight=payload.weight,
            goal=payload.goal,
            intensity=payload.intensity,
        )

        nutrition_tip = ai.generate_nutrition_tip(
            goal=payload.goal
        )

        user = save_user(
            db,

            user_id=payload.user_id,

            username=payload.username,

            age=payload.age,

            weight=payload.weight,

            goal=payload.goal,

            intensity=payload.intensity,

            original_plan=workout_plan,

            nutrition_tip=nutrition_tip,
        )

        return {
            "success": True,

            "user_id": user.user_id,

            "workout_plan": workout_plan,

            "nutrition_tip": nutrition_tip,

            "updated_plan": None,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI generation failed: {exc}",
        )


# ---------------------------------------------------------
# JSON API - FEEDBACK
# ---------------------------------------------------------

@router.post(
    "/api/submit-feedback"
)
def api_submit_feedback(
    payload: FeedbackRequest,

    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        payload.user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User ID not found.",
        )

    try:

        ai = get_gemini_service()

        revised_plan = ai.update_workout(
            original_plan=user.original_plan,

            feedback=payload.feedback,

            goal=user.goal,

            intensity=user.intensity,
        )

        nutrition_tip = ai.generate_nutrition_tip(
            goal=user.goal
        )

        update_plan(
            db,
            user,
            revised_plan,
            nutrition_tip,
        )

        return {
            "success": True,

            "user_id": user.user_id,

            "workout_plan": revised_plan,

            "nutrition_tip": nutrition_tip,

            "updated_plan": revised_plan,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI update failed: {exc}",
        )


# ---------------------------------------------------------
# ADMIN - GET USERS JSON
# ---------------------------------------------------------

@router.get(
    "/api/users"
)
def api_users(
    token: str | None = None,

    db: Session = Depends(get_db),
):

    settings = get_settings()

    if token != settings.admin_token:

        raise HTTPException(
            status_code=401,
            detail="Valid admin token required.",
        )

    users = get_all_users(
        db
    )

    return [
        {
            "user_id": user.user_id,

            "username": user.username,

            "age": user.age,

            "weight": user.weight,

            "goal": user.goal,

            "intensity": user.intensity,

            "created_at":
                user.created_at.isoformat(),

            "has_updated_plan":
                bool(user.updated_plan),
        }

        for user in users
    ]


# ---------------------------------------------------------
# ADMIN - DELETE USER
# ---------------------------------------------------------

@router.delete(
    "/api/users/{user_id}"
)
def api_delete_user(
    user_id: str,

    token: str | None = None,

    db: Session = Depends(get_db),
):

    settings = get_settings()

    if token != settings.admin_token:

        raise HTTPException(
            status_code=401,
            detail="Valid admin token required.",
        )

    user = get_user(
        db,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User ID not found.",
        )

    db.delete(user)

    db.commit()

    return {
        "success": True,

        "deleted": True,

        "user_id": user_id,
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@router.get(
    "/health"
)
def health():

    return {
        "status": "ok",

        "service": "FitBuddy",
    }