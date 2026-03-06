"""Tests for sortphotos."""

from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.sortphotos import (
    ExifTool,
    check_for_early_morning_photos,
    get_oldest_timestamp,
    parse_date_exif,
    sortPhotos,
)


# ---------------------------------------------------------------------------
# parse_date_exif
# ---------------------------------------------------------------------------

class TestParseDateExif:
    def test_basic_datetime(self):
        result = parse_date_exif('2023:06:15 14:30:00')
        assert result == datetime(2023, 6, 15, 14, 30, 0)

    def test_date_only_defaults_to_noon(self):
        result = parse_date_exif('2023:06:15')
        assert result == datetime(2023, 6, 15, 12, 0, 0)

    def test_with_positive_timezone(self):
        # +05:00 means subtract 5 hours to get UTC
        result = parse_date_exif('2023:06:15 14:30:00+05:00')
        assert result == datetime(2023, 6, 15, 9, 30, 0)

    def test_with_negative_timezone(self):
        result = parse_date_exif('2023:06:15 14:30:00-03:00')
        assert result == datetime(2023, 6, 15, 17, 30, 0)

    def test_with_z_timezone(self):
        result = parse_date_exif('2023:06:15 14:30:00Z')
        assert result == datetime(2023, 6, 15, 14, 30, 0)

    def test_empty_string(self):
        assert parse_date_exif('') is None

    def test_zero_date(self):
        assert parse_date_exif('0000:00:00 00:00:00') is None

    def test_invalid_string(self):
        assert parse_date_exif('not a date') is None

    def test_decimal_in_date(self):
        # timestamps with only time have decimals
        assert parse_date_exif('12.34.56') is None

    def test_subsecond_time(self):
        result = parse_date_exif('2023:06:15 14:30:05.123')
        assert result == datetime(2023, 6, 15, 14, 30, 5)

    def test_hh_mm_only(self):
        result = parse_date_exif('2023:06:15 14:30')
        assert result == datetime(2023, 6, 15, 14, 30, 0)

    def test_very_old_date(self):
        # Dates before 1900 may or may not be parseable depending on platform.
        # The function tries strftime and returns None if it fails.
        result = parse_date_exif('1800:01:01 00:00:00')
        # On platforms where strftime handles pre-1900, we get a valid date
        if result is not None:
            assert result == datetime(1800, 1, 1, 0, 0, 0)
        # On platforms where it fails, we get None — both are acceptable

    def test_none_input(self):
        # str(None) = 'None' which should fail gracefully
        assert parse_date_exif(None) is None

    def test_integer_input(self):
        assert parse_date_exif(12345) is None

    def test_whitespace_only(self):
        assert parse_date_exif('   ') is None

    def test_invalid_month(self):
        assert parse_date_exif('2023:13:15 14:30:00') is None

    def test_invalid_day(self):
        assert parse_date_exif('2023:06:32 14:30:00') is None


# ---------------------------------------------------------------------------
# get_oldest_timestamp
# ---------------------------------------------------------------------------

