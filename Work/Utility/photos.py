from PIL import Image
from copy import deepcopy


imgae = Image.open('/home/pfano/DEV/NextFarm/Work/static/product_images/test.jpeg')


new_image = deepcopy(imgae)

new_image_size = (1200, 900)

new_image.resize(new_image_size, Image.ANTIALIAS)
# new_image = Image.new('RGBA', new_image_size, (255, 255, 255, 0))
new_image.save('new_image.png')





