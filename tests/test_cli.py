import pytest

from io import BytesIO
from typing import Iterable

from protodump.cli import detect_all_proto_files_from_paths


@pytest.mark.parametrize(
    "file_contents,expected_names,expected_sources",
    [
        (
            [
                b"abcdefgb'\n&tests/fixtures/some_test_message.proto\"="
                b"\n\x0fSomeTestMessage\x12\x14\n\x0c\x66ield_name_a\x18"
                b"\x01 \x02(\t\x12\x14\n\x0c\x66ield_name_b\x18\x02 \x02(\x05'"
                b"asgiasgihasokghak"
            ],
            ["some_test_message.proto"],
            [
                """syntax = "proto2";

message SomeTestMessage {
  required string field_name_a = 1;
  required int32 field_name_b = 2;
}
"""
            ],
        )
    ],
)
def test_parser_extracts_names(
    file_contents: Iterable[bytes],
    expected_names: set[str],
    expected_sources: set[str],
):
    files = [BytesIO(contents) for contents in file_contents]
    proto_files = detect_all_proto_files_from_paths(files)
    assert set([f.name for f in proto_files]) == set(expected_names)
    assert set([f.source for f in proto_files]) == set(expected_sources)
