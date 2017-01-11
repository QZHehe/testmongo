import os
import numpy as np
from skimage.io import imread, imsave
from skimage.color import rgb2lab, lab2rgb
from sklearn.metrics import euclidean_distances
import util
import urllib
# from colordescriptor import ColorDescriptor


class PaletteQuery(object):
    """
    Extract a L*a*b color array from a dict representation of a palette query.
    The array can then be used to histogram colors, output a palette image, etc.

    Parameters
    ----------
    palette_query : dict
        A mapping of hex colors to unnormalized values, representing proportion
        in the palette (e.g. {'#ffffff': 20, '#cc3300': 0.5}).
    """
    def __init__(self, palette_query):
        rgb_image = util.palette_query_to_rgb_image(palette_query)
        h, w, d = tuple(rgb_image.shape)
        self.lab_array = rgb2lab(rgb_image).reshape((h * w, d))


class Image(object):
    """
    Read the image at the URL in RGB format, downsample if needed,
    and convert to Lab colorspace.
    Store original dimensions, resize_factor, and the filename of the image.

    Image dimensions will be resized independently such that neither width nor
    height exceed the maximum allowed dimension MAX_DIMENSION.

    Parameters
    ----------
    url : string
        URL or file path of the image to load.
    id : string, optional
        Name or some other id of the image. For example, the Flickr ID.
    """

    MAX_DIMENSION = 240 + 1

    def __init__(self, url, _id=None):
        self.id = _id
        self.url = url
        img = imread(url)

        # Handle grayscale and RGBA images.
        # TODO: Should be smarter here in the future, but for now simply remove
        # the alpha channel if present.
        if img.ndim == 2:
            img = np.tile(img[:, :, np.newaxis], (1, 1, 3))
        elif img.ndim == 4:
            img = img[:, :, :3]
        
        # Downsample for speed.
        #
        # NOTE: I can't find a good method to resize properly in Python!
        # scipy.misc.imresize uses PIL, which needs 8bit data.
        # Anyway, this is faster and almost as good.
        #
        # >>> def d(dim, max_dim): return arange(0, dim, dim / max_dim + 1).shape
        # >>> plot(range(1200), [d(x, 200) for x in range(1200)])
        h, w, d = tuple(img.shape)
        self.orig_h, self.orig_w, self.orig_d = tuple(img.shape)
        h_stride = h / self.MAX_DIMENSION + 1
        w_stride = w / self.MAX_DIMENSION + 1
        img = img[::h_stride, ::w_stride, :]

        # Convert to L*a*b colors.
        h, w, d = img.shape
        self.h, self.w, self.d = img.shape
        self.lab_array = rgb2lab(img).reshape((h * w, d))

    def as_dict(self):
        """
        Return relevant info about self in a dict.
        """
        return {'id': self.id, 'url': self.url,
                'resized_width': self.w, 'resized_height': self.h,
                'width': self.orig_w, 'height': self.orig_h}

    def output_quantized_to_palette(self, palette, filename):
        """
        Save to filename a version of the image with all colors quantized
        to the nearest color in the given palette.

        Parameters
        ----------
        palette : rayleigh.Palette
            Containing K colors.
        filename : string
            Where image will be written.
        """
        dist = euclidean_distances(
            palette.lab_array, self.lab_array, squared=True).T
        min_ind = np.argmin(dist, axis=1)
        quantized_lab_array = palette.lab_array[min_ind, :]
        img = lab2rgb(quantized_lab_array.reshape((self.h, self.w, self.d)))
        imsave(filename, img)
        

class ImageUpload(object):
    """
    Read the upload image , downsample if needed,
    and convert to Lab colorspace.
    Store original dimensions, resize_factor, and the filename of the image.

    Image dimensions will be resized independently such that neither width nor
    height exceed the maximum allowed dimension MAX_DIMENSION.

    Parameters
    ----------
    file : image file to load 
    """

    MAX_DIMENSION = 240 + 1

    def __init__(self, file, filename=None, url = None):
        self.file = file
        self.id = filename
        self.url = url
        img = imread(file)
        self.img = img

        # Handle grayscale and RGBA images.
        # TODO: Should be smarter here in the future, but for now simply remove
        # the alpha channel if present.
        h, w, d=tuple(img.shape);
        if d == 2:
            img = np.tile(img[:, :, np.newaxis], (1, 1, 3))
        elif d == 4:
            img = img[:, :, :3]
        
        # Downsample for speed.
        #
        # NOTE: I can't find a good method to resize properly in Python!
        # scipy.misc.imresize uses PIL, which needs 8bit data.
        # Anyway, this is faster and almost as good.
        #
        # >>> def d(dim, max_dim): return arange(0, dim, dim / max_dim + 1).shape
        # >>> plot(range(1200), [d(x, 200) for x in range(1200)])
        h, w, d = tuple(img.shape)
        self.orig_h, self.orig_w, self.orig_d = tuple(img.shape)
        h_stride = h / self.MAX_DIMENSION + 1
        w_stride = w / self.MAX_DIMENSION + 1
        img = img[::h_stride, ::w_stride, :]

        # Convert to L*a*b colors.
        h, w, d = img.shape
        self.h, self.w, self.d = img.shape
        self.lab_array = rgb2lab(img).reshape((h * w, d))
        # Return image
        root = os.path.dirname(__file__)
        file_name = os.path.join(root, 'image/'+'show_image.png')
        tfname = file_name
        imsave(tfname,img)
        self.dui=open(tfname, 'rb').read().encode('base64').replace('\n', '')
        os.remove(tfname)

    def get_spatial_features(self):
        cd = ColorDescriptor((8, 3, 3))
        feature = cd.describe(self.img)
        return feature

    def get_texture(self):
        texture = util.calculate_hash(self.img)
        return texture
        
        
        
        

    def as_dict(self):
        """
        Return relevant info about self in a dict.
        """
        return {'id': self.id, 'url': self.url,
                'resized_width': self.w, 'resized_height': self.h,
                'width': self.orig_w, 'height': self.orig_h}

    def output_quantized_to_palette(self, palette, filename):
        """
        Save to filename a version of the image with all colors quantized
        to the nearest color in the given palette.

        Parameters
        ----------
        palette : rayleigh.Palette
            Containing K colors.
        filename : string
            Where image will be written.
        """
        dist = euclidean_distances(
            palette.lab_array, self.lab_array, squared=True).T
        min_ind = np.argmin(dist, axis=1)
        quantized_lab_array = palette.lab_array[min_ind, :]
        img = lab2rgb(quantized_lab_array.reshape((self.h, self.w, self.d)))
        imsave(filename, img)


