# HyperScrub Benchmarks

## Sequential Baseline

The sequential engine was benchmarked before introducing multiprocessing.

### Test configuration

| Property | Value |
|---|---:|
| Platform | Windows 10 |
| Processor | Intel Core i7-7700K @ 4.20 GHz |
| Physical cores | 4 |
| Logical processors | 8 |
| Memory | 15.96 GB |
| Python | 3.12.10 |
| Pages | 1,000 |
| Runs | 7 |
| Redactions per run | 2,000 |

### Results

| Metric | Result |
|---|---:|
| Fastest time | 1.5245 seconds |
| Median time | 1.5769 seconds |
| Mean time | 1.5887 seconds |
| Median throughput | 634.14 pages/second |

These results establish the baseline for evaluating future multicore implementations. Results may vary depending on hardware, operating system, PDF structure, and redaction rules.
