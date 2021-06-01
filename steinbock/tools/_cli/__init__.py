import click

from pathlib import Path

from steinbock import io
from steinbock._cli.utils import OrderedClickGroup
from steinbock._env import check_steinbock_version
from steinbock.tools import matching
from steinbock.tools._cli.mosaics import mosaics_cmd_group


@click.group(
    name="tools", cls=OrderedClickGroup, help="Various utilities and tools"
)
def tools_cmd_group():
    pass


@tools_cmd_group.command(name="match", help="Match mask objects")
@click.argument(
    "masks1", nargs=1, type=click.Path(exists=True, file_okay=False)
)
@click.argument(
    "masks2", nargs=1, type=click.Path(exists=True, file_okay=False)
)
@click.option(
    "--dest",
    "table_dir",
    type=click.Path(file_okay=False),
    required=True,
    help="Path to the object table output directory",
)
@check_steinbock_version
def match_cmd(masks1, masks2, table_dir):
    if Path(masks1).is_file() and Path(masks2).is_file():
        mask_files1 = [Path(masks1)]
        mask_files2 = [Path(masks2)]
    elif Path(masks1).is_dir() and Path(masks2).is_dir():
        mask_files1 = io.list_mask_files(masks1)
        mask_files2 = io.list_mask_files(masks2, base_files=mask_files1)
    Path(table_dir).mkdir(exist_ok=True)
    for mask_file1, mask_file2, df in matching.match_masks_from_disk(
        mask_files1, mask_files2
    ):
        table_file = Path(table_dir) / mask_file1.with_suffix(".csv").name
        df.columns = [Path(masks1).name, Path(masks2).name]
        df.to_csv(table_file, index=False)
        click.echo(table_file)
        del df


tools_cmd_group.add_command(mosaics_cmd_group)
