#!/usr/bin/python
"""
Takes a path to a folder for input and one for output.

For help do:
>>> ./imgcrop.py --help
"""

import glob
import itertools
import optparse
import os
import PIL.Image


def get_optionparser():
    usage = 'usage: %prog [options] file1 ... fileN'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-s', '--shape', default='10x10',
                      help='Shape of cropped files, NxN')
    parser.add_option('-o', '--output', default='.')
    parser.add_option('-v', '--verbose', action='store_true', default=False,
                      help='Enable verbose output')
    return parser

def crop(image, new_shape):
    """
    Returns a cropped version of image with shape
    specified.

    Will resize and crop the image such that the minimum part of the image is
    removed and the cropped image contains the middle of the original one.
    """
    shape = image.size
    ratio = float(shape[0]) / shape[1]
    new_ratio = float(new_shape[0]) / new_shape[1]
    dim_compare = int(ratio > new_ratio)  # which dimenstion to compare
    scale_factor = float(new_shape[dim_compare]) / shape[dim_compare]
    # resize for crop with retained proportions and minimum area discarded
    image = image.resize(tuple(int(scale_factor*x) for x in shape))
    # crop middle
    horizontal_padding = int((image.size[0] - new_shape[0]) / 2)
    vertical_padding = int((image.size[1] - new_shape[1]) / 2)
    crop_box = (horizontal_padding,
                vertical_padding,
                horizontal_padding + new_shape[0],
                vertical_padding + new_shape[1])
    cropped_image = image.crop(crop_box)
    # crop is a lazy operation, load
    cropped_image.load()
    return cropped_image

def cropper(input_paths, output, shape, verbose=False):
    """
    Crops files listed in input_paths and saves them in output.
    """
    # Ensure the output folder exists
    if not os.path.isdir(output):
        os.makedirs(output)
    elif os.path.exists(output) and not os.path.isdir(output):
        print('Error: %s is not a folder, exiting' % output)
        return
    if verbose:
        count = 0
    for path in input_paths:
        try:
            image = PIL.Image.open(path)
        except IOError as e:
            print(str(e))
            print('Error: Could not open file %s, skipping' % path)
        else:
            target = os.path.join(output, os.path.basename(path))
            if os.path.exists(target):
                print('Error: Already exists a file in %s, skipping' % target)
            else:
                image = crop(image, shape)
                image.save(target)
                if verbose:
                    count += 1
                    print('Cropped %s and stored in %s' % (path, target))
    if verbose:
        print('Saved %s files in %s' % (count, output))

def main():
    parser = get_optionparser()
    options, filenames = parser.parse_args()
    if len(filenames) < 1:
        print('No input files supplied')
        return
    shape = map(int, options.shape.split('x'))
    paths = itertools.chain(*itertools.imap(glob.glob, filenames))
    cropper(paths, options.output, shape, verbose=options.verbose)

if __name__ == '__main__':
    main()
