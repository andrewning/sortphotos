#------------------------------------------------------------------------------
# File:         Panasonic.pm
#
# Description:  Panasonic/Leica maker notes tags
#
# Revisions:    11/10/2004 - P. Harvey Created
#
# References:   1) http://www.compton.nu/panasonic.html (based on FZ10)
#               2) Derived from DMC-FZ3 samples from dpreview.com
#               3) http://johnst.org/sw/exiftags/
#               4) Tels (http://bloodgate.com/) private communication (tests with FZ5)
#               7) http://homepage3.nifty.com/kamisaka/makernote/makernote_pana.htm (2007/10/02)
#               8) Marcel Coenen private communication (DMC-FZ50)
#               9) http://forums.dpreview.com/forums/read.asp?forum=1033&message=22756430
#              10) http://bretteville.com/pdfs/M8Metadata_v2.pdf
#              11) http://www.digital-leica.com/lens_codes/index.html
#              12) Joerg - http://www.cpanforum.com/threads/11602 (LX3 firmware 2.0)
#              13) Michael Byczkowski private communication (Leica M9)
#              14) Carl Bretteville private communication (M9)
#              15) Zdenek Mihula private communication (TZ8)
#              16) Olaf Ulrich private communication
#              17) http://u88.n24.queensu.ca/exiftool/forum/index.php/topic,4922.0.html
#              18) Thomas Modes private communication (G6)
#              19) http://u88.n24.queensu.ca/exiftool/forum/index.php/topic,5533.0.html
#              JD) Jens Duttke private communication (TZ3,FZ30,FZ50)
#------------------------------------------------------------------------------

package Image::ExifTool::Panasonic;

use strict;
use vars qw($VERSION %leicaLensTypes);
use Image::ExifTool qw(:DataAccess :Utils);
use Image::ExifTool::Exif;

$VERSION = '1.92';

sub ProcessLeicaLEIC($$$);
sub WhiteBalanceConv($;$$);

# Leica lens types (ref 10)
%leicaLensTypes = (
    OTHER => sub {
        my ($val, $inv, $conv) = @_;
        return undef if $inv or not $val =~ s/ .*//;
        return $$conv{$val};
    },
    Notes => q{
        the LensType value is obtained by splitting the stored value into 2
        integers:  The stored value divided by 4, and its lower 2 bits.  The second
        number is used only if necessary to identify certain manually coded lenses
        on the M9, or the focal length of some multi-focal lenses.
    },
    # All M9 codes (two numbers: first the LensID then the lower 2 bits)
    # are ref PH with samples from ref 13.  From ref 10, the lower 2 bits of
    # the LensType value give the frame selector position for most lenses,
    # although for the 28-35-50mm (at least) it gives the focal length selection.
    # The M9 also gives the focal length selection but for other lenses the
    # lower 3 bits don't change with frame selector position except for the lens
    # shows as uncoded for certain lenses and some incorrect positions of the
    # frame selector.  The bits are zero for uncoded lenses when manually coding
    # from the menu on the M9. - PH
    # Frame selector bits (from ref 10, M8):
    #   1 => '28/90mm frame lines engaged',
    #   2 => '24/35mm frame lines engaged',
    #   3 => '50/75mm frame lines engaged',
    '0 0' => 'Uncoded lens',
#
# NOTE: MUST ADD ENTRY TO %frameSelectorBits below when a new lens is added!!!!
#
                                            # model number(s):
    1 => 'Elmarit-M 21mm f/2.8',            # 11134
    3 => 'Elmarit-M 28mm f/2.8 (III)',      # 11804
    4 => 'Tele-Elmarit-M 90mm f/2.8 (II)',  # 11800
    5 => 'Summilux-M 50mm f/1.4 (II)',      # 11868/11856/11114
    6 => 'Summicron-M 35mm f/2 (IV)',       # 11310/11311
    '6 0' => 'Summilux-M 35mm f/1.4',       # 11869/11870/11860
    7 => 'Summicron-M 90mm f/2 (II)',       # 11136/11137
    9 => 'Elmarit-M 135mm f/2.8 (I/II)',    # 11829
    '9 0' => 'Apo-Telyt-M 135mm f/3.4',     # 11889
    16 => 'Tri-Elmar-M 16-18-21mm f/4 ASPH.',# 11626
    '16 1' => 'Tri-Elmar-M 16-18-21mm f/4 ASPH. (at 16mm)',
    '16 2' => 'Tri-Elmar-M 16-18-21mm f/4 ASPH. (at 18mm)',
    '16 3' => 'Tri-Elmar-M 16-18-21mm f/4 ASPH. (at 21mm)',
    23 => 'Summicron-M 50mm f/2 (III)',     # 11817, version (I) in camera menu
    24 => 'Elmarit-M 21mm f/2.8 ASPH.',     # 11135/11897
    25 => 'Elmarit-M 24mm f/2.8 ASPH.',     # 11878/11898
    26 => 'Summicron-M 28mm f/2 ASPH.',     # 11604
    27 => 'Elmarit-M 28mm f/2.8 (IV)',      # 11809
    28 => 'Elmarit-M 28mm f/2.8 ASPH.',     # 11606
    29 => 'Summilux-M 35mm f/1.4 ASPH.',    # 11874/11883
    '29 0' => 'Summilux-M 35mm f/1.4 ASPHERICAL', # 11873 (different from "ASPH." model!)
    30 => 'Summicron-M 35mm f/2 ASPH.',     # 11879/11882
    31 => 'Noctilux-M 50mm f/1',            # 11821/11822
    '31 0' => 'Noctilux-M 50mm f/1.2',      # 11820
    32 => 'Summilux-M 50mm f/1.4 ASPH.',    # 11891/11892
    33 => 'Summicron-M 50mm f/2 (IV, V)',   # 11819/11825/11826/11816, version (II,III) in camera menu
    34 => 'Elmar-M 50mm f/2.8',             # 11831/11823/11825
    35 => 'Summilux-M 75mm f/1.4',          # 11814/11815/11810
    36 => 'Apo-Summicron-M 75mm f/2 ASPH.', # 11637
    37 => 'Apo-Summicron-M 90mm f/2 ASPH.', # 11884/11885
    38 => 'Elmarit-M 90mm f/2.8',           # 11807/11808, version (II) in camera menu
    39 => 'Macro-Elmar-M 90mm f/4',         # 11633/11634
    '39 0' => 'Tele-Elmar-M 135mm f/4 (II)',# 11861
    40 => 'Macro-Adapter M',                # 14409
    '41 3' => 'Apo-Summicron-M 50mm f/2 Asph', #16
    42 => 'Tri-Elmar-M 28-35-50mm f/4 ASPH.',# 11625
    '42 1' => 'Tri-Elmar-M 28-35-50mm f/4 ASPH. (at 28mm)',
    '42 2' => 'Tri-Elmar-M 28-35-50mm f/4 ASPH. (at 35mm)',
    '42 3' => 'Tri-Elmar-M 28-35-50mm f/4 ASPH. (at 50mm)',
    43 => 'Summarit-M 35mm f/2.5',          # ? (ref PH)
    44 => 'Summarit-M 50mm f/2.5',          # ? (ref PH)
    45 => 'Summarit-M 75mm f/2.5',          # ? (ref PH)
    46 => 'Summarit-M 90mm f/2.5',          # ?
    47 => 'Summilux-M 21mm f/1.4 ASPH.',    # ? (ref 11)
    48 => 'Summilux-M 24mm f/1.4 ASPH.',    # ? (ref 11)
    49 => 'Noctilux-M 50mm f/0.95 ASPH.',   # ? (ref 11)
    50 => 'Elmar-M 24mm f/3.8 ASPH.',       # ? (ref 11)
    51 => 'Super-Elmar-M 21mm f/3.4 Asph',  # ? (ref 16, frameSelectorBits=1)
    '51 2' => 'Super-Elmar-M 14mm f/3.8 Asph', # ? (ref 16)
    52 => 'Super-Elmar-M 18mm f/3.8 ASPH.', # ? (ref PH/11)
    '53 2' => 'Apo-Telyt-M 135mm f/3.4', #16
    '53 3' => 'Apo-Summicron-M 50mm f/2 (VI)', #LR
);

# M9 frame selector bits for each lens
#  1 = towards lens    = 28/90mm or 21mm or Adapter (or Elmarit-M 135mm f/2.8)
#  2 = away from lens  = 24/35mm (or 35/135mm on the M9)
#  3 = middle position = 50/75mm or 18mm
my %frameSelectorBits = (
    1 => 1,
    3 => 1,
    4 => 1,
    5 => 3,
    6 => 2,
    7 => 1,
    9 => 1, # (because lens has special magnifier for the rangefinder)
    16 => 1, # or 2 or 3
    23 => 3,
    24 => 1,
    25 => 2,
    26 => 1,
    27 => 1,
    28 => 1,
    29 => 2,
    30 => 2,
    31 => 3,
    32 => 3,
    33 => 3,
    34 => 3,
    35 => 3,
    36 => 3,
    37 => 1,
    38 => 1,
    39 => 1,
    40 => 1,
    42 => 1, # or 2 or 3
    43 => 2, # (NC)
    44 => 3, # (NC)
    45 => 3,
    46 => 1, # (NC)
    47 => 1, # (NC)
    48 => 2, # (NC)
    49 => 3, # (NC)
    50 => 2, # (NC)
    51 => 1, # or 2 (ref 16)
    52 => 3,
    53 => 2, #16
);

# conversions for ShootingMode and SceneMode
my %shootingMode = (
    1  => 'Normal',
    2  => 'Portrait',
    3  => 'Scenery',
    4  => 'Sports',
    5  => 'Night Portrait',
    6  => 'Program',
    7  => 'Aperture Priority',
    8  => 'Shutter Priority',
    9  => 'Macro',
    10 => 'Spot', #7
    11 => 'Manual',
    12 => 'Movie Preview', #PH (LZ6)
    13 => 'Panning',
    14 => 'Simple', #PH (LZ6)
    15 => 'Color Effects', #7
    16 => 'Self Portrait', #PH (TZ5)
    17 => 'Economy', #7
    18 => 'Fireworks',
    19 => 'Party',
    20 => 'Snow',
    21 => 'Night Scenery',
    22 => 'Food', #7
    23 => 'Baby', #JD
    24 => 'Soft Skin', #PH (LZ6)
    25 => 'Candlelight', #PH (LZ6)
    26 => 'Starry Night', #PH (LZ6)
    27 => 'High Sensitivity', #7 (LZ6)
    28 => 'Panorama Assist', #7
    29 => 'Underwater', #7
    30 => 'Beach', #PH (LZ6)
    31 => 'Aerial Photo', #PH (LZ6)
    32 => 'Sunset', #PH (LZ6)
    33 => 'Pet', #JD
    34 => 'Intelligent ISO', #PH (LZ6)
    35 => 'Clipboard', #7
    36 => 'High Speed Continuous Shooting', #7
    37 => 'Intelligent Auto', #7
    39 => 'Multi-aspect', #PH (TZ5)
    41 => 'Transform', #PH (FS7)
    42 => 'Flash Burst', #PH (FZ28)
    43 => 'Pin Hole', #PH (FZ28)
    44 => 'Film Grain', #PH (FZ28)
    45 => 'My Color', #PH (GF1)
    46 => 'Photo Frame', #PH (FS7)
    48 => 'Movie', #PH (GM1)
    # 49 - seen for FS4 (snow?)
    51 => 'HDR', #12
    52 => 'Peripheral Defocus', #Horst Wandres
    55 => 'Handheld Night Shot', #PH (FZ47)
    57 => '3D', #PH (3D1)
    59 => 'Creative Control', #PH (FZ47)
    62 => 'Panorama', #17
    63 => 'Glass Through', #17
    64 => 'HDR', #17
    66 => 'Digital Filter', #PH (GF5 "Impressive Art", "Cross Process", "Color Select", "Star")
    67 => 'Clear Portrait', #18
    68 => 'Silky Skin', #18
    69 => 'Backlit Softness', #18
    70 => 'Clear in Backlight', #18
    71 => 'Relaxing Tone', #18
    72 => "Sweet Child's Face", #18
    73 => 'Distinct Scenery', #18
    74 => 'Bright Blue Sky', #18
    75 => 'Romantic Sunset Glow', #18
    76 => 'Vivid Sunset Glow', #18
    77 => 'Glistening Water', #18
    78 => 'Clear Nightscape', #18
    79 => 'Cool Night Sky', #18
    80 => 'Warm Glowing Nightscape', #18
    81 => 'Artistic Nightscape', #18
    82 => 'Glittering Illuminations', #18
    83 => 'Clear Night Portrait', #18
    84 => 'Soft Image of a Flower', #18
    85 => 'Appetizing Food', #18
    86 => 'Cute Desert', #18
    87 => 'Freeze Animal Motion', #18
    88 => 'Clear Sports Shot', #18
    89 => 'Monochrome', #18
    90 => 'Creative Control', #18
);

