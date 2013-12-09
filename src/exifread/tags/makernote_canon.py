"""
Makernote (proprietary) tag definitions for Canon.

http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/Canon.html
"""

TAGS = {
    0x0006: ('ImageType', ),
    0x0007: ('FirmwareVersion', ),
    0x0008: ('ImageNumber', ),
    0x0009: ('OwnerName', ),
    0x000C: ('SerialNumber', ),
    0x000E: ('FileLength', ),
    0x0015: ('SerialNumberFormat', {
        0x90000000: 'Format 1',
        0xA0000000: 'Format 2'
    }),
    0x001A: ('SuperMacro', {
        0: 'Off',
        1: 'On (1)',
        2: 'On (2)'
    }),
    0x001C: ('DateStampMode', {
        0: 'Off',
        1: 'Date',
        2: 'Date & Time',
    }),
    0x001E: ('FirmwareRevision', ),
    0x0028: ('ImageUniqueID', ),
    0x0095: ('LensModel', ),
    0x0096: ('InternalSerialNumber ', ),
    0x0097: ('DustRemovalData ', ),
    0x0098: ('CropInfo ', ),
    0x009A: ('AspectInfo', ),
    0x00b4: ('ColorSpace', {
        1: 'sRGB',
        2: 'Adobe RGB'
    }),
}

# this is in element offset, name, optional value dictionary format
# 0x0001
CAMERA_SETTINGS = {
    1: ('Macromode', {
        1: 'Macro',
        2: 'Normal'
    }),
    2: ('SelfTimer', ),
    3: ('Quality', {
        1: 'Economy',
        2: 'Normal',
        3: 'Fine',
        5: 'Superfine'
    }),
    4: ('FlashMode', {
        0: 'Flash Not Fired',
        1: 'Auto',
        2: 'On',
        3: 'Red-Eye Reduction',
        4: 'Slow Synchro',
        5: 'Auto + Red-Eye Reduction',
        6: 'On + Red-Eye Reduction',
        16: 'external flash'
    }),
    5: ('ContinuousDriveMode', {
        0: 'Single Or Timer',
        1: 'Continuous',
        2: 'Movie',
    }),
    7: ('FocusMode', {
        0: 'One-Shot',
        1: 'AI Servo',
        2: 'AI Focus',
        3: 'MF',
        4: 'Single',
        5: 'Continuous',
        6: 'MF'
    }),
    9: ('RecordMode', {
        1: 'JPEG',
        2: 'CRW+THM',
        3: 'AVI+THM',
        4: 'TIF',
        5: 'TIF+JPEG',
        6: 'CR2',
        7: 'CR2+JPEG',
        9: 'Video'
    }),
    10: ('ImageSize', {
        0: 'Large',
        1: 'Medium',
        2: 'Small'
    }),
    11: ('EasyShootingMode', {
        0: 'Full Auto',
        1: 'Manual',
        2: 'Landscape',
        3: 'Fast Shutter',
        4: 'Slow Shutter',
        5: 'Night',
        6: 'B&W',
        7: 'Sepia',
        8: 'Portrait',
        9: 'Sports',
        10: 'Macro/Close-Up',
        11: 'Pan Focus'
    }),
    12: ('DigitalZoom', {
        0: 'None',
        1: '2x',
        2: '4x',
        3: 'Other'
    }),
    13: ('Contrast', {
        0xFFFF: 'Low',
        0: 'Normal',
        1: 'High'
    }),
    14: ('Saturation', {
        0xFFFF: 'Low',
        0: 'Normal',
        1: 'High'
    }),
    15: ('Sharpness', {
        0xFFFF: 'Low',
        0: 'Normal',
        1: 'High'
    }),
    16: ('ISO', {
        0: 'See ISOSpeedRatings Tag',
        15: 'Auto',
        16: '50',
        17: '100',
        18: '200',
        19: '400'
    }),
    17: ('MeteringMode', {
        0: 'Default',
        1: 'Spot',
        2: 'Average',
        3: 'Evaluative',
        4: 'Partial',
        5: 'Center-weighted'
    }),
    18: ('FocusType', {
        0: 'Manual',
        1: 'Auto',
        3: 'Close-Up (Macro)',
        8: 'Locked (Pan Mode)'
    }),
    19: ('AFPointSelected', {
        0x3000: 'None (MF)',
        0x3001: 'Auto-Selected',
        0x3002: 'Right',
        0x3003: 'Center',
        0x3004: 'Left'
    }),
    20: ('ExposureMode', {
        0: 'Easy Shooting',
        1: 'Program',
        2: 'Tv-priority',
        3: 'Av-priority',
        4: 'Manual',
        5: 'A-DEP'
    }),
    22: ('LensType', ),
    23: ('LongFocalLengthOfLensInFocalUnits', ),
    24: ('ShortFocalLengthOfLensInFocalUnits', ),
    25: ('FocalUnitsPerMM', ),
    28: ('FlashActivity', {
        0: 'Did Not Fire',
        1: 'Fired'
    }),
    29: ('FlashDetails', {
        0: 'Manual',
        1: 'TTL',
        2: 'A-TTL',
        3: 'E-TTL',
        4: 'FP Sync Enabled',
        7: '2nd("Rear")-Curtain Sync Used',
        11: 'FP Sync Used',
        13: 'Internal Flash',
        14: 'External E-TTL'
    }),
    32: ('FocusMode', {
        0: 'Single',
        1: 'Continuous',
        8: 'Manual'
    }),
    33: ('AESetting', {
        0: 'Normal AE',
        1: 'Exposure Compensation',
        2: 'AE Lock',
        3: 'AE Lock + Exposure Comp.',
        4: 'No AE'
    }),
    34: ('ImageStabilization', {
        0: 'Off',
        1: 'On',
        2: 'Shoot Only',
        3: 'Panning',
        4: 'Dynamic',
        256: 'Off',
        257: 'On',
        258: 'Shoot Only',
        259: 'Panning',
        260: 'Dynamic'
    }),
    39: ('SpotMeteringMode', {
        0: 'Center',
        1: 'AF Point'
    }),
    41: ('ManualFlashOutput', {
        0x0: 'n/a',
        0x500: 'Full',
        0x502: 'Medium',
        0x504: 'Low',
        0x7FFF: 'n/a'
    }),
}

