"""Memory writer service."""

from services.memory_service import MemoryService
from services.message_service import MessageService


class MemoryWriterService:
    """Create conversation summaries."""

    def __init__(self):
        self.memory_service = MemoryService()
        self.message_service = MessageService()


    def should_update(
        self,
        user_id: int,
    ) -> bool:
        """Check if memory needs update."""

        messages = self.message_service.get_messages(
            user_id
        )

        return len(messages) > 0 and len(messages) >= 10