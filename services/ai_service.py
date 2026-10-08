import time
from ai_router import AIRouter
from services.ai_security_service import AISecurityService
from services.ai_request_service import AIRequestService
from services.message_service import MessageService
from services.ban_service import BanService
from services.rate_limit_service import RateLimitService
from services.memory_service import MemoryService
from services.memory_writer_service import MemoryWriterService

class AIService:
    """Handle AI conversations."""

    def __init__(self) -> None:
        self.ai_router = AIRouter()
        self.message_service = MessageService()
        self.security_service = AISecurityService()
        self.request_service = AIRequestService()
        self.ban_service = BanService()
        self.rate_limit_service = RateLimitService()
        self.memory_service = MemoryService()
        self.memory_writer_service = MemoryWriterService()
    def ask(
        self,
        user_id: int,
        prompt: str,
    ) -> str:
        if self.ban_service.is_banned(user_id):

            self.security_service.log_request(
                user_id=user_id,
                content=prompt,
                status="banned",
            )

            return "⛔ دسترسی شما به دستیار هوش مصنوعی مسدود شده است."

        if not self.rate_limit_service.is_allowed(user_id):

            self.security_service.log_request(
                user_id=user_id,
                content=prompt,
                status="rate_limited",
            )

            return "⛔ درخواست‌های زیادی ارسال کرده‌اید.\n" "لطفاً یک دقیقه صبر کنید."

        """Process user message and return AI response."""

        allowed = self.security_service.check_request(prompt)

        if not allowed:

            self.security_service.log_request(
                user_id=user_id,
                content=prompt,
                status="blocked",
            )

            return "⛔ درخواست شما به دلیل قوانین امنیتی " "قابل پردازش نیست."

        self.message_service.save_message(
            user_id=user_id,
            role="user",
            content=prompt,
        )

        if self.memory_writer_service.should_update(user_id):

            self.memory_service.save_memory(
                user_id=user_id,
                summary=(
                    "User conversation history exists. "
                    "Summary generation pending."
                ),
            )
                
        
        history = self.message_service.get_messages(
            user_id
            )

        memory = self.memory_service.get_memory(
                user_id
            )


        context = "\n".join(
            [
                f"{role}: {content}"
                for role, content, _ in history[-10:]
            ]
        )

        final_prompt = (
            "Conversation memory:\n"
            f"{memory}\n\n"
            "Recent conversation:\n"
            f"{context}\n\n"
            "User question:\n"
            f"{prompt}"
        )

        start_time = time.time()

        response = self.ai_router.ask(final_prompt)

        response_time = time.time() - start_time

        

        self.message_service.save_message(
            user_id=user_id,
            role="assistant",
            content=response,
        )

        self.request_service.log_request(
            user_id=user_id,
            content=prompt,
            status="allowed",
            provider=getattr(
                self.ai_router,
                "last_provider",
                "unknown",
            ),
            response_time=response_time,
            prompt_length=len(prompt),
            response_length=len(response),
        )

        return response