# 0x0002
FOCAL_LENGTH = {
    1: ('FocalType', {
        1: 'Fixed',
        2: 'Zoom',
    }),
    2: ('FocalLength', ),
}

# 0x0004
SHOT_INFO = {
    7: ('WhiteBalance', {
        0: 'Auto',
        1: 'Sunny',
        2: 'Cloudy',
        3: 'Tungsten',
        4: 'Fluorescent',
        5: 'Flash',
        6: 'Custom'
    }),
    8: ('SlowShutter', {
        -1: 'n/a',
        0: 'Off',
        1: 'Night Scene',
        2: 'On',
        3: 'None'
    }),
    9: ('SequenceNumber', ),
    14: ('AFPointUsed', ),
    15: ('FlashBias', {
        0xFFC0: '-2 EV',
        0xFFCC: '-1.67 EV',
        0xFFD0: '-1.50 EV',
        0xFFD4: '-1.33 EV',
        0xFFE0: '-1 EV',
        0xFFEC: '-0.67 EV',
        0xFFF0: '-0.50 EV',
        0xFFF4: '-0.33 EV',
        0x0000: '0 EV',
        0x000C: '0.33 EV',
        0x0010: '0.50 EV',
        0x0014: '0.67 EV',
        0x0020: '1 EV',
        0x002C: '1.33 EV',
        0x0030: '1.50 EV',
        0x0034: '1.67 EV',
        0x0040: '2 EV'
    }),
    19: ('SubjectDistance', ),
}

# 0x0026
AF_INFO_2 = {
    2: ('AFAreaMode', {
        0: 'Off (Manual Focus)',
        2: 'Single-point AF',
        4: 'Multi-point AF or AI AF',
        5: 'Face Detect AF',
        6: 'Face + Tracking',
        7: 'Zone AF',
        8: 'AF Point Expansion',
        9: 'Spot AF',
        11: 'Flexizone Multi',
        13: 'Flexizone Single',
    }),
    3: ('NumAFPoints', ),
    4: ('ValidAFPoints', ),
    5: ('CanonImageWidth', ),
}

