# OpenZoo Fonts Builder - general logic

from enum import Enum
from PIL import Image
from .tables import MappingTable
import codecs
import numpy as np
import re
import unicodedata

class Glyph:
	def __init__(self, width, height, data=None):
		self.width = width
		self.height = height
		self.data = np.zeros((height, width), dtype=bool)
		if data is not None:
			if isinstance(data, np.ndarray):
				# Load as NumPy array
				if data.shape != (height, width): 
					raise Exception("Invalid glyph data type")
				self.data = data.astype(bool)
				return
			elif type(data) is list:
				data = "".join(data)
			# Load as string
			if type(data) is not str:
				raise Exception("Invalid glyph data type")
			data = re.sub('[\n\t]', '', data)
			if len(data) != (width * height):
				raise Exception("Invalid glyph data size: %d != %d" % (len(data), width * height))
			for i in range(len(data)):
				self.data[int(i / width)][i % width] = not data[i].isspace()

	def union(self, other: 'Glyph'):
		if (self.width != other.width) or (self.height != other.height):
			raise Exception(f"Incompatible sizes: {self.width}x{self.height} != {other.width}x{other.height}")
		return Glyph(self.width, self.height, np.logical_or(self.data, other.data))

	def resize(self, new_width, new_height):
		if (new_width == self.width) and (new_height == self.height):
			return self
		elif (new_width < self.width) or (new_height < self.height):
			raise Exception(f"Glyph could not be resized: {self.width}x{self.height} < {new_width}x{new_height}")
		else:
			pad_x_before = int((new_width - self.width) / 2)
			pad_y_before = int((new_height - self.height) / 2)
			pad_x_after = new_width - self.width - pad_x_before
			pad_y_after = new_height - self.height - pad_y_before
			new_data = np.pad(
				self.data,
				[
					(pad_y_before, pad_y_after),
					(pad_x_before, pad_x_after)
				]
			)
			return Glyph(new_width, new_height, new_data)

class GlyphSetWidthMode(Enum):
	FIXED_WIDTH = 1
	DOUBLE_FIXED_WIDTH = 2
	PROPORTIONAL = 3

class GlyphSet:
	def __init__(self, width, height, width_mode=GlyphSetWidthMode.FIXED_WIDTH):
		self.width = width
		self.height = height
		self.width_mode = width_mode
		self.glyphs = {}

	def __scale_glyph(self, glyph: Glyph):
		if (self.width_mode == GlyphSetWidthMode.PROPORTIONAL):
			return glyph.resize(glyph.width, self.height)
		elif (self.width_mode == GlyphSetWidthMode.DOUBLE_FIXED_WIDTH) and (glyph.width > self.width):
			return glyph.resize(self.width * 2, self.height)
		else:
			return glyph.resize(self.width, self.height)
	
	def __key_to_int(self, key):
		if type(key) is str:
			if len(key) > 1:
				key = unicodedata.lookup(key)
			key = ord(key[0])
		return key

	def create(self, key, func=lambda x: x, width=None, height=None, doublewide_if_available=False, overwrite=False):
		key = self.__key_to_int(key)
		if width is None:
			if doublewide_if_available and (self.width_mode == GlyphSetWidthMode.DOUBLE_FIXED_WIDTH):
				width = self.width * 2
			else:
				width = self.width
		if height is None:
			height = self.height
		glyph = self.__scale_glyph(Glyph(width, height))
		if (not overwrite) and (key in self.glyphs):
			return None
		else:
			self.put(key, glyph)
			func(glyph)
			return glyph

	def get(self, key):
		key = self.__key_to_int(key)
		return self.glyphs[key]

	def put(self, key: int, value: Glyph, overwrite=True):
		key = self.__key_to_int(key)
		if overwrite or (key not in self.glyphs):
			self.glyphs[key] = self.__scale_glyph(value)

	def include(self, gs: 'GlyphSet', overwrite=True):
		for gk in gs.glyphs.keys():
			self.put(gk, gs.glyphs[gk], overwrite=overwrite)
	
	def remap(self, m_table: MappingTable, copy_on_fallback=False):
		new_set = GlyphSet(self.width, self.height, width_mode=self.width_mode)
		for gk in self.glyphs.keys():
			ngk = m_table.get(gk)
			if (ngk is None) and copy_on_fallback:
				ngk = [gk]
			if ngk is not None:
				for nngk in ngk:
					new_set.put(nngk, self.glyphs[gk])
		return new_set


def glyphset_from_image(filename, glyph_width, glyph_height, is_doublewide=False, blank_color=None):
	with Image.open(filename) as im:
		im = im.convert("RGBA")
		if blank_color is None:
			blank_color = im.getpixel((0, 0))
		im_width, im_height = im.size
		glyph_set = GlyphSet(glyph_width, glyph_height,
			width_mode=(GlyphSetWidthMode.DOUBLE_FIXED_WIDTH if is_doublewide else GlyphSetWidthMode.FIXED_WIDTH))
		if ((im_width % glyph_width) != 0) or ((im_height % glyph_height) != 0):
			raise Exception(f"Invalid image size ({im_width}x{im_height}) relative to glyph size ({glyph_width}x{glyph_height})")
		glyphs_x = int(im_width / glyph_width)
		glyphs_y = int(im_height / glyph_height)
		for iy in range(glyphs_y):
			for ix in range(glyphs_x):
				i = iy * glyphs_x + ix
				data = np.ones((glyph_height, glyph_width), dtype=bool)
				for ipy in range(glyph_height):
					for ipx in range(glyph_width):
						p = im.getpixel((ix * glyph_width + ipx, iy * glyph_height + ipy))
						if (p[3] < 128) or (p[0:2] == blank_color[0:2]):
							data[ipy][ipx] = False
				if data.any():
					if is_doublewide and (not data[0:glyph_height, int(glyph_width / 2):glyph_width].any()):
						data = data[0:glyph_height, 0:int(glyph_width / 2)]
					glyph_set.put(i, Glyph(glyph_width, glyph_height, data))
		return glyph_set

def glyphset_to_image(gs: GlyphSet, filename):
	glyph_width = gs.width
	glyph_height = gs.height
	if gs.width_mode == GlyphSetWidthMode.DOUBLE_FIXED_WIDTH:
		glyph_width *= 2
	glyph_width_multiplier = 256
	glyph_height_multiplier = int((max(gs.glyphs.keys()) + 255) / 256)
	im = Image.new("L", (glyph_width * glyph_width_multiplier, glyph_height * glyph_height_multiplier), color=255)
	for gk in gs.glyphs.keys():
		gx = int(gk % glyph_width_multiplier) * glyph_width
		gy = int(gk / glyph_width_multiplier) * glyph_height
		glyph = gs.glyphs[gk]
		for iy in range(glyph_height):
			for ix in range(glyph_width):
				if glyph.data[iy][ix]:
					im.putpixel((gx+ix, gy+iy), 0)
	im.save(filename)