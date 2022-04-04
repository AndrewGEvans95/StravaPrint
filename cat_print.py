import argparse
import asyncio
import logging
import sys
import os

from catprinter.cmds import PRINT_WIDTH, cmds_print_img
from catprinter.ble import run_ble
from catprinter.img import read_img

import strava_auth
import gen_strava_map

def parse_args():
    args = argparse.ArgumentParser(
        description='prints an image on your cat thermal printer')

    args.add_argument('--log-level', type=str,
                      choices=['debug', 'info', 'warn', 'error'], default='info')
    args.add_argument('--img-binarization-algo', type=str,
                      choices=['mean-threshold',
                               'floyd-steinberg', 'halftone'],
                      default='floyd-steinberg',
                      help='Which image binarization algorithm to use.')
    args.add_argument('--show-preview', action='store_true',
                      help='If set, displays the final image and asks the user for \
                          confirmation before printing.')
    args.add_argument('--devicename', type=str, default='',
                      help='Specify the Bluetooth Low Energy (BLE) device name to    \
                          search for. If not specified, the script will try to       \
                          auto discover the printer based on its advertised BLE      \
                          service UUIDs. Common names are similar to "GT01", "GB02", \
                          "GB03".')
    args.add_argument('--darker', action='store_true',
                      help="Print the image in text mode. This leads to more contrast, \
                          but slower speed.")
    return args.parse_args()


def make_logger(log_level):
    logger = logging.getLogger('catprinter')
    logger.setLevel(log_level)
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(log_level)
    logger.addHandler(h)
    return logger


def main():
    args = parse_args()

    log_level = getattr(logging, args.log_level.upper())
    logger = make_logger(log_level)

    # Retrieve access token from strava api
    logger.info('⏳ Retrieving access token from Strava...')
    access_token = strava_auth.get_access_token_from_file()
    if access_token is None:
        logger.info('Failed to retrieve access token from file.')
    else:
        logger.info('✅ Access token retrieved.')
    # Create strava map image
    logger.info('⏳ Generating strava map image...')
    img_strava_map = gen_strava_map.create_map_image(access_token, 1)
    logger.info('✅ Done.')

    filename = 'map.png'
    args.filename = filename
    if not os.path.exists(filename):
        logger.info('🛑 File not found. Exiting.')
        return

    bin_img = read_img('map.png', PRINT_WIDTH,
                       logger, args.img_binarization_algo, args.show_preview)
    if bin_img is None:
        logger.info(f'🛑 No image generated. Exiting.')
        return

    logger.info(f'✅ Read image: {bin_img.shape} (h, w) pixels')
    data = cmds_print_img(bin_img, dark_mode=args.darker)
    logger.info(f'✅ Generated BLE commands: {len(data)} bytes')

    # Try to autodiscover a printer if --devicename is not specified.
    autodiscover = not args.devicename
    asyncio.run(run_ble(data, args.devicename, autodiscover, logger))


if __name__ == '__main__':
    main()