# 0x0093
FILE_INFO = {
    1: ('FileNumber', ),
    3: ('BracketMode', {
        0: 'Off',
        1: 'AEB',
        2: 'FEB',
        3: 'ISO',
        4: 'WB',
    }),
    4: ('BracketValue', ),
    5: ('BracketShotNumber', ),
    6: ('RawJpgQuality', {
        0xFFFF: 'n/a',
        1: 'Economy',
        2: 'Normal',
        3: 'Fine',
        4: 'RAW',
        5: 'Superfine',
        130: 'Normal Movie'
    }),
    7: ('RawJpgSize', {
        0: 'Large',
        1: 'Medium',
        2: 'Small',
        5: 'Medium 1',
        6: 'Medium 2',
        7: 'Medium 3',
        8: 'Postcard',
        9: 'Widescreen',
        10: 'Medium Widescreen',
        14: 'Small 1',
        15: 'Small 2',
        16: 'Small 3',
        128: '640x480 Movie',
        129: 'Medium Movie',
        130: 'Small Movie',
        137: '1280x720 Movie',
        142: '1920x1080 Movie',
    }),
    8: ('LongExposureNoiseReduction2', {
        0: 'Off',
        1: 'On (1D)',
        2: 'On',
        3: 'Auto'
    }),
    9: ('WBBracketMode', {
        0: 'Off',
        1: 'On (shift AB)',
        2: 'On (shift GM)'
    }),
    12: ('WBBracketValueAB', ),
    13: ('WBBracketValueGM', ),
    14: ('FilterEffect', {
        0: 'None',
        1: 'Yellow',
        2: 'Orange',
        3: 'Red',
        4: 'Green'
    }),
    15: ('ToningEffect', {
        0: 'None',
        1: 'Sepia',
        2: 'Blue',
        3: 'Purple',
        4: 'Green',
    }),
    16: ('MacroMagnification', ),
    19: ('LiveViewShooting', {
        0: 'Off',
        1: 'On'
    }),
    25: ('FlashExposureLock', {
        0: 'Off',
        1: 'On'
    })
}

def add_one(value):
    return value + 1

def subtract_one(value):
    return value - 1

def convert_temp(value):
    return '%d C' % (value - 128)

# CameraInfo datastructures have variable sized members.  Each entry here is:
#   byte offset: (item name, data item type, decoding map).
# Note that the data item type is fed directly to struct.unpack at the
# specified offset.
CAMERA_INFO_TAG_NAME = 'MakerNote Tag 0x000D'

CAMERA_INFO_5D = {
    23: ('CameraTemperature', '<B', convert_temp),
    204: ('DirectoryIndex', '<L', subtract_one),
    208: ('FileIndex', '<H', add_one),
}

CAMERA_INFO_5DMKII = {
    25: ('CameraTemperature', '<B', convert_temp),
    443: ('FileIndex', '<L', add_one),
    455: ('DirectoryIndex', '<L', subtract_one),
}

CAMERA_INFO_5DMKIII = {
    27: ('CameraTemperature', '<B', convert_temp),
    652: ('FileIndex', '<L', add_one),
    656: ('FileIndex2', '<L', add_one),
    664: ('DirectoryIndex', '<L', subtract_one),
    668: ('DirectoryIndex2', '<L', subtract_one),
}

CAMERA_INFO_600D = {
    25: ('CameraTemperature', '<B', convert_temp),
    475: ('FileIndex', '<L', add_one),
    487: ('DirectoryIndex', '<L', subtract_one),
}

# A map of regular expressions on 'Image Model' to the CameraInfo spec
CAMERA_INFO_MODEL_MAP = {
    r'EOS 5D$': CAMERA_INFO_5D,
    r'EOS 5D Mark II$': CAMERA_INFO_5DMKII,
    r'EOS 5D Mark III$': CAMERA_INFO_5DMKIII,
    r'\b(600D|REBEL T3i|Kiss X5)\b': CAMERA_INFO_600D,
}
