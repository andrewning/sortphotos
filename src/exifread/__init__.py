import logging
from .classes import *
from .tags import *

__version__ = '1.4.2'

logger = logging.getLogger('exifread')


def increment_base(data, base):
    return ord(data[base+2]) * 256 + ord(data[base+3]) + 2


def process_file(f, stop_tag=DEFAULT_STOP_TAG, details=True, strict=False, debug=False):
    """
    Process an image file (expects an open file object).

    This is the function that has to deal with all the arbitrary nasty bits
    of the EXIF standard.
    """

    # by default do not fake an EXIF beginning
    fake_exif = 0

    # determine whether it's a JPEG or TIFF
    data = f.read(12)
    if data[0:4] in ['II*\x00', 'MM\x00*']:
        # it's a TIFF file
        logger.debug("TIFF format recognized in data[0:4]")
        f.seek(0)
        endian = f.read(1)
        f.read(1)
        offset = 0
    elif data[0:2] == '\xFF\xD8':
        # it's a JPEG file
        logger.debug("JPEG format recognized data[0:2]=0x%X%X", ord(data[0]), ord(data[1]))
        base = 2
        logger.debug("data[2]=0x%X data[3]=0x%X data[6:10]=%s",
                     ord(data[2]), ord(data[3]), data[6:10])
        while data[2] == '\xFF' and data[6:10] in ('JFIF', 'JFXX', 'OLYM', 'Phot'):
            length = ord(data[4]) * 256 + ord(data[5])
            logger.debug(" Length offset is %s", length)
            f.read(length-8)
            # fake an EXIF beginning of file
            # I don't think this is used. --gd
            data = '\xFF\x00' + f.read(10)
            fake_exif = 1
            if base > 2:
                logger.debug(" Added to base")
                base = base + length + 4 -2
            else:
                logger.debug(" Added to zero")
                base = length + 4
            logger.debug(" Set segment base to 0x%X", base)

        # Big ugly patch to deal with APP2 (or other) data coming before APP1
        f.seek(0)
        # in theory, this could be insufficient since 64K is the maximum size--gd
        data = f.read(base + 4000)
        # base = 2
        while 1:
            logger.debug(" Segment base 0x%X", base)
            if data[base:base+2] == '\xFF\xE1':
                # APP1
                logger.debug("  APP1 at base 0x%X", base)
                logger.debug("  Length: 0x%X 0x%X", ord(data[base+2]),
                             ord(data[base+3]))
                logger.debug("  Code: %s", data[base+4:base+8])
                if data[base+4:base+8] == "Exif":
                    logger.debug("  Decrement base by 2 to get to pre-segment header (for compatibility with later code)")
                    base = base-2
                    break
                increment = increment_base(data, base)
                logger.debug(" Increment base by %s", increment)
                base = base + increment
            elif data[base:base+2] == '\xFF\xE0':
                # APP0
                logger.debug("  APP0 at base 0x%X", base)
                logger.debug("  Length: 0x%X 0x%X", ord(data[base+2]),
                             ord(data[base+3]))
                logger.debug("  Code: %s", data[base+4:base+8])
                increment = increment_base(data, base)
                logger.debug(" Increment base by %s", increment)
                base = base + increment
            elif data[base:base+2] == '\xFF\xE2':
                # APP2
                logger.debug("  APP2 at base 0x%X", base)
                logger.debug("  Length: 0x%X 0x%X", ord(data[base+2]),
                             ord(data[base+3]))
                logger.debug(" Code: %s", data[base+4:base+8])
                increment = increment_base(data, base)
                logger.debug(" Increment base by %s", increment)
                base = base + increment
            elif data[base:base+2] == '\xFF\xEE':
                # APP14
                logger.debug("  APP14 Adobe segment at base 0x%X", base)
                logger.debug("  Length: 0x%X 0x%X", ord(data[base+2]),
                             ord(data[base+3]))
                logger.debug("  Code: %s", data[base+4:base+8])
                increment = increment_base(data, base)
                logger.debug(" Increment base by %s", increment)
                base = base + increment
                logger.debug("  There is useful EXIF-like data here, but we have no parser for it.")
            elif data[base:base+2] == '\xFF\xDB':
                logger.debug("  JPEG image data at base 0x%X No more segments are expected.",
                             base)
                break
            elif data[base:base+2] == '\xFF\xD8':
                # APP12
                logger.debug("  FFD8 segment at base 0x%X", base)
                logger.debug("  Got 0x%X 0x%X and %s instead",
                             ord(data[base]),
                             ord(data[base+1]),
                             data[4+base:10+base])
                logger.debug("  Length: 0x%X 0x%X", ord(data[base+2]),
                             ord(data[base+3]))
                logger.debug("  Code: %s", data[base+4:base+8])
                increment = increment_base(data, base)
                logger.debug("  Increment base by %s", increment)
                base = base + increment
            elif data[base:base+2] == '\xFF\xEC':
                # APP12
                logger.debug("  APP12 XMP (Ducky) or Pictureinfo segment at base 0x%X",
                             base)
                logger.debug("  Got 0x%X and 0x%X instead", ord(data[base]),
                             ord(data[base+1]))
                logger.debug("  Length: 0x%X 0x%X",
                             ord(data[base+2]),
                             ord(data[base+3]))
                logger.debug("Code: %s", data[base+4:base+8])
                increment = increment_base(data, base)
                logger.debug("  Increment base by %s", increment)
                base = base + increment
                logger.debug("  There is useful EXIF-like data here (quality, comment, copyright), but we have no parser for it.")
            else:
                try:
                    increment = increment_base(data, base)
                    logger.debug("  Got 0x%X and 0x%X instead",
                                 ord(data[base]),
                                 ord(data[base+1]))
                except:
                    logger.debug("  Unexpected/unhandled segment type or file content.")
                    return {}
                else:
                    logger.debug("  Increment base by %s", increment)
                    base = base + increment
        f.seek(base + 12)
        if data[2+base] == '\xFF' and data[6+base:10+base] == 'Exif':
            # detected EXIF header
            offset = f.tell()
            endian = f.read(1)
            #HACK TEST:  endian = 'M'
        elif data[2+base] == '\xFF' and data[6+base:10+base+1] == 'Ducky':
            # detected Ducky header.
            logger.debug("EXIF-like header (normally 0xFF and code): 0x%X and %s",
                         ord(data[2+base]) , data[6+base:10+base+1])
            offset = f.tell()
            endian = f.read(1)
        elif data[2+base] == '\xFF' and data[6+base:10+base+1] == 'Adobe':
            # detected APP14 (Adobe)
            logger.debug("EXIF-like header (normally 0xFF and code): 0x%X and %s",
                         ord(data[2+base]) , data[6+base:10+base+1])
            offset = f.tell()
            endian = f.read(1)
        else:
            # no EXIF information
            logger.debug("No EXIF header expected data[2+base]==0xFF and data[6+base:10+base]===Exif (or Duck)")
            logger.debug("Did get 0x%X and %s",
                         ord(data[2+base]), data[6+base:10+base+1])
            return {}
    else:
        # file format not recognized
        logger.debug("File format not recognized.")
        return {}

    # deal with the EXIF info we found
    logger.debug("Endian format is %s (%s)", endian, {
        'I': 'Intel',
        'M': 'Motorola',
        '\x01':'Adobe Ducky',
        'd':'XMP/Adobe unknown'
        }[endian])

    hdr = ExifHeader(f, endian, offset, fake_exif, strict, debug, details)
    ifd_list = hdr.list_IFDs()
    thumb_ifd = False
    ctr = 0
    for ifd in ifd_list:
        if ctr == 0:
            ifd_name = 'Image'
        elif ctr == 1:
            ifd_name = 'Thumbnail'
            thumb_ifd = ifd
        else:
            ifd_name = 'IFD %d' % ctr
        logger.debug('IFD %d (%s) at offset %d:', ctr, ifd_name, ifd)
        hdr.dump_IFD(ifd, ifd_name, stop_tag=stop_tag)
        # EXIF IFD
        exif_off = hdr.tags.get(ifd_name + ' ExifOffset')
        if exif_off:
            logger.debug(' Exif SubIFD at offset %d:', exif_off.values[0])
            hdr.dump_IFD(exif_off.values[0], 'EXIF', stop_tag=stop_tag)
            # Interoperability IFD contained in EXIF IFD
            intr_off = hdr.tags.get('EXIF SubIFD InteroperabilityOffset')
            if intr_off:
                logger.debug('  EXIF Interoperability SubSubIFD at offset %d:',
                          intr_off.values[0])
                hdr.dump_IFD(intr_off.values[0], 'EXIF Interoperability',
                             tag_dict=INTR_TAGS, stop_tag=stop_tag)
        # GPS IFD
        gps_off = hdr.tags.get(ifd_name+' GPSInfo')
        if gps_off:
            logger.debug(' GPS SubIFD at offset %d:', gps_off.values[0])
            hdr.dump_IFD(gps_off.values[0], 'GPS', tag_dict=GPS_TAGS, stop_tag=stop_tag)
        ctr += 1

    # deal with MakerNote contained in EXIF IFD
    # (Some apps use MakerNote tags but do not use a format for which we
    # have a description, do not process these).
    if details and 'EXIF MakerNote' in hdr.tags and 'Image Make' in hdr.tags:
        hdr.decode_maker_note()

    # extract thumbnails
    if details and thumb_ifd:
        hdr.extract_tiff_thumbnail(thumb_ifd)
        hdr.extract_jpeg_thumbnail()

    return hdr.tags