class TestGetOldestTimestamp:
    def test_single_date(self):
        data = {
            'SourceFile': '/photo.jpg',
            'EXIF:CreateDate': '2023:06:15 14:30:00',
        }
        src, date, keys = get_oldest_timestamp(data, ['File'], [])
        assert src == '/photo.jpg'
        assert date == datetime(2023, 6, 15, 14, 30, 0)
        assert keys == ['EXIF:CreateDate']

    def test_multiple_dates_picks_oldest(self):
        data = {
            'SourceFile': '/photo.jpg',
            'EXIF:CreateDate': '2023:06:15 14:30:00',
            'EXIF:DateTimeOriginal': '2023:06:14 10:00:00',
        }
        src, date, keys = get_oldest_timestamp(data, ['File'], [])
        assert date == datetime(2023, 6, 14, 10, 0, 0)
        assert keys == ['EXIF:DateTimeOriginal']

    def test_ignores_specified_groups(self):
        data = {
            'SourceFile': '/photo.jpg',
            'File:FileModifyDate': '2020:01:01 00:00:00',
            'EXIF:CreateDate': '2023:06:15 14:30:00',
        }
        src, date, keys = get_oldest_timestamp(data, ['File'], [])
        assert date == datetime(2023, 6, 15, 14, 30, 0)

    def test_ignores_gps_tags(self):
        data = {
            'SourceFile': '/photo.jpg',
            'Composite:GPSDateTime': '2020:01:01 00:00:00',
            'EXIF:CreateDate': '2023:06:15 14:30:00',
        }
        src, date, keys = get_oldest_timestamp(data, ['File'], [])
        assert date == datetime(2023, 6, 15, 14, 30, 0)

    def test_ignores_icc_profile_always(self):
        data = {
            'SourceFile': '/photo.jpg',
            'ICC_Profile:ProfileDateTime': '2020:01:01 00:00:00',
            'EXIF:CreateDate': '2023:06:15 14:30:00',
        }
        src, date, keys = get_oldest_timestamp(data, [], [])
        assert date == datetime(2023, 6, 15, 14, 30, 0)

    def test_ignores_xmp_historywhen_always(self):
        data = {
            'SourceFile': '/photo.jpg',
            'XMP:HistoryWhen': '2020:01:01 00:00:00',
            'EXIF:CreateDate': '2023:06:15 14:30:00',
        }
        src, date, keys = get_oldest_timestamp(data, [], [])
        assert date == datetime(2023, 6, 15, 14, 30, 0)

    def test_ignores_specified_tags(self):
        data = {
            'SourceFile': '/photo.jpg',
            'EXIF:CreateDate': '2020:01:01 00:00:00',
            'EXIF:DateTimeOriginal': '2023:06:15 14:30:00',
        }
        src, date, keys = get_oldest_timestamp(data, [], ['EXIF:CreateDate'])
        assert date == datetime(2023, 6, 15, 14, 30, 0)

    def test_no_valid_dates(self):
        data = {
            'SourceFile': '/photo.jpg',
            'EXIF:Something': 'not a date',
        }
        src, date, keys = get_oldest_timestamp(data, ['File'], [])
        assert date is None
        assert keys == []

    def test_equal_dates_both_reported(self):
        data = {
            'SourceFile': '/photo.jpg',
            'EXIF:CreateDate': '2023:06:15 14:30:00',
            'EXIF:DateTimeOriginal': '2023:06:15 14:30:00',
        }
        src, date, keys = get_oldest_timestamp(data, ['File'], [])
        assert len(keys) == 2
        assert date == datetime(2023, 6, 15, 14, 30, 0)

    def test_list_type_date_values(self):
        data = {
            'SourceFile': '/photo.jpg',
            'EXIF:CreateDate': ['2023:06:15 14:30:00', '2023:07:01 10:00:00'],
        }
        src, date, keys = get_oldest_timestamp(data, ['File'], [])
        assert date == datetime(2023, 6, 15, 14, 30, 0)

    def test_only_sourcefile_returns_none(self):
        data = {'SourceFile': '/photo.jpg'}
        src, date, keys = get_oldest_timestamp(data, ['File'], [])
        assert date is None


# ---------------------------------------------------------------------------
# check_for_early_morning_photos
# ---------------------------------------------------------------------------

class TestCheckForEarlyMorningPhotos:
    def test_no_adjustment_at_noon(self):
        date = datetime(2023, 6, 15, 12, 0, 0)
        result = check_for_early_morning_photos(date, 4)
        assert result == date

    def test_adjustment_at_2am(self):
        date = datetime(2023, 6, 15, 2, 0, 0)
        result = check_for_early_morning_photos(date, 4)
        assert result.day == 14  # pushed to previous day

    def test_no_adjustment_when_day_begins_0(self):
        date = datetime(2023, 6, 15, 2, 0, 0)
        result = check_for_early_morning_photos(date, 0)
        assert result == date

    def test_exactly_at_day_begins_no_adjustment(self):
        date = datetime(2023, 6, 15, 4, 0, 0)
        result = check_for_early_morning_photos(date, 4)
        assert result == date

    def test_midnight_with_day_begins_4(self):
        date = datetime(2023, 6, 15, 0, 0, 0)
        result = check_for_early_morning_photos(date, 4)
        assert result.day == 14


