# our-ai-demo V0

A reusable AI business/customer-support agent demonstration platform.

## Vision
Build a convincing, functional CLIENT DEMO that can be shown to potential paying businesses. The demo showcases an AI agent that understands customer messages, reasons about requests, uses approved business tools, verifies actions succeeded, and generates natural customer-facing responses.

## Key Differentiator
The AI must NOT claim that an action succeeded unless the actual simulated business state has been verified.

## Project Status
**Phases 0-5 Completed**: The platform is ready for client demonstrations.

### Phases Overview:
- **Phase 0**: Discovery and architecture (targets: TTFT <1s, simple requests <2s, complex requests <5s)
- **Phase 1**: Multi-AI provider support and business context management
- **Phase 2**: Core agent architecture (orchestrator, verifier, simulator, tool registry)
- **Phase 3**: Audit logging and verification components
- **Phase 4**: Frontend implementation (React + TypeScript, 3D hero, chat interface)
- **Phase 5**: Client demo finalization (deployment readiness, error handling, UX polish, monitoring, business context extensibility, demo scenarios, documentation)

## Key Features
- **Multi-Provider AI Support**: Easily switch between Anthropic, NVIDIA, or Mock providers
- **Deterministic Business Simulation**: Consistent demo environment with sample data
- **Transparent Reasoning**: Shows tool usage and verification steps to build trust
- **Interactive 3D Experience**: Engaging hero section with user-controlled rotation
- **Real-time Health Monitoring**: Backend status and audit log visibility
- **Business Context Updates**: Modify demo content without restarting
- **Containerized Deployment**: One-click startup with Docker Compose
- **Error Handling**: Sanitized error messages prevent internal details exposure
- **Performance Validated**: Meets or exceeds Phase 0 latency targets

## Demo Scenarios
The platform includes predefined demonstration scenarios that showcase key capabilities:

1. **Payment Inquiry**: Check payment status and verify results
2. **Subscription Management**: Check and reactivate subscriptions
3. **Product Information**: Retrieve and present business offerings
4. **General Inquiry**: Answer questions from business context
5. **Escalation Path**: Properly escalate to human agent when needed
6. **Error Handling**: Gracefully handle invalid requests and tool failures

Each scenario demonstrates the AI's understanding, planning, action, observation, verification, and response generation cycle.

## Getting Started

### Prerequisites
- Docker and Docker Compose (for containerized deployment)
- OR Python 3.11+ and Node.js 18+ (for local development)

### Option 1: Docker Compose (Recommended for Demos)
1. Copy `.env.example` to `.env` and configure as needed (optional - defaults work for demo)
2. Run: `docker-compose up --build`
3. Open your browser to `http://localhost:8000`
4. The demo will be available at the root URL

### Option 2: Local Development
1. Backend:
   - Copy `.env.example` to `.env` and configure as needed
   - Install Python dependencies: `pip install -r requirements.txt`
   - Start the backend: `python -m app.main`
2. Frontend:
   - Install Node.js dependencies: `cd frontend && npm install`
   - Start the frontend: `npm run dev`
   - The frontend will proxy API requests to the backend

## Performance Validation
Run the benchmark script to verify performance targets:
```bash
python benchmark.py
```
This will test simple and complex request latencies against Phase 0 targets (<2s simple, <5s complex).

## Updating Business Context
Modify the demo content without restarting:
1. Make a PUT request to `/v1/business-context` with the new context JSON
2. Or use the provided script: `python update_business_context.py` (see scripts directory)
3. The updated context will be used in subsequent requests

## Monitoring and Observability
- **Health Endpoint**: `GET /v1/health` returns basic service status
- **Audit Logs**: `GET /v1/audit-logs` returns recent agent operations for transparency
- **Frontend Health Indicator**: Shows backend status and audit log count in the UI

## Security Notes
- Error messages are sanitized to prevent internal details exposure
- No real customer data is used in the simulation
- Default configuration uses the mock provider for safe demonstrations

## Development
- Run tests: `pytest`
- Run specific test suites: `pytest tests/test_chat.py` or `pytest tests/test_health.py`
- Linting and formatting tools are configured in the respective package files

## Acknowledgments
Built with React, TypeScript, Three.js, FastAPI, and Python.

---
*Updated for Phase 5 completion on 2026-08-30*