%Image::ExifTool::Panasonic::Main = (
    WRITE_PROC => \&Image::ExifTool::Exif::WriteExif,
    CHECK_PROC => \&Image::ExifTool::Exif::CheckExif,
    GROUPS => { 0 => 'MakerNotes', 2 => 'Camera' },
    WRITABLE => 1,
    0x01 => {
        Name => 'ImageQuality',
        Writable => 'int16u',
        PrintConv => {
            1 => 'TIFF', #PH (FZ20)
            2 => 'High',
            3 => 'Normal',
            # 5 - seen this for 1920x1080, 30fps SZ7 video - PH
            6 => 'Very High', #3 (Leica)
            7 => 'Raw', #3 (Leica)
            9 => 'Motion Picture', #PH (LZ6)
            11 => 'Full HD Movie', #PH (V-LUX)
            12 => '4k Movie', #PH (V-LUX)
        },
    },
    0x02 => {
        Name => 'FirmwareVersion',
        Writable => 'undef',
        Notes => q{
            for some camera models such as the FZ30 this may be an internal production
            reference number and not the actual firmware version
        }, # (ref http://www.stevesforums.com/forums/view_topic.php?id=87764&forum_id=23&)
        # (can be either binary or ascii -- add decimal points if binary)
        ValueConv => '$val=~/[\0-\x2f]/ ? join(" ",unpack("C*",$val)) : $val',
        ValueConvInv => q{
            $val =~ /(\d+ ){3}\d+/ and $val = pack('C*',split(' ', $val));
            length($val) == 4 or warn "Version must be 4 numbers\n";
            return $val;
        },
        PrintConv => '$val=~tr/ /./; $val',
        PrintConvInv => '$val=~tr/./ /; $val',
    },
    0x03 => {
        Name => 'WhiteBalance',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Auto',
            2 => 'Daylight',
            3 => 'Cloudy',
            4 => 'Incandescent', #PH
            5 => 'Manual',
            8 => 'Flash',
            10 => 'Black & White', #3 (Leica)
            11 => 'Manual', #PH (FZ8)
            12 => 'Shade', #PH (FS7)
            13 => 'Kelvin', #PeterK (NC)
        },
    },
    0x07 => {
        Name => 'FocusMode',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Auto',
            2 => 'Manual',
            4 => 'Auto, Focus button', #4
            5 => 'Auto, Continuous', #4
            6 => 'AF-S', #18 (also seen for GF1 - PH)
            7 => 'AF-C', #18
            8 => 'AF-F', #18 (auto-focus flexible)
        },
    },
    0x0f => [
        {
            Name => 'AFAreaMode',
            Condition => '$$self{Model} =~ /DMC-FZ10\b/', #JD
            Writable => 'int8u',
            Count => 2,
            Notes => 'DMC-FZ10',
            PrintConv => {
                '0 1'   => 'Spot Mode On',
                '0 16'  => 'Spot Mode Off',
            },
        },{
            Name => 'AFAreaMode',
            Writable => 'int8u',
            Count => 2,
            Notes => 'other models',
            PrintConv => { #PH
                '0 1'   => '9-area', # (FS7)
                '0 16'  => '3-area (high speed)', # (FZ8)
                '0 23'  => '23-area', #PH (FZ47,NC)
                # '0 49' - seen for LX100, V-LUX (PH)
                '1 0'   => 'Spot Focusing', # (FZ8)
                '1 1'   => '5-area', # (FZ8)
                '16'    => 'Normal?', # (only mode for DMC-LC20)
                '16 0'  => '1-area', # (FZ8)
                '16 16' => '1-area (high speed)', # (FZ8)
                # '32 0' is Face Detect for FS7, and Face Detect or Focus Tracking
                # for the DMC-FZ200 (ref 17), and Auto is DMC-L1 guess,
                '32 0'  => 'Tracking',
                '32 1'  => '3-area (left)?', # (DMC-L1 guess)
                '32 2'  => '3-area (center)?', # (DMC-L1 guess)
                '32 3'  => '3-area (right)?', # (DMC-L1 guess)
                '64 0'  => 'Face Detect',
                '128 0' => 'Spot Focusing 2', #18
            },
        },
    ],
    0x1a => {
        Name => 'ImageStabilization',
        Writable => 'int16u',
        PrintConv => {
            2 => 'On, Mode 1',
            3 => 'Off',
            4 => 'On, Mode 2',
            5 => 'Panning', #18
            # GF1 also has a "Mode 3" - PH
            6 => 'On, Mode 3', #PH (GX7, sensor shift?)
        },
    },
    0x1c => {
        Name => 'MacroMode',
        Writable => 'int16u',
        PrintConv => {
            1 => 'On',
            2 => 'Off',
            0x101 => 'Tele-Macro', #7
            0x201 => 'Macro Zoom', #PH (FS7)
        },
    },
    0x1f => {
        Name => 'ShootingMode',
        Writable => 'int16u',
        PrintConvColumns => 2,
        PrintConv => \%shootingMode,
    },
    0x20 => {
        Name => 'Audio',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Yes',
            2 => 'No',
            3 => 'Stereo', #PH (NC)
        },
    },
    0x21 => { #2
        Name => 'DataDump',
        Writable => 0,
        Binary => 1,
    },
    # 0x22 - normally 0, but 2 for 'Simple' ShootingMode in LZ6 sample - PH
    0x23 => {
        Name => 'WhiteBalanceBias',
        Format => 'int16s',
        Writable => 'int16s',
        ValueConv => '$val / 3',
        ValueConvInv => '$val * 3',
        PrintConv => 'Image::ExifTool::Exif::PrintFraction($val)',
        PrintConvInv => 'Image::ExifTool::Exif::ConvertFraction($val)',
    },
    0x24 => {
        Name => 'FlashBias',
        Format => 'int16s',
        Writable => 'int16s',
        ValueConv => '$val / 3', #17 (older models may not have factor of 3? - PH)
        ValueConvInv => '$val * 3',
        PrintConv => 'Image::ExifTool::Exif::PrintFraction($val)',
        PrintConvInv => 'Image::ExifTool::Exif::ConvertFraction($val)',
    },
    0x25 => { #PH
        Name => 'InternalSerialNumber',
        Writable => 'undef',
        Count => 16,
        Notes => q{
            this number is unique, and contains the date of manufacture, but is not the
            same as the number printed on the camera body
        },
        PrintConv => q{
            return $val unless $val=~/^([A-Z]\d{2})(\d{2})(\d{2})(\d{2})(\d{4})/;
            my $yr = $2 + ($2 < 70 ? 2000 : 1900);
            return "($1) $yr:$3:$4 no. $5";
        },
        PrintConvInv => '$_=$val; tr/A-Z0-9//dc; s/(.{3})(19|20)/$1/; $_',
    },
    0x26 => { #PH
        Name => 'PanasonicExifVersion',
        Writable => 'undef',
    },
    # 0x27 - values: 0 (LZ6,FX10K)
    0x28 => {
        Name => 'ColorEffect',
        Writable => 'int16u',
        # FX30 manual: (ColorMode) natural, vivid, cool, warm, b/w, sepia
        PrintConv => {
            1 => 'Off',
            2 => 'Warm',
            3 => 'Cool',
            4 => 'Black & White',
            5 => 'Sepia',
            6 => 'Happy', #PH (FX70) (yes, really. you wouldn't want sad colors now would you?)
            8 => 'Vivid', #PH (SZ3)
        },
    },
    0x29 => { #JD
        Name => 'TimeSincePowerOn',
        Writable => 'int32u',
        Notes => q{
            time in 1/100 s from when the camera was powered on to when the image is
            written to memory card
        },
        ValueConv => '$val / 100',
        ValueConvInv => '$val * 100',
        PrintConv => sub { # convert to format "[DD days ]HH:MM:SS.ss"
            my $val = shift;
            my $str = '';
            if ($val >= 24 * 3600) {
                my $d = int($val / (24 * 3600));
                $str .= "$d days ";
                $val -= $d * 24 * 3600;
            }
            my $h = int($val / 3600);
            $val -= $h * 3600;
            my $m = int($val / 60);
            $val -= $m * 60;
            my $s = int($val);
            my $f = 100 * ($val - int($val));
            return sprintf("%s%.2d:%.2d:%.2d.%.2d",$str,$h,$m,$s,$f);
        },
        PrintConvInv => sub {
            my $val = shift;
            my @vals = ($val =~ /\d+(?:\.\d*)?/g);
            my $sec = 0;
            $sec += 24 * 3600 * shift(@vals) if @vals > 3;
            $sec += 3600 * shift(@vals) if @vals > 2;
            $sec += 60 * shift(@vals) if @vals > 1;
            $sec += shift(@vals) if @vals;
            return $sec;
        },
    },
    0x2a => { #4
        Name => 'BurstMode',
        Writable => 'int16u',
        Notes => 'decoding may be different for some models',
        PrintConv => {
            0 => 'Off',
            1 => 'On', #PH (TZ5) [was "Low/High Quality" from ref 4]
            2 => 'Auto Exposure Bracketing (AEB)', #17
            4 => 'Unlimited', #PH (TZ5)
            8 => 'White Balance Bracketing', #18
            17 => 'On (with flash)', #forum5597
        },
    },
    0x2b => { #4
        Name => 'SequenceNumber',
        Writable => 'int32u',
    },
    0x2c => [
        {
            Name => 'ContrastMode',
            Condition => '$$self{Model} !~ /^DMC-(FX10|G1|L1|L10|LC80|GF\d+|G2|TZ10|ZS7)$/',
            Flags => 'PrintHex',
            Writable => 'int16u',
            Notes => q{
                this decoding seems to work for some models such as the LC1, LX2, FZ7, FZ8,
                FZ18 and FZ50, but may not be correct for other models such as the FX10, G1, L1,
                L10 and LC80
            },
            PrintConv => {
                0x00 => 'Normal',
                0x01 => 'Low',
                0x02 => 'High',
                # 0x03 - observed with LZ6 and TZ5 in Fireworks mode
                #        and GX7 in Fantasy/Retro/OldDays/HighKey - PH
                # 0x04 - observed in MP4 movie with GM1 (EXIF and 0x39 Contrast "Normal") - PH
                # 0x05 - observed with FX01, FX40 and FP8 (EXIF contrast "Normal") - PH
                0x06 => 'Medium Low', #PH (FZ18)
                0x07 => 'Medium High', #PH (FZ18)
                # 0x08 - GX7 in DynamicMonochrome mode
                0x0d => 'High Dynamic', #PH (FZ47 in ?)
                # 0x13 - seen for LX100 (PH)
                # 0x18 - seen for FZ2500 (PH)
                # DMC-LC1 values:
                0x100 => 'Low',
                0x110 => 'Normal',
                0x120 => 'High',
            }
        },{
            Name => 'ContrastMode',
            Condition => '$$self{Model} =~ /^DMC-(GF\d+|G2)$/',
            Notes => 'these values are used by the G2, GF1, GF2, GF3, GF5 and GF6',
            Writable => 'int16u',
            PrintConv => { # (decoded for GF1 unless otherwise noted)
                0 => '-2',
                1 => '-1',
                2 => 'Normal',
                3 => '+1',
                4 => '+2',
                # Note: Other Contrast tags will be "Normal" in any of these modes:
                5 => 'Normal 2', # 5 - seen for Portrait (FX80) and Normal (GF6)
                7 => 'Nature (Color Film)', # (GF1,G2; GF3 "Miniature")
                9 => 'Expressive', #(GF3)
                12 => 'Smooth (Color Film) or Pure (My Color)', #(GF1,G2 "Smooth Color")
                17 => 'Dynamic (B&W Film)', #(GF1,G2)
                22 => 'Smooth (B&W Film)', #(GF1,G2)
                25 => 'High Dynamic', #(GF5)
                26 => 'Retro', #(GF5)
                27 => 'Dynamic (Color Film)', #(GF1,G2) (GF3 "High Key")
                28 => 'Low Key', #(GF5)
                29 => 'Toy Effect', #(GF5)
                32 => 'Vibrant (Color Film) or Expressive (My Color)', # (GF1; G2 "Vibrant"; GF2,GF5 "Expressive")
                33 => 'Elegant (My Color)',
                37 => 'Nostalgic (Color Film)', # (GF1,G2; GF5 "Sepia")
                41 => 'Dynamic Art (My Color)', # (GF5 "High Key")
                42 => 'Retro (My Color)',
                45 => 'Cinema', #(GF2)
                47 => 'Dynamic Mono', #(GF5)
                50 => 'Impressive Art', #(GF5)
                51 => 'Cross Process', #(GF5)
                100 => 'High Dynamic 2', #Exiv2 (G6)
                101 => 'Retro 2', #Exiv2 (G6)
                102 => 'High Key 2', #Exiv2 (G6)
                103 => 'Low Key 2', #Exiv2 (G6)
                104 => 'Toy Effect 2', #Exiv2 (G6)
                107 => 'Expressive 2', #(GF6)
                112 => 'Sepia', #Exiv2 (G6)
                117 => 'Miniature', #Exiv2 (G6)
                122 => 'Dynamic Monochrome', #(GF6)
                127 => 'Old Days', #Exiv2 (G6)
                132 => 'Dynamic Monochrome 2', #Exiv2 (G6)
                135 => 'Impressive Art 2', #Exiv2 (G6)
                136 => 'Cross Process 2', #Exiv2 (G6)
                137 => 'Toy Pop', #Exiv2 (G6)
                138 => 'Fantasy', #Exiv2 (G6)
                256 => 'Normal 3', #Exiv2 (G6)
                272 => 'Standard', #Exiv2 (G6)
                288 => 'High', #Exiv2 (G6)
                # more new modes for GF6:
                # ? => 'Old Days',
                # ? => 'Toy Pop',
                # ? => 'Bleach Bypass',
                # ? => 'Fantasy',
                # ? => 'Star Filter',
                # ? => 'One Point Color',
                # ? => 'Sunshine',
            },
        },{
            Name => 'ContrastMode',
            Condition => '$$self{Model} =~ /^DMC-(TZ10|ZS7)$/',
            Notes => 'these values are used by the TZ10 and ZS7',
            Writable => 'int16u',
            PrintConv => {
                0 => 'Normal',
                1 => '-2',
                2 => '+2',
                5 => '-1',
                6 => '+1',
            },
        },{
            Name => 'ContrastMode',
            Writable => 'int16u',
        },
    ],
    0x2d => {
        Name => 'NoiseReduction',
        Writable => 'int16u',
        Notes => 'the encoding for this value is not consistent between models',
        PrintConv => {
            0 => 'Standard',
            1 => 'Low (-1)',
            2 => 'High (+1)',
            3 => 'Lowest (-2)', #JD
            4 => 'Highest (+2)', #JD
            # 65531 - seen for LX100/FZ2500 "NR1" test shots at imaging-resource (PH)
            #     0 - seen for FZ2500 "NR6D" test shots (PH)
        },
    },
    0x2e => { #4
        Name => 'SelfTimer',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Off',
            2 => '10 s',
            3 => '2 s',
            4 => '10 s / 3 pictures', #17
            # 258 - seen for FZ2500,TZ90 (PH)
        },
    },
    # 0x2f - values: 1 (LZ6,FX10K)
    0x30 => { #7
        Name => 'Rotation',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Horizontal (normal)',
            3 => 'Rotate 180', #PH
            6 => 'Rotate 90 CW', #PH (ref 7 gives 270 CW)
            8 => 'Rotate 270 CW', #PH (ref 7 gives 90 CW)
        },
    },
    0x31 => { #PH (FS7)
        Name => 'AFAssistLamp',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Fired',
            2 => 'Enabled but Not Used',
            3 => 'Disabled but Required',
            4 => 'Disabled and Not Required',
            # have seen a value of 5 - PH
            # values possibly related to FOC-L? - JD
        },
    },
    0x32 => { #7
        Name => 'ColorMode',
        Writable => 'int16u',
        PrintConv => {
            0 => 'Normal',
            1 => 'Natural',
            2 => 'Vivid',
            # have seen 3 for GF2 - PH
        },
    },
    0x33 => { #JD
        Name => 'BabyAge',
        Writable => 'string',
        Notes => 'or pet age', #PH
        PrintConv => '$val eq "9999:99:99 00:00:00" ? "(not set)" : $val',
        PrintConvInv => '$val =~ /^\d/ ? $val : "9999:99:99 00:00:00"',
    },
    0x34 => { #7/PH
        Name => 'OpticalZoomMode',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Standard',
            2 => 'Extended',
        },
    },
    0x35 => { #9
        Name => 'ConversionLens',
        Writable => 'int16u',
        PrintConv => { #PH (unconfirmed)
            1 => 'Off',
            2 => 'Wide',
            3 => 'Telephoto',
            4 => 'Macro',
        },
    },
    0x36 => { #8
        Name => 'TravelDay',
        Writable => 'int16u',
        PrintConv => '$val == 65535 ? "n/a" : $val',
        PrintConvInv => '$val =~ /(\d+)/ ? $1 : $val',
    },
    # 0x37 - values: 0,1,2 (LZ6, 0 for movie preview); 257 (FX10K); 0,256 (TZ5, 0 for movie preview)
    # 0x38 - values: 0,1,2 (LZ6, same as 0x37); 1,2 (FX10K); 0,256 (TZ5, 0 for movie preview)
    0x39 => { #7 (L1/L10)
        Name => 'Contrast',
        Format => 'int16s',
        Writable => 'int16u',
        %Image::ExifTool::Exif::printParameter,
    },
    0x3a => {
        Name => 'WorldTimeLocation',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Home',
            2 => 'Destination',
        },
    },
    0x3b => { #PH (TZ5/FS7)
        # (tags 0x3b, 0x3e, 0x8008 and 0x8009 have the same values in all my samples - PH)
        Name => 'TextStamp',
        Writable => 'int16u',
        PrintConv => { 1 => 'Off', 2 => 'On' },
    },
    0x3c => { #PH
        Name => 'ProgramISO', # (maybe should rename this ISOSetting?)
        Writable => 'int16u',
        PrintConv => {
            OTHER => sub { shift },
            65534 => 'Intelligent ISO', #PH (FS7)
            65535 => 'n/a',
        },
    },
    0x3d => { #PH
        Name => 'AdvancedSceneType',
        Writable => 'int16u',
        Notes => 'used together with SceneMode to derive Composite AdvancedSceneMode',
    },
    0x3e => { #PH (TZ5/FS7)
        # (tags 0x3b, 0x3e, 0x8008 and 0x8009 have the same values in all my samples - PH)
        Name => 'TextStamp',
        Writable => 'int16u',
        PrintConv => { 1 => 'Off', 2 => 'On' },
    },
    0x3f => { #PH (TZ7)
        Name => 'FacesDetected',
        Writable => 'int16u',
    },
    0x40 => { #7 (L1/L10)
        Name => 'Saturation',
        Format => 'int16s',
        Writable => 'int16u',
        %Image::ExifTool::Exif::printParameter,
    },
    0x41 => { #7 (L1/L10)
        Name => 'Sharpness',
        Format => 'int16s',
        Writable => 'int16u',
        %Image::ExifTool::Exif::printParameter,
    },
    0x42 => { #7 (DMC-L1)
        Name => 'FilmMode',
        Writable => 'int16u',
        PrintConv => {
            0 => 'n/a', #PH (eg. FZ100 "Photo Frame" ShootingMode)
            1 => 'Standard (color)',
            2 => 'Dynamic (color)',
            3 => 'Nature (color)',
            4 => 'Smooth (color)',
            5 => 'Standard (B&W)',
            6 => 'Dynamic (B&W)',
            7 => 'Smooth (B&W)',
            # 8 => 'My Film 1'? (from owner manual)
            # 9 => 'My Film 2'?
            10 => 'Nostalgic', #(GH1)
            11 => 'Vibrant', #(GH1)
            # 12 => 'Multi Film'? (in the GH1 specs)
        },
    },
    # 0x43 - int16u: 2,3
    0x44 => {
        Name => 'ColorTempKelvin',
        Format => 'int16u',
    },
    0x45 => { #19
        Name => 'BracketSettings',
        Writable => 'int16u',
        PrintConv => {
            0 => 'No Bracket',
            1 => '3 Images, Sequence 0/-/+',
            2 => '3 Images, Sequence -/0/+',
            3 => '5 Images, Sequence 0/-/+',
            4 => '5 Images, Sequence -/0/+',
            5 => '7 Images, Sequence 0/-/+',
            6 => '7 Images, Sequence -/0/+',
        },
    },
    0x46 => { #PH/JD
        Name => 'WBShiftAB',
        Format => 'int16s',
        Writable => 'int16u',
        Notes => 'positive is a shift toward blue',
    },
    0x47 => { #PH/JD
        Name => 'WBShiftGM',
        Format => 'int16s',
        Writable => 'int16u',
        Notes => 'positive is a shift toward green',
    },
    0x48 => { #17
        Name => 'FlashCurtain',
        Writable => 'int16u',
        PrintConv => {
            0 => 'n/a',
            1 => '1st',
            2 => '2nd',
        },
    },
    0x49 => { #19
        Name => 'LongExposureNoiseReduction',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Off',
            2 => 'On'
        }
    },
    # 0x4a - int16u: 0
    0x4b => { #PH
        Name => 'PanasonicImageWidth',
        Writable => 'int32u',
    },
    0x4c => { #PH
        Name => 'PanasonicImageHeight',
        Writable => 'int32u',
    },
    0x4d => { #PH (FS7)
        Name => 'AFPointPosition',
        Writable => 'rational64u',
        Count => 2,
        Notes => 'X Y coordinates of primary AF area center, in the range 0.0 to 1.0',
        PrintConv => q{
            return 'none' if $val eq '16777216 16777216';
            my @a = split ' ', $val;
            sprintf("%.2g %.2g",@a);
        },
        PrintConvInv => '$val eq "none" ? "16777216 16777216" : $val',
    },
    0x4e => { #PH
        Name => 'FaceDetInfo',
        PrintConv => 'length $val',
        SubDirectory => {
            TagTable => 'Image::ExifTool::Panasonic::FaceDetInfo',
        },
    },
    # 0x4f,0x50 - int16u: 0
    0x51 => {
        Name => 'LensType',
        Writable => 'string',
        ValueConv => '$val=~s/ +$//; $val', # trim trailing spaces
        ValueConvInv => '$val',
    },
    0x52 => { #7 (DMC-L1)
        Name => 'LensSerialNumber',
        Writable => 'string',
        ValueConv => '$val=~s/ +$//; $val', # trim trailing spaces
        ValueConvInv => '$val',
    },
    0x53 => { #7 (DMC-L1)
        Name => 'AccessoryType',
        Writable => 'string',
        ValueConv => '$val=~s/ +$//; $val', # trim trailing spaces
        ValueConvInv => '$val',
    },
    0x54 => { #19
        Name => 'AccessorySerialNumber',
        Writable => 'string',
        ValueConv => '$val=~s/ +$//; $val', # trim trailing spaces
        ValueConvInv => '$val',
    },
    # 0x55 - int16u: 1
    # 0x57 - int16u: 0
    0x59 => { #PH (FS7)
        Name => 'Transform',
        Writable => 'undef',
        Notes => 'decoded as two 16-bit signed integers',
        Format => 'int16s',
        Count => 2,
        PrintConv => {
            '-3 2' => 'Slim High',
            '-1 1' => 'Slim Low',
            '0 0' => 'Off',
            '1 1' => 'Stretch Low',
            '3 2' => 'Stretch High',
        },
    },
    # 0x5a - int16u: 0,2
    # 0x5b - int16u: 0
    # 0x5c - int16u: 0,2
    0x5d => { #PH (GF1, FZ35)
        Name => 'IntelligentExposure',
        Notes => 'not valid for some models', # (doesn't change in ZS7 and GH1 images)
        Writable => 'int16u',
        PrintConv => {
            0 => 'Off',
            1 => 'Low',
            2 => 'Standard',
            3 => 'High',
        },
    },
    # 0x5e,0x5f - undef[4]
    0x60 => { #18
        Name => 'LensFirmwareVersion',
        Writable => 'undef',
        Format => 'int8u',
        Count => 4,
        PrintConv => '$val=~tr/ /./; $val',
        PrintConvInv => '$val=~tr/./ /; $val',
    },
    0x61 => { #PH
        Name => 'FaceRecInfo',
        SubDirectory => {
            TagTable => 'Image::ExifTool::Panasonic::FaceRecInfo',
        },
    },
    0x62 => { #PH (FS7)
        Name => 'FlashWarning',
        Writable => 'int16u',
        PrintConv => { 0 => 'No', 1 => 'Yes (flash required but disabled)' },
    },
    0x63 => { #PH
        # not sure exactly what this means, but in my samples this is
        # FacesRecognized bytes of 0x01, padded with 0x00 to a length of 4 - PH
        Name => 'RecognizedFaceFlags',
        Format => 'int8u',
        Count => 4,
        Writable => 'undef',
        Unknown => 1,
    },
    0x65 => { #15
        Name => 'Title',
        Format => 'string',
        Writable => 'undef', # (Count 64)
    },
    0x66 => { #15
        Name => 'BabyName',
        Notes => 'or pet name',
        Format => 'string',
        Writable => 'undef', # (Count 64)
    },
    0x67 => { #15
        Name => 'Location',
        Groups => { 2 => 'Location' },
        Format => 'string',
        Writable => 'undef', # (Count 64)
    },
    # 0x68 - int8u: 1
    0x69 => { #PH (ZS7)
        Name => 'Country', # (Country/Region)
        Groups => { 2 => 'Location' },
        Format => 'string',
        Writable => 'undef', # (Count 72)
    },
    # 0x6a - int8u: 1
    0x6b => { #PH (ZS7)
        Name => 'State', # (State/Province/Count -- what is Count?)
        Groups => { 2 => 'Location' },
        Format => 'string',
        Writable => 'undef', # (Count 72)
    },
    # 0x6c - int8u: 1
    0x6d => { #PH (ZS7) (also see forum5997)
        Name => 'City', # (City/Town)
        Groups => { 2 => 'Location' },
        Format => 'string',
        Writable => 'undef', # (Count 72)
        Notes => 'City/Town as stored by some models, or County/Township for others',
    },
    # 0x6e - int8u: 1
    0x6f => { #PH (ZS7)
        Name => 'Landmark', # (Landmark)
        Groups => { 2 => 'Location' },
        Format => 'string',
        Writable => 'undef', # (Count 128)
    },
    0x70 => { #PH (ZS7)
        Name => 'IntelligentResolution',
        Writable => 'int8u',
        PrintConv => {
            0 => 'Off',
            # Note: I think these values make sense for the GH2, but meanings
            #       may be different for other models
            1 => 'Low',
            2 => 'Standard',
            3 => 'High',
            4 => 'Extended',
        },
    },
    # 0x71 - undef[128] (maybe text stamp text?)
    0x77 => { #18
        Name => 'BurstSpeed',
        Writable => 'int16u',
        Notes => 'images per second',
    },
    # 0x72,0x73,0x74,0x75,0x77,0x78: 0
    # 0x76: 0, (3 for G6 with HDR on, ref 18)
    0x79 => { #PH (GH2)
        Name => 'IntelligentD-Range',
        Writable => 'int16u',
        PrintConv => {
            0 => 'Off',
            1 => 'Low',
            2 => 'Standard',
            3 => 'High',
        },
    },
    # 0x7a,0x7b: 0
    0x7c => { #18
        Name => 'ClearRetouch',
        Writable => 'int16u',
        PrintConv => { 0 => 'Off', 1 => 'On' },
    },
    0x80 => { #forum5997 (seen garbage here for SZ5 - PH)
        Name => 'City2', # (City/Town/Village)
        Groups => { 2 => 'Location' },
        Format => 'string',
        Writable => 'undef', # (Count 72)
        Notes => 'City/Town/Village as stored by some models',
    },
    # 0x81 - undef[72]: "---"
    # 0x82 - undef[72]: "---"
    # 0x83 - undef[72]: "---"
    # 0x84 - undef[72]: "---"
    # 0x85 - undef[128]: "---"
    0x86 => { #http://dev.exiv2.org/issues/825
        Name => 'ManometerPressure',
        Writable => 'int16u',
        RawConv => '$val==65535 ? undef : $val',
        ValueConv => '$val / 10',
        ValueConvInv => '$val * 10',
        PrintConv => 'sprintf("%.1f kPa",$val)',
        PrintConvInv => '$val=~s/ ?kPa//i; $val',
    },
    0x89 => {
        Name => 'PhotoStyle',
        Writable => 'int16u',
        PrintConv => {
            0 => 'Auto',
            1 => 'Standard or Custom',
            2 => 'Vivid',
            3 => 'Natural',
            4 => 'Monochrome',
            5 => 'Scenery',
            6 => 'Portrait',
        },
    },
    0x8a => { #18
        Name => 'ShadingCompensation',
        Writable => 'int16u',
        PrintConv => {
            0 => 'Off',
            1 => 'On'
        }
    },
    0x8c => {
        Name => 'AccelerometerZ',
        Writable => 'int16u',
        Format => 'int16s',
        Notes => 'positive is acceleration upwards',
    },
    0x8d => {
        Name => 'AccelerometerX',
        Writable => 'int16u',
        Format => 'int16s',
        Notes => 'positive is acceleration to the left',
    },
    0x8e => {
        Name => 'AccelerometerY',
        Writable => 'int16u',
        Format => 'int16s',
        Notes => 'positive is acceleration backwards',
    },
    0x8f => { #18
        Name => 'CameraOrientation',
        Writable => 'int8u',
        PrintConv => {
            0 => 'Normal',
            1 => 'Rotate CW',
            2 => 'Rotate 180',
            3 => 'Rotate CCW',
            4 => 'Tilt Upwards',
            5 => 'Tilt Downwards'
        }
    },
    0x90 => {
        Name => 'RollAngle',
        Writable => 'int16u',
        Format => 'int16s',
        Notes => 'converted to degrees of clockwise camera rotation',
        ValueConv => '$val / 10',
        ValueConvInv => '$val * 10',
    },
    0x91 => {
        Name => 'PitchAngle',
        Writable => 'int16u',
        Format => 'int16s',
        Notes => 'converted to degrees of upward camera tilt',
        ValueConv => '-$val / 10',
        ValueConvInv => '-$val * 10',
    },
    0x93 => { #18
        Name => 'SweepPanoramaDirection',
        Writable => 'int8u',
        PrintConv => {
            0 => 'Off',
            1 => 'Left to Right',
            2 => 'Right to Left',
            3 => 'Top to Bottom',
            4 => 'Bottom to Top'
        }
    },
    0x94 => { #18
        Name => 'SweepPanoramaFieldOfView',
        Writable => 'int16u'
    },
    0x96 => { #18
        Name => 'TimerRecording',
        Writable => 'int8u',
        PrintConv => {
            0 => 'Off',
            1 => 'Time Lapse',
            2 => 'Stop-motion Animation',
        },
    },
    0x9d => { #18
        Name => 'InternalNDFilter',
        Writable => 'rational64u'
    },
    0x9e => { #18
        Name => 'HDR',
        Writable => 'int16u',
        PrintConv => {
            0 => 'Off',
            100 => '1 EV',
            200 => '2 EV',
            300 => '3 EV',
            32868 => '1 EV (Auto)',
            32968 => '2 EV (Auto)',
            33068 => '3 EV (Auto)',
        },
    },
    0x9f => { #18
        Name => 'ShutterType',
        Writable => 'int16u',
        PrintConv => {
            0 => 'Mechanical',
            1 => 'Electronic',
            2 => 'Hybrid', #PH (GM1, 1st curtain electronic, 2nd curtain mechanical)
        },
    },
    0xa3 => { #18
        Name => 'ClearRetouchValue',
        Writable => 'rational64u',
        # undef if ClearRetouch is off, 0 if it is on
    },
    0xab => { #18
        Name => 'TouchAE',
        Writable => 'int16u',
        PrintConv => { 0 => 'Off', 1 => 'On' },
    },
    0xaf => { #PH
        Name => 'TimeStamp',
        Writable => 'string',
        Groups => { 2 => 'Time' },
        Shift => 'Time',
        PrintConv => '$self->ConvertDateTime($val)',
        PrintConvInv => '$self->InverseDateTime($val)',
    },
    0x0e00 => {
        Name => 'PrintIM',
        Description => 'Print Image Matching',
        Writable => 0,
        SubDirectory => {
            TagTable => 'Image::ExifTool::PrintIM::Main',
        },
    },
    0x8000 => { #PH
        Name => 'MakerNoteVersion',
        Format => 'undef',
    },
    0x8001 => { #7/PH/JD
        Name => 'SceneMode',
        Writable => 'int16u',
        PrintConvColumns => 2,
        PrintConv => {
            0  => 'Off',
            %shootingMode,
        },
    },
    # 0x8002 - values: 1,2 related to focus? (PH/JD)
    #          1 for HDR modes, 2 for Portrait (ref 12)
    # 0x8003 - values: 1,2 related to focus? (PH/JD)
    0x8004 => { #PH/JD
        Name => 'WBRedLevel',
        Writable => 'int16u',
    },
    0x8005 => { #PH/JD
        Name => 'WBGreenLevel',
        Writable => 'int16u',
    },
    0x8006 => { #PH/JD
        Name => 'WBBlueLevel',
        Writable => 'int16u',
    },
    0x8007 => { #PH
        Name => 'FlashFired',
        Writable => 'int16u',
        PrintConv => { 1 => 'No', 2 => 'Yes' },
    },
    0x8008 => { #PH (TZ5/FS7)
        # (tags 0x3b, 0x3e, 0x8008 and 0x8009 have the same values in all my samples - PH)
        Name => 'TextStamp',
        Writable => 'int16u',
        PrintConv => { 1 => 'Off', 2 => 'On' },
    },
    0x8009 => { #PH (TZ5/FS7)
        # (tags 0x3b, 0x3e, 0x8008 and 0x8009 have the same values in all my samples - PH)
        Name => 'TextStamp',
        Writable => 'int16u',
        PrintConv => { 1 => 'Off', 2 => 'On' },
    },
    0x8010 => { #PH
        Name => 'BabyAge',
        Writable => 'string',
        Notes => 'or pet age',
        PrintConv => '$val eq "9999:99:99 00:00:00" ? "(not set)" : $val',
        PrintConvInv => '$val =~ /^\d/ ? $val : "9999:99:99 00:00:00"',
    },
    0x8012 => { #PH (FS7)
        Name => 'Transform',
        Writable => 'undef',
        Notes => 'decoded as two 16-bit signed integers',
        Format => 'int16s',
        Count => 2,
        PrintConv => {
            '-3 2' => 'Slim High',
            '-1 1' => 'Slim Low',
            '0 0' => 'Off',
            '1 1' => 'Stretch Low',
            '3 2' => 'Stretch High',
        },
    },
);

