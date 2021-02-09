#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Slideshow module for Inkycal Project
Copyright by aceisace
"""
import logging
from os import listdir

from inkycal.config import config as inkycal_config
from inkycal.modules.template import inkycal_module

# from inkycal.custom import *

# PIL has a class named Image, use alias for Inkyimage -> Images
from inkycal.modules.inky_image import Inkyimage as Images

logger = logging.getLogger(__name__)

class Slideshow(inkycal_module):
  """Cycles through images in the image folder.
  
  As this module relies on external content, the path it uses is
  looked up from the config file.
  """
  name = "Slideshow - Cycle through images in the image folder"

  requires = {
    "palette": {
      "label":"Which palette should be used for converting images?",
      "options": ["bw", "bwr", "bwy"]
      }
    }

  optional = {
    
    "autoflip":{
        "label":"Should the image be flipped automatically? Default is False",
        "options": [False, True]
        },

    "orientation":{
      "label": "Please select the desired orientation",
      "options": ["vertical", "horizontal"]
      }
    }

  def __init__(self, config):
    """Initialize module"""

    super().__init__(config)

    config = config['config']

    # required parameters
    for param in self.requires:
      if not param in config:
        raise Exception(f'config is missing {param}')

    # optional parameters
    self.palette = config['palette']
    self.autoflip = config['autoflip']
    self.orientation = config['orientation']

    # Get the full path of all png/jpg/jpeg images in the given folder
    self.images = [f'{inkycal_config["IMAGE_DIR"]}{im}' for im in listdir(inkycal_config["IMAGE_DIR"])]

    if not self.images:
      logger.error('No images found in the given folder, please '
                   'double check your path!')
      raise FileNotFoundError('No images found in the given folder path :/')

    # set a 'first run' signal
    self._first_run = True

    # give an OK message
    print(f'{__name__} loaded')

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height

    logger.info(f'Image size: {im_size}')

    # rotates list items by 1 index
    def rotate(somelist):
      return somelist[1:] + somelist[:1]

    # Switch to the next image if this is not the first run
    if self._first_run == True:
      self._first_run = False
    else:
      self.images = rotate(self.images)

    # initialize custom image class
    im = Images()

    # temporary print method, prints current filename
    print(f'slideshow - current image name: {self.images[0].split("/")[-1]}')

    # use the image at the first index
    im.load(self.images[0])

    # Remove background if present
    im.remove_alpha()

    # if autoflip was enabled, flip the image
    if self.autoflip == True:
      im.autoflip(self.orientation)

    # resize the image so it can fit on the epaper
    im.resize( width=im_width, height=im_height )

    # convert images according to specified palette
    im_black, im_colour = im.to_palette(self.palette)

    # with the images now send, clear the current image
    im.clear()

    # return images
    return im_black, im_colour

if __name__ == '__main__':
  print('running module in standalone mode')
