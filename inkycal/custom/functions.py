#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Inkycal custom functions
Use these in all modules by using:
from inykcal.custom import *
or
from inkycal.custom import write, textwrap, draw_border

Contains write function for more controlled writing on the image
Contains text_wrap function for splitting a long string to smaller chunks
Contains draw_border function for drawing a border around a specified area

Copyright by aceisace
"""
import logging
from PIL import Image, ImageDraw, ImageFont
from inkycal.config import config

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

def write(image, xy, box_size, text, font=None, **kwargs):
  """Writes text on a image.

  Writes given text at given position on the specified image.

  Args:
    - image: The image to draw this text on, usually im_black or im_colour.
    - xy: tuple-> (x,y) representing the x and y co-ordinate.
    - box_size: tuple -> (width, height) representing the size of the text box.
    - text: string, the actual text to add on the image.
    - font: A PIL Font object e.g.
      ImageFont.truetype(fonts['fontname'], size = 10).

  Args: (optional)
    - alignment: alignment of the text, use 'center', 'left', 'right'.
    - autofit: bool (True/False). Automatically increases fontsize to fill in
      as much of the box-height as possible.
    - colour: black by default, do not change as it causes issues with rendering
      on e-Paper.
    - rotation: Rotate the text with the text-box by a given angle anti-clockwise.
    - fill_width: Decimal representing a percentage e.g. 0.9 # 90%. Fill a
      maximum of 90% of the size of the full width of text-box.
    - fill_height: Decimal representing a percentage e.g. 0.9 # 90%. Fill a
      maximum of 90% of the size of the full height of the text-box.
  """
  allowed_kwargs = ['alignment', 'autofit', 'colour', 'rotation',
                    'fill_width', 'fill_height']

  # Validate kwargs
  for key, value in kwargs.items():
    if key not in allowed_kwargs:
      print(f'{key} does not exist')

  # Set kwargs if given, it not, use defaults
  alignment = kwargs['alignment'] if 'alignment' in kwargs else 'center'
  autofit = kwargs['autofit'] if 'autofit' in kwargs else False
  fill_width = kwargs['fill_width'] if 'fill_width' in kwargs else 1.0
  fill_height = kwargs['fill_height'] if 'fill_height' in kwargs else 0.8
  colour = kwargs['colour'] if 'colour' in kwargs else 'black'
  rotation = kwargs['rotation'] if 'rotation' in kwargs else None

  x,y = xy
  box_width, box_height = box_size

  # Increase fontsize to fit specified height and width of text box
  if (autofit == True) or (fill_width != 1.0) or (fill_height != 0.8):
    size = 8
    font = ImageFont.truetype(font.path, size)
    text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
    while (text_width < int(box_width * fill_width) and
           text_height < int(box_height * fill_height)):
      size += 1
      font = ImageFont.truetype(font.path, size)
      text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]

  text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]


  # Truncate text if text is too long so it can fit inside the box
  if (text_width, text_height) > (box_width, box_height):
    logger.debug(f'truncating {text}')
    while (text_width, text_height) > (box_width, box_height):
      text=text[0:-1]
      text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
    logger.debug((text))

  # Align text to desired position
  if alignment == "center" or None:
    x = int((box_width / 2) - (text_width / 2))
  elif alignment == 'left':
    x = 0
  elif alignment == 'right':
    x = int(box_width - text_width)

  y = int((box_height / 2) - (text_height / 2))

  # Draw the text in the text-box
  draw  = ImageDraw.Draw(image)
  space = Image.new('RGBA', (box_width, box_height))
  draw2 = ImageDraw.Draw(space)
  draw2.fontmode = "1"
  draw2.text((x, y), text, fill=colour, font=font)
  # Uncomment following two lines, comment out above two lines to show
  # red text-box with white text (debugging purposes)

  #space = Image.new('RGBA', (box_width, box_height), color= 'red')
  #ImageDraw.Draw(space).text((x, y), text, fill='white', font=font)

  if rotation != None:
    space.rotate(rotation, expand = True)

  # Update only region with text (add text with transparent background)
  image.paste(space, xy, space)


def text_wrap(text, font=None, max_width = None):
  """Splits a very long text into smaller parts

  Splits a long text to smaller lines which can fit in a line with max_width.
  Uses a Font object for more accurate calculations.

  Args:
    - font: A PIL font object which is used to calculate the size.
    - max_width: int-> a width in pixels defining the maximum width before
      splitting the text into the next chunk.

  Returns:
    A list containing chunked strings of the full text.
  """
  lines = []
  if font.getsize(text)[0] < max_width:
    lines.append(text)
  else:
    words = text.split(' ')
    i = 0
    while i < len(words):
      line = ''
      while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
        line = line + words[i] + " "
        i += 1
      if not line:
        line = words[i]
        i += 1
      lines.append(line)
  return lines

def draw_border(image, xy, size, radius=5, thickness=1, shrinkage=(0.1,0.1)):
  """Draws a border at given coordinates.

  Args:
    - image: The image on which the border should be drawn (usually im_black or
      im_colour.

    - xy: Tuple representing the top-left corner of the border e.g. (32, 100)
      where 32 is the x co-ordinate and 100 is the y-coordinate.

    - size: Size of the border as a tuple -> (width, height).

    - radius: Radius of the corners, where 0 = plain rectangle, 5 = round corners.

    - thickness: Thickness of the border in pixels.

    - shrinkage: A tuple containing decimals presenting a percentage of shrinking
      -> (width_shrink_percentage, height_shrink_percentage).
      e.g. (0.1, 0.2) ~ shrinks the width of border by 10%, shrinks height of
      border by 20%
  """

  colour='black'

  # size from function paramter
  width, height = int(size[0]*(1-shrinkage[0])), int(size[1]*(1-shrinkage[1]))

  # shift cursor to move rectangle to center
  offset_x, offset_y = int((size[0] - width)/2), int((size[1]- height)/2)

  x, y, diameter = xy[0]+offset_x, xy[1]+offset_y, radius*2
  # lenght of rectangle size
  a,b = (width - diameter), (height-diameter)

  # Set coordinates for staright lines
  p1, p2 = (x+radius, y), (x+radius+a, y)
  p3, p4 = (x+width, y+radius), (x+width, y+radius+b)
  p5, p6 = (p2[0], y+height), (p1[0], y+height)
  p7, p8  = (x, p4[1]), (x,p3[1])
  if radius != 0:
    # Set coordinates for arcs
    c1, c2 = (x,y), (x+diameter, y+diameter)
    c3, c4 = ((x+width)-diameter, y), (x+width, y+diameter)
    c5, c6 = ((x+width)-diameter, (y+height)-diameter), (x+width, y+height)
    c7, c8 = (x, (y+height)-diameter), (x+diameter, y+height)

  # Draw lines and arcs, creating a square with round corners
  draw = ImageDraw.Draw(image)
  draw.line( (p1, p2) , fill=colour, width = thickness)
  draw.line( (p3, p4) , fill=colour, width = thickness)
  draw.line( (p5, p6) , fill=colour, width = thickness)
  draw.line( (p7, p8) , fill=colour, width = thickness)

  if radius != 0:
    draw.arc(  (c1, c2) , 180, 270, fill=colour, width=thickness)
    draw.arc(  (c3, c4) , 270, 360, fill=colour, width=thickness)
    draw.arc(  (c5, c6) , 0, 90, fill=colour, width=thickness)
    draw.arc(  (c7, c8) , 90, 180, fill=colour, width=thickness)
