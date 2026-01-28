"""Orchestration and workflow management.

This package provides the VideoGenerator for orchestrating the complete
video generation pipeline with error isolation and resource cleanup.

Exports:
    VideoGenerator: Main pipeline orchestrator
    GenerationResult: Result of single video generation
    BatchResult: Result of batch video generation
"""

from src.orchestration.video_generator import (
    VideoGenerator,
    GenerationResult,
    BatchResult,
)

__all__ = [
    "VideoGenerator",
    "GenerationResult",
    "BatchResult",
]
