from dataclasses import dataclass


@dataclass
class FaultConfig:
    drop_after_commit: bool = False
    fail_reads: int = 0
    response_delay_ms: int = 0
