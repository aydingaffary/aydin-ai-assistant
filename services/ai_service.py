from ai_router import AIRouter

from services.message_service import MessageService
from services.ai_security_service import AISecurityService


class AIService:
    """Handle AI conversations."""

    def __init__(self) -> None:
        self.ai_router = AIRouter()
        self.message_service = MessageService()
        self.security_service = AISecurityService()

    def ask(
        self,
        user_id: int,
        prompt: str,
    ) -> str:
        """Process user message and return AI response."""

        # Log user AI request
        self.security_service.log_request(
            user_id=user_id,
            content=prompt,
            status="allowed",
        )


        self.message_service.save_message(
            user_id=user_id,
            role="user",
            content=prompt,
        )


        history = self.message_service.get_messages(
            user_id
        )


        context = "\n".join(
            [
                f"{role}: {content}"
                for role, content, _ in history
            ]
        )


        final_prompt = (
            "Conversation history:\n"
            f"{context}\n\n"
            "User question:\n"
            f"{prompt}"
        )


        response = self.ai_router.ask(
            final_prompt
        )


        self.message_service.save_message(
            user_id=user_id,
            role="assistant",
            content=response,
        )


        return response