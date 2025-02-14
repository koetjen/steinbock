import click
import sys

from pathlib import Path

from steinbock._cli.utils import OrderedClickGroup
from steinbock.segmentation import cellprofiler


@click.group(
    name="cellprofiler",
    cls=OrderedClickGroup,
    help="Segment objects in probability images using CellProfiler",
)
def cellprofiler_cmd_group():
    pass


@cellprofiler_cmd_group.command(
    name="prepare", help="Prepare a CellProfiler segmentation pipeline"
)
@click.option(
    "-o",
    "segmentation_pipeline_file",
    type=click.Path(dir_okay=False),
    default="cell_segmentation.cppipe",
    show_default=True,
    help="Path to the CellProfiler segmentation pipeline output file",
)
def prepare_cmd(segmentation_pipeline_file):
    cellprofiler.create_and_save_segmentation_pipeline(
        segmentation_pipeline_file
    )
    click.echo(segmentation_pipeline_file)


@cellprofiler_cmd_group.command(
    name="run", help="Run a object segmentation batch using CellProfiler"
)
@click.option(
    "--cellprofiler",
    "cellprofiler_binary",
    type=click.STRING,
    default="cellprofiler",
    show_default=True,
    help="CellProfiler binary",
)
@click.option(
    "--plugins-directory",
    "cellprofiler_plugin_dir",
    type=click.Path(file_okay=False),
    default="/opt/cellprofiler_plugins",
    show_default=True,
    help="Path to the CellProfiler plugin directory",
)
@click.option(
    "--pipe",
    "segmentation_pipeline_file",
    type=click.Path(exists=True, dir_okay=False),
    default="cell_segmentation.cppipe",
    show_default=True,
    help="Path to the CellProfiler segmentation pipeline file",
)
@click.option(
    "--probabs",
    "probabilities_dir",
    type=click.Path(exists=True, file_okay=False),
    default="ilastik_probabilities",
    show_default=True,
    help="Path to the probabilities directory",
)
@click.option(
    "-o",
    "mask_dir",
    type=click.Path(file_okay=False),
    default="masks",
    show_default=True,
    help="Path to the mask output directory",
)
def run_cmd(
    cellprofiler_binary,
    cellprofiler_plugin_dir,
    segmentation_pipeline_file,
    probabilities_dir,
    mask_dir,
):
    if probabilities_dir not in ("ilastik_probabilities"):
        click.echo(
            "WARNING: When using custom probabilities from unknown origins, "
            "make sure to adapt the CellProfiler pipeline accordingly",
            file=sys.stderr,
        )
    Path(mask_dir).mkdir(exist_ok=True)
    result = cellprofiler.try_segment_objects(
        cellprofiler_binary,
        segmentation_pipeline_file,
        probabilities_dir,
        mask_dir,
        cellprofiler_plugin_dir=cellprofiler_plugin_dir,
    )
    sys.exit(result.returncode)