# Leica type2 maker notes (ref 10)
%Image::ExifTool::Panasonic::Leica2 = (
    WRITE_PROC => \&Image::ExifTool::Exif::WriteExif,
    CHECK_PROC => \&Image::ExifTool::Exif::CheckExif,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    WRITABLE => 1,
    NOTES => 'These tags are used by the Leica M8.',
    0x300 => {
        Name => 'Quality',
        Writable => 'int16u',
        PrintConv => {
            1 => 'Fine',
            2 => 'Basic',
        },
    },
    0x302 => {
        Name => 'UserProfile',
        Writable => 'int32u',
        PrintConv => {
            1 => 'User Profile 1',
            2 => 'User Profile 2',
            3 => 'User Profile 3',
            4 => 'User Profile 0 (Dynamic)',
        },
    },
    0x303 => {
        Name => 'SerialNumber',
        Writable => 'int32u',
        PrintConv => 'sprintf("%.7d", $val)',
        PrintConvInv => '$val',
    },
    0x304 => {
        Name => 'WhiteBalance',
        Writable => 'int16u',
        Notes => 'values above 0x8000 are converted to Kelvin color temperatures',
        PrintConv => {
            0 => 'Auto or Manual',
            1 => 'Daylight',
            2 => 'Fluorescent',
            3 => 'Tungsten',
            4 => 'Flash',
            10 => 'Cloudy',
            11 => 'Shade',
            OTHER => \&WhiteBalanceConv,
        },
    },
    0x310 => {
        Name => 'LensType',
        Writable => 'int32u',
        SeparateTable => 1,
        ValueConv => '($val >> 2) . " " . ($val & 0x3)',
        ValueConvInv => \&LensTypeConvInv,
        PrintConv => \%leicaLensTypes,
    },
    0x311 => {
        Name => 'ExternalSensorBrightnessValue',
        Format => 'rational64s', # (incorrectly unsigned in JPEG images)
        Writable => 'rational64s',
        Notes => '"blue dot" measurement',
        PrintConv => 'sprintf("%.2f", $val)',
        PrintConvInv => '$val',
    },
    0x312 => {
        Name => 'MeasuredLV',
        Format => 'rational64s', # (incorrectly unsigned in JPEG images)
        Writable => 'rational64s',
        Notes => 'imaging sensor or TTL exposure meter measurement',
        PrintConv => 'sprintf("%.2f", $val)',
        PrintConvInv => '$val',
    },
    0x313 => {
        Name => 'ApproximateFNumber',
        Writable => 'rational64u',
        PrintConv => 'sprintf("%.1f", $val)',
        PrintConvInv => '$val',
    },
    0x320 => {
        Name => 'CameraTemperature',
        Writable => 'int32s',
        PrintConv => '"$val C"',
        PrintConvInv => '$val=~s/ ?C//; $val',
    },
    0x321 => { Name => 'ColorTemperature',  Writable => 'int32u' },
    0x322 => { Name => 'WBRedLevel',        Writable => 'rational64u' },
    0x323 => { Name => 'WBGreenLevel',      Writable => 'rational64u' },
    0x324 => { Name => 'WBBlueLevel',       Writable => 'rational64u' },
    0x325 => {
        Name => 'UV-IRFilterCorrection',
        Description => 'UV/IR Filter Correction',
        Writable => 'int32u',
        PrintConv => {
            0 => 'Not Active',
            1 => 'Active',
        },
    },
    0x330 => { Name => 'CCDVersion',        Writable => 'int32u' },
    0x331 => { Name => 'CCDBoardVersion',   Writable => 'int32u' },
    0x332 => { Name => 'ControllerBoardVersion', Writable => 'int32u' },
    0x333 => { Name => 'M16CVersion',       Writable => 'int32u' },
    0x340 => { Name => 'ImageIDNumber',     Writable => 'int32u' },
);

