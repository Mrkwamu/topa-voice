from topa_voice.audio_processing.model import AudioFormat


class AudioChunker:
    CHUNK_MS = 20

    def __init__(self, audio_format: AudioFormat):
        self.audio_format = audio_format
        self.buffer = bytearray()
        self.bytes_per_frame = audio_format.channels * audio_format.sample_width

        frames_per_chunk = audio_format.sample_rate * self.CHUNK_MS // 1000

        self.bytes_per_chunk = frames_per_chunk * self.bytes_per_frame

    def add_audio(self, audio_data: bytes | bytearray | memoryview) -> list[bytes]:
        if not isinstance(audio_data, (bytes, bytearray, memoryview)):
            raise TypeError(
                f"Expected bytes for audio_data, got {type(audio_data).__name__}"
            )

        if not audio_data:
            return []

        self.buffer.extend(audio_data)
        return self._extract_chunks()

    def _extract_chunks(self) -> list[bytes]:
        size = self.bytes_per_chunk
        complete_chunks = []
        offset = 0

        while len(self.buffer) - offset >= size:
            chunk = bytes(self.buffer[offset : offset + size])

            complete_chunks.append(chunk)

            offset += size

        if offset > 0:
            del self.buffer[:offset]

        return complete_chunks

    def flush(self) -> list[bytes]:

        buffered_bytes = len(self.buffer)

        incomplete_bytes = buffered_bytes % self.bytes_per_frame

        if incomplete_bytes:
            raise ValueError(
        f"Cannot flush audio: {incomplete_bytes} trailing byte(s) "
        "do not form a complete PCM frame."
    )

        chunks = self._extract_chunks()

        if self.buffer:
            chunks.append(bytes(self.buffer))
            self.buffer.clear()

        return chunks
