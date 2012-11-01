#!/usr/bin/env python

import cStringIO
import Image
import ImageDraw
import ImageFont
import ImageColor

fontPath = '/Library/Fonts/Arial.ttf'

def makeImg(width=512, height=512, color='#ccc', text='placeholder',
            format='png'):
    '''Make a placeholder image.
    Args:
        width: The width of image in pixels.
        height: The height of image in pixels.
        color: Background color. See *The ImageColor Module* section in *Python
            Image Library Handbook*.
        text: Text in the middle of the image.
        format: See *Image File Formats* section in *Python Image Library
            Handbook*.
    Returns:
        Binary data of generated image.
    '''
    img = Image.new('RGBA', (width, height), color)
    draw = ImageDraw.Draw(img)
    fontSize = 32
    #Find the appropriate font size.
    while len(text):
        try:
            font = ImageFont.truetype(fontPath, fontSize)
        except IOError:
            raise IOError(
                'Can\'t load font file. Please set `fontPath` correctly.')
        textWidth, textHeight = draw.textsize(text, font=font)
        if textWidth > width or textHeight > height:
            fontSize /= 2
        else:
            break
    textLeft = (width - textWidth) / 2
    textTop = (height - textHeight) / 2
    if sum(ImageColor.getrgb(color)) < 255 * 3 / 2:
        textColor = 'White'
    else:
        textColor = 'Black'
    draw.text((textLeft, textTop), text, font=font, fill=textColor)
    #PIL Image -> Binary data
    fim = cStringIO.StringIO()
    img.save(fim, format)
    binData = fim.getvalue()
    fim.close()
    return binData

if __name__ == '__main__':
    from tornado.web import Application, RequestHandler
    from tornado.ioloop import IOLoop
    import re
    import argparse
    class IndexHandler(RequestHandler):
        def get(self):
            sizeArg = self.get_argument('size', '512x512')
            sizeMatch = re.match(r'(\d+)[xX](\d+)', sizeArg)
            width = int(sizeMatch.group(1))
            height = int(sizeMatch.group(2))
            color = self.get_argument('color', 'gray')
            try:
                int(color, 16)
                color = '#' + color
            except ValueError:
                pass
            text = self.get_argument('text', '%s * %s' % (width, height))
            img = makeImg(width, height, color, text, 'PNG')
            self.set_header('content-type', 'image/png')
            self.set_header('content-length', len(img))
            self.write(img)

    appSettings = {
        'debug': True,
    }
    application = Application([
        ('/', IndexHandler),
    ], **appSettings)
     
    parser = argparse.ArgumentParser(
        description='A simple server for generate placeholder image.\
        You can request a image like this:\
        http://localhost:port?size=300x100&color=cff&text=Hello')
    parser.add_argument('-p', '--port',
                        type=int, default=8080,
                        help='Port. Default is 8080')
    parser.add_argument('-f', '--font', dest='fontPath',
                        default='/Library/Fonts/Arial.ttf',
                        metavar="'Font file path.'",
                        help='Maybe you need to set the font file path.\
                        Default is \'/Library/Fonts/Arial.ttf\'')
    args = parser.parse_args()
    fontPath = args.fontPath
    application.listen(args.port)
    IOLoop.instance().start()