class ImageModify(object):
    """
    Read the image to be modified

    Parameters
    ----------
    file : image file to load
    """

    def __init__(self, url, id):
        root = os.path.dirname(__file__)
        file_name = os.path.join(root, 'image/'+id)
        urllib.urlretrieve(url,file_name)
        dui = open(file_name, 'rb').read().encode('base64').replace('\n', '')
        self.dui="data:image/"+url[url.rfind('.')+1:]+";base64," + dui
        os.remove(file_name)


class ImageMongo(object):
    """
    Read the upload image , downsample if needed,
    and convert to Lab colorspace.
    Store original dimensions, resize_factor, and the filename of the image.

    Image dimensions will be resized independently such that neither width nor
    height exceed the maximum allowed dimension MAX_DIMENSION.

    Parameters
    ----------
    file : image file to load
    """

    MAX_DIMENSION = 240 + 1

    def __init__(self, file, url=None):
        self.file = file
        self.id = str(file.filename)
        self.url = url
        img = imread(file)
        self.img = img
        root = os.path.dirname(__file__)
        file_name = os.path.join(root, 'image/' + self.id)
        self.url = file_name
        tfname = file_name
        imsave(tfname, self.img)
        # Handle grayscale and RGBA images.
        # TODO: Should be smarter here in the future, but for now simply remove
        # the alpha channel if present.
        h, w, d = tuple(img.shape);
        if d == 2:
            img = np.tile(img[:, :, np.newaxis], (1, 1, 3))
        elif d == 4:
            img = img[:, :, :3]

        # Downsample for speed.
        #
        # NOTE: I can't find a good method to resize properly in Python!
        # scipy.misc.imresize uses PIL, which needs 8bit data.
        # Anyway, this is faster and almost as good.
        #
        # >>> def d(dim, max_dim): return arange(0, dim, dim / max_dim + 1).shape
        # >>> plot(range(1200), [d(x, 200) for x in range(1200)])
        h, w, d = tuple(img.shape)
        self.orig_h, self.orig_w, self.orig_d = tuple(img.shape)
        h_stride = h / self.MAX_DIMENSION + 1
        w_stride = w / self.MAX_DIMENSION + 1
        img = img[::h_stride, ::w_stride, :]

        # Convert to L*a*b colors.
        h, w, d = img.shape
        self.h, self.w, self.d = img.shape
        self.lab_array = rgb2lab(img).reshape((h * w, d))
        # Return image
        # root = os.path.dirname(__file__)
        # file_name = os.path.join(root, 'image/' + 'show_image.png')
        # tfname = file_name
        # imsave(tfname, img)
        # self.dui = open(tfname, 'rb').read().encode('base64').replace('\n', '')

    def get_spatial_features(self):
        cd = ColorDescriptor((8, 3, 3))
        feature = cd.describe(self.img)
        return feature

    def get_texture(self):
        texture = util.calculate_hash(self.img)
        return texture

    def as_dict(self):
        """
        Return relevant info about self in a dict.
        """
        return {'id': self.id, 'url': self.url,
                'resized_width': self.w, 'resized_height': self.h,
                'width': self.orig_w, 'height': self.orig_h}

    def output_quantized_to_palette(self, palette, filename):
        """
        Save to filename a version of the image with all colors quantized
        to the nearest color in the given palette.

        Parameters
        ----------
        palette : rayleigh.Palette
            Containing K colors.
        filename : string
            Where image will be written.
        """
        dist = euclidean_distances(
            palette.lab_array, self.lab_array, squared=True).T
        min_ind = np.argmin(dist, axis=1)
        quantized_lab_array = palette.lab_array[min_ind, :]
        img = lab2rgb(quantized_lab_array.reshape((self.h, self.w, self.d)))
        imsave(filename, img)