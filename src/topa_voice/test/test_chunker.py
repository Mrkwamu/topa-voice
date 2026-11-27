from topa_voice.audio_processing.model import AudioFormat
from topa_voice.audio_processing.wav import AudioChunker


def make_chunker(sample_rate=8000):
    return AudioChunker(AudioFormat(sample_rate=sample_rate))


def expect_exception(exception_type, operation):
    try:
        operation()
    except exception_type:
        return

    raise AssertionError(f"Expected {exception_type.__name__}")


def test_buffers_incomplete_audio():
    chunker = make_chunker()

    chunks = chunker.add_audio(bytes(300))

    assert chunks == []
    assert len(chunker.buffer) == 300


def test_extracts_multiple_chunks():
    chunker = make_chunker()

    chunker.add_audio(bytes(300))
    chunks = chunker.add_audio(bytes(1000))

    assert len(chunks) == 4
    assert all(len(chunk) == 320 for chunk in chunks)
    assert len(chunker.buffer) == 20


def test_flush_returns_remaining_audio():
    chunker = make_chunker()

    chunker.add_audio(bytes(1300))
    chunks = chunker.flush()

    assert len(chunks) == 1
    assert len(chunks[0]) == 20
    assert len(chunker.buffer) == 0


def test_flush_rejects_incomplete_frame():
    chunker = make_chunker()

    chunks = chunker.add_audio(bytes(321))

    assert len(chunks) == 1
    assert len(chunker.buffer) == 1

    expect_exception(ValueError, chunker.flush)

    # Buffer should remain untouched after the error.
    assert len(chunker.buffer) == 1


def test_empty_audio():
    chunker = make_chunker()

    chunker.add_audio(bytes(100))
    chunks = chunker.add_audio(b"")

    assert chunks == []
    assert len(chunker.buffer) == 100


def test_rejects_invalid_input():
    chunker = make_chunker()

    expect_exception(
        TypeError,
        lambda: chunker.add_audio("not audio"),
    )


def test_accepts_bytearray_and_memoryview():
    chunker = make_chunker()

    chunker.add_audio(bytearray(160))
    chunks = chunker.add_audio(memoryview(bytes(160)))

    assert len(chunks) == 1
    assert len(chunks[0]) == 320


def test_chunkers_have_independent_buffers():
    chunker1 = make_chunker()
    chunker2 = make_chunker()

    chunker1.add_audio(bytes(100))

    assert len(chunker1.buffer) == 100
    assert len(chunker2.buffer) == 0


def test_chunk_size_depends_on_sample_rate():
    chunker_8k = make_chunker(8000)
    chunker_16k = make_chunker(16000)

    assert chunker_8k.bytes_per_chunk == 320
    assert chunker_16k.bytes_per_chunk == 640


if __name__ == "__main__":
    tests = [
        test_buffers_incomplete_audio,
        test_extracts_multiple_chunks,
        test_flush_returns_remaining_audio,
        test_flush_rejects_incomplete_frame,
        test_empty_audio,
        test_rejects_invalid_input,
        test_accepts_bytearray_and_memoryview,
        test_chunkers_have_independent_buffers,
        test_chunk_size_depends_on_sample_rate,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\n{len(tests)} tests passed.")
