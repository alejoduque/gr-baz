#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#  
#  Copyright 2013 Balint Seeber <balint@crawfish>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sys
from gnuradio import gr, gru
from baz import message_relay

class multi_channel_decoder(gr.hier_block2):
	def __init__(self, msgq, baseband_freq, frequencies, decoder, decoder_args=None, params={}, **kwargs):
		gr.hier_block2.__init__(self, "multi_channel_decoder",
			gr.io_signature(1, 1, gr.sizeof_gr_complex),
			gr.io_signature(0, 0, 0))
		
		self.msgq = msgq
		self.decoder = decoder
		self.decoder_args = decoder_args or ""
		self.params = params
		self.kwargs = kwargs
		
		self.decoders = []
		self.decoders_unused = []
		
		self.set_baseband_freq(baseband_freq)
		
		self.set_frequencies(frequencies)
	
	def set_frequencies(self, freq_list):
		current_freqs = []
		map_freqs = {}
		for decoder in self.decoders:
			current_freqs += [decoder.get_freq()]
			map_freqs[decoder.get_freq()] = decoder
		create = [f for f in freq_list if f not in current_freqs]
		remove = [f for f in current_freqs if f not in freq_list]
		try:
			decoder_factory = self.decoder
			if isinstance(self.decoder, str):
				decoder_factory = eval(self.decoder)
			#factory_eval_str = "decoder_factory(baseband_freq=%s,freq=%f,%s)" % (self.baseband_freq, f, self.decoder_args)
			for f in create:
				#d = eval(factory_eval_str)
				d = decoder_factory(baseband_freq=self.baseband_freq, freq=f, **self.kwargs)
				d._msgq_relay = message_relay.message_relay(self.msgq, d.msg_out.msgq())
				self.connect(self, d)
				self.decoders += [d]
		except Exception, e:
			print "Failed to create decoder:", e#, factory_eval_str
		try:
			for f in remove:
				decoder = map_freqs[f]
				self.disconnect(self, decoder)
				#self.decoders_unused += [decoder]	# FIXME: Re-use mode
		except Exception, e:
			print "Failed to remove decoder:", e
	
	def set_baseband_freq(self, baseband_freq):
		self.baseband_freq = baseband_freq
		for decoder in self.decoders:
			decoder.set_baseband_freq(baseband_freq)
	
	def update_parameters(self, params):
		for k in params:
			if k not in self.params or self.params[k] != params[k]:
				print "Updating parameter:", k, params[k]
				for decoder in self.decoders:
					try:
						fn = getattr(decoder, k)
						fn(params[k])
					except Exception, e:
						print "Exception updating parameter in:", decoder, k, params[k]
						traceback.print_exc()
				self.params[k] = params[k]

def main():
	return 0

if __name__ == '__main__':
	main()
