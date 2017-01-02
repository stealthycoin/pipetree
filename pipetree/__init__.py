__version__ = '0.1.0'

from pipetree.stage import LocalDirectoryPipelineStage, ExecutorPipelineStage

STAGES = [
    "LocalDirectoryPipelineStage",
    "ExecutorPipelineStage"
]

from pipetree.pipeline import Pipeline
