# Compile to C extension for zero-overhead unit conversions
cdef class MetersC:
    cdef public double value
    
    def __init__(self, double value):
        self.value = value
    
    cpdef PixelsC in_pixels(self):
        return PixelsC(<int>(self.value * PIXELS_PER_METER))