# Leica type3 maker notes (ref PH)
%Image::ExifTool::Panasonic::Leica3 = (
    WRITE_PROC => \&Image::ExifTool::Exif::WriteExif,
    CHECK_PROC => \&Image::ExifTool::Exif::CheckExif,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    WRITABLE => 1,
    NOTES => 'These tags are used by the Leica R8 and R9 digital backs.',
    0x0d => {
        Name => 'WB_RGBLevels',
        Writable => 'int16u',
        Count => 3,
    },
);

# Leica type4 maker notes (ref PH) (M9)
%Image::ExifTool::Panasonic::Leica4 = (
    WRITE_PROC => \&Image::ExifTool::Exif::WriteExif,
    CHECK_PROC => \&Image::ExifTool::Exif::CheckExif,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    WRITABLE => 1,
    NOTES => 'This information is written by the M9.',
    0x3000 => {
        Name => 'Subdir3000',
        SubDirectory => {
            TagTable => 'Image::ExifTool::Panasonic::Subdir',
            ByteOrder => 'Unknown',
        },
    },
    0x3100 => {
        Name => 'Subdir3100',
        SubDirectory => {
            TagTable => 'Image::ExifTool::Panasonic::Subdir',
            ByteOrder => 'Unknown',
        },
    },
    0x3400 => {
        Name => 'Subdir3400',
        SubDirectory => {
            TagTable => 'Image::ExifTool::Panasonic::Subdir',
            ByteOrder => 'Unknown',
        },
    },
    0x3900 => {
        Name => 'Subdir3900',
        SubDirectory => {
            TagTable => 'Image::ExifTool::Panasonic::Subdir',
            ByteOrder => 'Unknown',
        },
    },
);

