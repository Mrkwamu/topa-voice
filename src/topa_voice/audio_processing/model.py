from dataclasses import dataclass


SUPPORTED_SAMPLE_RATES = frozenset({8000, 16000, 32000, 48000})


@dataclass(frozen=True)
class AudioFormat:
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2

    def __post_init__(self):
        self._validate_sample_rate()
        self._validate_channels()
        self._validate_sample_width()

    def _validate_sample_rate(self) -> None:
        if type(self.sample_rate) is not int:
            raise TypeError("Sample rate must be an integer.")

        if self.sample_rate not in SUPPORTED_SAMPLE_RATES:
            raise ValueError(
                f"Unsupported sample rate: {self.sample_rate}. "
                f"Supported values: {sorted(SUPPORTED_SAMPLE_RATES)}."
            )

    def _validate_channels(self) -> None:
        if type(self.channels) is not int:
            raise TypeError("Channels must be an integer.")

        if self.channels != 1:
            raise ValueError("Only mono audio (1 channel) is supported.")

    def _validate_sample_width(self) -> None:
        if type(self.sample_width) is not int:
            raise TypeError("Sample width must be an integer.")

        if self.sample_width != 2:
            raise ValueError("Only 16-bit PCM (2 bytes) is supported.")
