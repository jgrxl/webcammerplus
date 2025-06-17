import logging
from typing import Optional, Dict, Any, TypeVar, Type
from functools import lru_cache
from flask_socketio import SocketIO

from client.influx_client import InfluxDBClient
from config import get_config
from repositories.user_repository import UserRepository, InMemoryUserRepository
from repositories.event_repository import EventRepository
from services.user_service import UserService
from services.stripe_service import StripeService
from services.chaturbate_event_service import EventProcessingService
from services.websocket_service import WebSocketService
from services.translate_service import TranslateService
from services.reply_service import ReplyService
from services.write_service import WriteService
from services.base_ai_client import NovitaAIClient
from services.demo_event_service import DemoEventService
from services.message_service import MessageService
from services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DependencyContainer:
    """Dependency injection container for managing service instances."""
    
    def __init__(self):
        self._instances: Dict[Type, Any] = {}
        self._factories: Dict[Type, Any] = {}
        self._config = get_config()
        
    def register_singleton(self, service_type: Type[T], instance: T) -> None:
        """Register a singleton instance.
        
        Args:
            service_type: The service type/interface
            instance: The instance to register
        """
        self._instances[service_type] = instance
        logger.debug(f"Registered singleton: {service_type.__name__}")
        
    def register_factory(self, service_type: Type[T], factory: Any) -> None:
        """Register a factory function for creating instances.
        
        Args:
            service_type: The service type/interface
            factory: Callable that creates instances
        """
        self._factories[service_type] = factory
        logger.debug(f"Registered factory: {service_type.__name__}")
        
    def get(self, service_type: Type[T]) -> T:
        """Get an instance of a service.
        
        Args:
            service_type: The service type to get
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service is not registered
        """
        # Check singletons first
        if service_type in self._instances:
            return self._instances[service_type]
            
        # Check factories
        if service_type in self._factories:
            return self._factories[service_type]()
            
        raise KeyError(f"Service not registered: {service_type.__name__}")
        
    def has(self, service_type: Type[T]) -> bool:
        """Check if a service is registered.
        
        Args:
            service_type: The service type to check
            
        Returns:
            True if registered, False otherwise
        """
        return service_type in self._instances or service_type in self._factories


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container."""
    global _container
    if _container is None:
        _container = DependencyContainer()
        _initialize_container(_container)
    return _container


def _initialize_container(container: DependencyContainer) -> None:
    """Initialize the dependency container with all services.
    
    Args:
        container: The container to initialize
    """
    config = get_config()
    
    # Register InfluxDB client
    try:
        influx_client = InfluxDBClient()
        container.register_singleton(InfluxDBClient, influx_client)
    except Exception as e:
        logger.error(f"Failed to initialize InfluxDB client: {e}")
        
    # Register repositories
    container.register_singleton(UserRepository, InMemoryUserRepository())
    
    if container.has(InfluxDBClient):
        container.register_factory(
            EventRepository,
            lambda: EventRepository(container.get(InfluxDBClient))
        )
    
    # Register AI client
    try:
        novita_client = NovitaAIClient(config.novita.api_key)
        container.register_singleton(NovitaAIClient, novita_client)
    except Exception as e:
        logger.error(f"Failed to initialize Novita AI client: {e}")
    
    # Register services
    container.register_factory(
        UserService,
        lambda: UserService(container.get(UserRepository))
    )
    
    # Register Stripe service if configured
    try:
        container.register_singleton(StripeService, StripeService())
    except Exception as e:
        logger.error(f"Failed to initialize Stripe service: {e}")
    
    # Register Authentication Service
    from services.auth_service import AuthService
    try:
        auth_service = AuthService(
            user_service=container.get(UserService) if container.has(UserService) else None,
            stripe_service=container.get(StripeService) if container.has(StripeService) else None
        )
        container.register_singleton(AuthService, auth_service)
    except Exception as e:
        logger.error(f"Failed to initialize Auth service: {e}")
    
    container.register_singleton(EventProcessingService, EventProcessingService())
    container.register_singleton(WebSocketService, WebSocketService())
    container.register_singleton(DemoEventService, DemoEventService())
    
    # Message and conversation services
    container.register_singleton(MessageService, MessageService())
    container.register_singleton(ConversationService, ConversationService())
    
    # Register AI services
    if container.has(NovitaAIClient):
        ai_client = container.get(NovitaAIClient)
        container.register_factory(
            TranslateService,
            lambda: TranslateService(ai_client)
        )
        container.register_factory(
            ReplyService,
            lambda: ReplyService(ai_client)
        )
        container.register_factory(
            WriteService,
            lambda: WriteService(ai_client)
        )


# Convenience functions for common services
@lru_cache(maxsize=1)
def get_user_service() -> UserService:
    """Get the user service instance."""
    return get_container().get(UserService)


@lru_cache(maxsize=1)
def get_stripe_service() -> StripeService:
    """Get the stripe service instance."""
    return get_container().get(StripeService)


@lru_cache(maxsize=1)
def get_event_service() -> EventProcessingService:
    """Get the event processing service instance."""
    return get_container().get(EventProcessingService)


@lru_cache(maxsize=1)
def get_websocket_service() -> WebSocketService:
    """Get the websocket service instance."""
    return get_container().get(WebSocketService)


@lru_cache(maxsize=1)
def get_translate_service() -> TranslateService:
    """Get the translate service instance."""
    return get_container().get(TranslateService)


@lru_cache(maxsize=1)
def get_reply_service() -> ReplyService:
    """Get the reply service instance."""
    return get_container().get(ReplyService)


@lru_cache(maxsize=1)
def get_write_service() -> WriteService:
    """Get the write service instance."""
    return get_container().get(WriteService)


def get_event_repository() -> Optional[EventRepository]:
    """Get the event repository instance."""
    container = get_container()
    if container.has(EventRepository):
        return container.get(EventRepository)
    return None


def set_socketio(socketio: SocketIO) -> None:
    """Set the SocketIO instance on the WebSocket service.
    
    Args:
        socketio: The SocketIO instance
    """
    websocket_service = get_websocket_service()
    websocket_service.set_socketio(socketio)


def get_dependency(service_type: Type[T]) -> T:
    """Get a dependency from the container.
    
    This is a convenience function for getting dependencies
    without needing to access the container directly.
    
    Args:
        service_type: The service type to get
        
    Returns:
        Service instance
    """
    return get_container().get(service_type)