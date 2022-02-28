from builder.builder import *

def generate_block_elements(gs: GlyphSet):
	def generate_quadrant(glyph, q1, q2, q3, q4):
		if q1:
			glyph.data[0:int(glyph.height / 2), 0:int(glyph.width / 2)].fill(True)
		if q2:
			glyph.data[0:int(glyph.height / 2), int(glyph.width / 2):glyph.width].fill(True)
		if q3:
			glyph.data[int(glyph.height / 2):glyph.height, 0:int(glyph.width / 2)].fill(True)
		if q4:
			glyph.data[int(glyph.height / 2):glyph.height, int(glyph.width / 2):glyph.width].fill(True)

	gs.create(0x2580, lambda glyph: glyph.data[0:int(glyph.height / 2), 0:glyph.width].fill(True))
	for i in range(8):
		gs.create(0x2581 + i, lambda glyph: glyph.data[min(glyph.height - 1, int(glyph.height * (7 - i) / 8)):glyph.height, 0:glyph.width].fill(True))
	for i in range(7):
		gs.create(0x2589 + i, lambda glyph: glyph.data[0:glyph.height, 0:max(1, int(glyph.width * (7 - i) / 8))].fill(True))
	gs.create(0x2590, lambda glyph: glyph.data[0:glyph.height, int(glyph.width / 2):glyph.width].fill(True))
	gs.create(0x2594, lambda glyph: glyph.data[0:max(1, int(glyph.height / 8)), 0:glyph.width].fill(True))
	gs.create(0x2595, lambda glyph: glyph.data[0:glyph.height, min(glyph.width - 1, int(glyph.width * 7 / 8)):glyph.width].fill(True))
	gs.create(0x2596, lambda glyph: generate_quadrant(glyph, False, False, True, False))
	gs.create(0x2597, lambda glyph: generate_quadrant(glyph, False, False, False, True))
	gs.create(0x2598, lambda glyph: generate_quadrant(glyph, True, False, False, False))
	gs.create(0x2599, lambda glyph: generate_quadrant(glyph, True, False, True, True))
	gs.create(0x259A, lambda glyph: generate_quadrant(glyph, True, False, False, True))
	gs.create(0x259B, lambda glyph: generate_quadrant(glyph, True, True, True, False))
	gs.create(0x259C, lambda glyph: generate_quadrant(glyph, True, True, False, True))
	gs.create(0x259D, lambda glyph: generate_quadrant(glyph, False, True, False, False))
	gs.create(0x259E, lambda glyph: generate_quadrant(glyph, False, True, True, False))
	gs.create(0x259F, lambda glyph: generate_quadrant(glyph, False, True, True, True))
	print(gs.get(0x2596).data)
