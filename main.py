import sys, io, argparse
from dataclasses import astuple

from constants import GAMELUMPS_ID
from bsp import BSP, Lump, LumpHeader, BSPReader, BSPWriter
from gamelump import GameLumpConverter
from brushside import BrushSideConverter
from worldlight import WorldLightConverter
from reader import Reader
from writer import Writer


def main(fname: str, should_extract_pakfile=False, new_pakfile=None):
    with open(fname, "rb") as handle:
        reader = Reader(handle)
        bsp = BSPReader(reader).read()

    bsp.version = 20

    if not bsp.header.lump_headers[8].length:
        new_header = bsp.header.lump_headers[53]
        new_header.offset = bsp.calc_new_offset(8)

        bsp.set_lump(8, bsp.lumps[53], new_header)

    brushside = bsp.lumps[19]
    brushside_header = bsp.header.lump_headers[19]
    brushside_ver, brushside_data = astuple(brushside)
    brushside_out = b""

    with io.BytesIO(brushside_data) as handle_in:
        with io.BytesIO() as handle_out:
            reader = Reader(handle_in)
            writer = Writer(handle_out)
            BrushSideConverter(reader, writer).convert()

            brushside_out = handle_out.getvalue()

    bsp.set_lump(19, Lump(brushside_ver, brushside_out), brushside_header)

    pakfile = bsp.lumps[40]
    pakfile_ver, original_pakfile_data = astuple(pakfile)
    new_pakfile_offset = bsp.calc_new_offset(40)

    if new_pakfile:
        with open(new_pakfile, "rb") as handle:
            pakfile_contents = handle.read()

        bsp.set_lump(
            40,
            Lump(pakfile_ver, pakfile_contents),
            LumpHeader(new_pakfile_offset, len(pakfile_contents), pakfile_ver, 0),
        )

    if should_extract_pakfile:
        with open(fname[:-4] + "_pakfile.zip", "wb") as handle:
            handle.write(original_pakfile_data)

        return

    gamelump_t = bsp.lumps[GAMELUMPS_ID]
    gamelump_offset = bsp.header.lump_headers[GAMELUMPS_ID].offset
    gamelump_ver, gamelump_data = astuple(gamelump_t)

    new_gamelump_offset = bsp.calc_new_offset(GAMELUMPS_ID)

    with io.BytesIO(gamelump_data) as handle_in:
        with io.BytesIO() as handle_out:
            reader = Reader(handle_in)
            writer = Writer(handle_out)
            GameLumpConverter(
                gamelump_offset, new_gamelump_offset, 6, reader, writer
            ).convert()

            gamelump_out = handle_out.getvalue()

    bsp.set_lump(
        GAMELUMPS_ID,
        Lump(gamelump_ver, gamelump_out),
        LumpHeader(new_gamelump_offset, len(gamelump_out), gamelump_ver, 0),
    )

    worldlight = bsp.lumps[54]
    worldlight_header = bsp.header.lump_headers[54]
    worldlight_ver, worldlight_data = astuple(worldlight)
    worldlight_out = b""
    with io.BytesIO(worldlight_data) as handle_in:
        with io.BytesIO() as handle_out:
            reader = Reader(handle_in)
            writer = Writer(handle_out)
            WorldLightConverter(reader, writer).convert()
            worldlight_out = handle_out.getvalue()

    bsp.set_lump(54, Lump(worldlight_ver, worldlight_out), worldlight_header)

    with open(fname[:-4] + "_d.bsp", "wb") as handle:
        writer = Writer(handle)
        BSPWriter(writer).write(bsp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Downport Portal 2 maps to Half-Life Source (ver.20 VBSP)",
        epilog="Only the first step in downporting maps. Downporting textures and models are separate.",
    )

    parser.add_argument("filename")
    parser.add_argument(
        "-e",
        "--extract_pakfile",
        help="Only extract the pakfile from the BSP. Useful for downporting textures, as cubemaps are stored in the BSP.",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--new_pakfile",
        help="Pakfile to be injected into BSP. Can be any zip file.",
    )

    args = parser.parse_args()
    fname: str = args.filename
    extract_pakfile: bool = args.extract_pakfile
    pakfile: str = args.new_pakfile

    main(fname, extract_pakfile, pakfile)
