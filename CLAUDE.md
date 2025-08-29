# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a microservices-based messaging bot system with moderation capabilities. The system is built around a central message handling bot with multiple moderation services that communicate via RabbitMQ messaging.

### Core Services

- **bot** - Main message bot service using async-max-api client for Max messenger API
- **media_facade** - Media processing facade with FastAPI serving as API gateway
- **auto_moderator** - Automated message moderation service
- **manual_moderator** - Human moderation interface
- **table_moderator** - Google Sheets-based moderation tracking
- **vision** - Computer vision service for image/video analysis using PaddleOCR
- **black_list_bot** - Blacklist management service

### Infrastructure

- **PostgreSQL** - Primary database for persistent data
- **Redis** - State management and caching (separate instances per service)  
- **RabbitMQ** - Inter-service messaging and event handling
- **nginx** - Reverse proxy and load balancing

## Development Commands

All services are Python-based using Poetry for dependency management:

```bash
# Run all services
docker-compose up

# Run specific service for development
cd services/[service_name]
poetry install
poetry run [service_name]

# Run tests (where available)
poetry run pytest

# Vision service has multiple entry points:
poetry run app              # Main vision app
poetry run frame_matcher    # Frame matching service
poetry run frame_processor  # Frame processing service  
poetry run mock_video_stream # Mock video stream for testing
```

## Key Libraries and Frameworks

- **aiomax** - Custom async Max messenger API client (in additional/aiomax/)
- **FastAPI** - Web framework for API services
- **FastStream** - Async messaging framework with RabbitMQ integration
- **Tortoise ORM** - Async database ORM
- **PaddleOCR** - Computer vision for text recognition
- **Redis** - Distributed state management via redis-py

## State Management

Services use Redis-based state machines for user session tracking:
- `MemoryStateMachine` for testing
- `RedisStateMachine` for production
- User states tracked in `utils/state_machine/` modules

## Configuration

Services use environment variables loaded via python-dotenv:
- Development configs in each service's `utils/config.py`
- Production secrets in `secrets.env` (not in repo)
- Docker environment variables in `docker-compose.yaml`

## Message Flow

1. User messages arrive at **bot** service via Max API
2. **bot** publishes to RabbitMQ for moderation pipeline
3. **auto_moderator**, **manual_moderator**, **table_moderator** process in parallel
4. **vision** service analyzes images/video content
5. **media_facade** aggregates results and responds back to **bot**
6. **bot** sends final response to user

## Testing

Limited test coverage exists primarily in:
- `services/bot/tests/` - Bot handler tests with factories
- `additional/aiomax/tests/` - API client tests
- Use `poetry run pytest` in individual service directories