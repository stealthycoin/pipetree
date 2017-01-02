from pipetree.stage import LocalFilePipelineStage,\
    LocalDirectoryPipelineStage, ExecutorPipelineStage

__version__ = '0.1.0'

STAGES = {
    "LocalDirectoryPipelineStage": LocalDirectoryPipelineStage,
    "LocalFilePipelineStage": LocalFilePipelineStage,
    "ExecutorPipelineStage": ExecutorPipelineStage
}

from pipetree.pipeline import Pipeline
