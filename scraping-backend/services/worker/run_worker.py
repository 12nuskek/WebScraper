#!/usr/bin/env python
"""
Worker runner script.

Usage:
    python run_worker.py [--poll-interval SECONDS]
"""

import argparse
from basic_worker import BasicWorker


def main():
    parser = argparse.ArgumentParser(description='Run the basic web scraping worker')
    parser.add_argument(
        '--poll-interval', 
        type=int, 
        default=5,
        help='Seconds to wait between checking for new jobs (default: 5)'
    )
    
    args = parser.parse_args()
    
    worker = BasicWorker(poll_interval=args.poll_interval)
    worker.start()


if __name__ == '__main__':
    main()