# Leica M9 SubDirectory tags (ref PH)
%Image::ExifTool::Panasonic::Subdir = (
    WRITE_PROC => \&Image::ExifTool::Exif::WriteExif,
    CHECK_PROC => \&Image::ExifTool::Exif::CheckExif,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    TAG_PREFIX => 'Leica_Subdir',
    WRITABLE => 1,
    # 0x3001 - normally 0 but value of 2 when manual coding is used
    #          with a coded lens (but only tested with Elmar-M 50mm f/2.8) - PH
    0x300a => {
        Name => 'Contrast',
        Writable => 'int32u',
        PrintConv => {
            0 => 'Low',
            1 => 'Medium Low',
            2 => 'Normal',
            3 => 'Medium High',
            4 => 'High',
        },
    },
    0x300b => {
        Name => 'Sharpening',
        Writable => 'int32u',
        PrintConv => {
            0 => 'Off',
            1 => 'Low',
            2 => 'Normal',
            3 => 'Medium High',
            4 => 'High',
        },
    },
    0x300d => {
        Name => 'Saturation',
        Writable => 'int32u',
        PrintConv => {
            0 => 'Low',
            1 => 'Medium Low',
            2 => 'Normal',
            3 => 'Medium High',
            4 => 'High',
            5 => 'Black & White',
            6 => 'Vintage B&W',
        },
    },
    # 0x3032 - some sort of RGB coefficients? (zeros unless Kelvin WB, but same for all Color Temps)
    0x3033 => {
        Name => 'WhiteBalance',
        Writable => 'int32u',
        PrintConv => { #13
            0 => 'Auto',
            1 => 'Tungsten',
            2 => 'Fluorescent',
            3 => 'Daylight Fluorescent',
            4 => 'Daylight',
            5 => 'Flash',
            6 => 'Cloudy',
            7 => 'Shade',
            8 => 'Manual',
            9 => 'Kelvin',
        },
    },
    0x3034 => {
        Name => 'JPEGQuality',
        Writable => 'int32u',
        PrintConv => {
            94 => 'Basic',
            97 => 'Fine',
        },
    },
    # 0x3035 (int32u): -1 unless Manual WB (2 in my Manual sample)
    0x3036 => {
        Name => 'WB_RGBLevels',
        Writable => 'rational64u',
        Count => 3,
    },
    0x3038 => {
        Name => 'UserProfile', # (CameraProfile according to ref 14)
        Writable => 'string',
    },
    0x303a => {
        Name => 'JPEGSize',
        Writable => 'int32u',
        PrintConv => {
            0 => '5216x3472',
            1 => '3840x2592',
            2 => '2592x1728',
            3 => '1728x1152',
            4 => '1280x864',
        },
    },
    0x3103 => { #13 (valid for FW 1.116 and later)
        Name => 'SerialNumber',
        Writable => 'string',
    },
    # 0x3104 body-dependent string ("00012905000000") (not serial number)
    # 0x3105 body-dependent string ("00012905000000")
    # 0x3107 - body-dependent string ("4H205800116800") (not serial number)
    0x3109 => {
        Name => 'FirmwareVersion',
        Writable => 'string',
    },
    0x312a => { #14 (NC)
        Name => 'BaseISO',
        Writable => 'int32u',
    },
    0x312b => {
        Name => 'SensorWidth',
        Writable => 'int32u',
    },
    0x312c => {
        Name => 'SensorHeight',
        Writable => 'int32u',
    },
    0x312d => { #14 (NC)
        Name => 'SensorBitDepth',
        Writable => 'int32u',
    },
    0x3402 => { #PH/13
        Name => 'CameraTemperature',
        Writable => 'int32s',
        PrintConv => '"$val C"',
        PrintConvInv => '$val=~s/ ?C//; $val',
    },
    0x3405 => {
        Name => 'LensType',
        Writable => 'int32u',
        SeparateTable => 1,
        ValueConv => '($val >> 2) . " " . ($val & 0x3)',
        ValueConvInv => \&LensTypeConvInv,
        PrintConv => \%leicaLensTypes,
    },
    0x3406 => { #PH/13
        Name => 'ApproximateFNumber',
        Writable => 'rational64u',
        PrintConv => 'sprintf("%.1f", $val)',
        PrintConvInv => '$val',
    },
    0x3407 => { #14
        Name => 'MeasuredLV',
        Writable => 'int32s',
        Notes => 'imaging sensor or TTL exposure meter measurement',
        ValueConv => '$val / 1e5', #PH (NC)
        ValueConvInv => '$val * 1e5', #PH (NC)
        PrintConv => 'sprintf("%.2f", $val)',
        PrintConvInv => '$val',
    },
    0x3408 => { #14
        Name => 'ExternalSensorBrightnessValue',
        Writable => 'int32s',
        Notes => '"blue dot" measurement',
        ValueConv => '$val / 1e5', #PH (NC)
        ValueConvInv => '$val * 1e5', #PH (NC)
        PrintConv => 'sprintf("%.2f", $val)',
        PrintConvInv => '$val',
    },
    0x3901 => {
        Name => 'Data1',
        SubDirectory => { TagTable => 'Image::ExifTool::Panasonic::Data1' },
    },
    0x3902 => {
        Name => 'Data2',
        SubDirectory => { TagTable => 'Image::ExifTool::Panasonic::Data2' },
    },
    # 0x3903 - larger binary data block
);

