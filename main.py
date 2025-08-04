import sys, io
from dataclasses import astuple

from constants import GAMELUMPS_ID
from bsp import BSP, Lump, LumpHeader, BSPReader, BSPWriter
from gamelump import GameLumpConverter
from brushside import BrushSideConverter
from worldlight import WorldLightConverter
from reader import Reader
from writer import Writer


def main():
    if len(sys.argv) < 2:
        print("expected usage of tool:")
        print("main [fname].bsp")

        exit(1)

    fname = sys.argv[1]
    with open(fname, "rb") as handle:
        reader = Reader(handle)
        bsp = BSPReader(reader).read()

    bsp.version = 20

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
    if not bsp.header.lump_headers[8].length:
        new_header = bsp.header.lump_headers[53]
        new_header.offset = bsp.calc_new_offset(8)

        bsp.set_lump(8, bsp.lumps[53], new_header)

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
    main()
