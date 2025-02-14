import click

from pathlib import Path

from steinbock import io
from steinbock.measurement.regionprops import try_measure_regionprops_from_disk


@click.command(name="regionprops", help="Measure object region properties")
@click.option(
    "--img",
    "img_dir",
    type=click.Path(exists=True, file_okay=False),
    default="img",
    show_default=True,
    help="Path to the image directory",
)
@click.option(
    "--masks",
    "mask_dir",
    type=click.Path(exists=True, file_okay=False),
    default="masks",
    show_default=True,
    help="Path to the mask directory",
)
@click.argument("skimage_regionprops", nargs=-1, type=click.STRING)
@click.option(
    "-o",
    "regionprops_dir",
    type=click.Path(file_okay=False),
    default="regionprops",
    show_default=True,
    help="Path to the object region properties output directory",
)
def regionprops_cmd(img_dir, mask_dir, skimage_regionprops, regionprops_dir):
    img_files = io.list_image_files(img_dir)
    mask_files = io.list_mask_files(mask_dir, base_files=img_files)
    Path(regionprops_dir).mkdir(exist_ok=True)
    if not skimage_regionprops:
        skimage_regionprops = [
            "area",
            "centroid",
            "major_axis_length",
            "minor_axis_length",
            "eccentricity",
        ]
    for img_file, mask_file, regionprops in try_measure_regionprops_from_disk(
        img_files, mask_files, skimage_regionprops
    ):
        regionprops_file = io._as_path_with_suffix(
            Path(regionprops_dir) / img_file.name, ".csv"
        )
        io.write_data(regionprops, regionprops_file)
        click.echo(regionprops_file)
        del regionprops