%Image::ExifTool::Panasonic::Data1 = (
    PROCESS_PROC => \&Image::ExifTool::ProcessBinaryData,
    WRITE_PROC => \&Image::ExifTool::WriteBinaryData,
    CHECK_PROC => \&Image::ExifTool::CheckBinaryData,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    WRITABLE => 1,
    TAG_PREFIX => 'Leica_Data1',
    FIRST_ENTRY => 0,
    0x0016 => {
        Name => 'LensType',
        Writable => 'int32u',
        Priority => 0,
        SeparateTable => 1,
        ValueConv => '($val >> 2) . " " . ($val & 0x3)',
        ValueConvInv => \&LensTypeConvInv,
        PrintConv => \%leicaLensTypes,
    },
);

%Image::ExifTool::Panasonic::Data2 = (
    PROCESS_PROC => \&Image::ExifTool::ProcessBinaryData,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    TAG_PREFIX => 'Leica_Data2',
    FIRST_ENTRY => 0,
);

# Leica type5 maker notes (ref PH) (X1)
%Image::ExifTool::Panasonic::Leica5 = (
    WRITE_PROC => \&Image::ExifTool::Exif::WriteExif,
    CHECK_PROC => \&Image::ExifTool::Exif::CheckExif,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    WRITABLE => 1,
    PRIORITY => 0,
    NOTES => 'This information is written by the X1, X2, X VARIO and T.',
    0x0303 => {
        Name => 'LensModel',
        Condition => '$format eq "string"',
        Notes => 'Leica T only',
        Writable => 'string',
    },
    # 0x0406 - saturation or sharpness
    0x0407 => { Name => 'OriginalFileName', Writable => 'string' },
    0x0408 => { Name => 'OriginalDirectory',Writable => 'string' },
    # 0x040b - related to white balance
    0x040d => {
        Name => 'ExposureMode',
        Format => 'int8u',
        Count => 4,
        PrintConv => {
            '0 0 0 0' => 'Program AE',
          # '0 1 0 0' - seen for X (Typ 113) - PH
            '1 0 0 0' => 'Aperture-priority AE',
            '1 1 0 0' => 'Aperture-priority AE (1)', # (see for Leica T)
            '2 0 0 0' => 'Shutter speed priority AE', #(guess)
            '3 0 0 0' => 'Manual',
        },
    },
    0x0410 => {
        Name => 'ShotInfo',
        SubDirectory => { TagTable => 'Image::ExifTool::Panasonic::ShotInfo' },
    },
    # 0x0410 - int8u[16]: first byte is FileNumber
    # 0x0411 - int8u[4]: first number is FilmMode (1=Standard,2=Vivid,3=Natural,4=BW Natural,5=BW High Contrast)
    0x0412 => { Name => 'FilmMode',         Writable => 'string' },
    0x0413 => { Name => 'WB_RGBLevels',     Writable => 'rational64u', Count => 3 },
);

# Leica type5 ShotInfo (ref PH) (X2)
%Image::ExifTool::Panasonic::ShotInfo = (
    PROCESS_PROC => \&Image::ExifTool::ProcessBinaryData,
    WRITE_PROC => \&Image::ExifTool::WriteBinaryData,
    CHECK_PROC => \&Image::ExifTool::CheckBinaryData,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    TAG_PREFIX => 'Leica_ShotInfo',
    FIRST_ENTRY => 0,
    WRITABLE => 1,
    0 => {
        Name => 'FileIndex',
        Format => 'int16u',
    },
);

# Leica type6 maker notes (ref PH) (S2)
%Image::ExifTool::Panasonic::Leica6 = (
    WRITE_PROC => \&Image::ExifTool::Exif::WriteExif,
    CHECK_PROC => \&Image::ExifTool::Exif::CheckExif,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    NOTES => q{
        This information is written by the S2 and M (Typ 240), as a trailer in JPEG
        images.
    },
    0x300 => {
        Name => 'PreviewImage',
        Groups => { 2 => 'Preview' },
        Writable => 'undef',
        Notes => 'S2 and M (Typ 240)',
        DataTag => 'PreviewImage',
        RawConv => q{
            return \$val if $val =~ /^Binary/;
            return \$val if $val =~ /^\xff\xd8\xff/;
            $$self{PreviewError} = 1 unless $val eq 'none';
            return undef;
        },
        ValueConvInv => '$val || "none"',
        WriteCheck => 'return $val=~/^(none|\xff\xd8\xff)/s ? undef : "Not a valid image"',
        ChangeBase => '$dirStart + $dataPos - 8',
    },
    0x301 => {
        Name => 'UnknownBlock',
        Notes => 'unknown 320kB block, not copied to JPEG images',
        Flags => [ 'Unknown', 'Binary', 'Drop' ],
    },
    # 0x302 - same value as 4 unknown bytes at the end of JPEG or after the DNG TIFF header
    0x303 => {
        Name => 'LensType',
        Writable => 'string',
        ValueConv => '$val=~s/ +$//; $val', # trim trailing spaces
        ValueConvInv => '$val',
    },
    # 0x340 - same as 0x302
);

# Leica type9 maker notes (ref PH) (S)
%Image::ExifTool::Panasonic::Leica9 = (
    WRITE_PROC => \&Image::ExifTool::Exif::WriteExif,
    CHECK_PROC => \&Image::ExifTool::Exif::CheckExif,
    GROUPS => { 0 => 'MakerNotes', 1 => 'Leica', 2 => 'Camera' },
    NOTES => 'This information is written by the Leica S (Typ 007).',
);

# Type 2 tags (ref PH)
%Image::ExifTool::Panasonic::Type2 = (
    PROCESS_PROC => \&Image::ExifTool::ProcessBinaryData,
    GROUPS => { 0 => 'MakerNotes', 2 => 'Image' },
    FIRST_ENTRY => 0,
    FORMAT => 'int16u',
    NOTES => q{
        This type of maker notes is used by models such as the NV-DS65, PV-D2002,
        PV-DC3000, PV-DV203, PV-DV401, PV-DV702, PV-L2001, PV-SD4090, PV-SD5000 and
        iPalm.
    },
    0 => {
        Name => 'MakerNoteType',
        Format => 'string[4]',
    },
    # seems to vary inversely with amount of light, so I'll call it 'Gain' - PH
    # (minimum is 16, maximum is 136.  Value is 0 for pictures captured from video)
    3 => 'Gain',
);

# Face detection position information (ref PH)
%Image::ExifTool::Panasonic::FaceDetInfo = (
    PROCESS_PROC => \&Image::ExifTool::ProcessBinaryData,
    WRITE_PROC => \&Image::ExifTool::WriteBinaryData,
    CHECK_PROC => \&Image::ExifTool::CheckBinaryData,
    GROUPS => { 0 => 'MakerNotes', 2 => 'Image' },
    WRITABLE => 1,
    FORMAT => 'int16u',
    FIRST_ENTRY => 0,
    DATAMEMBER => [ 0 ],
    NOTES => 'Face detection position information.',
    0 => {
        Name => 'NumFacePositions',
        Format => 'int16u',
        DataMember => 'NumFacePositions',
        RawConv => '$$self{NumFacePositions} = $val',
        Notes => q{
            number of detected face positions stored in this record.  May be less than
            FacesDetected
        },
    },
    1 => {
        Name => 'Face1Position',
        Format => 'int16u[4]',
        RawConv => '$$self{NumFacePositions} < 1 ? undef : $val',
        Notes => q{
            4 numbers: X/Y coordinates of the face center and width/height of face. 
            Coordinates are relative to an image twice the size of the thumbnail, or 320
            pixels wide
        },
    },
    5 => {
        Name => 'Face2Position',
        Format => 'int16u[4]',
        RawConv => '$$self{NumFacePositions} < 2 ? undef : $val',
    },
    9 => {
        Name => 'Face3Position',
        Format => 'int16u[4]',
        RawConv => '$$self{NumFacePositions} < 3 ? undef : $val',
    },
    13 => {
        Name => 'Face4Position',
        Format => 'int16u[4]',
        RawConv => '$$self{NumFacePositions} < 4 ? undef : $val',
    },
    17 => {
        Name => 'Face5Position',
        Format => 'int16u[4]',
        RawConv => '$$self{NumFacePositions} < 5 ? undef : $val',
    },
);

# Face recognition information from DMC-TZ7 (ref PH)
%Image::ExifTool::Panasonic::FaceRecInfo = (
    PROCESS_PROC => \&Image::ExifTool::ProcessBinaryData,
    WRITE_PROC => \&Image::ExifTool::WriteBinaryData,
    CHECK_PROC => \&Image::ExifTool::CheckBinaryData,
    GROUPS => { 0 => 'MakerNotes', 2 => 'Image' },
    WRITABLE => 1,
    FIRST_ENTRY => 0,
    DATAMEMBER => [ 0 ],
    NOTES => q{
        Tags written by cameras with facial recognition.  These cameras not only
        detect faces in an image, but also recognize specific people based a
        user-supplied set of known faces.
    },
    0 => {
        Name => 'FacesRecognized',
        Format => 'int16u',
        DataMember => 'FacesRecognized',
        RawConv => '$$self{FacesRecognized} = $val',
    },
    4 => {
        Name => 'RecognizedFace1Name',
        Format => 'string[20]',
        RawConv => '$$self{FacesRecognized} < 1 ? undef : $val',
    },
    24 => {
        Name => 'RecognizedFace1Position',
        Format => 'int16u[4]',
        RawConv => '$$self{FacesRecognized} < 1 ? undef : $val',
        Notes => 'coordinates in same format as face detection tags above',
    },
    32 => {
        Name => 'RecognizedFace1Age',
        Format => 'string[20]',
        RawConv => '$$self{FacesRecognized} < 1 ? undef : $val',
    },
    52 => {
        Name => 'RecognizedFace2Name',
        Format => 'string[20]',
        RawConv => '$$self{FacesRecognized} < 2 ? undef : $val',
    },
    72 => {
        Name => 'RecognizedFace2Position',
        Format => 'int16u[4]',
        RawConv => '$$self{FacesRecognized} < 2 ? undef : $val',
    },
    80 => {
        Name => 'RecognizedFace2Age',
        Format => 'string[20]',
        RawConv => '$$self{FacesRecognized} < 2 ? undef : $val',
    },
    100 => {
        Name => 'RecognizedFace3Name',
        Format => 'string[20]',
        RawConv => '$$self{FacesRecognized} < 3 ? undef : $val',
    },
    120 => {
        Name => 'RecognizedFace3Position',
        Format => 'int16u[4]',
        RawConv => '$$self{FacesRecognized} < 3 ? undef : $val',
    },
    128 => {
        Name => 'RecognizedFace3Age',
        Format => 'string[20]',
        RawConv => '$$self{FacesRecognized} < 3 ? undef : $val',
    },
);

