import os

def create_large_bmp(filename, size_mb):
    # Calculate dimensions for a 24-bit BMP (roughly size_mb)
    # 1 pixel = 3 bytes
    target_bytes = size_mb * 1024 * 1024
    pixels = target_bytes // 3
    side = int(pixels**0.5)
    
    # Simple BMP Header for a 24-bit image
    # Note: This is a very basic implementation to create a valid-ish file structure
    width = side
    height = side
    row_size = (width * 3 + 3) & ~3
    image_size = row_size * height
    file_size = 54 + image_size
    
    header = bytearray([
        0x42, 0x4D,              # Magic number 'BM'
        *file_size.to_bytes(4, 'little'),
        0, 0, 0, 0,              # Reserved
        54, 0, 0, 0,             # Offset to pixel data
        40, 0, 0, 0,             # Header size
        *width.to_bytes(4, 'little'),
        *height.to_bytes(4, 'little'),
        1, 0,                    # Planes
        24, 0,                   # Bits per pixel
        0, 0, 0, 0,              # Compression (BI_RGB)
        *image_size.to_bytes(4, 'little'),
        0, 0, 0, 0,              # X pixels per meter
        0, 0, 0, 0,              # Y pixels per meter
        0, 0, 0, 0,              # Colors in palette
        0, 0, 0, 0               # Important colors
    ])
    
    with open(filename, 'wb') as f:
        f.write(header)
        # Write dummy pixel data (blue color)
        pixel_row = bytearray([255, 0, 0] * width + [0] * (row_size - width * 3))
        for _ in range(height):
            f.write(pixel_row)

if __name__ == "__main__":
    output_path = "test_data/test_image_25mb.bmp"
    create_large_bmp(output_path, 25)
    print(f"File created: {output_path}")
    print(f"Size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
