### Experiment 1 Log

- **SO_REUSEPORT** enabled
- **Receive Buffer Limit** configured
  - Command: `sysctl -w net.ipv4.tcp_rmem="40960 40960 40960"`

This configuration sets the minimum, default, and maximum receive buffer sizes for TCP connections to 40,960 bytes.