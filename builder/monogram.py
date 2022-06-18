# OpenZoo Fonts Builder - Monogram JSON importer

from .builder import *
import json

def glyphset_from_monogram_json(filename, glyph_width, glyph_height, glyph_mode=GlyphSetWidthMode.PROPORTIONAL, min_glyph_width=1):
	with open(filename, "r") as fp:
		fnt = json.load(fp)
		glyph_set = GlyphSet(glyph_width, glyph_height, glyph_mode)
		for k in fnt.keys():
			i = ord(k[0])
			d = fnt[k]
			local_width = glyph_width
			if glyph_mode == GlyphSetWidthMode.PROPORTIONAL:
				local_width = max(min_glyph_width, max(map(lambda x: x.bit_length() + 1, d)))
			data = np.ones((glyph_height, local_width), dtype=bool)
			for ipy in range(glyph_height):
				for ipx in range(local_width):
					data[ipy][ipx] = (((d[ipy]) >> ipx) & 1) != 0
			glyph_set.put(i, Glyph(local_width, glyph_height, data))
		return glyph_set
