"""
Multi-Agent Orchestrator
Implements the Orchestrator-Worker pattern for intelligent agent coordination.
Manages the full lifecycle of a query: routing -> execution -> synthesis -> memory.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base import AgentConfig, AgentInput, AgentOutput, AgentStatus, BaseAgent
from .memory import AgentMemory, EpisodicMemory

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    agent_name: str
    input_data: AgentInput
    output: Optional[AgentOutput] = None
    duration_ms: float = 0
    status: str = "pending"
    error: Optional[str] = None


@dataclass
class WorkflowResult:
    """Complete result of an orchestrated workflow."""
    query: str
    final_answer: str
    confidence: float
    steps: List[WorkflowStep] = field(default_factory=list)
    total_duration_ms: float = 0
    agents_used: List[str] = field(default_factory=list)
    case_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """
    Central orchestrator implementing the Orchestrator-Worker paradigm.

    Flow:
    1. Receive query with optional image/context
    2. Consult memory for similar past cases
    3. Route to specialist agent(s)
    4. Execute agent(s), optionally in parallel
    5. Synthesize results
    6. Store interaction in memory
    7. Optionally record as episodic memory (resolved case)
    """

    def __init__(
        self,
        agents: Dict[str, BaseAgent],
        route_agent: Optional[BaseAgent] = None,
        memory: Optional[AgentMemory] = None,
        llm_provider=None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.agents = agents
        self.route_agent = route_agent
        self.memory = memory or AgentMemory()
        self.llm = llm_provider
        self.config = config or {}

        self.workflow_history: List[WorkflowResult] = []
        logger.info(
            f"Orchestrator initialized with {len(agents)} agents, "
            f"memory={'enabled' if memory else 'default'}"
        )

    async def process(
        self,
        query: str,
        image: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        case_id: Optional[str] = None,
        force_agent: Optional[str] = None,
    ) -> WorkflowResult:
        """
        Main entry point: process a user query through the multi-agent pipeline.
        """
        start_time = time.time()
        context = context or {}
        steps: List[WorkflowStep] = []

        self.memory.add_message("user", query, case_id=case_id)

        # Step 1: Retrieve similar past cases from episodic memory
        similar_cases = self.memory.search_episodes(query, top_k=2)
        if similar_cases:
            case_context = self._format_episode_context(similar_cases)
            context["similar_cases"] = case_context
            logger.info(f"Found {len(similar_cases)} similar past cases")

        # Step 2: Add conversation history to context
        conv_history = self.memory.get_context_window(max_tokens_estimate=2000)
        context["conversation_history"] = conv_history

        if image:
            context["image"] = image

        input_data = AgentInput(query=query, context=context)

        # Step 3: Route to appropriate agent(s)
        if force_agent and force_agent in self.agents:
            selected_agents = [force_agent]
            route_reasoning = f"User forced agent: {force_agent}"
        else:
            selected_agents, route_reasoning = await self._route(input_data)

        # Step 4: Execute selected agents
        agent_outputs = []
        for agent_name in selected_agents:
            step = WorkflowStep(agent_name=agent_name, input_data=input_data)
            step_start = time.time()
            try:
                agent = self.agents[agent_name]
                output = await agent.execute(input_data)
                step.output = output
                step.status = "completed"
                agent_outputs.append((agent_name, output))
            except Exception as e:
                step.error = str(e)
                step.status = "failed"
                logger.error(f"Agent {agent_name} failed: {e}")
            step.duration_ms = (time.time() - step_start) * 1000
            steps.append(step)

        # Step 5: Synthesize final answer
        final_answer, confidence = await self._synthesize(
            query, agent_outputs, context
        )

        # Step 6: Build result
        total_duration = (time.time() - start_time) * 1000
        result = WorkflowResult(
            query=query,
            final_answer=final_answer,
            confidence=confidence,
            steps=steps,
            total_duration_ms=total_duration,
            agents_used=selected_agents,
            case_id=case_id,
            metadata={
                "route_reasoning": route_reasoning,
                "similar_cases_found": len(similar_cases),
                "image_provided": image is not None,
            },
        )

        # Step 7: Store in memory
        self.memory.add_message(
            "assistant",
            final_answer,
            agent_name=",".join(selected_agents),
            case_id=case_id,
            metadata={"confidence": confidence, "duration_ms": total_duration},
        )
        self.workflow_history.append(result)

        return result

    async def _route(self, input_data: AgentInput) -> tuple:
        """Use route agent or LLM to determine which agents to invoke."""
        if self.route_agent:
            try:
                output = await self.route_agent.execute(input_data)
                agent_name = output.result
                reasoning = output.context.get("route_info", {}).get(
                    "reasoning", "Route agent decision"
                )
                if agent_name in self.agents:
                    return [agent_name], reasoning

                if "comprehensive_agent" in self.agents:
                    return ["comprehensive_agent"], f"Fallback: {agent_name} not available"
            except Exception as e:
                logger.warning(f"Route agent failed: {e}")

        return [list(self.agents.keys())[0] if self.agents else "comprehensive_agent"], "Default routing"

    async def _synthesize(
        self,
        query: str,
        agent_outputs: List[tuple],
        context: Dict[str, Any],
    ) -> tuple:
        """Synthesize final answer from agent outputs."""
        if not agent_outputs:
            return "Sorry, no agent could process your query.", 0.0

        if len(agent_outputs) == 1:
            name, output = agent_outputs[0]
            return output.result or output.response, output.confidence

        # Multiple agent outputs -> synthesize with LLM or simple merge
        if self.llm:
            try:
                summaries = []
                for name, output in agent_outputs:
                    summaries.append(f"[{name}] (confidence: {output.confidence:.2f}):\n{output.result}")

                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are synthesizing multiple agent outputs into a coherent, "
                            "actionable answer for a DevOps engineer. Prioritize higher-confidence "
                            "answers. Be concise and structured."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nAgent outputs:\n" + "\n---\n".join(summaries),
                    },
                ]
                resp = await self.llm.generate(messages, max_tokens=1024, temperature=0.3)
                if resp.success:
                    avg_conf = sum(o.confidence for _, o in agent_outputs) / len(agent_outputs)
                    return resp.content, min(avg_conf + 0.1, 1.0)
            except Exception as e:
                logger.warning(f"LLM synthesis failed: {e}")

        # Fallback: pick highest confidence
        best = max(agent_outputs, key=lambda x: x[1].confidence)
        return best[1].result or best[1].response, best[1].confidence

    def _format_episode_context(self, episodes: List[EpisodicMemory]) -> str:
        parts = []
        for ep in episodes:
            parts.append(
                f"[Past Case: {ep.title}]\n"
                f"Problem: {ep.problem_description}\n"
                f"Root Cause: {ep.root_cause}\n"
                f"Solution: {ep.solution}\n"
                f"Tags: {', '.join(ep.tags)}"
            )
        return "\n---\n".join(parts)

    def resolve_case(
        self,
        case_id: str,
        title: str,
        problem: str,
        root_cause: str,
        solution: str,
        steps: List[str],
        tags: List[str],
        resolution_time_min: float = 0,
    ):
        """Record a resolved case as episodic memory."""
        episode = EpisodicMemory(
            case_id=case_id,
            title=title,
            problem_description=problem,
            root_cause=root_cause,
            solution=solution,
            steps=steps,
            tags=tags,
            resolution_time_min=resolution_time_min,
            created_at=time.time(),
        )
        self.memory.add_episode(episode)
        return episode

    def get_workflow_stats(self) -> Dict[str, Any]:
        if not self.workflow_history:
            return {"total_queries": 0}

        durations = [w.total_duration_ms for w in self.workflow_history]
        agents_counter: Dict[str, int] = {}
        for w in self.workflow_history:
            for a in w.agents_used:
                agents_counter[a] = agents_counter.get(a, 0) + 1

        return {
            "total_queries": len(self.workflow_history),
            "avg_duration_ms": sum(durations) / len(durations),
            "avg_confidence": sum(w.confidence for w in self.workflow_history) / len(self.workflow_history),
            "agent_usage": agents_counter,
            "memory_stats": self.memory.get_stats(),
        }
