import os
import pytest

from io import BytesIO
from typing import List
from pathlib import Path

from protodump.cli import detect_all_proto_files_from_paths, main


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
        ),
        (
            [
                b"\n&tests/fixtures/rich_test_message.proto\x12\x07"
                b'foo.bar"\xab\x01\n\x0fSomeTestMessage\x12\x14\n\x0c'
                b"field_name_a\x18\x01 \x02(\t\x12\x14\n\x0cfield_name_b"
                b"\x18\x02 \x01(\x05\x12\x14\n\x0cfield_name_c\x18\x03 "
                b"\x03(\t\x12\x17\n\x0cfield_name_d\x18\x04 \x02(\x05:"
                b"\x014\x12\x18\n\x0cfield_name_e\x18\x05 \x02(\x05B\x02"
                b"\x18\x01\x12\x18\n\x0cfield_name_f\x18\x06 \x03(\x05B"
                b"\x02\x10\x01*\t\x08\xe8\x07\x10\x80\x80\x80\x80\x02*0"
                b"\n\x08SomeEnum\x12\x11\n\rSOME_ENUM_FOO\x10\x00\x12\x11"
                b"\n\rSOME_ENUM_BAR\x10\x01:3\n\x10field_name_other\x12"
                b"\x18.foo.bar.SomeTestMessage\x18\xb9` \x03(\t\t"
            ],
            ["rich_test_message.proto"],
            [
                """syntax = "proto2";

package foo.bar;

enum SomeEnum {
  SOME_ENUM_FOO = 0;
  SOME_ENUM_BAR = 1;
}
message SomeTestMessage {
  required string field_name_a = 1;
  optional int32 field_name_b = 2;
  repeated string field_name_c = 3;
  required int32 field_name_d = 4 [default = 4];
  required int32 field_name_e = 5 [deprecated = true];
  repeated int32 field_name_f = 6 [packed = true];
  extensions 1000 to 536870911;
}

extend .foo.bar.SomeTestMessage {
  repeated string field_name_other = 12345;
}"""
            ],
        ),
    ],
)
def test_parser_extracts_names(
    file_contents: List[bytes],
    expected_names: set[str],
    expected_sources: set[str],
    tmpdir: Path,
):
    files = [BytesIO(contents) for contents in file_contents]
    proto_files = detect_all_proto_files_from_paths(files)
    assert len(proto_files) == len(expected_names)
    assert set([f.name for f in proto_files]) == set(expected_names)
    assert set([f.source for f in proto_files]) == set(expected_sources)

    # Test the same with a temporary file via the "main" interface:
    for i, contents in enumerate(file_contents):
        with open(tmpdir.join(f"{i:05d}.bin"), "wb") as f:
            f.write(contents)

    out_path = tmpdir / "output"
    main([str(tmpdir), str(out_path)])
    assert len(list(os.listdir(str(out_path)))) == len(file_contents)