# ---------------------------------------------------------------------------
# ExifTool
# ---------------------------------------------------------------------------

class TestExifTool:
    @pytest.mark.skipif(
        shutil.which('perl') is None,
        reason='perl not available',
    )
    def test_context_manager_starts_and_stops_process(self):
        with ExifTool() as et:
            assert et.process.pid is not None
            assert et.process.poll() is None  # still running
            pid = et.process.pid
        # after exit, process should have terminated
        assert et.process.poll() is not None

    def test_get_metadata_raises_on_invalid_json(self):
        et = ExifTool()
        et.execute = MagicMock(return_value='not valid json')
        with pytest.raises(RuntimeError, match='No files to parse or invalid data'):
            et.get_metadata()

    def test_get_metadata_parses_valid_json(self):
        et = ExifTool()
        et.execute = MagicMock(return_value='[{"SourceFile": "test.jpg"}]')
        result = et.get_metadata()
        assert result == [{"SourceFile": "test.jpg"}]


# ---------------------------------------------------------------------------
# sortPhotos (integration tests with mocked ExifTool)
# ---------------------------------------------------------------------------

class TestSortPhotos:
    def _create_source_files(self, src_dir: Path, filenames: list[str]) -> None:
        """Create test files with distinct content."""
        for i, name in enumerate(filenames):
            filepath = src_dir / name
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(f'content of {name} #{i}')

    def _mock_metadata(self, src_dir: Path, file_dates: dict[str, str]) -> list[dict]:
        """Create mock metadata for files."""
        metadata = []
        for filename, date_str in file_dates.items():
            entry = {
                'SourceFile': str(src_dir / filename),
                'EXIF:CreateDate': date_str,
            }
            metadata.append(entry)
        return metadata

    def test_test_mode_does_not_move_files(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        self._create_source_files(src_dir, ['photo1.jpg'])
        metadata = self._mock_metadata(src_dir, {'photo1.jpg': '2023:06:15 14:30:00'})

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None, test=True)

        # file should still be in source
        assert (src_dir / 'photo1.jpg').exists()
        # destination should not have the file
        assert not list(dest_dir.rglob('*.jpg'))
        assert stats['processed'] == 1

    def test_copy_mode_preserves_source(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        self._create_source_files(src_dir, ['photo1.jpg'])
        metadata = self._mock_metadata(src_dir, {'photo1.jpg': '2023:06:15 14:30:00'})

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None, copy_files=True)

        # source file preserved
        assert (src_dir / 'photo1.jpg').exists()
        # destination has the file
        dest_files = list(dest_dir.rglob('*.jpg'))
        assert len(dest_files) == 1
        assert stats['processed'] == 1

    def test_move_mode_removes_source(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        self._create_source_files(src_dir, ['photo1.jpg'])
        metadata = self._mock_metadata(src_dir, {'photo1.jpg': '2023:06:15 14:30:00'})

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None, copy_files=False)

        # source file gone
        assert not (src_dir / 'photo1.jpg').exists()
        # destination has it
        dest_files = list(dest_dir.rglob('*.jpg'))
        assert len(dest_files) == 1
        assert stats['processed'] == 1

    def test_duplicate_detection_skips_identical(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        # create source file
        (src_dir / 'photo1.jpg').write_text('identical content')

        # create identical file at destination
        dest_subdir = dest_dir / '2023' / '06-Jun'
        dest_subdir.mkdir(parents=True)
        (dest_subdir / 'photo1.jpg').write_text('identical content')

        metadata = self._mock_metadata(src_dir, {'photo1.jpg': '2023:06:15 14:30:00'})

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None, copy_files=True)

        assert stats['skipped_duplicate'] == 1
        assert stats['processed'] == 0

    def test_collision_appends_number(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        # create source file
        (src_dir / 'photo1.jpg').write_text('new content')

        # create different file at destination with same name
        dest_subdir = dest_dir / '2023' / '06-Jun'
        dest_subdir.mkdir(parents=True)
        (dest_subdir / 'photo1.jpg').write_text('old content')

        metadata = self._mock_metadata(src_dir, {'photo1.jpg': '2023:06:15 14:30:00'})

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None, copy_files=True)

        assert stats['renamed_collision'] >= 1
        # should have both original and renamed file
        dest_files = list(dest_subdir.glob('*.jpg'))
        assert len(dest_files) == 2

    def test_hidden_files_skipped(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        self._create_source_files(src_dir, ['.hidden.jpg'])
        metadata = self._mock_metadata(src_dir, {'.hidden.jpg': '2023:06:15 14:30:00'})

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None, test=True)

        assert stats['skipped_hidden'] == 1
        assert stats['processed'] == 0

    def test_no_date_skipped(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        self._create_source_files(src_dir, ['nodate.jpg'])
        metadata = [{'SourceFile': str(src_dir / 'nodate.jpg'), 'EXIF:Something': 'not a date'}]

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None, test=True)

        assert stats['skipped_no_date'] == 1

    def test_exclude_patterns(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        self._create_source_files(src_dir, ['photo.jpg', 'photo.raw'])
        metadata = self._mock_metadata(src_dir, {
            'photo.jpg': '2023:06:15 14:30:00',
            'photo.raw': '2023:06:15 14:30:00',
        })

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None,
                             test=True, exclude_patterns=['*.raw'])

        assert stats['skipped_excluded'] == 1
        assert stats['processed'] == 1

    def test_nonexistent_source_raises(self, tmp_path):
        with pytest.raises(Exception, match='Source directory does not exist'):
            sortPhotos(str(tmp_path / 'nonexistent'), str(tmp_path), '%Y/%m-%b', None)

    def test_rename_format(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        self._create_source_files(src_dir, ['photo1.JPG'])
        metadata = self._mock_metadata(src_dir, {'photo1.JPG': '2023:06:15 14:30:00'})

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b',
                             '%Y%m%d_%H%M%S', copy_files=True)

        dest_files = list(dest_dir.rglob('*.jpg'))
        assert len(dest_files) == 1
        # renamed file should have date-based name with lowercase extension
        assert dest_files[0].name == '20230615_143000.jpg'

    def test_stats_returned(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        self._create_source_files(src_dir, ['photo1.jpg'])
        metadata = self._mock_metadata(src_dir, {'photo1.jpg': '2023:06:15 14:30:00'})

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None, test=True)

        assert isinstance(stats, dict)
        assert 'processed' in stats
        assert 'skipped_no_date' in stats
        assert 'skipped_hidden' in stats
        assert 'skipped_duplicate' in stats
        assert 'errors' in stats

    def test_parallel_jobs(self, tmp_path):
        src_dir = tmp_path / 'src'
        dest_dir = tmp_path / 'dest'
        src_dir.mkdir()
        dest_dir.mkdir()

        files = {f'photo{i}.jpg': f'2023:06:{15+i:02d} 14:30:00' for i in range(5)}
        self._create_source_files(src_dir, list(files.keys()))
        metadata = self._mock_metadata(src_dir, files)

        with patch('src.sortphotos.ExifTool') as MockExifTool:
            mock_et = MagicMock()
            mock_et.get_metadata.return_value = metadata
            mock_et.__enter__ = MagicMock(return_value=mock_et)
            mock_et.__exit__ = MagicMock(return_value=False)
            MockExifTool.return_value = mock_et

            stats = sortPhotos(str(src_dir), str(dest_dir), '%Y/%m-%b', None,
                             copy_files=True, jobs=2)

        assert stats['processed'] == 5
        dest_files = list(dest_dir.rglob('*.jpg'))
        assert len(dest_files) == 5