# PANA atom found in user data of MP4 videos (ref PH)
%Image::ExifTool::Panasonic::PANA = (
    PROCESS_PROC => \&Image::ExifTool::ProcessBinaryData,
    GROUPS => { 0 => 'MakerNotes', 2 => 'Image' },
    NOTES => q{
        Tags extracted from the PANA and LEIC user data found in MP4 videos from
        various Panasonic and Leica models.
    },
    0x00 => {
        Name => 'Make',
        Condition => '$$valPt =~ /^(LEICA|Panasonic)/', # (only seen "LEICA")
        Groups => { 2 => 'Camera' },
        Format => 'string[22]',
        RawConv => '$$self{LeicaLEIC} = 1;$$self{Make} = $val',
    },
    0x04 => {
        Name => 'Model',
        Condition => '$$valPt =~ /^[^\0]{6}/ and not $$self{LeicaLEIC}',
        Description => 'Camera Model Name',
        Groups => { 2 => 'Camera' },
        Format => 'string[16]',
        RawConv => '$$self{Model} = $val',
    },
    0x0c => { # (FZ1000)
        Name => 'Model',
        Condition => '$$valPt =~ /^[^\0]{6}/ and not $$self{LeicaLEIC} and not $$self{Model}',
        Description => 'Camera Model Name',
        Groups => { 2 => 'Camera' },
        Format => 'string[16]',
        RawConv => '$$self{Model} = $val',
    },
    0x16 => {
        Name => 'Model',
        Condition => '$$self{LeicaLEIC}',
        Description => 'Camera Model Name',
        Groups => { 2 => 'Camera' },
        Format => 'string[30]',
        RawConv => '$$self{Model} = $val',
    },
    0x40 => {
        Name => 'ThumbnailTest',
        Format => 'undef[0x600]',
        Hidden => 1,
        RawConv => q{
            if (substr($val,0x1c,3) eq "\xff\xd8\xff") { # offset 0x5c
                $$self{ThumbType} = 1;
            } elsif (substr($val,0x506,3) eq "\xff\xd8\xff") { # offset 0x546
                $$self{ThumbType} = 2;
            } elsif (substr($val,0x51e,3) eq "\xff\xd8\xff") { # offset 0x55e (Leica T)
                $$self{ThumbType} = 3;
            } else {
                $$self{ThumbType} = 0;
            }
            return undef;
        },
    },
    0x34 => {
        Name => 'Version1',
        Condition => '$$self{LeicaLEIC}',
        Format => 'string[14]',
    },
    0x3e => {
        Name => 'Version2',
        Condition => '$$self{LeicaLEIC}',
        Format => 'string[14]',
    },
    0x50 => {
        Name => 'MakerNoteLeica5',
        Condition => '$$self{LeicaLEIC}',
        SubDirectory => {
            TagTable => 'Image::ExifTool::Panasonic::Leica5',
            ProcessProc => \&ProcessLeicaLEIC,
        },
    },
    0x58 => {
        Name => 'ThumbnailWidth',
        Condition => '$$self{ThumbType} == 1',
        Notes => 'Panasonic models',
        Format => 'int16u',
    },
    0x5a => {
        Name => 'ThumbnailHeight',
        Condition => '$$self{ThumbType} == 1',
        Format => 'int16u',
    },
    0x5c => {
        Name => 'ThumbnailImage',
        Condition => '$$self{ThumbType} == 1',
        Groups => { 2 => 'Preview' },
        Format => 'undef[16384]',
        ValueConv => '$val=~s/\0*$//; \$val',   # remove trailing zeros
    },
    # 0x5c - there is some messed-up EXIF-IFD-looking data starting here in
    #        Leica X VARIO MP4 videos, but it doesn't quite make sense
    0x536 => { # (Leica X VARIO)
        Name => 'ThumbnailWidth',
        Condition => '$$self{ThumbType} == 2',
        Notes => 'Leica X Vario',
        Format => 'int32uRev', # (little-endian)
    },
    0x53a => { # (Leica X VARIO)
        Name => 'ThumbnailHeight',
        Condition => '$$self{ThumbType} == 2',
        Format => 'int32uRev', # (little-endian)
    },
    0x53e => { # (Leica X VARIO)
        Name => 'ThumbnailLength',
        Condition => '$$self{ThumbType} == 2',
        Format => 'int32uRev', # (little-endian)
    },
    0x546 => { # (Leica X VARIO)
        Name => 'ThumbnailImage',
        Condition => '$$self{ThumbType} == 2',
        Groups => { 2 => 'Preview' },
        Format => 'undef[$val{0x53e}]',
        Binary => 1,
    },
    0x54e => { # (Leica T)
        Name => 'ThumbnailWidth',
        Condition => '$$self{ThumbType} == 3',
        Notes => 'Leica X Vario',
        Format => 'int32uRev', # (little-endian)
    },
    0x552 => { # (Leica T)
        Name => 'ThumbnailHeight',
        Condition => '$$self{ThumbType} == 3',
        Format => 'int32uRev', # (little-endian)
    },
    0x556 => { # (Leica T)
        Name => 'ThumbnailLength',
        Condition => '$$self{ThumbType} == 3',
        Format => 'int32uRev', # (little-endian)
    },
    0x55e => { # (Leica T)
        Name => 'ThumbnailImage',
        Condition => '$$self{ThumbType} == 3',
        Groups => { 2 => 'Preview' },
        Format => 'undef[$val{0x556}]',
        Binary => 1,
    },
    0x4068 => {
        Name => 'ExifData',
        Condition => '$$valPt =~ /^\xff\xd8\xff\xe1..Exif\0\0/s',
        SubDirectory => {
            TagTable => 'Image::ExifTool::Exif::Main',
            ProcessProc => \&Image::ExifTool::ProcessTIFF,
            Start => 12,
        },
    },
    0x4080 => { # (FZ1000)
        Name => 'ExifData',
        Condition => '$$valPt =~ /^\xff\xd8\xff\xe1..Exif\0\0/s',
        SubDirectory => {
            TagTable => 'Image::ExifTool::Exif::Main',
            ProcessProc => \&Image::ExifTool::ProcessTIFF,
            Start => 12,
        },
    },
);

# Panasonic Composite tags
%Image::ExifTool::Panasonic::Composite = (
    GROUPS => { 2 => 'Camera' },
    AdvancedSceneMode => {
        SeparateTable => 'Panasonic AdvancedSceneMode',    # print values in a separate table
        Require => {
            0 => 'Model',
            1 => 'SceneMode',
            2 => 'AdvancedSceneType',
        },
        ValueConv => '"$val[0] $val[1] $val[2]"',
        PrintConv => { #PH
            OTHER => sub {
                my ($val,$flag,$conv) = @_;
                $val =~ s/.* (\d+ \d+)/$1/; # drop model name
                return $$conv{$val} if $$conv{$val};
                my @v = split ' ', $val;
                my $prt = $shootingMode{$v[0]};
                # AdvancedSceneType=1 for non-automatic modes P,A,S,SCN (ref 19)
                # AdvancedSceneType=5 for automatic mode iA (ref 19)
                if ($prt) {
                    return $prt if $v[1] == 1;
                    return "$prt (intelligent auto)" if $v[1] == 5;
                    return "$prt ($v[1])";
                }
                return "Unknown ($val)";
            },
            Notes => 'A Composite tag derived from Model, SceneMode and AdvancedSceneType.',
            '0 1' => 'Off',
            # '0 7' - seen this for V-LUX movies (PH)
            # '0 8' - seen for D-LUX(Typ104) movies (PH)
            '2 2' => 'Outdoor Portrait', #(FZ28)
            '2 3' => 'Indoor Portrait', #(FZ28)
            '2 4' => 'Creative Portrait', #(FZ28)
            '3 2' => 'Nature', #(FZ28)
            '3 3' => 'Architecture', #(FZ28)
            '3 4' => 'Creative Scenery', #(FZ28)
            #'3 5' - ? (FT1)
            '4 2' => 'Outdoor Sports', #(FZ28)
            '4 3' => 'Indoor Sports', #(FZ28)
            '4 4' => 'Creative Sports', #(FZ28)
            '9 2' => 'Flower', #(FZ28)
            '9 3' => 'Objects', #(FZ28)
            '9 4' => 'Creative Macro', #(FZ28)
            #'9 5' - ? (GF3)
            '21 2' => 'Illuminations', #(FZ28)
            '21 4' => 'Creative Night Scenery', #(FZ28)
            #'21 5' - ? (LX3)
            #'37 5' - ? (various)
            '45 2' => 'Cinema', #(GF2)
            '45 7' => 'Expressive', #(GF1,GF2)
            '45 8' => 'Retro', #(GF1,GF2)
            '45 9' => 'Pure', #(GF1,GF2)
            '45 10' => 'Elegant', #(GF1,GF2)
            '45 12' => 'Monochrome', #(GF1,GF2)
            '45 13' => 'Dynamic Art', #(GF1,GF2)
            '45 14' => 'Silhouette', #(GF1,GF2)
            '51 2' => 'HDR Art', #12
            '51 3' => 'HDR B&W', #12
            '59 1' => 'Expressive', #(GF5)
            '59 2' => 'Retro', #(GF5)
            '59 3' => 'High Key', #(GF5)
            '59 4' => 'Sepia', #(GF3,GF5)
            '59 5' => 'High Dynamic', #(GF3,GF5)
            '59 6' => 'Miniature', #(GF3)
            '59 9' => 'Low Key', #(GF5)
            '59 10' => 'Toy Effect', #(GF5)
            '59 11' => 'Dynamic Monochrome', #(GF5)
            '59 12' => 'Soft', #(GF5)
            '66 1' => 'Impressive Art', #19
            '66 2' => 'Cross Process', #(GF5)
            '66 3' => 'Color Select', #(GF5) (called "One Point Color" by some other models - PH)
            '66 4' => 'Star', #(GF5)
            '90 3' => 'Old Days', #18
            '90 4' => 'Sunshine', #18
            '90 5' => 'Bleach Bypass', #18
            '90 6' => 'Toy Pop', #18
            '90 7' => 'Fantasy', #18
            '90 8' => 'Monochrome', #PH (GX7)
            '90 9' => 'Rough Monochrome', #PH (GX7)
            '90 10' => 'Silky Monochrome', #PH (GX7)
            '92 1' => 'Handheld Night Shot', #Horst Wandres (FZ1000)
            # TZ40 Creative Control modes (ref 19)
            'DMC-TZ40 90 1' => 'Expressive',
            'DMC-TZ40 90 2' => 'Retro',
            'DMC-TZ40 90 3' => 'High Key',
            'DMC-TZ40 90 4' => 'Sepia',
            'DMC-TZ40 90 5' => 'High Dynamic',
            'DMC-TZ40 90 6' => 'Miniature',
            'DMC-TZ40 90 9' => 'Low Key',
            'DMC-TZ40 90 10' => 'Toy Effect',
            'DMC-TZ40 90 11' => 'Dynamic Monochrome',
            'DMC-TZ40 90 12' => 'Soft',
        },
    },
);

# add our composite tags
Image::ExifTool::AddCompositeTags('Image::ExifTool::Panasonic');

#------------------------------------------------------------------------------
# Inverse conversion for Leica M9 lens codes
# Inputs: 0) value
# Returns: Converted value, or undef on error
sub LensTypeConvInv($)
{
    my $val = shift;
    if ($val =~ /^(\d+) (\d+)$/) {
        return ($1 << 2) + ($2 & 0x03);
    } elsif ($val =~ /^\d+$/) {
        my $bits = $frameSelectorBits{$val};
        return undef unless defined $bits;
        return ($val << 2) | $bits;
    } else {
        return undef;
    }
}

#------------------------------------------------------------------------------
# Convert Leica Kelvin white balance
# Inputs: 0) value, 1) flag to perform inverse conversion
# Returns: Converted value, or undef on error
sub WhiteBalanceConv($;$$)
{
    my ($val, $inv) = @_;
    if ($inv) {
        return $1 + 0x8000 if $val =~ /(\d+)/;
    } else {
        return ($val - 0x8000) . ' Kelvin' if $val > 0x8000;
    }
    return undef;
}

#------------------------------------------------------------------------------
# Process Leica makernotes in LEIC atom of MP4 videos (Leica T and X Vario)
# Inputs: 0) ExifTool ref, 1) dirInfo ref, 2) tag table ref
# Returns: 1 on success
sub ProcessLeicaLEIC($$$)
{
    my ($et, $dirInfo, $tagTablePtr) = @_;
    my $dataPt = $$dirInfo{DataPt};
    my $dirStart = $$dirInfo{DirStart} || 0;
    my $dirLen = $$dirInfo{DirLen} || (length($$dataPt) - $dirStart);
    return 0 if $dirLen < 6;
    SetByteOrder('II');
    my $numEntries = Get16u($dataPt, $dirStart);
    return 0 if $numEntries < 1 or $numEntries > 255;
    my $size = Get32u($dataPt, $dirStart + 2);
    return 0 if $size < $numEntries * 12 or $size + 6 > $dirLen;
    # the Leica programmers want to make things difficult, so they store
    # the entry count before the directory size, making it impossible to
    # process as a standard TIFF IFD without a bit of reorganization...
    Set16u($numEntries, $dataPt, $dirStart + 4);
    my %dirInfo = %$dirInfo;
    $dirInfo{DirStart} = $dirStart + 4;
    $dirInfo{DirLen} = $size - 4;
    $dirInfo{DataPos} -= $dirStart;
    $dirInfo{Base} += $dirStart;
    return Image::ExifTool::Exif::ProcessExif($et, \%dirInfo, $tagTablePtr);
    return 1;
}

#------------------------------------------------------------------------------
# Process MakerNote trailer written by Leica S2
# Inputs: 0) ExifTool object ref, 1) new absolute position of Leica trailer when writing
# Returns: On success: 1 when reading, directory data when writing; othewise undef
# Notes:
# - may be called twice for a file if the first call doesn't succeed
# - must leave RAF position unchanged
# - uses information from LeicaTrailer member:
#      TagInfo = tag info ref for MakerNote SubDirectory
#      Offset/Size = value offset/size from MakerNote IFD
#      TrailStart/TrailLen = actual JPEG trailer position/size (2nd call only)
# - deletes LeicaTrailer member and sets LeicaTrailerPos when successful
sub ProcessLeicaTrailer($;$)
{
    my ($et, $newPos) = @_;
    my $trail = $$et{LeicaTrailer};
    my $raf = $$et{RAF};
    my $trailPos = $$trail{TrailPos};
    my $pos = $trailPos || $$trail{Offset};
    my $len = $$trail{TrailLen} || $$trail{Size};
    my ($buff, $result, %tagPtr);

    delete $$et{LeicaTrailer} if $trailPos;   # done after this
    unless ($len > 0) {
        $et->Warn('Missing Leica MakerNote trailer', 1) if $trailPos;
        delete $$et{LeicaTrailer};
        return undef;
    }
    my $oldPos = $raf->Tell();
    my $ok = ($raf->Seek($pos, 0) and $raf->Read($buff, $len) == $len);
    $raf->Seek($oldPos, 0);
    unless ($ok) {
        $et->Warn('Error reading Leica MakerNote trailer', 1) if $trailPos;
        return undef;
    }
    # look for Leica MakerNote header (should be at start of
    # trailer, but allow up to 256 bytes of garbage just in case)
    if ($buff !~ /^(.{0,256})LEICA\0..../sg) {
        my $what = $trailPos ? 'trailer' : 'offset';
        $et->Warn("Invalid Leica MakerNote $what", 1);
        return undef;
    }
    my $junk = $1;
    my $start = pos($buff) - 10;
    if ($start and not $trailPos) {
        $et->Warn('Invalid Leica MakerNote offset', 1);
        return undef;
    }
#
# all checks passed -- go ahead and process the trailer now
#
    my $hdrLen = 8;
    my $dirStart = $start + $hdrLen;
    my $tagInfo = $$trail{TagInfo};
    if ($$et{HTML_DUMP}) {
        my $name = $$tagInfo{Name};
        $et->HDump($pos+$start, $len-$start, "$name value", 'Leica MakerNote trailer', 4);
        $et->HDump($pos+$start, $hdrLen, "MakerNotes header", $name);
    } elsif ($et->Options('Verbose')) {
        my $where = sprintf('at offset 0x%x', $pos);
        $et->VPrint(0, "Leica MakerNote trailer ($len bytes $where):\n");
    }
    # delete LeicaTrailer member so we don't try to process it again
    delete $$et{LeicaTrailer};
    $$et{LeicaTrailerPos} = $pos + $start;    # return actual start position of Leica trailer

    my $oldOrder = GetByteOrder();
    my $num = Get16u(\$buff, $dirStart);            # get entry count
    ToggleByteOrder() if ($num>>8) > ($num&0xff);   # set byte order

    # use specialized algorithm to automatically fix offsets
    my $valStart = $dirStart + 2 + 12 * $num + 4;
    my $fix = 0;
    if ($valStart < $len) {
        my $valBlock = Image::ExifTool::MakerNotes::GetValueBlocks(\$buff, $dirStart, \%tagPtr);
        # find the minimum offset (excluding the PreviewImage tag 0x300 and 0x301)
        my $minPtr;
        foreach (keys %tagPtr) {
            my $ptr = $tagPtr{$_};
            next if $_ == 0x300 or $_ == 0x301 or not $ptr or $ptr == 0xffffffff;
            $minPtr = $ptr if not defined $minPtr or $minPtr > $ptr;
        }
        if ($minPtr) {
            my $diff = $minPtr - ($valStart + $pos);
            pos($buff) = $valStart;
            my $expect;
            if ($$et{Model} eq 'S2') {
                # scan value data for the first non-zero byte
                if ($buff =~ /[^\0]/g) {
                    my $n = pos($buff) - 1 - $valStart; # number of zero bytes
                    # S2 writes 282 bytes of zeros, exiftool writes none
                    $expect = $n >= 282 ? 282 : 0;
                }
            } else { # M (Type 240)
                # scan for the lens type (M writes 114 bytes of garbage first)
                if ($buff =~ /\G.{114}([\x20-\x7f]*\0*)/sg and length($1) >= 50) {
                    $expect = 114;
                }
            }
            my $fixBase = $et->Options('FixBase');
            if (not defined $expect) {
                $et->Warn('Unrecognized Leica trailer structure');
            } elsif ($diff != $expect or defined $fixBase) {
                $fix = $expect - $diff;
                if (defined $fixBase) {
                    $fix = $fixBase if $fixBase ne '';
                    $et->Warn("Adjusted MakerNotes base by $fix",1);
                } else {
                    $et->Warn("Possibly incorrect maker notes offsets (fixed by $fix)",1);
                }
            }
        }
    }
    # generate dirInfo for Leica MakerNote directory
    my %dirInfo = (
        Name       => $$tagInfo{Name},
        Base       => $fix,
        DataPt     => \$buff,
        DataPos    => $pos - $fix,
        DataLen    => $len,
        DirStart   => $dirStart,
        DirLen     => $len - $dirStart,
        DirName    => 'MakerNotes',
        Parent     => 'ExifIFD',
        TagInfo    => $tagInfo,
    );
    my $tagTablePtr = GetTagTable($$tagInfo{SubDirectory}{TagTable});
    if ($newPos) { # are we writing?
        if ($$et{Model} ne 'S2') {
            $et->Warn('Leica MakerNote trailer too messed up to edit.  Copying as a block', 1);
            return $buff;
        }
        # set position of new MakerNote IFD (+ 8 for Leica MakerNote header)
        $dirInfo{NewDataPos} = $newPos + $start + 8;
        $result = $et->WriteDirectory(\%dirInfo, $tagTablePtr);
        # write preview image last if necessary and fix up the preview offsets
        my $previewInfo = $$et{PREVIEW_INFO};
        delete $$et{PREVIEW_INFO};
        if ($result) {
            if ($previewInfo) {
                my $fixup = $previewInfo->{Fixup};
                # set preview offset (relative to start of makernotes, + 8 for makernote header)
                $fixup->SetMarkerPointers(\$result, 'PreviewImage', length($result) + 8);
                $result .= $$previewInfo{Data};
            }
            return $junk . substr($buff, $start, $hdrLen) . $result;
        }
    } else {
        # extract information
        $result = $et->ProcessDirectory(\%dirInfo, $tagTablePtr);
        # also extract as a block if necessary
        if ($et->Options('MakerNotes') or
            $$et{REQ_TAG_LOOKUP}{lc($$tagInfo{Name})})
        {
            # makernote header must be included in RebuildMakerNotes call
            $dirInfo{DirStart} -= 8;
            $dirInfo{DirLen} += 8;
            $$et{MAKER_NOTE_BYTE_ORDER} = GetByteOrder();
            # rebuild maker notes (creates $$et{MAKER_NOTE_FIXUP})
            my $val = Image::ExifTool::Exif::RebuildMakerNotes($et, $tagTablePtr, \%dirInfo);
            unless (defined $val) {
                $et->Warn('Error rebuilding maker notes (may be corrupt)') if $len > 4;
                $val = $buff,
            }
            my $key = $et->FoundTag($tagInfo, $val);
            $et->SetGroup($key, 'ExifIFD');
        }
    }
    SetByteOrder($oldOrder);
    return $result;
}

1;  # end

__END__

=head1 NAME

Image::ExifTool::Panasonic - Panasonic/Leica maker notes tags

=head1 SYNOPSIS

This module is loaded automatically by Image::ExifTool when required.

=head1 DESCRIPTION

This module contains definitions required by Image::ExifTool to interpret
Panasonic and Leica maker notes in EXIF information.

=head1 AUTHOR

Copyright 2003-2017, Phil Harvey (phil at owl.phy.queensu.ca)

This library is free software; you can redistribute it and/or modify it
under the same terms as Perl itself.

=head1 REFERENCES

=over 4

=item L<http://www.compton.nu/panasonic.html>

=item L<http://johnst.org/sw/exiftags/>

=item L<http://homepage3.nifty.com/kamisaka/makernote/makernote_pana.htm>

=item L<http://bretteville.com/pdfs/M8Metadata_v2.pdf>

=item L<http://www.digital-leica.com/lens_codes/index.html>

=item (...plus lots of testing with store demos and my wife's DMC-FS7!)

=back

=head1 ACKNOWLEDGEMENTS

Thanks to Tels, Marcel Coenen, Jens Duttke, Joerg, Michael Byczkowski, Carl
Bretteville, Zdenek Mihula and Olaf Ulrich for their contributions.

=head1 SEE ALSO

L<Image::ExifTool::TagNames/Panasonic Tags>,
L<Image::ExifTool(3pm)|Image::ExifTool>

=cut
